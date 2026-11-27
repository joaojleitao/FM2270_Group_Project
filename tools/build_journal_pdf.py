"""Convert journal/JOURNAL.md into journal/FM2270_Project_Journal.pdf (A4, readable font, tables, page numbers).

Usage (from the project root):  python tools/build_journal_pdf.py
Needs: markdown-pdf (which installs PyMuPDF, used here to stamp page numbers).
"""
from pathlib import Path

import pymupdf as fitz  # PyMuPDF, a dependency of markdown-pdf
from markdown_pdf import MarkdownPdf, Section

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "journal" / "JOURNAL.md"
OUT = ROOT / "journal" / "FM2270_Project_Journal.pdf"

CSS = """
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; }
h1 { font-size: 18pt; } h2 { font-size: 14pt; margin-top: 14pt; } h3 { font-size: 11.5pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; }
th, td { border: 1px solid #888; padding: 3px 5px; text-align: left; vertical-align: top; }
th { background-color: #e8e8e8; }
code { font-family: Courier, monospace; font-size: 8.5pt; }
pre { font-size: 8pt; background-color: #f4f4f4; padding: 5px; }
"""


def main():
    pdf = MarkdownPdf(toc_level=2)
    pdf.meta["title"] = "FM2270 Project Journal"
    pdf.add_section(Section(SRC.read_text(encoding="utf-8"), paper_size="A4", borders=(40, 45, -40, -45)),
                    user_css=CSS)
    tmp = OUT.with_suffix(".tmp.pdf")
    pdf.save(str(tmp))

    # stamp "Page x of n" at the bottom centre of every page
    doc = fitz.open(str(tmp))
    for i, page in enumerate(doc, start=1):
        r = page.rect
        page.insert_textbox(fitz.Rect(0, r.height - 30, r.width, r.height - 12),
                            f"Page {i} of {doc.page_count}", fontsize=8, align=fitz.TEXT_ALIGN_CENTER)
    doc.save(str(OUT))
    doc.close()
    tmp.unlink()
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
