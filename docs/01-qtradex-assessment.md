# 01 — Đánh giá QTradeX so với đề tài mới (04-11-2026)

Repo GVHD gửi: https://github.com/squidKid-deluxe/QTradeX-Algo-Trading-SDK (commit `447d65c`, 30-07-2026).
Mới đọc code, **chưa cài, chưa chạy**. License WTFPL: được phép copy/fork tự do.

## QTradeX là gì

SDK Python để viết bot, backtest và tối ưu tham số, thiết kế cho **crypto**. Viết bot bằng cách kế thừa
`BaseBot` (`indicators()`, `strategy()`, `fitness()`), chạy qua menu CLI `qx.dispatch`. Lấy data qua CCXT,
yfinance, FinanceDataReader, hoặc CSV (`qx.load_csv`).

## Khoảng cách so với hệ thống cần xây

| Hạng mục | QTradeX (đọc từ code) | Cần cho đề tài | Mức xử lý |
|---|---|---|---|
| "AI" | Thuật toán tối ưu **tham số** bot: QPSO, LSGA, IPSE, AION, PPO (`optimizers/`). Không có model dự báo hay nhận diện | Lớp AI sinh tín hiệu và khuyến nghị | Tự xây |
| Hỗ trợ ra quyết định | Không có: chỉ menu CLI + plot matplotlib, chạy bot/backtest | Khuyến nghị kèm lý do, rủi ro, giao diện | Tự xây |
| Danh mục | Backtest 1 cặp `asset/currency` trong 1 wallet | Nhiều mã HOSE cùng lúc | Tự xây hoặc chạy từng mã rồi gộp (kém) |
| Luật thị trường VN | Phí phẳng `BASE_FEE = 1%`; không có lô 100, bước giá, biên ±7%, T+2, thuế bán | Bắt buộc theo Hard Rules | Viết lớp thực thi riêng |
| Data VN | Không có nguồn HOSE nào; CSV dùng được | SSI đã build | Adapter từ parquet sang CSV/`Data` |
| Kiểm định | Có chia 2/3 + 1/3 trong LSGA, PPO; không có DSR, PBO, purged CV | DSR + PBO + walk-forward | Tự xây |
| Nền tảng | Linux-only theo `pyproject.toml` và `AGENTS.md`, Windows nằm trong roadmap; cần Cython, `numpy<2` | Máy dev là Windows 10 | Dùng WSL hoặc venv riêng, cần thử |
| Test | `AGENTS.md`: "No formal test suite or CI tests" | Kết quả phải bảo vệ được | Không tin kết quả khi chưa kiểm tra đối chiếu |

## Cần kiểm tra kỹ trước khi tin số của nó

- `WalletBase.value` trả về `(asset*price + currency) / sqrt(price)`, không phải NAV theo VND. Cần xác minh ROI báo cáo
  có bị ảnh hưởng không.
- `trade()` mặc định khớp ở `close` của chính bar đang xét. Cần đọc tiếp để xác minh tín hiệu có dùng close đó không
  (nguy cơ look-ahead).

## Dùng được gì

- Khung `BaseBot` + menu backtest, tiện cho demo.
- Các optimizer (QPSO, LSGA, PPO): đúng chữ "AI" của repo. Mỗi lần thử phải tính vào số trial cho DSR.
- Thư viện chỉ báo Tulip, plot.

## Phần đã làm còn giá trị với đề tài mới

- **Data layer A/B + EDA + report §3.1:** giữ nguyên, không phụ thuộc đề tài.
- **Wyckoff detector:** chưa viết dòng nào. Đề tài mới không nhắc Wyckoff; có thể là một module tín hiệu.
- **MT5, vectorbt:** chưa viết gì; có thể bị QTradeX thay thế.

## Kiến trúc đề xuất (chờ chốt)

```
SSI data (đã có) → làm sạch → AI tín hiệu (Wyckoff hybrid + ML) → lớp quyết định (khuyến nghị, lý do, sizing)
                                       ↓                                   ↓
                     QTradeX + lớp luật VN (backtest, tối ưu)        giao diện cho người dùng
```

## Đã chốt (04-11-2026, theo lời tác giả)

1. QTradeX: **tham khảo trước**, không bắt buộc build lên. GVHD chỉ đưa thêm hướng đi.
2. Sản phẩm cuối: **có giao diện, demo, kịch bản theo tình huống**; đi đường dài tới thesis.
3. **MT5 vẫn cần.**
4. **Được dùng lại toàn bộ** từ project cũ (`quant_trading_telegram_bot`).
5. (17-11-2026) Tác giả **toàn quyền** quyết định viết gì, làm gì — không cần chờ GVHD duyệt từng hướng.
   Đã chốt theo đó: ghi rõ HOSE trong scope, nêu Wyckoff là một module có cổng kiểm định.

## Còn mở

- Wyckoff giữ vai trò gì: đề xuất là một giả thuyết phải qua cổng kiểm định, không còn là lõi.

## Mốc thời gian

- Tuần sau (GVHD yêu cầu): viết phần mở bài report.
- Tháng 1-2027: nộp pre-thesis.
- Tháng 6-2027: nộp thesis.
