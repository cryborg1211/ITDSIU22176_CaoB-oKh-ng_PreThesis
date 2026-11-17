"""Chapter 3, Section 3.1 (Data), English and Vietnamese, for the Word export.

Mirrors report/chapters/03-methodology.tex; the LaTeX is the source of truth. Block kinds are the
ones build_thesis_docx.py renders: h1/h2/h3/p/lead/lp/ul/table/fig/algo.
"""
from __future__ import annotations

Block = tuple

TABLE_LAYERS_ROWS = [
    ["Period", "2020-02 – 2026-10", "2013 – 2026-10"],
    ["Stocks", "448", "308"],
    ["Stock-sessions", "648,901", "861,923"],
    ["Delisted / moved stocks included", "36", "0"],
    ["Raw prices, reference/limit prices", "yes", "no"],
    ["Foreign flow", "yes", "no"],
    ["Median bar completeness (a)", "1.000 (p5 0.995)", "1.000 (p5 0.971)"],
]
TABLE_ROWS_EN = [
    ["Stock rows in layer A", "689,541"],
    ["Dropped: zero close (never traded) or before 26 Feb 2020", "40,674"],
    ["Kept", "648,867"],
    ["   flagged non-trading (zero matched volume)", "51,132"],
    ["   flagged price suspect (ELC to Sep 2022, MCP)", "641"],
    ["   flagged limits unknown (zero reference price)", "2,685"],
    ["   repaired bars (range not containing open/close)", "737"],
    ["Usable priced bars", "597,097"],
    ["   of which on top-150 sessions", "248,585"],
]
TABLE_GAPS = [["487", "291"], ["216", "115"], ["283", "2"], ["44", "1"]]
TABLE_BUCKETS = [
    ["1–50", "82,950", "0.004", "2.67", "2.81", "158.2"],
    ["51–150", "165,900", "0.04", "3.24", "2.85", "20.1"],
    ["151–300", "248,850", "0.91", "2.97", "1.87", "0.78"],
    [">300", "146,692", "33.1", "2.83", "1.94", "0.008"],
]

CH3_EN: list[Block] = [
    ("h1", "Chapter 3. Methodology"),
    ("h2", "3.1 Data"),
    ("p", "Every number in this section is produced by code in the thesis repository: scripts/build_data.py "
          "(collection), src/wyckoff/data/clean.py and scripts/build_clean.py (cleaning and its validation), "
          "scripts/eda_data_layers.py and scripts/eda_universe.py (exploratory analysis). Prices are in absolute VND."),
    ("h3", "3.1.1 Sources"),
    ("p", "Two daily price layers were built for the HOSE equity market."),
    ("lp", "Layer A. ", "The SSI FastConnect Data API (DailyStockPrice), pulled market-wide. It returns, for every "
           "listed instrument and session, raw OHLCV, the exchange's reference, ceiling and floor prices, an adjusted "
           "close, matched and put-through volume and value, and foreign buy/sell flow. Because each request is made by "
           "date rather than by ticker, stocks later delisted or moved to another exchange are included: the layer is "
           "free of survivorship bias. The cross-section is complete from 26 February 2020."),
    ("lp", "Layer B. ", "A one-pass refetch of adjusted daily bars from a third-party vendor (VCI), 2013–2026. It is "
           "longer, but it only holds tickers still listed when it was fetched and it carries no raw prices, limit "
           "prices or foreign flow."),
    ("p", "The two layers are not spliced into one series. They use different adjustment conventions (Section 3.1.5), "
          "so joining them would put a seam at the splice date."),
    ("h3", "3.1.2 Collection"),
    ("p", "The API serves at most 30 calendar days per request, so the period is split into 83 consecutive windows. "
          "Each window is requested as a single page and accepted only if the number of unique (ticker, date) pairs "
          "equals the total the server reports; a window that fails is refetched whole, up to three times. All windows "
          "are fetched on the same day, so the vendor's adjusted prices share one adjustment basis."),
    ("p", "Both rules exist because of failures met on the way. With the default page size the server's pages overlap: "
          "on average 35% of the rows of a window were repeats while other rows were never served, yet the row count "
          "matched the reported total. The first build looked complete and held 533 bars for HPG over 6.7 years instead "
          "of about 1,680. Counting rows is therefore not a completeness check; counting unique keys is."),
    ("h3", "3.1.3 Coverage"),
    ("table", "Table 3.1: Daily data layers for HOSE stocks.", ["", "Layer A (SSI)", "Layer B (VCI)"],
     TABLE_LAYERS_ROWS, "(a) Bars per stock divided by exchange sessions between its first and last bar."),
    ("fig", "Figure 3.1: HOSE stocks with at least one bar per year in each layer.", "data_coverage.png", 14),
    ("p", "Of the 448 stocks in layer A, 140 are absent from layer B, 35 of them stocks that stopped trading on HOSE "
          "before the end of the sample. A backtest on layer B alone would only ever trade companies known, in "
          "hindsight, to have survived."),
    ("h3", "3.1.4 Cleaning"),
    ("p", "The raw feed reports success while containing rows that are wrong in ways that raise no error. Algorithm 1 "
          "lists the cleaning steps in the order they run, and Table 3.2 accounts for every row."),
    ("algo", "Algorithm 1: Cleaning of layer A", [
        "Keep stocks only; drop rows with a zero close (listed, never traded) and rows before 26 Feb 2020.",
        "Flag non-trading: zero matched volume. Keep the row, discard its prices (placeholders).",
        "Flag price suspect: a raw price that is not a multiple of the 10 VND tick (already scaled by the vendor); "
        "treat as non-trading.",
        "Flag limits unknown: reference price is zero; never count such a session as a limit-lock.",
        "Compute liquidity: 20-session median matched value, shifted one session; rank stocks each day.",
        "For each stock and session: reference = midpoint of ceiling and floor if it differs from the reported "
        "reference by more than 1%, else the reported reference; r = reference / previous close.",
        "If r < 0.995 and (r < 0.89, or the stock ranks in the top 150, or the vendor's factor also stepped), "
        "mark an ex-right with ratio r.",
        "Adjustment factor of a bar = product of all ex-right ratios after it.",
        "Repair bars whose high/low do not contain open/close, keeping the close.",
        "Adjusted prices = raw × factor; adjusted volume = volume / factor.",
    ]),
    ("table", "Table 3.2: Row accounting of the cleaning step (stocks only).", ["Step", "Rows"], TABLE_ROWS_EN, None),
    ("p", "Two of these defects matter far more than their size suggests. The non-trading rows (7.9% of the kept rows) "
          "carry placeholder prices: 29,200 of them are not even flat bars, so each would print a fake bar spanning the "
          "daily band. And the vendor's adjustment is incomplete, the subject of the next section."),
    ("h3", "3.1.5 Corporate-Action Adjustment"),
    ("p", "Stock dividends, bonus shares and rights issues lower the price on the ex-right date without any change in "
          "value; on an unadjusted series these drops look like crashes. SSI's adjusted close is correct where it "
          "adjusts, stepping on the ex-date itself, but it covers only 195 of the 350 large ex-right sessions and ignores "
          "cash dividends. Layer B adjusts cash dividends too, which is why the two layers agree within 0.5% on only 50% "
          "of 2020 sessions but 87% of 2026 sessions while the median ratio stays at 1.00 every year."),
    ("p", "The thesis therefore rebuilds the adjustment from the exchange reference price, which on HOSE equals the "
          "previous close on every session except an ex-right date (Algorithm 1). On some ex-right dates the reference "
          "field keeps its old value while the ceiling and floor have moved, so the band midpoint is used instead. On "
          "thinly traded stocks the close goes stale and the ratio moves without any corporate action, so a small drop "
          "is accepted only on a liquid stock or when the vendor's own factor confirms it."),
    ("p", "This yields 1,985 ex-right events, of which the vendor's factor covers 1,325. Layer B is not an input to this "
          "procedure, so it serves as an independent check: where it could be compared, its factor stepped by the same "
          "ratio on the same date in 97–99% of events. Table 3.3 shows the result."),
    ("table", "Table 3.3: Opening gaps below −11% (impossible inside the ±7% band without a corporate action), "
              "26 Feb 2020 – 30 Oct 2026.", ["Series", "All stocks", "Top-150 sessions"],
     [[name, *v] for name, v in zip(["Layer A, raw", "Layer A, vendor adjusted", "Layer B, adjusted",
                                     "Layer A, cleaned"], TABLE_GAPS)], None),
    ("h3", "3.1.6 Exploratory Analysis"),
    ("p", "The analysis asks one practical question: which stocks should the models learn from and be evaluated on? "
          "Liquidity ranks are the lagged ranks of Algorithm 1, so a stock's membership on any day uses only earlier sessions."),
    ("lp", "Trading is highly concentrated. ", "On the median day the 30 most traded stocks account for 64.8% of matched "
           "value, the top 100 for 94.5% and the top 150 for 98.5% (Figure 3.2). Beyond the top 200 lies 0.4% of the "
           "market's value."),
    ("fig", "Figure 3.2: Share of each day's matched value traded in the N most traded stocks (orange line: N = 150).",
     "universe_concentration.png", 13),
    ("lp", "Data quality falls with liquidity. ", "Table 3.4 splits all ranked stock-sessions into liquidity buckets. "
           "Inside the top 150 almost every session has a trade; beyond rank 300 a third of the sessions have none, and "
           "the median stock trades about 8 million VND a day."),
    ("table", "Table 3.4: Stock-sessions by liquidity bucket (rank by lagged 20-session median matched value).",
     ["Rank", "Stock-sessions", "No trade (%)", "At ceiling (%)", "At floor (%)", "Median value (bn VND)"],
     TABLE_BUCKETS, None),
    ("lp", "The liquid universe changes, slowly. ", "306 different stocks were in the top 150 at some point, and a member "
           "stays a median of 685 sessions; on a typical day one stock enters and one leaves. Seventeen of the 306 were "
           "later delisted (among them FLC, HAI, HVG and POM). A universe picked from today's most traded stocks and "
           "applied to the past would silently drop all seventeen."),
    ("lp", "The price band truncates returns. ", "Daily returns of top-150 stocks have a standard deviation (σ) of 2.67% "
           "and an excess kurtosis of 6.5: peaked with fat tails, as usual for stocks. Unusually, almost no day lies "
           "beyond 3σ (0.006%, against 0.27% for a normal distribution): 3σ is about 8%, and the ±7% band does not allow "
           "it. Extreme moves are spread over consecutive limit-locked sessions instead (Figure 3.3), which is exactly "
           "what makes exits uncertain."),
    ("fig", "Figure 3.3: Daily returns of top-150 and other stocks (log density). Both stop at the ±7% band.",
     "universe_returns.png", 13),
    ("lp", "Stocks move together. ", "The 30 most traded stocks have a mean pairwise return correlation of 0.39, from "
           "0.02 to 0.82 (Figure 3.4). Within the liquid universe the mean pairwise correlation peaks in the 2022 bear "
           "market (0.43) and is lowest in 2026 (0.28). Positions in several of these stocks are far less diversified "
           "than their number suggests, which the decision layer must account for when sizing."),
    ("fig", "Figure 3.4: Correlation matrix of daily returns, 30 most traded stocks on 30 October 2026.",
     "universe_corr.png", 11),
    ("h3", "3.1.7 Choice of Universe"),
    ("p", "The models learn from and are evaluated on the top 150 stocks by lagged traded value, re-ranked every session:"),
    ("ul", ["it holds 98.5% of the market's traded value, so little opportunity is lost;",
            "its data are reliable: almost every session trades, and one impossible gap remains after cleaning (Table 3.3);",
            "positions in it can actually be entered and exited at a realistic size;",
            "ranking on earlier sessions only keeps the delisted stocks that were once liquid, so the universe is free "
            "of survivorship and look-ahead bias;",
            "training on every listed stock would teach the models from stale and placeholder prices of stocks that "
            "could not be traded, while a fixed list of today's leaders would introduce exactly the hindsight the "
            "ranking avoids."]),
    ("p", "A stock's full history is still used to compute its features, so a stock entering the universe has its "
          "indicators ready on the first day. Only the rows used for training, signals and evaluation are limited to "
          "universe members."),
    ("h3", "3.1.8 Choice of Sample Period"),
    ("fig", "Figure 3.5: VNINDEX and the period covered by each data layer.", "data_vnindex_regimes.png", 14),
    ("table", "Table 3.5: Start-date options.", ["Option", "For", "Against"], [
        ["Layer A, 2020-02 on (chosen)",
         "Survivorship-free; raw and exchange limit prices for limit-lock and execution modelling; foreign flow; "
         "exchange reference prices allow an exact own adjustment",
         "About 6.7 years; one full bear market (2022, −40%) plus the COVID crash"],
        ["Layer B, 2013 on", "Twice the history; adds the 2018 correction (−27%)",
         "Survivorship-biased; no limit prices; vendor adjustment with residual seams; no raw prices"],
        ["Splice B (pre-2020) + A", "Longest series",
         "Adjustment convention changes at the splice, creating a seam exactly at the join"],
    ], None),
    ("p", "The main sample is layer A from 26 February 2020 to 30 October 2026. It covers three distinct regimes: the "
          "COVID crash and recovery (2020–2021), the 2022 bear market and the 2023–2026 range. Layer B before 2020 is used "
          "only as a secondary, out-of-period robustness check, reported with its survivorship bias stated next to every number."),
]

CH3_VI: list[Block] = [
    ("h1", "Chương 3. Phương pháp"),
    ("h2", "3.1 Dữ liệu"),
    ("p", "Mọi con số trong mục này đều được sinh từ mã nguồn trong kho mã của khóa luận: scripts/build_data.py "
          "(thu thập), src/wyckoff/data/clean.py và scripts/build_clean.py (làm sạch và kiểm tra), "
          "scripts/eda_data_layers.py và scripts/eda_universe.py (phân tích khám phá). Giá tính bằng VND tuyệt đối."),
    ("h3", "3.1.1 Nguồn dữ liệu"),
    ("p", "Khóa luận xây dựng hai lớp dữ liệu giá theo ngày cho thị trường cổ phiếu HOSE."),
    ("lp", "Lớp A. ", "API FastConnect Data của SSI (DailyStockPrice), lấy cho toàn thị trường. Với mỗi mã và mỗi phiên, "
           "API trả về OHLCV thô, giá tham chiếu, giá trần, giá sàn của sở, giá đóng cửa đã điều chỉnh, khối lượng và giá "
           "trị khớp lệnh và thỏa thuận, cùng giao dịch mua/bán của nhà đầu tư nước ngoài. Vì mỗi lần gọi lấy theo ngày "
           "chứ không theo mã, các cổ phiếu sau này hủy niêm yết hoặc chuyển sàn vẫn có mặt: lớp dữ liệu không bị thiên "
           "lệch sống sót. Dữ liệu đầy đủ toàn thị trường từ ngày 26/02/2020."),
    ("lp", "Lớp B. ", "Bộ nến ngày đã điều chỉnh lấy một lần từ nhà cung cấp thứ ba (VCI), giai đoạn 2013–2026. Dài hơn, "
           "nhưng chỉ chứa các mã còn niêm yết tại thời điểm lấy dữ liệu và không có giá thô, giá trần/sàn hay giao dịch "
           "khối ngoại."),
    ("p", "Hai lớp không được nối thành một chuỗi. Chúng điều chỉnh giá theo quy ước khác nhau (Mục 3.1.5), nên nối lại "
          "sẽ tạo ra một điểm gãy ngay tại ngày nối."),
    ("h3", "3.1.2 Thu thập"),
    ("p", "API chỉ trả tối đa 30 ngày lịch cho mỗi lần gọi, nên toàn giai đoạn được chia thành 83 cửa sổ liên tiếp. Mỗi "
          "cửa sổ được lấy trong một trang duy nhất và chỉ được chấp nhận khi số cặp (mã, ngày) không trùng bằng đúng "
          "tổng số dòng máy chủ báo; cửa sổ lỗi được lấy lại toàn bộ, tối đa ba lần. Mọi cửa sổ được lấy trong cùng một "
          "ngày, nên giá điều chỉnh của nhà cung cấp dùng chung một mốc điều chỉnh."),
    ("p", "Hai quy tắc này xuất phát từ các lỗi gặp phải trong quá trình làm. Với kích thước trang mặc định, các trang của "
          "máy chủ chồng lên nhau: trung bình 35% số dòng của một cửa sổ bị lặp trong khi một số dòng khác không bao giờ "
          "được trả về, dù tổng số dòng vẫn khớp với con số máy chủ báo. Lần build đầu tiên trông có vẻ đầy đủ nhưng HPG "
          "chỉ có 533 nến trong 6,7 năm thay vì khoảng 1.680. Vì vậy đếm số dòng không phải là cách kiểm tra đầy đủ; phải "
          "đếm số khóa không trùng."),
    ("h3", "3.1.3 Độ phủ"),
    ("table", "Bảng 3.1: Các lớp dữ liệu ngày cho cổ phiếu HOSE.", ["", "Lớp A (SSI)", "Lớp B (VCI)"], [
        ["Giai đoạn", "02/2020 – 10/2026", "2013 – 10/2026"],
        ["Số mã", "448", "308"],
        ["Số mã-phiên", "648.901", "861.923"],
        ["Mã đã hủy niêm yết / chuyển sàn", "36", "0"],
        ["Giá thô, giá tham chiếu/trần/sàn", "có", "không"],
        ["Giao dịch khối ngoại", "có", "không"],
        ["Độ đầy đủ trung vị (a)", "1,000 (p5 0,995)", "1,000 (p5 0,971)"],
    ], "(a) Số nến của mỗi mã chia cho số phiên giao dịch từ nến đầu đến nến cuối của mã đó."),
    ("fig", "Hình 3.1: Số mã HOSE có ít nhất một nến trong năm, theo từng lớp.", "data_coverage.png", 14),
    ("p", "Trong 448 mã của lớp A có 140 mã không có trong lớp B, trong đó 35 mã đã ngừng giao dịch trên HOSE trước khi "
          "kết thúc giai đoạn mẫu. Kiểm thử chỉ trên lớp B vì thế chỉ giao dịch những công ty mà nhìn lại mới biết là đã "
          "tồn tại được."),
    ("h3", "3.1.4 Làm sạch"),
    ("p", "Nguồn dữ liệu thô báo thành công nhưng vẫn chứa những dòng sai mà không phát sinh lỗi nào. Thuật toán 1 liệt "
          "kê các bước làm sạch theo đúng thứ tự thực hiện, và Bảng 3.2 thống kê số dòng ở từng bước."),
    ("algo", "Thuật toán 1: Làm sạch lớp A", [
        "Chỉ giữ cổ phiếu; bỏ các dòng có giá đóng cửa bằng 0 (niêm yết nhưng chưa từng giao dịch) và các dòng trước 26/02/2020.",
        "Gắn cờ không giao dịch: khối lượng khớp bằng 0. Giữ dòng, bỏ giá (giá giữ chỗ).",
        "Gắn cờ giá nghi vấn: giá thô không phải bội số của bước giá 10 đồng (đã bị nhà cung cấp điều chỉnh sẵn); xử lý như "
        "phiên không giao dịch.",
        "Gắn cờ không rõ trần/sàn: giá tham chiếu bằng 0; không bao giờ tính phiên đó là nằm trần/sàn.",
        "Tính thanh khoản: trung vị giá trị khớp 20 phiên, lùi một phiên; xếp hạng các mã mỗi ngày.",
        "Với mỗi mã và mỗi phiên: tham chiếu = trung điểm của giá trần và giá sàn nếu chênh hơn 1% so với giá tham chiếu "
        "được báo, ngược lại dùng giá tham chiếu được báo; r = tham chiếu / giá đóng cửa phiên trước.",
        "Nếu r < 0,995 và (r < 0,89, hoặc mã nằm trong top 150, hoặc hệ số của nhà cung cấp cũng thay đổi) thì ghi nhận một "
        "ngày giao dịch không hưởng quyền với tỷ lệ r.",
        "Hệ số điều chỉnh của một nến = tích các tỷ lệ của mọi ngày không hưởng quyền sau nến đó.",
        "Sửa các nến có high/low không bao trùm open/close, giữ nguyên giá đóng cửa.",
        "Giá điều chỉnh = giá thô × hệ số; khối lượng điều chỉnh = khối lượng / hệ số.",
    ]),
    ("table", "Bảng 3.2: Thống kê số dòng của bước làm sạch (chỉ cổ phiếu).", ["Bước", "Số dòng"], [
        ["Số dòng cổ phiếu trong lớp A", "689.541"],
        ["Bỏ: giá đóng cửa bằng 0 (chưa từng giao dịch) hoặc trước 26/02/2020", "40.674"],
        ["Giữ lại", "648.867"],
        ["   gắn cờ không giao dịch (khối lượng khớp bằng 0)", "51.132"],
        ["   gắn cờ giá nghi vấn (ELC đến 09/2022, MCP)", "641"],
        ["   gắn cờ không rõ trần/sàn (giá tham chiếu bằng 0)", "2.685"],
        ["   nến được sửa (biên độ không bao trùm open/close)", "737"],
        ["Số nến có giá dùng được", "597.097"],
        ["   trong đó thuộc các phiên top 150", "248.585"],
    ], None),
    ("p", "Hai lỗi trong số này quan trọng hơn nhiều so với quy mô của chúng. Các dòng không giao dịch (7,9% số dòng giữ "
          "lại) mang giá giữ chỗ: 29.200 dòng trong số đó thậm chí không phải nến phẳng, nên mỗi dòng sẽ vẽ ra một cây nến "
          "giả trải hết biên độ ngày. Và việc điều chỉnh giá của nhà cung cấp không đầy đủ, là nội dung của mục tiếp theo."),
    ("h3", "3.1.5 Điều chỉnh giá theo sự kiện doanh nghiệp"),
    ("p", "Chia cổ tức bằng cổ phiếu, cổ phiếu thưởng và phát hành quyền mua làm giá giảm vào ngày giao dịch không hưởng "
          "quyền mà giá trị không đổi; trên chuỗi giá chưa điều chỉnh, các cú giảm này trông như sập giá. Giá điều chỉnh "
          "của SSI đúng ở những chỗ có điều chỉnh, thay đổi đúng vào ngày không hưởng quyền, nhưng chỉ phủ 195 trong 350 "
          "phiên không hưởng quyền lớn và bỏ qua cổ tức tiền mặt. Lớp B có điều chỉnh cả cổ tức tiền mặt, vì vậy hai lớp "
          "chỉ khớp trong phạm vi 0,5% ở 50% số phiên năm 2020 nhưng 87% số phiên năm 2026, trong khi tỷ lệ trung vị vẫn "
          "bằng 1,00 mọi năm."),
    ("p", "Do đó khóa luận tự xây dựng lại việc điều chỉnh từ giá tham chiếu của sở, giá này trên HOSE bằng giá đóng cửa "
          "phiên trước ở mọi phiên trừ ngày không hưởng quyền (Thuật toán 1). Ở một số ngày không hưởng quyền, trường giá "
          "tham chiếu vẫn giữ giá cũ trong khi trần và sàn đã đổi, nên dùng trung điểm của biên độ thay thế. Ở các mã thanh "
          "khoản thấp, giá đóng cửa bị \"đứng\" và tỷ lệ thay đổi dù không có sự kiện doanh nghiệp, nên một cú giảm nhỏ chỉ "
          "được chấp nhận ở mã thanh khoản cao hoặc khi hệ số của chính nhà cung cấp xác nhận."),
    ("p", "Kết quả là 1.985 sự kiện không hưởng quyền, trong đó hệ số của nhà cung cấp chỉ phủ 1.325. Lớp B không phải đầu "
          "vào của quy trình này nên được dùng làm kiểm tra độc lập: ở những chỗ so sánh được, hệ số của lớp B thay đổi "
          "đúng tỷ lệ và đúng ngày trong 97–99% số sự kiện. Bảng 3.3 cho thấy kết quả."),
    ("table", "Bảng 3.3: Số gap mở cửa dưới −11% (không thể xảy ra trong biên độ ±7% nếu không có sự kiện doanh nghiệp), "
              "26/02/2020 – 30/10/2026.", ["Chuỗi", "Mọi mã", "Phiên top 150"],
     [[name, *v] for name, v in zip(["Lớp A, giá thô", "Lớp A, nhà cung cấp điều chỉnh", "Lớp B, đã điều chỉnh",
                                     "Lớp A, sau làm sạch"], TABLE_GAPS)], None),
    ("h3", "3.1.6 Phân tích khám phá"),
    ("p", "Phần phân tích trả lời một câu hỏi thực tế: mô hình nên học và được đánh giá trên những mã nào? Thứ hạng thanh "
          "khoản là thứ hạng có độ trễ của Thuật toán 1, nên việc một mã có thuộc nhóm hay không vào một ngày chỉ dùng dữ "
          "liệu của các phiên trước."),
    ("lp", "Giao dịch tập trung rất cao. ", "Trong ngày trung vị, 30 mã giao dịch nhiều nhất chiếm 64,8% giá trị khớp lệnh, "
           "top 100 chiếm 94,5% và top 150 chiếm 98,5% (Hình 3.2). Ngoài top 200 chỉ còn 0,4% giá trị thị trường."),
    ("fig", "Hình 3.2: Tỷ trọng giá trị khớp lệnh mỗi ngày của N mã giao dịch nhiều nhất (đường cam: N = 150).",
     "universe_concentration.png", 13),
    ("lp", "Chất lượng dữ liệu giảm theo thanh khoản. ", "Bảng 3.4 chia các mã-phiên theo nhóm thanh khoản. Trong top 150 "
           "gần như phiên nào cũng có khớp lệnh; ngoài hạng 300, một phần ba số phiên không có giao dịch nào, và mã trung "
           "vị chỉ khớp khoảng 8 triệu đồng mỗi ngày."),
    ("table", "Bảng 3.4: Mã-phiên theo nhóm thanh khoản (xếp theo trung vị giá trị khớp 20 phiên có độ trễ).",
     ["Hạng", "Mã-phiên", "Không khớp (%)", "Nằm trần (%)", "Nằm sàn (%)", "Giá trị trung vị (tỷ đồng)"],
     [[r[0], r[1].replace(",", "."), *[x.replace(".", ",") for x in r[2:]]] for r in TABLE_BUCKETS], None),
    ("lp", "Nhóm thanh khoản thay đổi, nhưng chậm. ", "Có 306 mã từng nằm trong top 150, mỗi mã ở lại trung vị 685 phiên; "
           "một ngày điển hình có một mã vào và một mã ra. 17 trong 306 mã sau đó hủy niêm yết (trong đó có FLC, HAI, HVG "
           "và POM). Nếu chọn theo danh sách mã giao dịch nhiều nhất hiện nay rồi áp dụng cho quá khứ thì cả 17 mã này sẽ "
           "bị loại bỏ mà không ai biết."),
    ("lp", "Biên độ giá cắt cụt lợi suất. ", "Lợi suất ngày của các mã top 150 có độ lệch chuẩn (σ) 2,67% và độ nhọn dư "
           "6,5: phân phối nhọn và đuôi dày, như thường thấy ở cổ phiếu. Điều bất thường là gần như không có ngày nào vượt "
           "3σ (0,006%, so với 0,27% của phân phối chuẩn): 3σ khoảng 8%, mà biên độ ±7% không cho phép. Thay vào đó, các "
           "biến động cực đoan bị chia ra nhiều phiên nằm trần/sàn liên tiếp (Hình 3.3), và đó chính là điều khiến việc "
           "thoát vị thế không chắc chắn."),
    ("fig", "Hình 3.3: Lợi suất ngày của nhóm top 150 và các mã còn lại (mật độ, thang log). Cả hai dừng ở biên độ ±7%.",
     "universe_returns.png", 13),
    ("lp", "Các mã biến động cùng nhau. ", "30 mã giao dịch nhiều nhất có hệ số tương quan lợi suất trung bình theo cặp là "
           "0,39, từ 0,02 đến 0,82 (Hình 3.4). Trong nhóm thanh khoản, tương quan trung bình cao nhất trong thị trường giá "
           "xuống năm 2022 (0,43) và thấp nhất năm 2026 (0,28). Nắm giữ nhiều mã trong nhóm này vì vậy ít đa dạng hóa hơn "
           "nhiều so với số lượng mã, và lớp quyết định phải tính đến điều này khi phân bổ vốn."),
    ("fig", "Hình 3.4: Ma trận tương quan lợi suất ngày của 30 mã giao dịch nhiều nhất tại ngày 30/10/2026.",
     "universe_corr.png", 11),
    ("h3", "3.1.7 Lựa chọn tập mã"),
    ("p", "Mô hình được huấn luyện và đánh giá trên top 150 mã theo giá trị giao dịch có độ trễ, xếp hạng lại mỗi phiên, vì:"),
    ("ul", ["nhóm này chiếm 98,5% giá trị giao dịch của thị trường, nên gần như không bỏ lỡ cơ hội;",
            "dữ liệu đáng tin: gần như phiên nào cũng có giao dịch, và sau làm sạch chỉ còn một gap bất khả (Bảng 3.3);",
            "vị thế trong nhóm này thực sự có thể mở và đóng ở quy mô thực tế;",
            "xếp hạng chỉ dựa trên các phiên trước nên giữ lại các mã đã hủy niêm yết từng có thanh khoản cao, tránh được "
            "thiên lệch sống sót và nhìn trước tương lai;",
            "huấn luyện trên mọi mã niêm yết sẽ bắt mô hình học từ giá \"đứng\" và giá giữ chỗ của những mã không thể giao "
            "dịch, còn một danh sách cố định các mã dẫn đầu hiện nay lại đưa vào đúng sự nhìn trước mà cách xếp hạng tránh."]),
    ("p", "Toàn bộ lịch sử của một mã vẫn được dùng để tính đặc trưng, nên mã vừa vào nhóm đã có sẵn chỉ báo từ ngày đầu. "
          "Chỉ các dòng dùng để huấn luyện, ra tín hiệu và đánh giá là giới hạn trong nhóm."),
    ("h3", "3.1.8 Lựa chọn giai đoạn mẫu"),
    ("fig", "Hình 3.5: VNINDEX và giai đoạn mỗi lớp dữ liệu bao phủ.", "data_vnindex_regimes.png", 14),
    ("table", "Bảng 3.5: Các phương án mốc bắt đầu.", ["Phương án", "Ưu điểm", "Nhược điểm"], [
        ["Lớp A, từ 02/2020 (chọn)",
         "Không thiên lệch sống sót; có giá thô và giá trần/sàn để mô phỏng nằm trần/sàn và khớp lệnh; có khối ngoại; "
         "giá tham chiếu cho phép tự điều chỉnh chính xác",
         "Khoảng 6,7 năm; một thị trường giá xuống trọn vẹn (2022, −40%) cùng cú sập COVID"],
        ["Lớp B, từ 2013", "Dài gấp đôi; thêm đợt điều chỉnh 2018 (−27%)",
         "Thiên lệch sống sót; không có trần/sàn; điều chỉnh của nhà cung cấp còn điểm gãy; không có giá thô"],
        ["Nối B (trước 2020) + A", "Chuỗi dài nhất", "Quy ước điều chỉnh đổi tại điểm nối, tạo điểm gãy đúng chỗ nối"],
    ], None),
    ("p", "Mẫu chính là lớp A từ 26/02/2020 đến 30/10/2026, bao gồm ba giai đoạn thị trường khác nhau: cú sập COVID và "
          "phục hồi (2020–2021), thị trường giá xuống năm 2022 và giai đoạn đi ngang 2023–2026. Lớp B trước 2020 chỉ dùng "
          "để kiểm tra độ bền ngoài giai đoạn, luôn ghi kèm thiên lệch sống sót bên cạnh mọi con số."),
]
