#!/usr/bin/env python3
"""Deterministically render the repository research brief Markdown to PDF."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs/research_brief/ReBaseGuard_Research_Brief.md"
DEFAULT_OUTPUT = ROOT / "docs/research_brief/ReBaseGuard_Research_Brief.pdf"
IMAGE_RE = re.compile(r"^!\[(.+)]\((.+)\)$")


def inline_markup(text: str) -> str:
    value = escape(text.strip())
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*(.+?)\*", r"<i>\1</i>", value)
    value = re.sub(r"`(.+?)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"\[(.+?)]\((.+?)\)", r'<u color="#1d4e89">\1</u>', value)
    return value


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "BriefTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=22, leading=25, textColor=colors.HexColor("#17324d"),
            alignment=TA_CENTER, spaceAfter=5 * mm,
        ),
        "h2": ParagraphStyle(
            "BriefH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12.3, leading=14.5, textColor=colors.HexColor("#17324d"),
            spaceBefore=2.5 * mm, spaceAfter=1.3 * mm,
        ),
        "h3": ParagraphStyle(
            "BriefH3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=10.2, leading=12, textColor=colors.HexColor("#355b78"),
            spaceBefore=2 * mm, spaceAfter=1 * mm,
        ),
        "body": ParagraphStyle(
            "BriefBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.35, leading=10.4, alignment=TA_LEFT,
            textColor=colors.HexColor("#222b33"), spaceAfter=1.8 * mm,
        ),
        "author": ParagraphStyle(
            "BriefAuthor", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.3, leading=11.5, alignment=TA_CENTER,
            textColor=colors.HexColor("#263746"), spaceAfter=1 * mm,
        ),
        "note": ParagraphStyle(
            "BriefNote", parent=base["BodyText"], fontName="Helvetica-Oblique",
            fontSize=7.7, leading=9.2, alignment=TA_CENTER,
            textColor=colors.HexColor("#596673"), spaceAfter=2.5 * mm,
        ),
        "bullet": ParagraphStyle(
            "BriefBullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.1, leading=9.8, leftIndent=10, firstLineIndent=-6,
            bulletIndent=2, textColor=colors.HexColor("#222b33"),
            spaceAfter=0.8 * mm,
        ),
        "caption": ParagraphStyle(
            "BriefCaption", parent=base["BodyText"], fontName="Helvetica-Oblique",
            fontSize=7.1, leading=8.4, alignment=TA_CENTER,
            textColor=colors.HexColor("#4d5964"), spaceAfter=1.8 * mm,
        ),
        "code": ParagraphStyle(
            "BriefCode", parent=base["Code"], fontName="Courier",
            fontSize=8, leading=10, leftIndent=8, rightIndent=8,
            backColor=colors.HexColor("#f3f6f8"), borderPadding=5,
            spaceAfter=2 * mm,
        ),
    }


def image_flowable(source: Path, target: str, caption: str) -> list:
    path = (source.parent / target).resolve()
    if not path.is_file() or ROOT not in path.parents:
        raise ValueError(f"invalid or missing brief image: {target}")
    item = Image(str(path))
    max_width, max_height = 174 * mm, 70 * mm
    scale = min(max_width / item.imageWidth, max_height / item.imageHeight)
    item.drawWidth = item.imageWidth * scale
    item.drawHeight = item.imageHeight * scale
    item.hAlign = "CENTER"
    return [item, Spacer(1, 1 * mm), Paragraph(inline_markup(caption), styles()["caption"])]


def table_flowable(rows: list[list[str]]) -> Table:
    rendered = [[Paragraph(inline_markup(cell), styles()["body"]) for cell in row] for row in rows]
    widths = [60 * mm, 50 * mm, 64 * mm] if len(rows[0]) == 3 else None
    table = Table(rendered, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8f2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17324d")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#a9b7c3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return table


def parse_markdown(source: Path) -> list:
    lines = source.read_text(encoding="utf-8").splitlines()
    flow: list = []
    paragraph: list[str] = []
    index = 0
    code_mode = False
    code_lines: list[str] = []
    author_lines = 0
    style_map = styles()

    def flush_paragraph() -> None:
        nonlocal paragraph, author_lines
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph)
        if text.startswith("**Jingzhe Su**"):
            style = style_map["author"]
            rendered = "<br/>".join(inline_markup(part) for part in paragraph)
        elif text.startswith("*Academic research brief"):
            style = style_map["note"]
            rendered = inline_markup(text.replace("  ", " "))
        else:
            style = style_map["body"]
            rendered = inline_markup(text.replace("  ", " "))
        flow.append(Paragraph(rendered, style))
        paragraph = []
        author_lines += 1

    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith("```"):
            flush_paragraph()
            if code_mode:
                flow.append(Preformatted("\n".join(code_lines), style_map["code"]))
                code_lines = []
            code_mode = not code_mode
            index += 1
            continue
        if code_mode:
            code_lines.append(line)
            index += 1
            continue
        if line == "<!-- PAGEBREAK -->":
            flush_paragraph()
            flow.append(PageBreak())
            index += 1
            continue
        if not line:
            flush_paragraph()
            index += 1
            continue
        if line.startswith("| "):
            flush_paragraph()
            raw_rows: list[list[str]] = []
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-:]+", cell) for cell in cells):
                    raw_rows.append(cells)
                index += 1
            flow.append(table_flowable(raw_rows))
            flow.append(Spacer(1, 2 * mm))
            continue
        match = IMAGE_RE.match(line)
        if match:
            flush_paragraph()
            flow.extend(image_flowable(source, match.group(2), match.group(1)))
            index += 1
            continue
        if line.startswith("# "):
            flush_paragraph()
            flow.append(Paragraph(inline_markup(line[2:]), style_map["title"]))
            index += 1
            continue
        if line.startswith("## "):
            flush_paragraph()
            flow.append(Paragraph(inline_markup(line[3:]), style_map["h2"]))
            index += 1
            continue
        if line.startswith("### "):
            flush_paragraph()
            flow.append(Paragraph(inline_markup(line[4:]), style_map["h3"]))
            index += 1
            continue
        if line.startswith("- "):
            flush_paragraph()
            bullet_lines = [line[2:]]
            index += 1
            while index < len(lines) and lines[index].startswith("  "):
                bullet_lines.append(lines[index].strip())
                index += 1
            flow.append(Paragraph(
                inline_markup(" ".join(bullet_lines)),
                style_map["bullet"],
                bulletText="•",
            ))
            continue
        paragraph.append(line.rstrip("  "))
        index += 1
    flush_paragraph()
    if code_mode:
        raise ValueError("unclosed Markdown code fence")
    return flow


def page_decor(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#b8c4ce"))
    canvas.setLineWidth(0.35)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64717c"))
    canvas.drawString(18 * mm, 9 * mm, "ReBaseGuard - Academic Research Brief")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def render(source: Path, output: Path) -> None:
    rl_config.invariant = 1
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=14 * mm, bottomMargin=18 * mm,
        title="ReBaseGuard Academic Research Brief", author="Jingzhe Su",
        subject="Presentation summary of the ReBaseGuard research repository",
        creator="ReBaseGuard deterministic ReportLab renderer",
    )
    document.build(parse_markdown(source), onFirstPage=page_decor, onLaterPages=page_decor)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render(args.source.resolve(), args.output.resolve())
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
