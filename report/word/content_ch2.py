"""Chapter 2, Section 2.1 (the Vietnamese market), English and Vietnamese, for the Word export.

Mirrors report/chapters/02-related-work.tex; the LaTeX is the source of truth.
"""
from __future__ import annotations

CH2_EN: list[tuple] = [
    ("h1", "Chapter 2. Related Work"),
    ("h2", "2.1 The Vietnamese Stock Market and How It Differs"),
    ("p", "Much of the published work on machine learning for stock trading uses data from the United States, and much "
          "of the work on Asian markets uses mainland China. HOSE shares some features with China but few with the "
          "United States, and several of its differences change what a model can learn and what a strategy can earn. "
          "Table 2.1 summarises them."),
    ("table", "Table 2.1: Trading rules of HOSE compared with the markets most studies use (individual investors, "
              "ordinary shares; to be verified against current regulations before final submission).",
     ["", "HOSE (Vietnam)", "NYSE / Nasdaq (US)", "Shanghai / Shenzhen (China A-shares)"], [
         ["Daily price limit per stock", "±7%", "none; five-minute pauses when a stock leaves a band around its recent price", "±10% (±20% on growth boards)"],
         ["Earliest sale after a purchase", "after T+2 settlement", "same day", "next day"],
         ["Minimum order", "100 shares", "1 share", "100 shares"],
         ["Short selling by individuals", "not available", "available", "limited"],
         ["Tax on a sale", "0.1% of value", "none", "stamp duty"],
         ["Liquid cross-section", "about 150 stocks hold 98.5% of traded value (Section 3.1.6)",
          "thousands of stocks", "thousands of stocks"],
         ["Survivorship-free daily history available to this study", "from 2020", "decades", "decades"],
     ], None),
    ("p", "These differences have direct consequences for the models in this thesis."),
    ("lp", "1. Returns are truncated, risk is not. ", "No stock can move more than 7% in a day, so almost no daily return "
           "lies beyond three standard deviations (Section 3.1.6). A large fall is instead spread over several sessions "
           "locked at the floor, during which a sell order may not fill. Price limits delay price discovery rather than "
           "remove the move (Kim and Rhee, 1997). A model must therefore treat a predicted exit as uncertain and a "
           "stop-loss as a wish, not a guarantee."),
    ("lp", "2. Every position is held for days. ", "A share bought today cannot be sold until settlement, so same-day "
           "reversals and intraday strategies are impossible, and a wrong signal is paid for over several sessions."),
    ("lp", "3. Only rises can be traded. ", "Without short selling, a model can profit only from stocks that go up; in "
           "the 2022 bear market (−40%) the only defensive action was to hold cash. Long–short anomalies that drive much "
           "of the US literature cannot be exploited here."),
    ("lp", "4. Few independent bets. ", "The liquid cross-section is about 150 stocks, and the most traded ones move "
           "together (mean pairwise correlation 0.39). Ranking-based strategies have far fewer independent choices than "
           "on a market of thousands of stocks, and five positions may behave like two."),
    ("lp", "5. Short, imperfect history. ", "A clean, survivorship-free daily history covers under seven years and three "
           "market regimes. Every configuration tried is a chance to fit noise, so corrections for multiple testing are "
           "essential rather than optional (Bailey and López de Prado, 2014; Bailey et al., 2017)."),
    ("lp", "6. Data must be repaired before use. ", "Unlike the curated databases behind most US studies, the available "
           "feeds contain placeholder prices, incomplete corporate-action adjustment and silent paging errors (Section 3.1.4)."),
    ("lp", "7. Costs bite harder at small size. ", "A minimum order of 100 shares of a 100,000 VND stock is 10 million VND, "
           "so a small account cannot size positions finely, and fees on both sides plus the sales tax are paid on "
           "every round trip."),
    ("lp", "8. Speculative operators. ", "Thinly traded stocks can be moved by coordinated trading that paints chart "
           "patterns (Allen and Gale, 1992; Aggarwal and Wu, 2006). No public record marks which episodes were "
           "manipulated, so the system flags the risk and restricts itself to the liquid universe rather than claiming "
           "to detect it."),
    ("p", "Models and results published on US data cannot therefore be carried over as they are. The closest analogue is "
          "the Chinese A-share market, which also has daily price limits, a 100-share minimum, delayed selling and "
          "restricted short selling, but HOSE has a tighter band, a longer settlement delay and a much smaller liquid "
          "cross-section."),
    ("p", "[Other sections of this chapter are in progress.]"),
]

CH2_VI: list[tuple] = [
    ("h1", "Chương 2. Tổng quan nghiên cứu liên quan"),
    ("h2", "2.1 Thị trường chứng khoán Việt Nam và những khác biệt"),
    ("p", "Phần lớn các nghiên cứu đã công bố về học máy cho giao dịch cổ phiếu dùng dữ liệu Mỹ, và phần lớn nghiên "
          "cứu về thị trường châu Á dùng dữ liệu Trung Quốc đại lục. HOSE có vài điểm giống Trung Quốc nhưng rất ít điểm "
          "giống Mỹ, và nhiều khác biệt trong số đó làm thay đổi điều mà mô hình có thể học và lợi nhuận mà chiến lược "
          "có thể đạt. Bảng 2.1 tóm tắt các khác biệt này."),
    ("table", "Bảng 2.1: Luật giao dịch của HOSE so với các thị trường thường được nghiên cứu (nhà đầu tư cá nhân, cổ "
              "phiếu thường; cần đối chiếu quy định hiện hành trước khi nộp bản cuối).",
     ["", "HOSE (Việt Nam)", "NYSE / Nasdaq (Mỹ)", "Thượng Hải / Thâm Quyến (cổ phiếu A, Trung Quốc)"], [
         ["Biên độ giá mỗi phiên của một mã", "±7%", "không có; tạm dừng 5 phút khi giá một mã vượt khỏi dải quanh giá gần nhất",
          "±10% (±20% ở các bảng tăng trưởng)"],
         ["Thời điểm sớm nhất được bán sau khi mua", "sau khi thanh toán T+2", "ngay trong ngày", "ngày hôm sau"],
         ["Lệnh tối thiểu", "100 cổ phiếu", "1 cổ phiếu", "100 cổ phiếu"],
         ["Bán khống của nhà đầu tư cá nhân", "không có", "có", "hạn chế"],
         ["Thuế khi bán", "0,1% giá trị", "không", "thuế tem (stamp duty)"],
         ["Số mã thanh khoản", "khoảng 150 mã chiếm 98,5% giá trị giao dịch (Mục 3.1.6)", "hàng nghìn mã",
          "hàng nghìn mã"],
         ["Lịch sử ngày không thiên lệch sống sót mà nghiên cứu này có", "từ 2020", "hàng chục năm", "hàng chục năm"],
     ], None),
    ("p", "Những khác biệt này tác động trực tiếp đến các mô hình trong khóa luận."),
    ("lp", "1. Lợi suất bị cắt cụt, rủi ro thì không. ", "Không mã nào được biến động quá 7% trong một phiên, nên gần "
           "như không có lợi suất ngày nào vượt ba độ lệch chuẩn (Mục 3.1.6). Thay vào đó, một cú giảm mạnh bị chia ra "
           "nhiều phiên nằm sàn liên tiếp, trong lúc đó lệnh bán có thể không khớp. Biên độ giá làm chậm quá trình xác "
           "lập giá chứ không xóa được biến động (Kim và Rhee, 1997). Vì vậy mô hình phải coi điểm thoát dự kiến là "
           "không chắc chắn, và lệnh cắt lỗ chỉ là mong muốn chứ không phải bảo đảm."),
    ("lp", "2. Vị thế nào cũng phải giữ vài ngày. ", "Cổ phiếu mua hôm nay chưa bán được cho đến khi thanh toán xong, "
           "nên không thể giao dịch đảo chiều trong ngày hay giao dịch trong phiên, và một tín hiệu sai phải trả giá qua "
           "nhiều phiên."),
    ("lp", "3. Chỉ kiếm lời được khi giá tăng. ", "Không có bán khống, mô hình chỉ có lãi từ những mã tăng giá; trong "
           "thị trường giá xuống năm 2022 (−40%), cách phòng thủ duy nhất là giữ tiền mặt. Các chiến lược mua–bán khống "
           "song song vốn là nền tảng của nhiều nghiên cứu ở Mỹ không áp dụng được ở đây."),
    ("lp", "4. Ít lựa chọn độc lập. ", "Số mã thanh khoản chỉ khoảng 150, và các mã giao dịch nhiều nhất biến động cùng "
           "nhau (tương quan trung bình theo cặp 0,39). Chiến lược xếp hạng có ít lựa chọn độc lập hơn nhiều so với thị "
           "trường hàng nghìn mã, và năm vị thế có thể hành xử như hai."),
    ("lp", "5. Lịch sử ngắn và chưa hoàn hảo. ", "Lịch sử ngày sạch, không thiên lệch sống sót chỉ dài chưa đến bảy năm "
           "với ba giai đoạn thị trường. Mỗi cấu hình thử thêm là một cơ hội khớp nhiễu, nên hiệu chỉnh cho kiểm định đa "
           "giả thuyết là bắt buộc chứ không phải tùy chọn (Bailey và López de Prado, 2014; Bailey và cộng sự, 2017)."),
    ("lp", "6. Dữ liệu phải sửa trước khi dùng. ", "Khác với các cơ sở dữ liệu được chuẩn hóa sau phần lớn nghiên cứu ở "
           "Mỹ, các nguồn hiện có chứa giá giữ chỗ, điều chỉnh sự kiện doanh nghiệp không đầy đủ và lỗi phân trang không "
           "báo lỗi (Mục 3.1.4)."),
    ("lp", "7. Chi phí nặng hơn với vốn nhỏ. ", "Lệnh tối thiểu 100 cổ phiếu của một mã giá 100.000 đồng đã là 10 triệu "
           "đồng, nên tài khoản nhỏ không chia vị thế chi tiết được, và phí hai chiều cộng thuế bán phải trả ở mỗi vòng "
           "giao dịch."),
    ("lp", "8. Các nhóm đầu cơ. ", "Các mã thanh khoản thấp có thể bị kéo giá bởi giao dịch phối hợp, tạo ra mẫu hình "
           "biểu đồ giả (Allen và Gale, 1992; Aggarwal và Wu, 2006). Không có ghi nhận công khai nào cho biết đợt nào bị "
           "thao túng, nên hệ thống chỉ cảnh báo rủi ro và giới hạn trong nhóm mã thanh khoản chứ không tuyên bố phát "
           "hiện được thao túng."),
    ("p", "Vì vậy, mô hình và kết quả công bố trên dữ liệu Mỹ không thể mang sang nguyên vẹn. Thị trường gần nhất để so "
          "sánh là cổ phiếu A của Trung Quốc, cũng có biên độ giá, lệnh tối thiểu 100 cổ phiếu, bán trễ và hạn chế bán "
          "khống, nhưng HOSE có biên độ hẹp hơn, thời gian thanh toán dài hơn và số mã thanh khoản ít hơn nhiều."),
    ("p", "[Các mục khác của chương này đang thực hiện.]"),
]
