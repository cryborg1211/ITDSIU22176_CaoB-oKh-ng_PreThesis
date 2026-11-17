# 02 — Theo dõi tiến độ (cập nhật 17-11-2026)

Đề tài: **An AI-Driven Decision Support System for Intelligent Stock Trading**
GVHD: Assoc. Prof. Ha Viet Uyen Synh · Pre-thesis: 01-2027 · Thesis: 06-2027
Tác giả toàn quyền quyết định hướng đi (`docs/01-qtradex-assessment.md`).

Ký hiệu: ✅ xong · 🟡 đang làm / làm dở · ⬜ chưa bắt đầu · 💡 đề xuất, chưa chốt

---

## 1. Câu hỏi cốt lõi (một câu)

> Một lớp **hỗ trợ ra quyết định** (sizing, phanh rủi ro, cảnh báo đầu cơ, giải thích) đặt trên tín hiệu
> học máy có giúp nhà đầu tư ra quyết định **tốt hơn và ít lỗ nặng hơn** trên HOSE — khi tính đủ luật
> sàn và chi phí — so với dùng tín hiệu thô hay mua-và-giữ không?

Điểm mới nằm ở **lớp quyết định + cách đánh giá trung thực theo luật VN**, không nằm ở việc có model
dự báo tốt hơn. Model dự báo là phần dùng lại, đóng vai baseline mạnh.

## 2. Thuật toán 💡

| Lớp | Thuật toán | Nguồn | Trạng thái |
|---|---|---|---|
| Nhãn | Triple-barrier (chốt lời / cắt lỗ / hết hạn), chỉnh theo biên ±7% và T+2 | port từ `../src/labels/triple_barrier.py` | ⬜ |
| Tín hiệu chính | Ensemble cây: LightGBM + XGBoost + CatBoost → logistic meta | port từ `../src/models/tabular_ensemble.py` | ⬜ |
| Meta-labeling | Model thứ hai quyết định **có vào lệnh không và vào bao nhiêu** từ tín hiệu chính | López de Prado (2018) | ⬜ — ứng viên lõi thuật toán |
| Đặc trưng | Giá–khối lượng, thanh khoản, độ rộng thị trường, regime; Wyckoff/VSA để sau, phải qua cổng kiểm định | mới + port | ⬜ |
| Sizing | Xác suất → fractional Kelly, có trần mỗi mã / mỗi ngành | port `../src/bot/sizing.py` | ⬜ |
| Phanh thị trường | Regime HMM/GARCH + drift + breadth → hệ số phơi nhiễm | port `../src/bot/garch_brake.py` | ⬜ |
| Cảnh báo đầu cơ | Điểm rủi ro theo luật: chuỗi trần/sàn, đột biến khối lượng, tỷ trọng thỏa thuận, thanh khoản mỏng | **mới** | ⬜ |
| Giải thích | Top đặc trưng theo SHAP + lý do theo luật cho mỗi khuyến nghị | mới | ⬜ |
| Kiểm định | Backtest theo luật VN (lô 100, bước giá, khớp khi nằm trần/sàn, T+2, phí + thuế), walk-forward / purged CV, DSR + PBO, ablation từng thành phần | port `../src/execution/vn_cost_model.py`, `../src/backtest/walk_forward.py` | ⬜ |

Cảnh báo đầu cơ không có nhãn "bị lái thật", nên chỉ đánh giá được gián tiếp: loại các mã bị cảnh báo
có giảm lỗ đuôi (tail loss) không.

## 3. Thiết kế hệ thống 💡

```
SSI FastConnect ─► làm sạch (✅) ─► kho đặc trưng ─► LỚP TÍN HIỆU ─► LỚP QUYẾT ĐỊNH ─► khuyến nghị
                                                     (ensemble,        (sizing, phanh,      + lý do
                                                      meta-label)       cảnh báo, giải thích)  + rủi ro
                                                                              │
                         ┌────────────────────────────────────────────────────┼──────────────────┐
                         ▼                                                    ▼                  ▼
              Backtest luật VN (Python)                          Ứng dụng: replay kịch bản     MT5: indicator
              walk-forward, DSR/PBO, ablation                    theo ngày (Streamlit, port    + EA đối chiếu
                                                                 từ dashboard cũ)              (đọc tín hiệu xuất ra)
```

Nguyên tắc: replay trong ứng dụng chỉ dùng model train **trước** ngày đang xem, nếu không demo chính là look-ahead.

## 4. Câu hỏi nghiên cứu (nháp, chưa đưa vào report) 💡

- **RQ1** Tín hiệu có giá trị ngoài mẫu sau chi phí và luật sàn không? Thành phần nào đóng góp (ablation)?
- **RQ2** Lớp quyết định có cải thiện kết quả điều chỉnh rủi ro và cắt lỗ nặng so với tín hiệu thô không?
- **RQ3** Kết quả có bền qua các regime, qua DSR/PBO, và khớp giữa Python và MT5 không?

## 5. Tiến độ

### Code / dữ liệu

| Hạng mục | Trạng thái | Ở đâu |
|---|---|---|
| Layer A (SSI 2020+) + layer B (VCI 2013+) + chỉ số | ✅ | `scripts/build_data.py`, commit `073fe03` |
| EDA so sánh 2 layer, chọn mốc 26-02-2020 | ✅ | `docs/eda/data-layers.md` |
| Làm sạch + tự back-adjust từ giá tham chiếu | ✅ | `src/wyckoff/data/clean.py`, `docs/eda/clean-validation.md`, commit `dbb3fe6` |
| Backtest theo luật VN | ⬜ | |
| Lớp tín hiệu | ⬜ | |
| Lớp quyết định | ⬜ | |
| Ứng dụng demo / replay | ⬜ | |
| MT5 | ⬜ | |

### Report

| Phần | Trạng thái | Ghi chú |
|---|---|---|
| Template IU (LaTeX) + bìa có logo, GVHD, "pre-thesis report", 01-2027 | ✅ | `report/` |
| Abstract, Acknowledgements | ⬜ | viết cuối |
| Ch1 Introduction | ✅ | 3 trang: bối cảnh, điểm yếu, hướng đi sơ bộ. Không có RQ/scope chi tiết, không nhắc Wyckoff |
| Ch2 Related Work | ⬜ | chỉ có khung đề mục, còn khung theo hướng Wyckoff cũ → phải viết lại |
| Ch3 Methodology | 🟡 | §3.1 Data xong; các mục khác còn khung theo hướng cũ |
| Ch4–Ch7 | ⬜ | |
| Tài liệu tham khảo | 🟡 | 17 mục, ghi từ trí nhớ, **chưa đối chiếu bản gốc** |

## 6. Bản nào là bản gốc

**LaTeX trong `report/` là bản gốc duy nhất.** Mọi bản Word / Google Doc là bản sinh ra từ đó tại một thời điểm.
Sửa thì sửa LaTeX rồi chạy lại script; nếu lỡ sửa trên Google Doc thì phải chép ngược về LaTeX.

| Bản | Nội dung | Sinh bằng | Ngày |
|---|---|---|---|
| `report/main.pdf` | toàn bộ report | `tectonic -X compile main.tex` | luôn mới nhất |
| `report/word/pre_thesis_report.docx` + Google Doc *Pre Thesis Report - Cao Bao Khuong (v2, logo + supervisor)* | bìa + front matter + Ch1, tiếng Anh | `report/word/build_thesis_docx.py` | 17-11-2026 |
| `report/word/introduction_en.docx` / `introduction_vi.docx` + 2 Google Doc *Chapter 1 (EN)*, *Chương 1 (VI)* | chỉ Ch1 | `report/word/build_intro_docx.py` | 17-11-2026 |

Trên Drive: doc *Pre Thesis Report* (trống) và *Pre Thesis Report - Cao Bao Khuong (formatted)* (bản v1, chưa có
logo) là bản cũ, có thể xóa. Bản tiếng Việt chỉ có Ch1 và **không** tự cập nhật theo LaTeX.

## 7. Kế hoạch tới pre-thesis (01-2027) 💡

| Tuần | Việc |
|---|---|
| 17–23/11 | Viết Ch2 (ML cho giao dịch, DSS, overfitting backtest, nghiên cứu về VN). Port backtest luật VN |
| 24–30/11 | Backtest chạy được + kết quả baseline (mua-và-giữ VN-Index, momentum đơn giản) |
| 01–07/12 | Lớp tín hiệu trên data sạch, walk-forward |
| 08–14/12 | Lớp quyết định v0 (sizing + phanh) + ablation đầu tiên |
| 15–21/12 | Viết Ch3 đầy đủ + kết quả sơ bộ |
| 22–28/12 | Khung ứng dụng replay + abstract |
| 29/12–01/2027 | Chỉnh sửa, đối chiếu tài liệu tham khảo, nộp |

Để sau pre-thesis: ứng dụng hoàn chỉnh, MT5, cảnh báo đầu cơ, cổng kiểm định Wyckoff.

## 8. Nhật ký quyết định

| Ngày | Quyết định |
|---|---|
| 30-10 | Bỏ vnstock; dùng SSI FastConnect; report LaTeX theo format IU |
| 31-10 | Mẫu chính = layer A từ 26-02-2020; layer B chỉ để kiểm tra robustness, không nối |
| 04-11 | Tên đề tài mới (GVHD). QTradeX chỉ tham khảo. Có giao diện + demo kịch bản. MT5 vẫn cần. Được dùng lại toàn bộ project cũ |
| 04-11 | Kết quả báo cáo trên top 150 mã thanh khoản (data chỉ đáng tin ở nhóm này) |
| 17-11 | Tác giả toàn quyền. Intro chỉ nêu vấn đề + hướng đi sơ bộ; chưa nêu Wyckoff |
