"""Cleaning of layer A: the only price series the rest of the thesis may read.

Defects handled, all measured on the 31-10-2026 build (docs/eda/clean-validation.md):

- rows with close <= 0: listed but never traded, dropped.
- zero matched volume: SSI carries a stale close and placeholder open/high/low. The session stays
  as a row (non-trading is information) but its prices are nulled.
- non-tick "raw" prices (ELC to 2022-09, MCP): the OHLC fields are already scaled by SSI while
  ref_price and avg_price are not, so the ratio to ref_price means nothing. Treated like
  non-trading, flagged `price_suspect`.
- ref_price <= 0: limits unknown for that session, flagged `limit_known = False`.
- `ClosePriceAdjusted` misses about half of the ex-right dates, so the back-adjustment is
  rebuilt from the exchange reference price: on an ex-right date, ref / previous close is the
  exact factor.

ref / previous close is only trustworthy on liquid names. On thin names the close field goes
stale and the ratio moves with no corporate action (against layer B's factor: 98-100% match in
the top 150 by traded value, 35% below it). So a drop counts as an ex-right only if the name was
liquid that day, the drop is too big to be a stale close, or SSI's own factor stepped too.
A missed event leaves one bad return on that date; it does not distort any other date.
"""
from __future__ import annotations

from dataclasses import dataclass

import polars as pl

_PRICE_COLS = ("open", "high", "low", "close")


@dataclass(frozen=True)
class CleanConfig:
    start: str = "2020-02-26"       # the cross-section holds one ticker before this date
    tick_vnd: float = 10.0          # every HOSE price is a multiple of the smallest tick
    adv_window: int = 20
    adv_min_samples: int = 10
    liquid_top_n: int = 150
    ex_ratio_max: float = 0.995     # smaller drops are rounding, not corporate actions
    ex_ratio_certain: float = 0.89  # below the -7% band plus a margin: cannot be a stale close
    ssi_step_min: float = 0.005
    ref_mid_tolerance: float = 0.01 # limits round to ticks, so the midpoint only roughly equals ref


def add_validity_flags(df: pl.DataFrame, cfg: CleanConfig) -> pl.DataFrame:
    """Drop never-traded rows; flag non-trading, non-tick and limit-less sessions."""
    return (
        df.filter((pl.col("instrument") == "stock") & (pl.col("close") > 0)
                  & (pl.col("date") >= pl.lit(cfg.start).str.to_date()))
        .sort("ticker", "date")
        .with_columns(
            (pl.col("match_vol") > 0).alias("is_traded"),
            ((pl.col("close") % cfg.tick_vnd).abs() > 1e-6).alias("price_suspect"),
            (pl.col("ref_price") > 0).alias("limit_known"),
        )
        .with_columns((pl.col("is_traded") & ~pl.col("price_suspect")).alias("has_price"))
    )


def add_liquidity(df: pl.DataFrame, cfg: CleanConfig) -> pl.DataFrame:
    """Trailing median matched value, lagged one session so today's rank uses no future data."""
    return (
        df.with_columns(
            pl.col("match_val").shift(1)
            .rolling_median(cfg.adv_window, min_samples=cfg.adv_min_samples)
            .over("ticker").alias("adv_vnd"))
        .with_columns(
            pl.when(pl.col("adv_vnd").is_not_null())
            .then(pl.col("adv_vnd").rank("ordinal", descending=True).over("date"))
            .alias("adv_rank"))
        .with_columns((pl.col("adv_rank") <= cfg.liquid_top_n).fill_null(False).alias("is_liquid"))
    )


def add_ex_ratio(df: pl.DataFrame, cfg: CleanConfig) -> pl.DataFrame:
    """`ex_ratio` = ref / previous close on accepted ex-right dates, 1.0 everywhere else."""
    prev_close = (
        pl.when(pl.col("is_traded")).then(pl.col("close")).otherwise(pl.col("ref_price"))
        .shift(1).over("ticker")
    )
    prev_ok = (~pl.col("price_suspect")).shift(1).over("ticker").fill_null(False)
    ssi_step = (pl.col("adj_factor") / pl.col("adj_factor").shift(1).over("ticker") - 1).abs()
    # On some ex-right dates ref_price stays at the old level while ceiling and floor have moved
    # (SSI 2026-08-17: ref 24500, floor 18250). The band midpoint is then the real reference.
    mid = (pl.col("ceiling_price") + pl.col("floor_price")) / 2
    effective_ref = (
        pl.when(((mid / pl.col("ref_price")) - 1).abs() > cfg.ref_mid_tolerance).then(mid)
        .otherwise(pl.col("ref_price"))
    )
    return (
        df.with_columns((effective_ref / prev_close).alias("_r"), ssi_step.alias("_ssi"))
        .with_columns(
            pl.when(~pl.col("limit_known") | pl.col("price_suspect") | ~prev_ok
                    | pl.col("_r").is_null() | (pl.col("_r") <= 0) | (pl.col("_r") >= cfg.ex_ratio_max))
            .then(pl.lit(None, dtype=pl.String))
            .when(pl.col("_r") < cfg.ex_ratio_certain).then(pl.lit("band"))
            .when(pl.col("is_liquid")).then(pl.lit("liquid"))
            .when(pl.col("_ssi") > cfg.ssi_step_min).then(pl.lit("ssi"))
            .otherwise(pl.lit(None, dtype=pl.String))
            .alias("ex_source"))
        .with_columns(
            pl.when(pl.col("ex_source").is_not_null()).then(pl.col("_r")).otherwise(1.0).alias("ex_ratio"))
        .drop("_r", "_ssi")
    )


def repair_ohlc(df: pl.DataFrame) -> pl.DataFrame:
    """Make high/low contain open/close (737 bars, nearly all 2020-21). The close is left alone:
    the next session's reference confirms it, so the open and the range are what is wrong."""
    hi = pl.max_horizontal("high", "close")
    lo = pl.min_horizontal("low", "close")
    bad = (pl.col("open") <= 0) | (pl.col("open") > pl.col("high")) | (pl.col("open") < pl.col("low")) \
        | (pl.col("close") > pl.col("high")) | (pl.col("close") < pl.col("low"))
    return df.with_columns(bad.fill_null(False).alias("ohlc_repaired"), hi.alias("high"), lo.alias("low")) \
        .with_columns(
            pl.when(pl.col("open") <= 0).then(pl.col("close"))
            .otherwise(pl.col("open").clip(pl.col("low"), pl.col("high"))).alias("open"))


def add_back_adjustment(df: pl.DataFrame) -> pl.DataFrame:
    """Back-adjust onto the latest session: a bar is scaled by every ex-right after it."""
    factor = (
        pl.col("ex_ratio").reverse().cum_prod().reverse().shift(-1).fill_null(1.0).over("ticker")
    )
    return df.rename({"close_adj": "ssi_close_adj", "adj_factor": "ssi_adj_factor"}, strict=False) \
        .with_columns(factor.alias("adj_factor")) \
        .with_columns(
            *[pl.when(pl.col("has_price")).then(pl.col(c)).otherwise(None).alias(c) for c in _PRICE_COLS],
            pl.when(pl.col("has_price")).then(pl.col("match_vol") / pl.col("adj_factor")).otherwise(0.0)
            .alias("volume_adj"),
        ) \
        .with_columns(*[(pl.col(c) * pl.col("adj_factor")).alias(f"{c}_adj") for c in _PRICE_COLS])


def add_limit_flags(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("limit_known") & (pl.col("close") >= pl.col("ceiling_price"))).fill_null(False).alias("at_ceiling"),
        (pl.col("limit_known") & (pl.col("close") <= pl.col("floor_price"))).fill_null(False).alias("at_floor"),
    )


def clean_layer_a(df: pl.DataFrame, cfg: CleanConfig = CleanConfig()) -> pl.DataFrame:
    """Layer A as built by `ssi_fastconnect.build_layer_a` -> the frame downstream code reads."""
    raw_adj = df.select(pl.exclude("open_adj", "high_adj", "low_adj", "match_vol_adj", "at_ceiling", "at_floor"))
    flagged = add_ex_ratio(add_liquidity(add_validity_flags(raw_adj, cfg), cfg), cfg)
    out = add_limit_flags(add_back_adjustment(repair_ohlc(flagged)))
    return out.drop("has_price").sort("ticker", "date")
