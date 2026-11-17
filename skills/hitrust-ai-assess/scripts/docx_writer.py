"""Render the template markup used in templates_content.py to a Word document (python-docx).

Markup (one block per paragraph, blocks separated by blank lines):
  # Title / ## Heading / ### Subheading
  - bullet item              (consecutive lines form one list)
  1. numbered item           (numbers are written as text, so every list restarts at 1)
  | a | b |                  (pipe table; first row is the header, second row the --- separator)
  > note                     (italic guidance note for the person filling in the template)
  plain text                 (paragraph)
Inline: **bold**, *italic*, `code`.
"""
import re

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Calibri"
ACCENT = RGBColor(0x1F, 0x3A, 0x5F)
MUTED = RGBColor(0x59, 0x59, 0x59)
HEADER_FILL = "D9E2EC"
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|(?<![\w*])\*[^*\s][^*]*?\*(?![\w*]))")


def _shade(cell, hex_fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def _repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def _add_runs(par, text, size=None, italic=False, color=None):
    for part in INLINE.split(text):
        if not part:
            continue
        bold = ital = code = False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part, bold = part[2:-2], True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            part, code = part[1:-1], True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part, ital = part[1:-1], True
        run = par.add_run(part)
        run.bold = bold or None
        run.italic = (ital or italic) or None
        if code:
            run.font.name = "Consolas"
        if size:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color


def _page_number_field(par):
    run = par.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tag)
            run._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = text
            run._r.append(it)


class DocBuilder:
    def __init__(self, landscape=False, header_text="", footer_text=""):
        self.doc = Document()
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        if landscape:
            sec.orientation = WD_ORIENT.LANDSCAPE
            sec.page_width, sec.page_height = Inches(11), Inches(8.5)
        for side in ("left_margin", "right_margin"):
            setattr(sec, side, Inches(0.8))
        sec.top_margin = sec.bottom_margin = Inches(0.8)
        self.text_width = sec.page_width - sec.left_margin - sec.right_margin
        self._styles()
        if header_text:
            hp = sec.header.paragraphs[0]
            _add_runs(hp, header_text, size=8, color=MUTED)
            hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _add_runs(fp, (footer_text + "  |  Page ") if footer_text else "Page ", size=8, color=MUTED)
        _page_number_field(fp)
        for r in fp.runs:
            r.font.size = Pt(8)

    def _styles(self):
        st = self.doc.styles
        normal = st["Normal"]
        normal.font.name = FONT
        normal.font.size = Pt(10.5)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.line_spacing = 1.1
        for name, size, before, after in (("Title", 22, 0, 6), ("Heading 1", 15, 16, 6),
                                          ("Heading 2", 12.5, 12, 4), ("Heading 3", 11, 10, 3)):
            s = st[name]
            s.font.name = FONT
            s.font.size = Pt(size)
            s.font.bold = True
            s.font.color.rgb = ACCENT
            rfonts = s.element.rPr.find(qn("w:rFonts"))
            if rfonts is not None:
                for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                    rfonts.attrib.pop(qn(a), None)
                rfonts.set(qn("w:ascii"), FONT)
                rfonts.set(qn("w:hAnsi"), FONT)
            pf = s.paragraph_format
            pf.space_before, pf.space_after, pf.keep_with_next = Pt(before), Pt(after), True
        tb = st["Title"]
        pbdr = tb.element.pPr.find(qn("w:pBdr")) if tb.element.pPr is not None else None
        if pbdr is not None:
            tb.element.pPr.remove(pbdr)

    # ---- blocks ----
    def heading(self, text, level):
        style = {1: "Title", 2: "Heading 1", 3: "Heading 2", 4: "Heading 3"}[level]
        p = self.doc.add_paragraph(style=style)
        _add_runs(p, text)

    def para(self, text, italic=False, color=None):
        p = self.doc.add_paragraph()
        _add_runs(p, text, italic=italic, color=color)
        return p

    def note(self, text):
        p = self.para(text, italic=True, color=MUTED)
        p.paragraph_format.left_indent = Inches(0.2)

    def bullets(self, items):
        for it in items:
            p = self.doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(3)
            _add_runs(p, it)

    def numbered(self, items):
        for i, it in enumerate(items, 1):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent, pf.space_after = Inches(0.35), Inches(-0.25), Pt(3)
            pf.tab_stops.add_tab_stop(Inches(0.35))
            _add_runs(p, f"{i}.\t{it}")

    def table(self, rows):
        header, body = rows[0], rows[1:]
        ncol = len(header)
        body = [r + [""] * (ncol - len(r)) if len(r) < ncol else r[:ncol] for r in body]
        t = self.doc.add_table(rows=1 + len(body), cols=ncol)
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        widths = self._col_widths([header] + body)
        size = 9 if ncol <= 5 else 8.5 if ncol <= 7 else 8
        for ri, row in enumerate([header] + body):
            for ci, txt in enumerate(row):
                cell = t.cell(ri, ci)
                cell.width = widths[ci]
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                _add_runs(p, txt.strip(), size=size)
                if ri == 0:
                    for r in p.runs:
                        r.bold = True
                    _shade(cell, HEADER_FILL)
        _repeat_header(t.rows[0])
        grid = t._tbl.tblGrid
        for ci, gc in enumerate(grid.findall(qn("w:gridCol"))):
            gc.set(qn("w:w"), str(int(widths[ci] / 635)))  # EMU -> twips
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def _col_widths(self, rows):
        ncol = len(rows[0])
        weight = []
        for c in range(ncol):
            longest = max(len(r[c]) for r in rows)
            words = max((len(w) for r in rows for w in r[c].split()), default=4)
            weight.append(max(min(longest, 60), words + 2, 6))
        total = sum(weight)
        return [int(self.text_width * w / total) for w in weight]

    # ---- markup ----
    def render(self, markup):
        lines = markup.strip("\n").split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line.strip():
                i += 1
                continue
            m = re.match(r"^(#{1,4})\s+(.*)$", line)
            if m:
                self.heading(m.group(2), len(m.group(1)))
                i += 1
                continue
            if line.startswith("|"):
                block = []
                while i < len(lines) and lines[i].startswith("|"):
                    block.append(lines[i])
                    i += 1
                rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in block]
                rows = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
                self.table(rows)
                continue
            if line.startswith("- "):
                items = []
                while i < len(lines) and lines[i].startswith("- "):
                    items.append(lines[i][2:].strip())
                    i += 1
                self.bullets(items)
                continue
            if re.match(r"^\d+\.\s", line):
                items = []
                while i < len(lines) and re.match(r"^\d+\.\s", lines[i]):
                    items.append(re.sub(r"^\d+\.\s+", "", lines[i]).strip())
                    i += 1
                self.numbered(items)
                continue
            if line.startswith("> "):
                self.note(line[2:].strip())
                i += 1
                continue
            buf = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||- |\d+\.\s|> )", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            self.para(" ".join(buf))

    def save(self, path):
        self.doc.core_properties.author = ""
        self.doc.save(path)
