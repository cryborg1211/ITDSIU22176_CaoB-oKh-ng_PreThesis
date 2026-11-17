"""The pre-thesis report as one Word file in the IU SCSE thesis format, with Chapter 1 inside.

    python report/word/build_thesis_docx.py

Writes report/word/pre_thesis_report.docx. Layout follows report/iuthesis.sty: cover, committee
approval, acknowledgements, contents, abbreviations, abstract (roman page numbers), then chapters
(arabic, restarting at 1). Chapter text comes from build_intro_docx.EN so the two never diverge.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_intro_docx import EN, REFERENCES, _font  # noqa: E402

OUT = Path(__file__).resolve().parent / "pre_thesis_report.docx"

META = {
    "title": "An AI-Driven Decision Support System for Intelligent Stock Trading",
    "student": "Cao Bao Khuong",
    "id": "ITDSIU22176",
    "supervisor": "Assoc. Prof. Ha Viet Uyen Synh",
    "kind": "pre-thesis report",
    "degree": "Bachelor of Data Science",
    "date": "January 2027",
}
ABBREVIATIONS = [
    ("AI", "Artificial Intelligence"),
    ("DSS", "Decision Support System"),
    ("HOSE", "Ho Chi Minh City Stock Exchange"),
    ("MT5", "MetaTrader 5"),
]


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


def _front_heading(doc, text: str) -> None:
    """Unnumbered chapter-level heading that still appears in the table of contents."""
    h = doc.add_heading(text, level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER


def build() -> None:
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.top_margin, sec.bottom_margin, sec.left_margin, sec.right_margin = Cm(2.5), Cm(2.5), Cm(3), Cm(2)
    sec.different_first_page_header_footer = True          # no number on the cover
    _font(doc.styles["Normal"], "Times New Roman", 12)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.5
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    for name, size in (("Heading 1", 16), ("Heading 2", 14)):
        _font(doc.styles[name], "Times New Roman", size, bold=True)
        doc.styles[name].font.color.rgb = None
        doc.styles[name].paragraph_format.space_before = Pt(12)
        doc.styles[name].paragraph_format.space_after = Pt(12)
        doc.styles[name].paragraph_format.keep_with_next = True
    _font(doc.styles["List Bullet"], "Times New Roman", 12)

    # cover ---------------------------------------------------------------------------------
    for line in ("VIETNAM NATIONAL UNIVERSITY OF HO CHI MINH CITY", "THE INTERNATIONAL UNIVERSITY",
                 "SCHOOL OF COMPUTER SCIENCE AND ENGINEERING"):
        _centered(doc, line, 13, bold=True, space_after=2)
    doc.add_paragraph()
    logo = Path(__file__).resolve().parents[1] / "figures" / "iu-logo.png"
    if logo.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(logo), width=Cm(3.5))
    doc.add_paragraph()
    _centered(doc, META["title"].upper(), 18, bold=True, space_after=36)
    _centered(doc, "By", 13)
    _centered(doc, f"{META['student']} – {META['id']}", 13, bold=True, space_after=18)
    _centered(doc, "Instructed by", 13)
    _centered(doc, META["supervisor"], 13, bold=True)
    for _ in range(3):
        doc.add_paragraph()
    _centered(doc, f"A {META['kind']} submitted to the School of Computer Science and Engineering "
                   "in partial fulfillment of the requirements for the degree of", 12)
    _centered(doc, META["degree"], 12, space_after=18)
    _centered(doc, "Ho Chi Minh City, Vietnam", 12)
    _centered(doc, META["date"], 12)
    _page_break(doc)

    # committee approval --------------------------------------------------------------------
    _centered(doc, META["title"], 15, bold=True, space_after=36)
    _centered(doc, "APPROVED BY:", 12, bold=True, space_after=36)
    for role in ("Chair", "Member", "Member", "Member"):
        p = doc.add_paragraph("_" * 40)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p = doc.add_paragraph(f"(Typed committee name here – {role})")
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_after = Pt(30)
    _centered(doc, "THESIS COMMITTEE", 12, bold=True)
    _page_break(doc)

    # acknowledgements, contents, abbreviations, abstract -------------------------------------
    _front_heading(doc, "Acknowledgements")
    doc.add_paragraph("[To be written.]")
    _page_break(doc)
    _centered(doc, "Table of Contents", 16, bold=True, space_after=12)
    _field(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u',
           "Right-click and choose Update Field to build the table of contents.")
    _page_break(doc)
    _front_heading(doc, "List of Abbreviations")
    table = doc.add_table(rows=0, cols=2)
    for short, long in ABBREVIATIONS:
        cells = table.add_row().cells
        cells[0].text, cells[1].text = short, long
        cells[0].width, cells[1].width = Cm(3), Cm(12)
    _page_break(doc)
    _front_heading(doc, "Abstract")
    doc.add_paragraph("[To be written last.]")
    _page_numbers(sec, "lowerRoman", None)

    # main matter: new section so page numbers restart in arabic ------------------------------
    main = doc.add_section(WD_SECTION.NEW_PAGE)
    main.different_first_page_header_footer = False
    _page_numbers(main, "decimal", 1)

    for kind, content in EN:
        if kind == "h1":
            number, _, name = str(content).partition(". ")
            h = doc.add_heading(f"{number.replace('Chapter', 'CHAPTER')}: {name.upper()}", level=1)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif kind == "h2":
            doc.add_heading(str(content), level=2)
        elif kind == "lead":
            doc.add_paragraph().add_run(str(content)).bold = True
        elif kind == "ul":
            for item in content:  # type: ignore[union-attr]
                doc.add_paragraph(str(item), style="List Bullet")
        else:
            doc.add_paragraph(str(content)).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    _page_break(doc)
    _front_heading(doc, "References")
    for ref in REFERENCES:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Cm(1)
        p.paragraph_format.first_line_indent = Cm(-1)
    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
