"""Word copies of Chapter 1 (Introduction), English and Vietnamese.

    python report/word/build_intro_docx.py

Writes report/word/introduction_en.docx and introduction_vi.docx. The LaTeX chapter
(report/chapters/01-introduction.tex) is the source of truth; keep this text in step with it.
Citations are written author-year here because Word has no BibTeX.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

OUT = Path(__file__).resolve().parent

# Each block: ("h1", text) | ("h2", text) | ("p", text) | ("lead", text) | ("ul", [items])
Block = tuple[str, object]

EN: list[Block] = [
    ("h1", "Chapter 1. Introduction"),
    ("h2", "1.1 Background"),
    ("p", "Deciding when to buy a stock and when to sell it is one of the most common financial "
          "decisions an individual makes, and one of the hardest to make well. The classical view "
          "holds that prices already reflect available information, so that no rule can beat the "
          "market after costs (Fama, 1970); the adaptive view holds that predictability can appear "
          "and fade as conditions change, so whether an edge exists is an empirical question for each "
          "market (Lo, 2004). Machine learning now routinely finds weak but real structure in stock "
          "returns (Krauss et al., 2017; Gu et al., 2020). Whether that structure can be turned into "
          "better decisions on the Vietnamese market, under its own rules, is far less studied."),
    ("h2", "1.2 Problem Statement"),
    ("p", "A trading aid for the Ho Chi Minh City Stock Exchange (HOSE) faces weaknesses on three "
          "sides. Each one, if ignored, makes a system look better on paper than it can be in practice."),
    ("lead", "The market."),
    ("ul", ["The ±7% daily band can lock a falling stock at the floor, so exits are not guaranteed; "
            "settlement forces a position to be held for several sessions.",
            "Trading concentrates in a small group of stocks. Thin stocks have stale prices and are "
            "exposed to speculative operators who move prices and paint misleading chart patterns "
            "(Allen and Gale, 1992; Aggarwal and Wu, 2006).",
            "Fees on both sides and a tax on every sale erase many small statistical edges."]),
    ("lead", "The data."),
    ("ul", ["Sources built from current listings omit delisted companies (survivorship bias).",
            "Corporate actions are adjusted inconsistently; taken as delivered, a commercial feed "
            "contains hundreds of price drops that never happened (Section 3.1).",
            "Defects are silent: duplicated rows reported as success, placeholder prices for sessions "
            "with no trade, fields that disagree with each other."]),
    ("lead", "Common approaches."),
    ("ul", ["Backtests ignore the band, settlement, lot size, fees and taxes, and report the best of "
            "many configurations without correcting for the number tried (Harvey et al., 2016; "
            "Bailey and López de Prado, 2014; Bailey et al., 2017).",
            "Features and labels leak information not yet known on the day of the decision, and a "
            "single test period covers only one market regime.",
            "Models output a probability, not a decision: they do not say whether to act, how much, "
            "when to exit or why, which matters most for investors already prone to overtrading and "
            "to holding losers (Barber and Odean, 2000; Shefrin and Statman, 1985)."]),
    ("h2", "1.3 Proposed Direction"),
    ("p", "This thesis develops an AI-driven decision support system (DSS) for trading HOSE stocks: a "
          "system that supports the investor's decision rather than replacing it (Power, 2002). In outline:"),
    ("ul", ["a cleaned, survivorship-free daily dataset of HOSE stocks, with its defects measured and documented;",
            "a signal layer built on machine-learning models and interpretable price–volume features;",
            "a decision layer that turns signals into recommendations with reasons, position sizes and risk warnings;",
            "an evaluation that enforces HOSE rules and costs, uses walk-forward validation and corrects "
            "for multiple testing;",
            "an interactive application with historical scenario replays, and a MetaTrader 5 "
            "implementation as an independent check."]),
    ("p", "Research questions, scope and the detailed design are fixed in the following chapters as "
          "the work progresses."),
    ("h2", "1.4 Thesis Structure"),
    ("p", "Chapter 2 reviews related work. Chapter 3 describes the data and the system design. Chapter 4 "
          "presents the implementation, Chapter 5 the experiments and Chapter 6 their interpretation. "
          "Chapter 7 concludes."),
]

VI: list[Block] = [
    ("h1", "Chương 1. Giới thiệu"),
    ("h2", "1.1 Bối cảnh"),
    ("p", "Quyết định khi nào mua và khi nào bán một cổ phiếu là một trong những quyết định tài chính "
          "phổ biến nhất của nhà đầu tư cá nhân, và cũng là một trong những quyết định khó làm tốt nhất. "
          "Quan điểm cổ điển cho rằng giá đã phản ánh mọi thông tin sẵn có, nên không quy tắc nào thắng "
          "được thị trường sau chi phí (Fama, 1970); quan điểm thích nghi cho rằng khả năng dự báo có thể "
          "xuất hiện rồi biến mất khi điều kiện thay đổi, nên việc có tồn tại lợi thế hay không là câu hỏi "
          "thực nghiệm cho từng thị trường (Lo, 2004). Học máy ngày nay thường xuyên tìm ra những cấu trúc "
          "yếu nhưng có thật trong lợi suất cổ phiếu (Krauss và cộng sự, 2017; Gu và cộng sự, 2020). Tuy "
          "nhiên, việc biến các cấu trúc đó thành quyết định tốt hơn trên thị trường Việt Nam, theo đúng "
          "luật của thị trường này, vẫn còn rất ít được nghiên cứu."),
    ("h2", "1.2 Đặt vấn đề"),
    ("p", "Một công cụ hỗ trợ giao dịch trên Sở Giao dịch Chứng khoán TP.HCM (HOSE) phải đối mặt với các "
          "điểm yếu từ ba phía. Bỏ qua bất kỳ điểm nào cũng khiến hệ thống trông tốt trên giấy hơn so với "
          "khi vận hành thực tế."),
    ("lead", "Thị trường."),
    ("ul", ["Biên độ ±7% mỗi phiên có thể khiến cổ phiếu đang giảm nằm sàn, nên không đảm bảo thoát được "
            "vị thế; chu kỳ thanh toán buộc phải nắm giữ vị thế trong vài phiên.",
            "Giao dịch tập trung vào một nhóm nhỏ cổ phiếu. Cổ phiếu thanh khoản thấp có giá bị \"đứng\" và "
            "dễ bị các nhóm đầu cơ thao túng giá, tạo ra các mẫu hình biểu đồ gây hiểu lầm (Allen và "
            "Gale, 1992; Aggarwal và Wu, 2006).",
            "Phí giao dịch hai chiều và thuế trên mỗi lệnh bán xóa đi nhiều lợi thế thống kê nhỏ."]),
    ("lead", "Dữ liệu."),
    ("ul", ["Các nguồn dữ liệu xây dựng từ danh sách mã đang niêm yết bỏ sót các công ty đã hủy niêm yết "
            "(thiên lệch sống sót – survivorship bias).",
            "Các sự kiện doanh nghiệp (chia cổ tức, phát hành thêm) được điều chỉnh giá không nhất quán; nếu "
            "dùng nguyên trạng, một nguồn dữ liệu thương mại chứa hàng trăm cú giảm giá chưa từng xảy ra "
            "(Mục 3.1).",
            "Lỗi dữ liệu không báo lỗi: dòng bị trùng lặp mà vẫn trả về thành công, giá giữ chỗ ở các phiên "
            "không có giao dịch, các trường dữ liệu mâu thuẫn nhau."]),
    ("lead", "Các cách tiếp cận phổ biến."),
    ("ul", ["Kiểm thử lịch sử (backtest) bỏ qua biên độ giá, chu kỳ thanh toán, lô giao dịch, phí và thuế, "
            "đồng thời chỉ báo cáo cấu hình tốt nhất trong rất nhiều cấu hình đã thử mà không hiệu chỉnh "
            "cho số lần thử (Harvey và cộng sự, 2016; Bailey và López de Prado, 2014; Bailey và cộng sự, 2017).",
            "Đặc trưng và nhãn rò rỉ thông tin mà vào ngày ra quyết định chưa thể biết, và một giai đoạn "
            "kiểm thử duy nhất chỉ bao phủ một trạng thái thị trường.",
            "Mô hình chỉ đưa ra một xác suất chứ không phải một quyết định: không cho biết có nên hành động "
            "không, với bao nhiêu vốn, khi nào thoát và vì sao. Điều này càng quan trọng với nhà đầu tư vốn "
            "dễ giao dịch quá mức và gồng lỗ (Barber và Odean, 2000; Shefrin và Statman, 1985)."]),
    ("h2", "1.3 Hướng tiếp cận đề xuất"),
    ("p", "Khóa luận nghiên cứu và phát triển một hệ thống hỗ trợ ra quyết định (DSS) dựa trên trí tuệ nhân "
          "tạo cho giao dịch cổ phiếu trên HOSE: một hệ thống hỗ trợ quyết định của nhà đầu tư chứ không "
          "thay thế họ (Power, 2002). Cụ thể gồm:"),
    ("ul", ["bộ dữ liệu ngày của cổ phiếu HOSE đã được làm sạch, không có thiên lệch sống sót, với các lỗi "
            "được đo lường và ghi nhận đầy đủ;",
            "lớp tín hiệu dựa trên các mô hình học máy và các đặc trưng giá – khối lượng có thể diễn giải;",
            "lớp quyết định chuyển tín hiệu thành khuyến nghị kèm lý do, quy mô vị thế và cảnh báo rủi ro;",
            "quy trình đánh giá tuân thủ luật và chi phí giao dịch của HOSE, sử dụng kiểm định "
            "walk-forward và hiệu chỉnh cho kiểm định đa giả thuyết;",
            "ứng dụng tương tác cho phép tái hiện các kịch bản thị trường trong quá khứ, và một bản triển "
            "khai trên MetaTrader 5 để đối chiếu độc lập."]),
    ("p", "Câu hỏi nghiên cứu, phạm vi và thiết kế chi tiết sẽ được xác định ở các chương sau theo tiến độ "
          "thực hiện."),
    ("h2", "1.4 Bố cục khóa luận"),
    ("p", "Chương 2 tổng quan các nghiên cứu liên quan. Chương 3 trình bày dữ liệu và thiết kế hệ thống. "
          "Chương 4 trình bày phần hiện thực, Chương 5 các thực nghiệm và Chương 6 phân tích kết quả. "
          "Chương 7 kết luận."),
]

REFERENCES = [
    "Aggarwal, R. K. and Wu, G. (2006). Stock market manipulations. The Journal of Business, 79(4), 1915–1953.",
    "Allen, F. and Gale, D. (1992). Stock-price manipulation. The Review of Financial Studies, 5(3), 503–529.",
    "Bailey, D. H., Borwein, J. M., López de Prado, M. and Zhu, Q. J. (2017). The probability of backtest "
    "overfitting. Journal of Computational Finance, 20(4), 39–69.",
    "Bailey, D. H. and López de Prado, M. (2014). The deflated Sharpe ratio: correcting for selection bias, "
    "backtest overfitting, and non-normality. The Journal of Portfolio Management, 40(5), 94–107.",
    "Barber, B. M. and Odean, T. (2000). Trading is hazardous to your wealth: the common stock investment "
    "performance of individual investors. The Journal of Finance, 55(2), 773–806.",
    "Fama, E. F. (1970). Efficient capital markets: a review of theory and empirical work. The Journal of "
    "Finance, 25(2), 383–417.",
    "Gu, S., Kelly, B. and Xiu, D. (2020). Empirical asset pricing via machine learning. The Review of "
    "Financial Studies, 33(5), 2223–2273.",
    "Harvey, C. R., Liu, Y. and Zhu, H. (2016). ... and the cross-section of expected returns. The Review of "
    "Financial Studies, 29(1), 5–68.",
    "Krauss, C., Do, X. A. and Huck, N. (2017). Deep neural networks, gradient-boosted trees, random forests: "
    "statistical arbitrage on the S&P 500. European Journal of Operational Research, 259(2), 689–702.",
    "Lo, A. W. (2004). The adaptive markets hypothesis: market efficiency from an evolutionary perspective. "
    "The Journal of Portfolio Management, 30(5), 15–29.",
    "Power, D. J. (2002). Decision Support Systems: Concepts and Resources for Managers. Westport, CT: Quorum Books.",
    "Shefrin, H. and Statman, M. (1985). The disposition to sell winners too early and ride losers too long: "
    "theory and evidence. The Journal of Finance, 40(3), 777–790.",
]

TITLES = {
    "en": ("An AI-Driven Decision Support System for Intelligent Stock Trading", "References"),
    "vi": ("Nghiên cứu và phát triển hệ thống hỗ trợ ra quyết định giao dịch chứng khoán thông minh "
           "dựa trên trí tuệ nhân tạo", "Tài liệu tham khảo"),
}


def _font(style, name: str, size: float, bold: bool = False) -> None:
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    rfonts = style.element.rPr.rFonts
    rfonts.set(qn("w:eastAsia"), name)   # keeps Vietnamese glyphs in the same font
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rfonts.attrib.pop(qn(attr), None)  # heading styles default to the theme font otherwise


def build(blocks: list[Block], lang: str, path: Path) -> None:
    doc = Document()
    for s in doc.sections:
        s.page_height, s.page_width = Cm(29.7), Cm(21.0)
        s.top_margin, s.bottom_margin, s.left_margin, s.right_margin = Cm(2), Cm(2), Cm(3), Cm(2)
    _font(doc.styles["Normal"], "Times New Roman", 13 if lang == "vi" else 12)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.5
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    for name, size in (("Title", 16), ("Heading 1", 16), ("Heading 2", 14)):
        _font(doc.styles[name], "Times New Roman", size, bold=True)
        doc.styles[name].font.color.rgb = None
        doc.styles[name].paragraph_format.space_before = Pt(12)
        doc.styles[name].paragraph_format.space_after = Pt(6)
        doc.styles[name].paragraph_format.keep_with_next = True
    _font(doc.styles["List Bullet"], "Times New Roman", 13 if lang == "vi" else 12)

    title, refs = TITLES[lang]
    doc.add_paragraph(title, style="Title").alignment = WD_ALIGN_PARAGRAPH.CENTER
    for kind, content in blocks:
        if kind == "h1":
            doc.add_heading(str(content), level=1)
        elif kind == "h2":
            doc.add_heading(str(content), level=2)
        elif kind == "lead":
            doc.add_paragraph().add_run(str(content)).bold = True
        elif kind == "ul":
            for item in content:  # type: ignore[union-attr]
                doc.add_paragraph(str(item), style="List Bullet")
        else:
            doc.add_paragraph(str(content)).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.add_heading(refs, level=1)
    for ref in REFERENCES:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Cm(1)
        p.paragraph_format.first_line_indent = Cm(-1)
    doc.save(path)


if __name__ == "__main__":
    build(EN, "en", OUT / "introduction_en.docx")
    build(VI, "vi", OUT / "introduction_vi.docx")
    print("wrote", OUT / "introduction_en.docx", OUT / "introduction_vi.docx")
