"""
Shared engine for the plain-language CFA Level I study guides.

Volume 9 (Portfolio Construction) was built by make_cfa_pc_pdf.py with the
layout code inlined. That layout is now here so every remaining volume comes
out identical: same cover, same running head, same panels, same tables.

A volume script does only two things:

    from cfa_guide import Guide, cover, make_table
    d = Guide(volume=1, subject="Quantitative Methods")
    cover(d, modules=[(1, "Title", "one-line summary"), ...], standfirst="...")
    d.h1(1, "Title", "standfirst"); d.p("..."); d.key("..."); d.warn("...")
    d.output(path)

DejaVu is used throughout (it ships with matplotlib) because fpdf2's built-in
core fonts are cp1252 only and blow up on sigma, beta and rho — which appear on
nearly every page of a quantitative curriculum.
"""
import os

import matplotlib
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")

# Palette — matches the Volume 9 guide exactly.
INK = (28, 34, 45)
MUTED = (95, 105, 120)
ACCENT = (17, 78, 138)
RULE = (198, 206, 216)
BOXBG = (238, 243, 249)
WARNBG = (253, 244, 232)
WARNBAR = (198, 118, 20)
EXBG = (238, 247, 240)
EXBAR = (33, 122, 72)


class Guide(FPDF):
    def __init__(self, volume, subject):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.volume = volume
        self.subject = subject
        self.set_margins(20, 18, 20)
        self.set_auto_page_break(True, margin=20)
        for style, fn in [("", "DejaVuSans.ttf"),
                          ("B", "DejaVuSans-Bold.ttf"),
                          ("I", "DejaVuSans-Oblique.ttf"),
                          ("BI", "DejaVuSans-BoldOblique.ttf")]:
            self.add_font("DejaVu", style, os.path.join(FONT_DIR, fn))
        self.add_font("DejaVuMono", "", os.path.join(FONT_DIR, "DejaVuSansMono.ttf"))
        self.chapter = ""
        self.cover = True
        self._pending_h3 = None

    # ---- running head / foot ----------------------------------------------
    def header(self):
        if self.cover or self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, self.chapter, align="L")
        self.cell(0, 5, f"{self.subject} — Level I, Volume {self.volume}", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y() + 0.5, self.w - self.r_margin, self.get_y() + 0.5)
        self.ln(4)

    def footer(self):
        # Page 1 is the cover. Test the page number, not self.cover: the flag is
        # cleared by the next h1() before page 1's footer is actually emitted.
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("DejaVu", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, str(self.page_no()), align="C")

    # ---- building blocks ---------------------------------------------------
    def h1(self, num, title, standfirst=""):
        self.cover = False
        # Set the running head BEFORE add_page(): add_page() fires header()
        # immediately, so otherwise each chapter's first page carries the
        # previous chapter's name.
        self._pending_h3 = None
        self.chapter = f"Module {num} — {title}" if num else title
        self.add_page()
        self.set_text_color(*ACCENT)
        self.set_font("DejaVu", "B", 9)
        if num:
            self.cell(0, 6, f"LEARNING MODULE {num}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*INK)
        self.set_font("DejaVu", "B", 20)
        self.multi_cell(self.epw, 9, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.5)
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.l_margin + 32, self.get_y())
        self.ln(5)
        if standfirst:
            self.set_font("DejaVu", "I", 10.5)
            self.set_text_color(*MUTED)
            self.multi_cell(self.epw, 5.6, standfirst, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*INK)
            self.ln(3)

    def h2(self, title):
        if self.get_y() > self.h - 55:
            self.add_page()
        self.ln(3)
        self.set_font("DejaVu", "B", 13.5)
        self.set_text_color(*ACCENT)
        self.multi_cell(self.epw, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*INK)
        self.ln(1.5)

    H3_HEIGHT = 8.0

    def h3(self, title):
        # Deferred: a sub-heading is drawn only once we know the block that
        # follows it fits on the same page, so a heading never strands itself
        # at the foot of a page with its content overleaf.
        self._pending_h3 = title

    def _draw_h3(self):
        title, self._pending_h3 = self._pending_h3, None
        self.ln(1.5)
        self.set_font("DejaVu", "B", 10.8)
        self.set_text_color(*INK)
        self.multi_cell(self.epw, 5.6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

    def _flush(self, need):
        extra = self.H3_HEIGHT if self._pending_h3 else 0.0
        if self.get_y() + extra + need > self.h - 22:
            self.add_page()
        if self._pending_h3:
            self._draw_h3()

    def p(self, text):
        self._flush(11)          # keep a heading with at least two lines of text
        self.set_font("DejaVu", "", 9.8)
        self.set_text_color(*INK)
        self.multi_cell(self.epw, 5.2, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def bullets(self, items, marker="•"):
        self._flush(11)
        self.set_font("DejaVu", "", 9.8)
        self.set_text_color(*INK)
        for it in items:
            if self.get_y() > self.h - 30:
                self.add_page()
            x = self.get_x()
            self.cell(5, 5.2, marker)
            self.multi_cell(self.epw - 5, 5.2, it, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_x(x)
        self.ln(2)

    def numbered(self, items):
        self._flush(11)
        self.set_font("DejaVu", "", 9.8)
        self.set_text_color(*INK)
        for i, it in enumerate(items, 1):
            if self.get_y() > self.h - 30:
                self.add_page()
            x = self.get_x()
            self.set_font("DejaVu", "B", 9.8)
            self.cell(6, 5.2, f"{i}.")
            self.set_font("DejaVu", "", 9.8)
            self.multi_cell(self.epw - 6, 5.2, it, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_x(x)
        self.ln(2)

    def _panel(self, label, text, bg, bar):
        self.set_font("DejaVu", "", 9.6)
        lines = self.multi_cell(self.epw - 12, 5.0, text, dry_run=True, output="LINES")
        need = len(lines) * 5.0 + 9 + (5.5 if label else 0)
        self._flush(need)
        y0 = self.get_y()
        self.set_fill_color(*bg)
        self.rect(self.l_margin, y0, self.epw, need, style="F")
        self.set_fill_color(*bar)
        self.rect(self.l_margin, y0, 1.6, need, style="F")
        self.set_xy(self.l_margin + 7, y0 + 5)
        if label:
            self.set_font("DejaVu", "B", 8)
            self.set_text_color(*bar)
            self.cell(0, 4, label.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_x(self.l_margin + 7)
            self.ln(1.5)
            self.set_x(self.l_margin + 7)
        self.set_font("DejaVu", "", 9.6)
        self.set_text_color(*INK)
        self.multi_cell(self.epw - 12, 5.0, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Restore a neutral fill: fpdf2 paints table body cells with whatever
        # fill colour is current, so a leftover bar colour tints the next table.
        self.set_fill_color(255, 255, 255)
        self.set_text_color(*INK)
        self.set_y(y0 + need + 3)

    def key(self, text, label="Key idea"):
        self._panel(label, text, BOXBG, ACCENT)

    def warn(self, text, label="Exam trap"):
        self._panel(label, text, WARNBG, WARNBAR)

    def example(self, text, label="Worked example"):
        self._panel(label, text, EXBG, EXBAR)

    def formula(self, text, note=""):
        self.set_font("DejaVuMono", "", 9.5)
        lines = self.multi_cell(self.epw - 10, 5.2, text, dry_run=True, output="LINES")
        need = len(lines) * 5.2 + 8
        self._flush(need)
        y0 = self.get_y()
        self.set_fill_color(245, 246, 248)
        self.rect(self.l_margin, y0, self.epw, need, style="F")
        self.set_xy(self.l_margin + 5, y0 + 4)
        self.set_text_color(*INK)
        self.multi_cell(self.epw - 10, 5.2, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(y0 + need + 1.5)
        if note:
            self.set_font("DejaVu", "I", 8.6)
            self.set_text_color(*MUTED)
            self.multi_cell(self.epw, 4.4, note, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*INK)
        self.ln(2.5)


# Tables go through fpdf2's own table() context manager.
_ORIG_TABLE = FPDF.table


def make_table(pdf, headers, rows, widths=None, align="LEFT"):
    from fpdf.fonts import FontFace
    need = (len(rows) + 1) * 7.5 + 6
    pdf._flush(need)
    pdf.set_font("DejaVu", "", 8.8)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.2)
    pdf.set_fill_color(255, 255, 255)   # body rows must not inherit a stray fill
    pdf.set_text_color(*INK)
    with _ORIG_TABLE(pdf, col_widths=widths, text_align=align,
                     borders_layout="HORIZONTAL_LINES",
                     line_height=5.0, padding=(1.8, 2.0),
                     cell_fill_color=None, cell_fill_mode="NONE",
                     headings_style=FontFace(emphasis="BOLD", color=255,
                                             fill_color=ACCENT)) as t:
        r = t.row()
        for h in headers:
            r.cell(h)
        for row in rows:
            r = t.row()
            for c in row:
                r.cell(str(c))
    pdf.ln(3)


def cover(d, modules, standfirst, title=None):
    """Cover page: banner, subject, standfirst, then the module contents list."""
    d.add_page()
    d.set_fill_color(*ACCENT)
    d.rect(0, 0, d.w, 62, style="F")
    d.set_xy(20, 20)
    d.set_text_color(255, 255, 255)
    d.set_font("DejaVu", "", 10)
    d.cell(0, 6, f"CFA® PROGRAM CURRICULUM  ·  2027  ·  LEVEL I  ·  VOLUME {d.volume}",
           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    d.set_x(20)
    d.ln(2)
    d.set_x(20)
    name = title or d.subject
    d.set_font("DejaVu", "B", 30 if len(name) < 22 else 24)
    d.cell(0, 15, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    d.set_xy(20, 78)
    d.set_text_color(*INK)
    d.set_font("DejaVu", "B", 15)
    d.cell(0, 9, "A Plain-Language Study Guide", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    d.set_x(20)
    d.set_font("DejaVu", "", 11)
    d.set_text_color(*MUTED)
    d.multi_cell(d.epw, 6, standfirst, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    d.ln(6)
    # Long module lists need a tighter line so they still fit on the cover.
    tight = len(modules) > 8
    for num, mtitle, sub in modules:
        if d.get_y() > d.h - 34:
            break
        y = d.get_y()
        d.set_x(20)
        d.set_font("DejaVu", "B", 12 if tight else 16)
        d.set_text_color(*ACCENT)
        d.cell(11 if tight else 14, 6 if tight else 8, str(num))
        d.set_font("DejaVu", "B", 9.4 if tight else 11)
        d.set_text_color(*INK)
        d.cell(0, 6 if tight else 8, mtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        d.set_xy(20 + (11 if tight else 14), d.get_y() - (0.5 if tight else 1))
        d.set_font("DejaVu", "", 8.4 if tight else 9.4)
        d.set_text_color(*MUTED)
        d.cell(0, 4.6, sub, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        d.ln(1 if tight else 2)

    # The disclaimer runs to four lines. At -26 its last line crosses the
    # auto-break margin and throws a near-empty page 2, so give it room and
    # switch the break off while it is drawn.
    d.set_auto_page_break(False)
    d.set_y(-34)
    d.set_x(20)
    d.set_font("DejaVu", "I", 7.6)
    d.set_text_color(*MUTED)
    d.multi_cell(d.epw, 3.8,
                 f"Study aid prepared from the 2027 Level I Volume {d.volume} curriculum. "
                 "Summary and wording are original; it is a companion to the official "
                 "curriculum, not a substitute for it. CFA® is a registered trademark of "
                 "CFA Institute, which does not endorse this document.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    d.set_auto_page_break(True, margin=20)
