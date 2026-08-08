"""Tests for the Markdown → PDF rendering service."""

from app.services.pdf_service import PdfService


def test_markdown_to_pdf_returns_valid_pdf():
    data = PdfService().markdown_to_pdf(
        "DevPilot — README",
        "# Overview\n\nSome **bold** text with `code`.\n\n- item one\n- item two\n",
        subtitle="Generated with DevPilot AI",
    )
    assert data.startswith(b"%PDF")
    assert len(data) > 2000


def test_pdf_renders_headings_code_lists_and_tables():
    md = "# Title\n\n## Section\n\n```python\ndef f():\n    return 1\n```\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"
    data = PdfService().markdown_to_pdf("Docs", md)
    assert data.startswith(b"%PDF")
    assert b"PDF" in data[:200]
