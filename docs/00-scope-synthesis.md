# 00 — Tổng hợp scope (draft 30-10-2026)

Tên đề tài (tạm): **Wyckoff Pattern Detection for Market Phase Identification — a study on the Vietnamese equity market (HOSE)**

Mục tiêu cốt lõi: tìm **điểm vào / điểm ra** cổ phiếu HOSE dựa trên nhận diện pha Wyckoff, chứng minh bằng backtest có kiểm soát chi phí, out-of-sample, và đối chiếu trên MetaTrader 5.

---

## 1. Câu hỏi nghiên cứu (đề xuất)

- **RQ1 — Detection:** Có thể nhận diện tự động các sự kiện (SC, AR, ST, Spring, SOS, LPS, UTAD, SOW, LPSY…) và pha A–E của Wyckoff trên dữ liệu ngày HOSE với độ chính xác bao nhiêu so với nhãn do người gán?
- **RQ2 — Profitability:** Tín hiệu vào/ra suy ra từ pha Wyckoff có tạo lợi nhuận điều chỉnh rủi ro vượt baseline (buy-and-hold VNINDEX, breakout đơn giản) sau phí + thuế không?
- **RQ3 — Robustness:** Kết quả có giữ được qua các giai đoạn thị trường (2018 sụt, 2020–21 bull, 2022 sập, 2023–26) và qua hai engine backtest độc lập (Python vs MT5) không?

Pre-thesis nên chốt RQ1 + baseline của RQ2. Thesis mở rộng RQ2 + RQ3 (+ ML).

## 2. Universe — HOSE hay cả 3 sàn?

**Khuyến nghị: HOSE + lọc thanh khoản. Không cần scale HNX/UPCoM cho pre-thesis.**

Lý do:
1. Wyckoff là phương pháp **giá–khối lượng**. Mã thanh khoản thấp (phần lớn UPCoM, nhiều mã HNX) có volume nhiễu, dễ bị làm giá → "Spring", "climax" giả rất nhiều → detector học sai.
2. Biên độ khác nhau (HOSE ±7%, HNX ±10%, UPCoM ±15%) → phải chuẩn hóa ngưỡng theo sàn, thêm biến không liên quan câu hỏi chính.
3. Khó thực thi thật: mã illiquid không vào/ra được với size hợp lý → backtest đẹp nhưng vô nghĩa.
4. Dữ liệu sẵn có (parent repo): ~360 mã, phủ HOSE thanh khoản từ 2016.

Tùy chọn cho thesis: thêm **HNX top-thanh-khoản** làm tập kiểm tra robustness (out-of-universe), không phải universe chính.

Lọc đề xuất: ADV20 giá trị ≥ 10 tỷ VND (hoặc top-100 theo ADV), loại mã bị kiểm soát/cảnh báo.

## 3. Trường phái — đánh cổ phiếu VN kiểu gì là hợp lý?

Ràng buộc thị trường quyết định trường phái:

| Ràng buộc | Hệ quả |
|---|---|
| T+2 (hàng về chiều T+2) | Không day-trade được cổ phiếu cơ sở → nắm giữ tối thiểu ~3 phiên |
| Không bán khống (retail) | **Long-only.** Pha distribution chỉ dùng để **thoát/né**, không short |
| Biên độ ±7%, có thể kẹt sàn | Stop-loss không đảm bảo khớp → rủi ro gap phải vào hệ số an toàn |
| Lô 100, bước giá theo vùng giá | Phải mô hình hóa trong backtest |
| Phí ~0.15–0.25%/chiều + thuế bán 0.1% | Tần suất giao dịch thấp mới sống được |

→ **Swing / position trading trên khung ngày** (giữ vài tuần – vài tháng), đúng tinh thần Wyckoff gốc (trading range dài hàng tuần/tháng). Khung tuần dùng xác nhận xu hướng lớn; intraday chỉ (tùy chọn) để tinh chỉnh điểm vào.

## 4. Chiến thuật (draft)

Quy trình 5 bước Wyckoff → chuyển thành pipeline:

1. **Bối cảnh thị trường:** VNINDEX đang ở pha nào (dùng cùng detector trên index) → chỉ mua khi thị trường không ở distribution/markdown.
2. **Chọn mã mạnh hơn thị trường:** relative strength vs VNINDEX.
3. **Có "cause":** trading range đủ dài (≥ N phiên), độ rộng hợp lý theo ATR.
4. **Sẵn sàng tăng:** đã thấy Spring/Test hoặc SOS.
5. **Thời điểm vào:**

| Điểm vào | Mô tả | Stop |
|---|---|---|
| E1 – Spring + Test | Thủng đáy range rồi rút lên, test lại với volume thấp | Dưới đáy Spring |
| E2 – SOS → LPS / BU | Phá đỉnh range volume lớn, pullback volume thấp | Dưới LPS / giữa range |

| Điểm ra | Mô tả |
|---|---|
| X1 – Mục tiêu | Target từ Point & Figure (cause → effect) hoặc bội số R |
| X2 – Dấu hiệu phân phối | BC / UTAD / SOW / LPSY xuất hiện |
| X3 – Stop / trailing | Stop cấu trúc + trailing theo ATR hoặc theo đáy swing |
| X4 – Time stop | Không chạy sau K phiên → thoát |

Hướng phương pháp detector (so sánh trong thesis):
- **A. Rule-based** (baseline, giải thích được): zigzag swing → xác định trading range → luật cho từng event dựa trên spread/volume tương đối.
- **B. ML/probabilistic:** HMM / segmentation cho pha; classifier xác nhận event (meta-labeling bằng triple-barrier đã có ở parent repo).
- **C. Hybrid (khuyến nghị cho thesis):** A sinh ứng viên → B lọc. Đóng góp rõ ràng, dễ bảo vệ.

## 5. Dữ liệu

| Có sẵn | Ghi chú |
|---|---|
| OHLCV ngày ~360 mã từ 2016 (parent `data/ohlcv_*.parquet`) | Giá **nghìn VND**, back-adjusted |
| SSI FastConnect API (đã có key) | OHLCV ngày, foreign flow, có intraday giới hạn |
| Foreign flow, market breadth daily | Có thể làm feature phụ |
| Nhãn triple-barrier (T+5/T+20) | **Đây là nhãn kết quả (outcome), KHÔNG phải nhãn pha Wyckoff** |

⚠️ **Chưa có nhãn Wyckoff.** Cần tự tạo:
1. Detector rule-based sinh nhãn yếu (weak labels).
2. Gán nhãn tay một mẫu (≈150–300 trading range, ưu tiên đa dạng ngành/giai đoạn) bằng công cụ như Label Studio → làm ground truth đánh giá RQ1.
3. Ghi rõ guideline gán nhãn trong `docs/` (người khác đọc phải gán ra gần giống — hội đồng sẽ hỏi).

⚠️ **Điều chỉnh giá:** parent repo từng có 878 bước nhảy giả do corporate action (xem `../scripts/refetch_adjusted_ohlcv.py`). Một bước -30% giả sẽ tạo "Selling Climax" giả → phải dùng chuỗi đã refetch trên cùng một basis adjustment trước khi gán nhãn.

## 6. Backtest trên MetaTrader 5

Thực tế cần biết:
- **Không broker nào cung cấp cổ phiếu HOSE trên MT5.** Cách làm: tạo **Custom Symbol** trong MT5, nạp nến ngày từ parquet (MQL5 script `CustomSymbolCreate` + `CustomRatesUpdate`, hoặc import CSV qua giao diện). Strategy Tester chạy được trên custom symbol.
- Phải tự mô hình hóa trong EA: long-only, lô 100, bước giá HOSE (10/50/100 VND theo vùng giá), biên ±7%, giữ tối thiểu T+2, phí + thuế bán.
- Package Python `MetaTrader5` (chỉ Windows — OK) **chưa cài** trong môi trường hiện tại; cần cài terminal MT5 (bất kỳ broker demo nào) + `pip install MetaTrader5`.

**Đề xuất:** Python là engine nghiên cứu chính (nhanh, walk-forward, nhiều mã), MT5 là engine **xác nhận độc lập** trên tập mã đại diện. Hai engine ra cùng kết quả = luận điểm robustness mạnh cho RQ3.

## 7. Chỉ báo cần chú ý

| Nhóm | Chỉ báo | Dùng cho |
|---|---|---|
| Volume / VSA | Relative volume (z-score), spread (H−L)/ATR, close location | Nhận diện climax, Spring, test volume thấp |
| Dòng tiền tích lũy | OBV, Accumulation/Distribution, **Weis Wave** | Effort vs result, phân kỳ |
| Biến động | ATR | Độ rộng range, stop, trailing |
| Sức mạnh tương đối | RS vs VNINDEX | Bước 2 của Wyckoff |
| Mục tiêu giá | Point & Figure count | Target (cause → effect) |
| Bổ trợ | VWAP, RSI phân kỳ | Xác nhận climax |
| Riêng VN | Foreign net flow, breadth | Feature phụ, kiểm định có giá trị thêm không |

Lưu ý: parent repo đo foreign flow ≈ price impact cùng phiên, không dự báo phiên sau → dùng làm xác nhận volume, không làm tín hiệu dự báo.

## 8. Hệ số an toàn (risk management)

Đề xuất định nghĩa "hệ số an toàn" thành các tham số đo được:

| Tham số | Giá trị khởi điểm | Ý nghĩa |
|---|---|---|
| Rủi ro mỗi lệnh | 1% NAV | Size = 1% NAV / (giá vào − stop) |
| R:R tối thiểu | ≥ 2.5 (target P&F hoặc đỉnh range) | Bỏ lệnh nếu không đạt |
| Gap buffer | stop × (1 + biên độ sàn) cho trường hợp kẹt sàn | Mô hình hóa rủi ro không khớp |
| Trần vị thế | ≤ 10–20% NAV/mã, ≤ 2 mã/ngành | Tập trung rủi ro |
| Thanh khoản | Lệnh ≤ 5–10% ADV20 | Khớp được thật |
| Tổng exposure | Giảm khi VNINDEX ở distribution/markdown | Bối cảnh thị trường |

Về **thống kê** (bài học từ parent repo): báo cáo Deflated Sharpe Ratio + PBO, walk-forward/purged CV. Sharpe đẹp trên một lần chạy không đủ.

## 9. Đánh giá

- RQ1: precision/recall/F1 theo event (cho phép lệch ±k phiên), confusion matrix theo pha.
- RQ2: CAGR, Sharpe, Sortino, MaxDD, win rate, expectancy (R), số lệnh, turnover — sau phí.
- Baseline: buy-and-hold VNINDEX, breakout N-ngày, (tùy) mô hình ML của parent repo.
- RQ3: chia giai đoạn, walk-forward, Python vs MT5.

## 10. Lộ trình (draft)

| Giai đoạn | Nội dung |
|---|---|
| Pre-thesis | Literature review; dữ liệu sạch (adjusted); guideline + gán nhãn mẫu; detector rule-based v1; backtest Python baseline; prototype MT5 custom symbol trên 3–5 mã |
| Thesis | Detector hybrid (ML); toàn universe + walk-forward; MT5 xác nhận; robustness theo giai đoạn / HNX-liquid; viết báo cáo |

## 11. Câu hỏi mở (cần chốt)

1. Repo GitHub: tên `wyckoff-thesis`, **private**? (gh CLI chưa cài — cần tạo repo trống trên github.com hoặc cài `gh`.)
2. Ngôn ngữ báo cáo: tiếng Anh hay tiếng Việt? LaTeX (Overleaf) hay Word?
3. Trường/GVHD có yêu cầu bắt buộc MT5 không, hay MT5 là lựa chọn của mình? (Ảnh hưởng mức đầu tư cho EA.)
4. Có cần intraday không, hay chỉ ngày/tuần?
5. Ai gán nhãn tay — một mình hay có người thứ hai (để đo inter-annotator agreement)?
