"""Render Markdown documentation into a properly formatted PDF.

Built on ReportLab Platypus (already a project dependency) so no extra system
libraries are required. Supports the Markdown subset used across DevPilot docs:
ATX headings, paragraphs with inline formatting, fenced code blocks, bullet and
ordered lists, blockquotes, horizontal rules, links and pipe tables. Output
gets a title header, footer with page numbers, and clean typography.
"""

import re
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfgen_canvas
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND = colors.HexColor("#2563EB")
INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#6B7280")
CODE_BG = colors.HexColor("#F3F4F6")
CODE_BORDER = colors.HexColor("#D1D5DB")
QUOTE_LINE = colors.HexColor("#93C5FD")

_MONO_FONT = "Courier"
_BODY_FONT = "Helvetica"
_BODY_BOLD = "Helvetica-Bold"
_BODY_ITALIC = "Helvetica-Oblique"


def _register_fonts() -> None:
    """Load a nicer monospace font if the bundled font file is available."""
    from pathlib import Path

    candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "JetBrainsMono-Regular.ttf",
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSansMono.ttf",
        Path("/System/Library/Fonts/Menlo.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]
    for font_path in candidates:
        try:
            if font_path.exists():
                pdfmetrics.registerFont(TTFont("Mono", str(font_path)))
                return
        except Exception:  # noqa: S112  # fall back to Courier
            continue


_register_fonts()
MONO_FONT = "Mono" if "Mono" in pdfmetrics.getRegisteredFontNames() else _MONO_FONT


def _inline(text: str) -> str:
    """Convert Markdown inline syntax into ReportLab Paragraph markup."""
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    spans: list[str] = []

    def _capture(match: "re.Match[str]") -> str:
        spans.append(match.group(1))
        return f"§{len(spans)}§"

    text = re.sub(r"`([^`]+)`", _capture, escaped)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<link href="\2" color="#2563EB">\1</link>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*])\*([^*\n]+)\*(?![\*])", r"<i>\1</i>", text)
    text = re.sub(r"^(#{1,6})\s+(.+?)\s*#*\s*$", r"<b>\2</b>", text, flags=re.M)

    for index, span in enumerate(spans, start=1):
        code = span.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace(f"§{index}§", f'<font face="{MONO_FONT}">{code}</font>')
    return text


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _split_blocks(markdown: str) -> list[tuple[str, list[str]]]:
    """Split raw markdown into ``("fence" | "block", lines)`` groups."""
    blocks: list[tuple[str, list[str]]] = []
    current: list[str] = []
    fence: list[str] | None = None
    fence_marker: str | None = None

    for line in markdown.split("\n"):
        stripped = line.strip()
        if fence_marker is not None:
            if stripped.startswith(fence_marker):
                blocks.append(("fence", fence or []))
                fence, fence_marker = None, None
            else:
                fence.append(line)
            continue
        if stripped.startswith("```"):
            if current:
                blocks.append(("block", current))
                current = []
            fence_marker = stripped[:3]
            fence = []
            continue
        if stripped == "":
            if current:
                blocks.append(("block", current))
                current = []
            continue
        current.append(line)

    if fence_marker is not None:
        blocks.append(("fence", fence or []))
    if current:
        blocks.append(("block", current))
    return blocks


class _NumberedCanvas(pdfgen_canvas.Canvas):
    """Canvas that draws ``Page X of Y`` in the footer on save."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont(_BODY_FONT, 8)
            self.setFillColor(MUTED)
            self.drawRightString(letter[0] - 0.75 * inch, 0.55 * inch, f"Page {self._pageNumber} of {total}")
            super().showPage()
        super().save()


class PdfService:
    """Build a formatted PDF document from Markdown source."""

    def markdown_to_pdf(self, title: str, markdown: str, subtitle: str = "") -> bytes:
        styles = self._styles()
        story: list = []

        story.append(Paragraph(_escape(title), styles["title"]))
        if subtitle:
            story.append(Spacer(1, 0.08 * inch))
            story.append(Paragraph(_escape(subtitle), styles["subtitle"]))
        story.append(Spacer(1, 0.16 * inch))
        story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND, spaceAfter=0.25 * inch))

        for kind, lines in _split_blocks(markdown):
            if kind == "fence":
                story.append(self._code_block(lines))
            else:
                story.append(self._block(lines, styles))

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.9 * inch,
            rightMargin=0.9 * inch,
            topMargin=0.9 * inch,
            bottomMargin=0.9 * inch,
            title=title,
            author="DevPilot AI",
            subject=title,
        )

        def _decorate(canvas: pdfgen_canvas.Canvas, _doc) -> None:
            canvas.saveState()
            canvas.setFont(_BODY_FONT, 8)
            canvas.setFillColor(MUTED)
            canvas.drawString(0.9 * inch, letter[1] - 0.62 * inch, title[:80])
            canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
            canvas.setLineWidth(0.5)
            canvas.line(0.9 * inch, letter[1] - 0.7 * inch, letter[0] - 0.9 * inch, letter[1] - 0.7 * inch)
            canvas.restoreState()

        doc.build(story, onFirstPage=_decorate, onLaterPages=_decorate, canvasmaker=_NumberedCanvas)
        return buffer.getvalue()

    def _styles(self) -> dict[str, ParagraphStyle]:
        base = ParagraphStyle(
            "body",
            fontName=_BODY_FONT,
            fontSize=10,
            leading=14.5,
            alignment=TA_JUSTIFY,
            textColor=INK,
            spaceAfter=8,
        )
        return {
            "title": ParagraphStyle(
                "title", fontName=_BODY_BOLD, fontSize=26, leading=31, textColor=INK, spaceAfter=2, alignment=TA_LEFT
            ),
            "subtitle": ParagraphStyle(
                "subtitle",
                fontName=_BODY_FONT,
                fontSize=10.5,
                leading=14,
                textColor=MUTED,
                spaceAfter=4,
            ),
            "h1": ParagraphStyle(
                "h1", fontName=_BODY_BOLD, fontSize=20, leading=25, textColor=INK, spaceBefore=14, spaceAfter=7
            ),
            "h2": ParagraphStyle(
                "h2", fontName=_BODY_BOLD, fontSize=15, leading=19, textColor=INK, spaceBefore=12, spaceAfter=5
            ),
            "h3": ParagraphStyle(
                "h3", fontName=_BODY_BOLD, fontSize=12, leading=16, textColor=INK, spaceBefore=10, spaceAfter=4
            ),
            "h4": ParagraphStyle(
                "h4", fontName=_BODY_BOLD, fontSize=10.5, leading=14, textColor=MUTED, spaceBefore=8, spaceAfter=3
            ),
            "body": base,
            "bullet": ParagraphStyle(
                "bullet",
                parent=base,
                alignment=TA_LEFT,
                spaceAfter=2,
                leftIndent=16,
                bulletIndent=4,
            ),
            "blockquote": ParagraphStyle(
                "blockquote",
                parent=base,
                fontName=_BODY_ITALIC,
                alignment=TA_LEFT,
                textColor=colors.HexColor("#4B5563"),
                leftIndent=14,
                spaceAfter=10,
            ),
            "cell": ParagraphStyle(
                "cell", fontName=_BODY_FONT, fontSize=9, leading=12, alignment=TA_LEFT, textColor=INK
            ),
        }

    def _block(self, lines: list[str], styles: dict[str, ParagraphStyle]):
        stripped = lines[0].strip()
        if not lines or stripped == "":
            return Spacer(1, 4)

        # Horizontal rule
        if len(lines) == 1 and re.fullmatch(r"[-*_]{3,}", stripped):
            return HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#D1D5DB"), spaceAfter=10)

        # Setext headings
        if len(lines) >= 2 and re.fullmatch(r"=+\s*", lines[1]):
            return Paragraph(_inline(" ".join(lines[:-1])), styles["h1"])
        if len(lines) >= 2 and re.fullmatch(r"-{3,}\s*", lines[1]):
            return Paragraph(_inline(" ".join(lines[:-1])), styles["h2"])

        # ATX headings
        match = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if match:
            level = len(match.group(1))
            return Paragraph(_inline(match.group(2)), styles[f"h{min(level, 4)}"])

        # Blockquote
        if all(line.lstrip().startswith(">") for line in lines):
            quote_lines = [re.sub(r"^\s*>\s?", "", line) for line in lines if line.strip()]
            quote = Paragraph(_inline(" ".join(quote_lines)), styles["blockquote"])
            box = Table([[quote]], colWidths=[None])
            box.setStyle(
                TableStyle(
                    [
                        ("LINEBEFORE", (0, 0), (0, -1), 2.5, QUOTE_LINE),
                        ("LEFTPADDING", (0, 0), (0, -1), 8),
                        ("RIGHTPADDING", (0, 0), (0, -1), 0),
                        ("TOPPADDING", (0, 0), (0, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (0, -1), 0),
                    ]
                )
            )
            return box

        # Unordered list
        if re.match(r"^[-*+]\s+", stripped):
            items = []
            for line in lines:
                if re.match(r"^[-*+]\s+", line.strip()):
                    items.append(ListItem(Paragraph(_inline(re.sub(r"^[-*+]\s+", "", line.strip())), styles["bullet"])))
            return ListFlowable(items, bulletType="bullet", start="•", leftIndent=12, bulletFontSize=9)

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            for line in lines:
                if re.match(r"^\d+\.\s+", line.strip()):
                    items.append(ListItem(Paragraph(_inline(re.sub(r"^\d+\.\s+", "", line.strip())), styles["bullet"])))
            return ListFlowable(items, bulletType="1", leftIndent=12)

        # Pipe table
        if stripped.startswith("|") and "|" in stripped[1:]:
            table = self._pipe_table(lines, styles)
            if table:
                return table

        # Paragraph
        return Paragraph(_inline(" ".join(line.strip() for line in lines if line.strip())), styles["body"])

    def _code_block(self, lines: list[str]):
        code = "\n".join(lines) + ("\n" if lines else "")
        style = ParagraphStyle(
            "code",
            fontName=MONO_FONT,
            fontSize=8.5,
            leading=11.5,
            textColor=INK,
        )
        box = Table([[Preformatted(code.rstrip("\n"), style)]], colWidths=[None])
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                    ("BOX", (0, 0), (-1, -1), 0.6, CODE_BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return box

    def _pipe_table(self, lines: list[str], styles: dict[str, ParagraphStyle]):
        rows: list[list[str]] = []
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            rows.append(cells)
        if not rows:
            return None
        data = [row for row in rows if not all(re.fullmatch(r":?-{2,}:?", cell) for cell in row)]
        if len(data) < 1:
            return None
        body_rows = data[1:] if len(data) > 1 else []

        header = [Paragraph(_inline(cell), styles["cell"]) for cell in data[0]]
        body = [[Paragraph(_inline(cell), styles["cell"]) for cell in row] for row in body_rows]

        table = Table([header, *body], colWidths=None, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
                    ("FONTNAME", (0, 0), (-1, 0), _BODY_BOLD),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table
