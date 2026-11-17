"""The pre-thesis report as Word files in the IU SCSE thesis format, English and Vietnamese.

    python report/word/build_thesis_docx.py

Writes report/word/pre_thesis_report_en.docx and pre_thesis_report_vi.docx. Layout follows
report/iuthesis.sty: cover, committee approval, acknowledgements, contents, abbreviations, abstract
(roman page numbers), then chapters (arabic, restarting at 1). Chapter text comes from
build_intro_docx (Chapter 1) and content_ch3 (Section 3.1); the LaTeX in report/ is the source of truth.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_intro_docx import EN, REFERENCES, VI, _font  # noqa: E402
from content_ch2 import CH2_EN, CH2_VI  # noqa: E402
from content_ch3 import CH3_EN, CH3_VI  # noqa: E402

FIGURES = HERE.parent / "figures"
LOGO = FIGURES / "iu-logo.png"

META = {
    "en": {
        "header": ["VIETNAM NATIONAL UNIVERSITY OF HO CHI MINH CITY", "THE INTERNATIONAL UNIVERSITY",
                   "SCHOOL OF COMPUTER SCIENCE AND ENGINEERING"],
        "title": "An AI-Driven Decision Support System for Intelligent Stock Trading",
        "by": "By", "student": "Cao Bao Khuong – ITDSIU22176",
        "instructed": "Instructed by", "supervisor": "Assoc. Prof. Ha Viet Uyen Synh",
        "statement": ["A pre-thesis report submitted to the School of Computer Science and Engineering "
                      "in partial fulfillment of the requirements for the degree of", "Bachelor of Data Science"],
        "place": ["Ho Chi Minh City, Vietnam", "January 2027"],
        "approved": "APPROVED BY:", "committee": "THESIS COMMITTEE",
        "member": "(Typed committee name here – {})", "roles": ["Chair", "Member", "Member", "Member"],
        "ack": "Acknowledgements", "toc": "Table of Contents", "abbr": "List of Abbreviations",
        "abstract": "Abstract", "refs": "References", "todo": "[To be written.]", "todo_last": "[To be written last.]",
        "toc_hint": "Right-click and choose Update Field to build the table of contents.",
        "abstract_text": [
            "Choosing when to buy and sell stocks is hard, and harder on the Ho Chi Minh City Stock Exchange (HOSE), "
            "where a ±7% daily price band, delayed settlement, trading costs and speculative operators make many "
            "strategies that look profitable on paper impossible to trade. This thesis develops an AI-driven decision "
            "support system that turns machine-learning signals into explained recommendations with position sizes and "
            "risk warnings, and evaluates it under the exchange's own rules.",
            "This pre-thesis report presents the problem, the proposed system and its data foundation. A "
            "survivorship-free daily dataset of 448 HOSE stocks from February 2020 to October 2026 was collected from "
            "the SSI FastConnect API and cleaned. The work exposed defects that a vendor's success code hides: "
            "overlapping result pages, placeholder prices on 7.9% of stock-sessions and a corporate-action adjustment "
            "that covers only part of the events. Rebuilding the adjustment from the exchange's reference prices left a "
            "single impossible price gap among liquid stocks, and was confirmed by an independent source in 97–99% of "
            "events. Exploratory analysis shows that the 150 most traded stocks carry 98.5% of traded value and nearly "
            "all reliable data, that the daily price band truncates the tails of the return distribution, and that the "
            "most traded stocks are strongly correlated. The models will therefore be trained and evaluated on a liquid "
            "universe re-ranked every session.",
            "The next stages build the signal and decision layers, a backtest that enforces HOSE rules and corrects for "
            "multiple testing, an interactive application that replays historical market scenarios, and a MetaTrader 5 "
            "implementation as an independent check.",
        ],
        "keywords": ("Keywords: ", "decision support system, machine learning, stock trading, Vietnamese stock "
                                   "market, data quality, backtesting."),
        "ch2": ("Chapter 2. Related Work", "[In progress.]"),
        "algo_steps": "Steps",
        "abbreviations": [("AI", "Artificial Intelligence"), ("API", "Application Programming Interface"),
                          ("DSS", "Decision Support System"), ("HOSE", "Ho Chi Minh City Stock Exchange"),
                          ("MT5", "MetaTrader 5"), ("OHLCV", "Open, High, Low, Close, Volume"),
                          ("SSI", "SSI Securities Corporation")],
    },
    "vi": {
        "header": ["ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH", "TRƯỜNG ĐẠI HỌC QUỐC TẾ",
                   "KHOA KHOA HỌC VÀ KỸ THUẬT MÁY TÍNH"],
        "title": "Nghiên cứu và phát triển hệ thống hỗ trợ ra quyết định giao dịch chứng khoán thông minh "
                 "dựa trên trí tuệ nhân tạo",
        "by": "Sinh viên thực hiện", "student": "Cao Bảo Khương – ITDSIU22176",
        "instructed": "Giảng viên hướng dẫn", "supervisor": "PGS. TS. Hà Việt Uyên Synh",
        "statement": ["Báo cáo tiền khóa luận nộp cho Khoa Khoa học và Kỹ thuật Máy tính "
                      "để đáp ứng một phần yêu cầu xét cấp bằng", "Cử nhân Khoa học Dữ liệu"],
        "place": ["Thành phố Hồ Chí Minh, Việt Nam", "Tháng 01 năm 2027"],
        "approved": "ĐƯỢC PHÊ DUYỆT BỞI:", "committee": "HỘI ĐỒNG ĐÁNH GIÁ KHÓA LUẬN",
        "member": "(Họ tên thành viên hội đồng – {})", "roles": ["Chủ tịch", "Thành viên", "Thành viên", "Thành viên"],
        "ack": "Lời cảm ơn", "toc": "Mục lục", "abbr": "Danh mục từ viết tắt",
        "abstract": "Tóm tắt", "refs": "Tài liệu tham khảo", "todo": "[Sẽ viết sau.]", "todo_last": "[Viết sau cùng.]",
        "toc_hint": "Nhấp chuột phải và chọn Update Field để tạo mục lục.",
        "abstract_text": [
            "Quyết định khi nào mua và bán cổ phiếu đã khó, trên Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE) còn "
            "khó hơn: biên độ giá ±7% mỗi phiên, thanh toán trễ, chi phí giao dịch và các nhóm đầu cơ khiến nhiều chiến "
            "lược trông có lãi trên giấy nhưng không thể giao dịch thực tế. Khóa luận phát triển một hệ thống hỗ trợ ra "
            "quyết định dựa trên trí tuệ nhân tạo, chuyển tín hiệu từ học máy thành khuyến nghị kèm lý do, quy mô vị "
            "thế và cảnh báo rủi ro, và đánh giá hệ thống theo đúng luật của sàn.",
            "Báo cáo tiền khóa luận này trình bày vấn đề, hệ thống đề xuất và nền tảng dữ liệu. Bộ dữ liệu ngày của "
            "448 mã HOSE từ tháng 02/2020 đến tháng 10/2026, không có thiên lệch sống sót, được thu thập từ API "
            "FastConnect của SSI và làm sạch. Quá trình này phát hiện các lỗi mà mã báo thành công của nhà cung cấp che "
            "giấu: các trang kết quả chồng lấn nhau, giá giữ chỗ ở 7,9% số mã-phiên và việc điều chỉnh giá theo sự kiện "
            "doanh nghiệp chỉ phủ một phần các sự kiện. Việc tự điều chỉnh lại từ giá tham chiếu của sở chỉ còn để lại "
            "một gap giá bất khả trong nhóm mã thanh khoản, và được một nguồn độc lập xác nhận ở 97–99% số sự kiện. "
            "Phân tích khám phá cho thấy 150 mã giao dịch nhiều nhất chiếm 98,5% giá trị giao dịch và gần như toàn bộ "
            "dữ liệu đáng tin, biên độ giá cắt cụt đuôi phân phối lợi suất, và các mã giao dịch nhiều nhất có tương "
            "quan mạnh với nhau. Vì vậy mô hình sẽ được huấn luyện và đánh giá trên nhóm mã thanh khoản được xếp hạng "
            "lại mỗi phiên.",
            "Các giai đoạn tiếp theo xây dựng lớp tín hiệu và lớp quyết định, một hệ thống kiểm thử lịch sử tuân thủ "
            "luật HOSE và hiệu chỉnh cho kiểm định đa giả thuyết, một ứng dụng tương tác tái hiện các kịch bản thị "
            "trường trong quá khứ, và một bản triển khai trên MetaTrader 5 để đối chiếu độc lập.",
        ],
        "keywords": ("Từ khóa: ", "hệ thống hỗ trợ ra quyết định, học máy, giao dịch chứng khoán, thị trường chứng "
                                  "khoán Việt Nam, chất lượng dữ liệu, kiểm thử lịch sử."),
        "ch2": ("Chương 2. Tổng quan nghiên cứu liên quan", "[Đang thực hiện.]"),
        "algo_steps": "Các bước",
        "abbreviations": [("AI", "Trí tuệ nhân tạo (Artificial Intelligence)"),
                          ("API", "Giao diện lập trình ứng dụng (Application Programming Interface)"),
                          ("DSS", "Hệ thống hỗ trợ ra quyết định (Decision Support System)"),
                          ("HOSE", "Sở Giao dịch Chứng khoán TP. Hồ Chí Minh"), ("MT5", "MetaTrader 5"),
                          ("OHLCV", "Giá mở cửa, cao nhất, thấp nhất, đóng cửa, khối lượng"),
                          ("SSI", "Công ty Cổ phần Chứng khoán SSI")],
    },
}


def _field(paragraph, instr: str, placeholder: str = "") -> None:
    """Insert a Word field (PAGE, TOC ...). Word fills it in; press F9 / update to refresh."""
    run = paragraph.add_run()
    for tag, attr in (("w:fldChar", "begin"), ("w:instrText", None), ("w:fldChar", "separate")):
        el = OxmlElement(tag)
        if attr:
            el.set(qn("w:fldCharType"), attr)
        else:
            el.set(qn("xml:space"), "preserve")
            el.text = instr
        run._r.append(el)
    paragraph.add_run(placeholder)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    paragraph.add_run()._r.append(end)


def _page_numbers(section, fmt: str, start: int | None) -> None:
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _field(p, "PAGE", "1")
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    section._sectPr.append(pg)


def _centered(doc, text: str, size: float, bold: bool = False, space_after: float = 0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    r.bold, r.font.size = bold, Pt(size)
    return p


def _page_break(doc) -> None:
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def _caption(doc, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    r.italic, r.font.size = True, Pt(11)


def _cell_text(cell, text: str, bold: bool = False, size: float = 10) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold, r.font.size = bold, Pt(size)


def _table(doc, caption: str, header: list[str], rows: list[list[str]], note: str | None) -> None:
    _caption(doc, caption)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(header):
        _cell_text(t.cell(0, j), h, bold=True)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            _cell_text(t.cell(i, j), v)
    if note:
        p = doc.add_paragraph()
        p.add_run(note).font.size = Pt(9)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(0)


def _figure(doc, caption: str, file: str, width_cm: float) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(FIGURES / file), width=Cm(width_cm))
    _caption(doc, caption)


def _algorithm(doc, caption: str, steps: list[str]) -> None:
    """A boxed, numbered list: Word has no algorithm environment."""
    t = doc.add_table(rows=2, cols=1)
    t.style = "Table Grid"
    _cell_text(t.cell(0, 0), caption, bold=True, size=11)
    cell = t.cell(1, 0)
    cell.text = ""
    for k, step in enumerate(steps, start=1):
        p = cell.paragraphs[0] if k == 1 else cell.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.7)
        p.add_run(f"{k}.\t{step}").font.size = Pt(10.5)
    doc.add_paragraph()


def _body(doc, blocks: list) -> None:
    for block in blocks:
        kind = block[0]
        if kind == "h1":
            number, _, name = str(block[1]).partition(". ")
            h = doc.add_heading(f"{number.upper()}: {name.upper()}", level=1)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif kind == "h2":
            doc.add_heading(block[1], level=2)
        elif kind == "h3":
            doc.add_heading(block[1], level=3)
        elif kind == "lead":
            doc.add_paragraph().add_run(block[1]).bold = True
        elif kind == "lp":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.add_run(block[1]).bold = True
            p.add_run(block[2])
        elif kind == "ul":
            for item in block[1]:
                doc.add_paragraph(item, style="List Bullet")
        elif kind == "table":
            _table(doc, *block[1:])
        elif kind == "fig":
            _figure(doc, *block[1:])
        elif kind == "algo":
            _algorithm(doc, *block[1:])
        else:
            doc.add_paragraph(block[1]).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def build(lang: str, ch1: list, ch2: list, ch3: list, out: Path) -> None:
    m = META[lang]
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.top_margin, sec.bottom_margin, sec.left_margin, sec.right_margin = Cm(2.5), Cm(2.5), Cm(3), Cm(2)
    sec.different_first_page_header_footer = True          # no number on the cover
    body_size = 13 if lang == "vi" else 12
    _font(doc.styles["Normal"], "Times New Roman", body_size)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.5
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 13)):
        _font(doc.styles[name], "Times New Roman", size, bold=True)
        doc.styles[name].font.color.rgb = None
        doc.styles[name].font.italic = False
        doc.styles[name].paragraph_format.space_before = Pt(12)
        doc.styles[name].paragraph_format.space_after = Pt(8)
        doc.styles[name].paragraph_format.keep_with_next = True
    _font(doc.styles["List Bullet"], "Times New Roman", body_size)

    # cover --------------------------------------------------------------------------------
    for line in m["header"]:
        _centered(doc, line, 13, bold=True, space_after=2)
    doc.add_paragraph()
    if LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO), width=Cm(3.5))
    doc.add_paragraph()
    _centered(doc, m["title"].upper(), 17, bold=True, space_after=30)
    _centered(doc, m["by"], 13)
    _centered(doc, m["student"], 13, bold=True, space_after=18)
    _centered(doc, m["instructed"], 13)
    _centered(doc, m["supervisor"], 13, bold=True)
    for _ in range(3):
        doc.add_paragraph()
    _centered(doc, m["statement"][0], 12)
    _centered(doc, m["statement"][1], 12, space_after=18)
    for line in m["place"]:
        _centered(doc, line, 12)
    _page_break(doc)

    # committee approval -------------------------------------------------------------------
    _centered(doc, m["title"], 15, bold=True, space_after=36)
    _centered(doc, m["approved"], 12, bold=True, space_after=36)
    for role in m["roles"]:
        p = doc.add_paragraph("_" * 40)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p = doc.add_paragraph(m["member"].format(role))
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_after = Pt(30)
    _centered(doc, m["committee"], 12, bold=True)
    _page_break(doc)

    # acknowledgements, contents, abbreviations, abstract ------------------------------------
    for heading, text in ((m["ack"], m["todo"]),):
        doc.add_heading(heading, level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(text)
    _page_break(doc)
    _centered(doc, m["toc"], 16, bold=True, space_after=12)
    _field(doc.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u', m["toc_hint"])
    _page_break(doc)
    doc.add_heading(m["abbr"], level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    table = doc.add_table(rows=0, cols=2)
    for short, long in m["abbreviations"]:
        cells = table.add_row().cells
        cells[0].text, cells[1].text = short, long
        cells[0].width, cells[1].width = Cm(3), Cm(12)
    _page_break(doc)
    doc.add_heading(m["abstract"], level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    for para in m["abstract_text"]:
        doc.add_paragraph(para).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    kw = doc.add_paragraph()
    kw.add_run(m["keywords"][0]).bold = True
    kw.add_run(m["keywords"][1])
    _page_numbers(sec, "lowerRoman", None)

    # main matter -------------------------------------------------------------------------------
    main = doc.add_section(WD_SECTION.NEW_PAGE)
    main.different_first_page_header_footer = False
    _page_numbers(main, "decimal", 1)
    _body(doc, ch1)
    _page_break(doc)
    _body(doc, ch2)
    _page_break(doc)
    _body(doc, ch3)
    _page_break(doc)
    doc.add_heading(m["refs"], level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    for ref in REFERENCES:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Cm(1)
        p.paragraph_format.first_line_indent = Cm(-1)
    doc.save(out)
    print("wrote", out)


if __name__ == "__main__":
    build("en", EN, CH2_EN, CH3_EN, HERE / "pre_thesis_report_en.docx")
    build("vi", VI, CH2_VI, CH3_VI, HERE / "pre_thesis_report_vi.docx")
