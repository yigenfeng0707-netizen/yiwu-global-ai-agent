#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English one-pager docx generator (P3-3).

Dedicated typography for the English investor/competition one-pager —
distinct from generate_all_docx.py which uses Chinese fonts (微软雅黑/黑体).

Design:
  - Body: Calibri 9.5pt (clean sans, universally available on Windows/Mac)
  - Headings: Georgia bold (classic business serif) with Yiwu-red accent
  - Margins: 1.5cm all sides to fit a single page
  - Tables: light borders + header shading, 9pt body
  - Compact paragraph spacing to maximise information density

Input : docs/OnePager_EN.md
Output: docs/OnePager_EN.docx
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml
from docx.shared import Cm, Pt, RGBColor

# ── Paths ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent / "docs"
MD_PATH = BASE_DIR / "OnePager_EN.md"
DOCX_PATH = BASE_DIR / "OnePager_EN.docx"

# ── Typography ───────────────────────────────────────
FONT_BODY = "Calibri"
FONT_HEADING = "Georgia"
ACCENT = RGBColor(0xD4, 0x27, 0x2C)          # Yiwu red #D4272C
DARK = RGBColor(0x1F, 0x29, 0x37)            # near-black for body
MUTED = RGBColor(0x6B, 0x72, 0x80)           # gray for tagline/meta
TABLE_HEADER_BG = "F3F4F6"                   # light gray
TABLE_ALT_BG = "FAFAFA"                      # subtle zebra


# ── Low-level helpers ────────────────────────────────

def set_cell_shading(cell, color_hex: str) -> None:
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_table_borders(table) -> None:
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{edge}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:color"), "D1D5DB")
        borders.append(b)
    tblPr.append(borders)


def set_paragraph_spacing(paragraph, before: int = 0, after: int = 2, line: float = 1.08) -> None:
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def add_runs_with_inline_formatting(paragraph, text: str, base_font: str = FONT_BODY,
                                    base_size: Pt = Pt(9.5), base_color: RGBColor = DARK) -> None:
    """Render **bold** and *italic* inline markdown; strip backticks to plain text."""
    # Strip code ticks (rare in one-pager, keep plain)
    text = text.replace("`", "")
    # Tokenise by **bold** and *italic*
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*)")
    parts = pattern.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        else:
            run = paragraph.add_run(part)
        run.font.name = base_font
        run.font.size = base_size
        run.font.color.rgb = base_color
        # Ensure East-Asian font slot is also set (Word quirk)
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn("w:ascii"), base_font)
        rFonts.set(qn("w:hAnsi"), base_font)
        rFonts.set(qn("w:cs"), base_font)


# ── Block renderers ──────────────────────────────────

def add_title(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=2, line=1.0)
    run = p.add_run(text)
    run.font.name = FONT_HEADING
    run.font.size = Pt(20)
    run.bold = True
    run.font.color.rgb = ACCENT
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), FONT_HEADING)
    rFonts.set(qn("w:hAnsi"), FONT_HEADING)
    rPr.append(rFonts)


def add_tagline(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=4, line=1.05)
    run = p.add_run(text)
    run.font.name = FONT_HEADING
    run.font.size = Pt(11)
    run.italic = True
    run.font.color.rgb = MUTED
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), FONT_HEADING)
    rFonts.set(qn("w:hAnsi"), FONT_HEADING)
    rPr.append(rFonts)


def add_meta_line(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=0, after=6, line=1.0)
    add_runs_with_inline_formatting(p, text, base_font=FONT_BODY, base_size=Pt(9), base_color=MUTED)


def add_blockquote(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_paragraph_spacing(p, before=2, after=6, line=1.15)
    p.paragraph_format.left_indent = Cm(0.4)
    p.paragraph_format.right_indent = Cm(0.4)
    add_runs_with_inline_formatting(p, text, base_size=Pt(9.5), base_color=DARK)
    # Left accent bar via paragraph border
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:color"), "D4272C")
    left.set(qn("w:space"), "8")
    pBdr.append(left)
    pPr.append(pBdr)


def add_h2(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=8, after=3, line=1.0)
    run = p.add_run(text)
    run.font.name = FONT_HEADING
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = ACCENT
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), FONT_HEADING)
    rFonts.set(qn("w:hAnsi"), FONT_HEADING)
    rPr.append(rFonts)
    # Bottom hairline under heading
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:color"), "E5E7EB")
    bottom.set(qn("w:space"), "2")
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_body_paragraph(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_paragraph_spacing(p, before=0, after=3, line=1.15)
    add_runs_with_inline_formatting(p, text, base_size=Pt(9.5))


def add_bullet(doc: Document, text: str, level: int = 0) -> None:
    p = doc.add_paragraph(style="List Bullet")
    set_paragraph_spacing(p, before=0, after=2, line=1.1)
    p.paragraph_format.left_indent = Cm(0.5 + 0.4 * level)
    add_runs_with_inline_formatting(p, text, base_size=Pt(9.5))


def add_numbered(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Number")
    set_paragraph_spacing(p, before=0, after=2, line=1.1)
    p.paragraph_format.left_indent = Cm(0.5)
    add_runs_with_inline_formatting(p, text, base_size=Pt(9.5))


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table)

    # Header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        set_paragraph_spacing(p, before=1, after=1, line=1.0)
        run = p.add_run(h.strip())
        run.bold = True
        run.font.name = FONT_BODY
        run.font.size = Pt(9)
        run.font.color.rgb = DARK
        set_cell_shading(hdr_cells[i], TABLE_HEADER_BG)

    # Body rows
    for r_idx, row in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            if c_idx >= len(cells):
                break
            cells[c_idx].text = ""
            p = cells[c_idx].paragraphs[0]
            set_paragraph_spacing(p, before=1, after=1, line=1.05)
            add_runs_with_inline_formatting(p, val.strip(), base_size=Pt(9))
            if r_idx % 2 == 1:
                set_cell_shading(cells[c_idx], TABLE_ALT_BG)

    # Spacer after table
    sp = doc.add_paragraph()
    set_paragraph_spacing(sp, before=0, after=2, line=1.0)


def add_horizontal_rule(doc: Document) -> None:
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=2, after=4, line=1.0)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:color"), "D4272C")
    bottom.set(qn("w:space"), "1")
    pBdr.append(bottom)
    pPr.append(pBdr)


# ── Markdown parser (focused subset) ─────────────────

def parse_markdown(md: str):
    """Yield (kind, payload) tuples for the one-pager's markdown subset."""
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            yield ("hr", None)
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            yield ("h1", stripped[2:].strip())
            i += 1
            continue
        if stripped.startswith("## "):
            yield ("h2", stripped[3:].strip())
            i += 1
            continue

        # Blockquote (single or multi-line contiguous)
        if stripped.startswith("> "):
            buf = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            yield ("quote", " ".join(buf))
            continue

        # Table (header | sep | rows)
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_line = lines[i].strip().strip("|")
                rows.append([c.strip() for c in row_line.split("|")])
                i += 1
            yield ("table", (headers, rows))
            continue

        # Numbered list
        m_num = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m_num:
            yield ("numbered", m_num.group(2))
            i += 1
            continue

        # Bullet list
        if stripped.startswith("- "):
            yield ("bullet", stripped[2:].strip())
            i += 1
            continue

        # Plain paragraph (merge contiguous non-blank, non-special lines)
        buf = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if (nxt.startswith("#") or nxt.startswith(">") or nxt.startswith("|")
                    or nxt.startswith("- ") or nxt in ("---", "***", "___")
                    or re.match(r"^\d+\.\s+", nxt)):
                break
            buf.append(nxt)
            i += 1
        yield ("para", " ".join(buf))


# ── Document assembly ────────────────────────────────

def build_document(md_text: str) -> Document:
    doc = Document()

    # Page setup: A4, tight margins to fit one page
    section = doc.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.4)
    section.bottom_margin = Cm(1.4)
    section.left_margin = Cm(1.6)
    section.right_margin = Cm(1.6)

    # Default style
    style = doc.styles["Normal"]
    style.font.name = FONT_BODY
    style.font.size = Pt(9.5)
    style.font.color.rgb = DARK
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), FONT_BODY)
    rFonts.set(qn("w:hAnsi"), FONT_BODY)

    # First-pass: pull title + tagline + meta from leading blocks so we can
    # render them with dedicated typography (centered, accent color).
    blocks = list(parse_markdown(md_text))

    title_done = False
    tagline_done = False
    meta_done = False

    for kind, payload in blocks:
        if kind == "h1" and not title_done:
            add_title(doc, payload)
            title_done = True
            continue
        if kind == "para" and title_done and not tagline_done and payload.startswith("**") and "**" in payload[2:]:
            # First paragraph right after H1 with bold — treat as tagline
            # Strip **...** wrapper for display
            clean = payload.replace("**", "")
            add_tagline(doc, clean)
            tagline_done = True
            continue
        if kind == "quote" and tagline_done and not meta_done:
            add_blockquote(doc, payload)
            meta_done = True
            continue
        if kind == "para" and meta_done and payload.startswith("**Founder:**"):
            add_meta_line(doc, payload)
            continue

        if kind == "hr":
            add_horizontal_rule(doc)
        elif kind == "h2":
            add_h2(doc, payload)
        elif kind == "quote":
            add_blockquote(doc, payload)
        elif kind == "table":
            headers, rows = payload
            add_table(doc, headers, rows)
        elif kind == "bullet":
            add_bullet(doc, payload)
        elif kind == "numbered":
            add_numbered(doc, payload)
        elif kind == "para":
            add_body_paragraph(doc, payload)

    return doc


def main() -> int:
    if not MD_PATH.exists():
        print(f"[ERROR] Markdown source not found: {MD_PATH}")
        return 1

    md_text = MD_PATH.read_text(encoding="utf-8")
    doc = build_document(md_text)
    doc.save(DOCX_PATH)
    print(f"[OK] Generated: {DOCX_PATH}")
    print(f"     Source:    {MD_PATH}")
    print(f"     Size:      {DOCX_PATH.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
