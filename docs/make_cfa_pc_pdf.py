"""
Build a plain-language study guide PDF for:
    CFA Program Curriculum 2027, Level I, Volume 9 - Portfolio Construction

Uses DejaVu (shipped with matplotlib) so Greek letters and maths symbols
render properly - fpdf2's built-in core fonts are cp1252 only and would
crash on sigma/beta/rho.

Run:  venv/Scripts/python.exe docs/make_cfa_pc_pdf.py
"""
import os
import matplotlib
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V9-Portfolio-Construction-Summary.pdf")

# Palette
INK = (28, 34, 45)
MUTED = (95, 105, 120)
ACCENT = (17, 78, 138)
RULE = (198, 206, 216)
BOXBG = (238, 243, 249)
WARNBG = (253, 244, 232)
WARNBAR = (198, 118, 20)


class Guide(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
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

    # ---- running head / foot -------------------------------------------
    def header(self):
        if self.cover or self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, self.chapter, align="L")
        self.cell(0, 5, "Portfolio Construction - Level I, Volume 9", align="R",
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

    # ---- building blocks -----------------------------------------------
    def h1(self, num, title, standfirst=""):
        self.cover = False
        # Set the running head BEFORE add_page(), because add_page() triggers
        # header() immediately - otherwise every chapter's first page carries
        # the previous chapter's name.
        self._pending_h3 = None
        self.chapter = f"Module {num} - {title}" if num else title
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
        # Deferred: a sub-heading is only drawn once we know the block that
        # follows it will fit on the same page. Otherwise the heading strands
        # itself at the foot of a page with its content overleaf.
        self._pending_h3 = title

    def _draw_h3(self):
        title, self._pending_h3 = self._pending_h3, None
        self.ln(1.5)
        self.set_font("DejaVu", "B", 10.8)
        self.set_text_color(*INK)
        self.multi_cell(self.epw, 5.6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

    def _flush(self, need):
        """Break the page if the next block (plus any pending sub-heading)
        will not fit, then emit the sub-heading."""
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
        # fill colour is current, so leaving the panel's bar colour set here
        # tints the next table's rows.
        self.set_fill_color(255, 255, 255)
        self.set_text_color(*INK)
        self.set_y(y0 + need + 3)

    def key(self, text, label="Key idea"):
        self._panel(label, text, BOXBG, ACCENT)

    def warn(self, text, label="Exam trap"):
        self._panel(label, text, WARNBG, WARNBAR)

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


# Tables are rendered through fpdf2's own table() context manager.
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


# ======================================================================
def cover(d):
    d.add_page()
    d.set_fill_color(*ACCENT)
    d.rect(0, 0, d.w, 62, style="F")
    d.set_xy(20, 20)
    d.set_text_color(255, 255, 255)
    d.set_font("DejaVu", "", 10)
    d.cell(0, 6, "CFA® PROGRAM CURRICULUM  ·  2027  ·  LEVEL I  ·  VOLUME 9",
           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    d.set_x(20)
    d.ln(2)
    d.set_x(20)
    d.set_font("DejaVu", "B", 30)
    d.cell(0, 15, "Portfolio Construction", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    d.set_xy(20, 78)
    d.set_text_color(*INK)
    d.set_font("DejaVu", "B", 15)
    d.cell(0, 9, "A Plain-Language Study Guide", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    d.set_x(20)
    d.set_font("DejaVu", "", 11)
    d.set_text_color(*MUTED)
    d.multi_cell(d.epw, 6,
                 "All six learning modules explained in everyday English, with the "
                 "formulas you must memorise, the worked examples from the curriculum, "
                 "and the traps that catch candidates in the exam.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    d.set_xy(20, 118)
    rows = [
        ("1", "Portfolio Risk and Return: Part I", "Diversification, utility, the efficient frontier"),
        ("2", "Portfolio Risk and Return: Part II", "CAPM, beta, and performance measurement"),
        ("3", "Portfolio Management: An Overview", "The process, investor types, the industry"),
        ("4", "Basics of Portfolio Planning & Construction", "The IPS, constraints, asset allocation"),
        ("5", "The Behavioral Biases of Individuals", "Why real investors act irrationally"),
        ("6", "Introduction to Risk Management", "Governance, risk budgeting, hedging"),
    ]
    for num, title, sub in rows:
        y = d.get_y()
        d.set_font("DejaVu", "B", 16)
        d.set_text_color(*ACCENT)
        d.set_x(20)
        d.cell(11, 8, num)
        d.set_font("DejaVu", "B", 10.5)
        d.set_text_color(*INK)
        d.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        d.set_xy(31, y + 7)
        d.set_font("DejaVu", "", 9)
        d.set_text_color(*MUTED)
        d.cell(0, 5, sub, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        d.ln(2.5)

    d.set_draw_color(*RULE)
    d.line(20, d.h - 46, d.w - 20, d.h - 46)
    d.set_xy(20, d.h - 42)
    d.set_font("DejaVu", "I", 8.2)
    d.set_text_color(*MUTED)
    d.multi_cell(d.epw, 4.4,
                 "Study aid prepared from the 2027 Level I Volume 9 curriculum. "
                 "Summary and wording are original; it is a companion to the official "
                 "readings, not a replacement for them. CFA Institute holds copyright in "
                 "the underlying curriculum. CFA® is a registered trademark of CFA Institute.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def how_to_use(d):
    d.h1("", "How to use this guide",
         "Six modules, one continuous argument. Read it in order the first time.")
    d.p("Volume 9 looks like six separate topics. It is really one argument told in six "
        "steps, and it is much easier to remember once you can see the thread running "
        "through it:")
    d.numbered([
        "Modules 1 and 2 build the theory. They answer one question: which risks does "
        "the market pay you to take, and which does it not? The answer - systematic risk "
        "is paid, non-systematic risk is not - is the foundation of everything after it.",
        "Module 3 zooms out. It shows why you must think in portfolios rather than "
        "individual securities, and who the different investors are.",
        "Module 4 makes it personal. It turns the theory into a written plan for one "
        "specific client: the investment policy statement.",
        "Module 5 is the reality check. It explains why that client - and you - will "
        "quietly sabotage the plan through predictable psychological biases.",
        "Module 6 gives you the machinery to hold the line: governance, risk budgets, "
        "measurement, and hedging tools.",
    ])
    d.key("Volume 9 in one sentence: risk is not the enemy - unmeasured, unchosen, "
          "unmanaged risk is. Every module is about choosing risk deliberately and then "
          "keeping the risk you actually have lined up with the risk you meant to take.")

    d.h2("How the panels work")
    d.p("Three kinds of highlighted box appear throughout:")
    d.key("A blue KEY IDEA box holds a conclusion worth memorising outright. If you "
          "remember nothing else from a section, remember these.")
    d.warn("An orange EXAM TRAP box flags a place where the obvious answer is wrong, or "
           "where two similar-sounding concepts are routinely confused. These are where "
           "marks are actually lost.")
    d.formula("Formulas sit in a grey monospaced box like this one.",
              "A short note underneath explains what each symbol means and when to use it.")

    d.h2("A note on the mathematics")
    d.p("You do not need to derive anything in Volume 9. You do need to be able to plug "
        "numbers into perhaps a dozen formulas quickly and correctly, and - more "
        "importantly - to say in words what each one means. Examiners test understanding "
        "far more often than arithmetic. Where a formula appears in this guide, the note "
        "underneath tells you what it is really saying.")
    d.p("One habit will save you marks repeatedly: check whether a question is asking "
        "about total risk (standard deviation) or systematic risk (beta). A large number "
        "of Volume 9 questions hinge on nothing more than that distinction.")


# ======================================================================
def module1(d):
    d.h1(1, "Portfolio Risk and Return: Part I",
         "How individual investments combine into portfolios, why correlation matters "
         "more than anything else, and how to find the one portfolio that is best for a "
         "particular investor.")

    d.h2("1.1  Historical returns: what the record actually shows")
    d.p("Before any theory, the curriculum establishes a factual base. Over 1926-2017 in "
        "the United States, asset classes lined up almost exactly as risk-return theory "
        "would predict.")
    make_table(d,
               ["Asset class", "Return", "Risk (SD)"],
               [["Small company stocks", "12.1%", "31.7%"],
                ["Large company stocks", "10.2%", "19.8%"],
                ["Long-term corporate bonds", "6.1%", "8.3%"],
                ["Long-term government bonds", "5.5%", "9.9%"],
                ["Treasury bills", "3.4%", "3.1%"],
                ["Inflation", "2.9%", "4.0%"]],
               widths=(46, 20, 22), align=("LEFT", "RIGHT", "RIGHT"))
    d.p("Read down the table and the pattern is unmistakable: every step up in return "
        "came with a step up in risk. That is the risk-return trade-off, and it is not a "
        "coincidence. It exists precisely because investors are risk-averse. If people "
        "did not dislike risk, risky assets would not have to offer more to attract "
        "buyers, and the two columns would not line up at all.")
    d.p("There is one instructive exception. Long-term government bonds carried more "
        "total risk (9.9%) than corporate bonds (8.3%) yet returned slightly less. This "
        "does not mean governments were more likely to default. It means government "
        "bonds happened to be more variable over this particular period, largely because "
        "of interest-rate movements. Real data is messy; the trend still holds.")

    d.h3("Historical return is not expected return")
    d.p("The curriculum is emphatic about this. Historical return is what actually "
        "happened. Expected return is what a marginal investor requires going forward, "
        "and it is built from three pieces:")
    d.formula("1 + E(R) = (1 + r_rF) × [1 + E(π)] × [1 + E(RP)]",
              "r_rF = real risk-free rate (payment for postponing consumption); "
              "E(π) = expected inflation; E(RP) = expected risk premium.")
    d.p("In practice everyone uses historical averages as a proxy for expected returns, "
        "because there is nothing better. But it is an assumption, and the curriculum "
        "wants you to know it is an assumption. Large US stocks returned 18.2% in the "
        "1990s and minus 1.0% in the 2000s. Whichever decade you had used to set "
        "expectations, you would have been badly wrong about the next one.")

    d.h3("Real returns and the power of compounding")
    d.p("Because inflation ranged from minus 10.3% to plus 13.3%, comparing nominal "
        "returns across eras is misleading. In real terms, 1900-2017, one dollar grew to "
        "$1,654 in equities, $10.20 in bonds and $2.60 in bills. The annual gap looks "
        "modest - 6.5% versus 2.0% versus 0.8% - but compounded over 118 years it is "
        "enormous. This is the single best argument in the curriculum for holding "
        "growth assets over long horizons.")

    d.h2("1.2  Why the normal distribution is not enough")
    d.p("Mean and variance fully describe an investment only if returns are normally "
        "distributed and markets are efficient both informationally and operationally. "
        "Real returns violate this in two specific ways.")
    d.bullets([
        "Skewness. Returns are negatively (left) skewed: the distribution has a long "
        "tail of large losses. Crashes are bigger and faster than booms.",
        "Kurtosis (fat tails). Extreme outcomes of either sign happen far more often "
        "than a bell curve predicts. Because mean-variance analysis assumes they are "
        "rare, it systematically understates real risk.",
    ])
    d.p("The practical response is to supplement standard deviation with measures aimed "
        "at the tail, such as value at risk and conditional tail expectations - both of "
        "which return in Module 6. Market participants widely regard the "
        "underappreciation of tail events as a major contributing factor to the 2008 "
        "financial crisis.")

    d.h3("Market characteristics: liquidity is a cost and a risk")
    d.p("Trading costs have three parts: brokerage commission, the bid-ask spread, and "
        "price impact. Liquidity affects the last two. The curriculum's arithmetic is "
        "worth remembering because it is so clean: a 10-cent spread on a $100 stock is "
        "0.1%, but the same 10-cent spread on a $10 stock is 1%. The cheaper stock must "
        "earn 0.9% more just to break even against the dearer one.")
    d.p("Price impact is the second effect. Buying 100 shares of a liquid stock may move "
        "nothing; buying 100,000 shares may move the price a long way, because you have "
        "to keep raising your bid to persuade more holders to sell. Liquidity matters "
        "most in emerging markets, in corporate bonds, and for large institutions.")

    d.h2("1.3  Risk aversion and utility")
    d.p("The curriculum's set-up: you may take GBP 50 with certainty, or a coin flip "
        "paying GBP 100 or nothing. Both have an expected value of GBP 50. Your choice "
        "reveals your type.")
    make_table(d,
               ["Choice", "Type", "What it implies"],
               [["Takes the gamble", "Risk seeking",
                 "Gains utility from uncertainty; would accept an expected GBP 45 gamble over a sure GBP 50"],
                ["Genuinely indifferent", "Risk neutral",
                 "Cares only about return, not risk"],
                ["Takes the sure GBP 50", "Risk averse",
                 "Might accept a sure GBP 45 to avoid the gamble entirely"]],
               widths=(30, 24, 84))
    d.p("The curriculum then makes a point that is easy to skim past but often tested: a "
        "single choice does not determine anybody's risk aversion. Buying a lottery "
        "ticket or visiting a casino does not make somebody a risk seeker in their "
        "investment portfolio. Because historical data shows a consistently positive "
        "risk-return relationship, we conclude that market prices are set by risk-averse "
        "investors, and every remaining assumption in the volume follows from that.")
    d.warn("Risk tolerance and risk aversion are opposites, not synonyms. Higher risk "
           "tolerance means lower risk aversion, which means a lower value of A in the "
           "utility function. Questions frequently swap the two words to see whether you "
           "are reading carefully.")

    d.h3("The utility function")
    d.formula("U = E(r) − ½ A σ²",
              "U = utility; E(r) = expected return; σ² = variance; "
              "A = risk aversion coefficient. Returns and standard deviations must be "
              "entered as decimals, not percentages.")
    d.p("Five properties the curriculum draws out, all of which have appeared as "
        "questions:")
    d.numbered([
        "Utility is unbounded in both directions - it can be hugely positive or hugely "
        "negative.",
        "Higher return raises utility; higher variance lowers it, and the reduction is "
        "amplified by A.",
        "A > 0 for a risk-averse investor, A = 0 for a risk-neutral one, and A < 0 for a "
        "risk lover, for whom extra risk actually raises utility.",
        "Utility only ranks investments. A portfolio scoring 4 is preferred to one "
        "scoring 2, but it is not 'twice as good'. There is no meaningful unit.",
        "A risk-free asset has σ² = 0, so the second term vanishes and it "
        "produces identical utility for everyone regardless of A.",
    ])
    d.h3("Worked example")
    d.p("Expected return 10%, standard deviation 20%, A = 3.")
    d.formula("U = 0.10 − 0.5 × 3 × 0.20² = 0.10 − 0.06 = 0.04",
              "The certainty equivalent is therefore 4%. To this investor, a risky 10% "
              "is worth exactly the same as a guaranteed 4%. The 6% gap is the price "
              "they place on the risk.")

    d.h3("Indifference curves")
    d.p("An indifference curve joins every risk-return pair giving the same utility. For "
        "a risk-averse investor it slopes upward (more risk demands more return) and is "
        "convex, because each extra unit of risk requires an increasingly large "
        "compensation. Curves for the same investor can never touch or cross - if they "
        "did, the investor's preferences would be internally inconsistent.")
    d.bullets([
        "Steeper curve = more risk-averse. The most risk-averse investor has the "
        "steepest slope.",
        "Utility rises to the north-west: more return, less risk.",
        "Risk-neutral investors have flat, horizontal curves - risk simply does not "
        "enter their utility.",
        "Risk lovers have downward-sloping curves - they will give up return to obtain "
        "more risk.",
    ])

    d.h2("1.4  Portfolio return and portfolio risk")
    d.p("This is the mathematical heart of Module 1, and the asymmetry between the two "
        "formulas is the whole point.")
    d.formula("Return:  R_p = w₁R₁ + w₂R₂          (a simple weighted average)\n\n"
              "Risk:    σ_p² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρ₁₂σ₁σ₂\n"
              "         σ_p  = √(w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρ₁₂σ₁σ₂)\n\n"
              "Covariance: Cov(R₁,R₂) = ρ₁₂ σ₁ σ₂",
              "Weights must sum to 1. Note the third term: it is the only place "
              "correlation enters, and it is where all diversification comes from.")
    d.key("Portfolio return is always a weighted average of the component returns. "
          "Portfolio risk is NOT a weighted average of the component risks - except in "
          "the single case where ρ = +1. That exception is the entire reason "
          "diversification works.")

    d.h3("What correlation does, case by case")
    make_table(d,
               ["Correlation", "Effect on portfolio risk", "Interpretation"],
               [["ρ = +1", "σ_p = w₁σ₁ + w₂σ₂ (weighted average)",
                 "No diversification benefit at all"],
                ["ρ < +1", "σ_p < weighted average",
                 "Risk falls while return is unchanged"],
                ["ρ = 0", "Substantial reduction",
                 "Assets move independently"],
                ["ρ = −1", "Risk can be driven to exactly zero",
                 "A perfect hedge is possible"]],
               widths=(24, 62, 52))
    d.p("The curriculum demonstrates this with two identical stocks, each returning 10% "
        "with 20% risk, held 50/50. At ρ = +1 portfolio risk is 20% - no improvement. "
        "At ρ = 0 it falls to 14%. At ρ = −1 it falls to 0%. The expected "
        "return is 10% in all three cases. You have removed risk without giving up a "
        "single basis point of return.")

    d.h3("The Beachwear example - why correlation, not count, is what matters")
    d.p("This is the clearest illustration in the volume. Beachwear earns 20% in a sunny "
        "year and 0% in a rainy one; average 10%, and risky.")
    d.bullets([
        "Add Snackshop, which also earns 20% when sunny and 0% when rainy. You now hold "
        "two businesses instead of one - but they are perfectly correlated (ρ = +1). "
        "The portfolio still earns 20% or 0%. Risk is completely unchanged.",
        "Add DVDrental instead, which earns 20% when rainy and 0% when sunny "
        "(ρ = −1). Now you earn exactly 10% whether it rains or shines. Risk "
        "has been eliminated and the return is untouched.",
    ])
    d.key("Adding more holdings does not diversify a portfolio. Adding holdings that "
          "behave differently does. This is why a portfolio of ten bank stocks is barely "
          "diversified at all.")

    d.h2("1.5  Many assets: what survives diversification")
    d.p("Extend to N assets, equally weighted, with average variance and average "
        "covariance:")
    d.formula("σ_p² = σ̄²/N + [(N−1)/N] × Cov̄\n\n"
              "and if all variances and correlations are equal:\n"
              "σ_p = √( σ²/N + [(N−1)/N] ρ σ² )",
              "As N rises, the first term (individual variance) shrinks toward zero; the "
              "second term converges on the average covariance.")
    d.key("In a large portfolio, individual asset variances become irrelevant. Almost "
          "all remaining risk comes from how the assets move together. If assets were "
          "genuinely unrelated, portfolio risk could approach zero - but in reality most "
          "assets are positively correlated, so a floor of undiversifiable risk always "
          "remains. That floor is systematic risk, and Module 2 prices it.")
    d.p("Historical correlations confirm the difficulty. US large-cap versus US small-cap "
        "is about 0.72; US large-cap versus international is 0.66. Real diversification "
        "comes from bonds: US small-cap versus long-term Treasuries is actually negative "
        "at minus 0.15, and T-bills are close to zero against everything. Above 0.90 is "
        "considered high and offers little help; below 0.50 is genuinely useful.")

    d.h3("Practical avenues for diversification")
    d.bullets([
        "Across asset classes - the biggest single lever available.",
        "Through index funds and ETFs - covering ten asset classes properly might need "
        "300 securities, which is expensive to trade and track directly.",
        "Across countries - different industry mixes, policies and currencies. Currency "
        "returns are largely uncorrelated with stock returns, which helps even when the "
        "foreign market itself is risky.",
        "By NOT owning your employer's stock. You have already invested your human "
        "capital there. If the company fails you lose your job and your savings "
        "together.",
        "By evaluating each addition properly rather than accumulating holdings.",
        "By buying insurance or put options - assets with negative correlation and "
        "negative expected return that are still rational to hold because of the risk "
        "they remove.",
    ])
    d.h3("The rule for adding a new asset")
    d.formula("Add the asset if:\n\n"
              "  [E(R_new) − R_f] / σ_new  >  { [E(R_p) − R_f] / σ_p } × ρ_new,p",
              "In words: add the asset if its Sharpe ratio beats the existing portfolio's "
              "Sharpe ratio multiplied by its correlation with that portfolio. Low "
              "correlation lowers the hurdle - which is why a mediocre but uncorrelated "
              "asset can still improve a portfolio.")

    d.h2("1.6  Frontiers, the CAL, and the optimal portfolio")
    d.p("The construction runs in a fixed order. Examiners test the order as often as "
        "the content.")
    d.numbered([
        "Investment opportunity set - every portfolio that can be built from the "
        "available assets. Adding a new asset class that is not perfectly correlated "
        "pushes the whole set north-west, which is strictly better.",
        "Minimum-variance frontier - for each level of return, the portfolio with the "
        "least risk. No risk-averse investor holds anything to the right of it.",
        "Global minimum-variance portfolio - the leftmost point on that frontier. No "
        "portfolio of risky assets can have less risk than this one.",
        "Markowitz efficient frontier - the portion of the minimum-variance frontier "
        "lying ABOVE the global minimum-variance portfolio. The part below is "
        "inefficient: for the same risk you could have had more return.",
        "Add the risk-free asset. Lines from R_f to points on the efficient frontier are "
        "capital allocation lines. The steepest one - the tangent - dominates all "
        "others, and its tangency point is the optimal risky portfolio, P.",
        "Overlay the investor's indifference curves. The point where the highest "
        "attainable curve touches the CAL is that investor's optimal portfolio.",
    ])
    d.formula("E(R_p) = R_f + [ (E(R_i) − R_f) / σ_i ] × σ_p",
              "Intercept = R_f. Slope = the market price of risk: the extra return "
              "demanded for each additional unit of risk.")
    d.p("Note the slope of the efficient frontier flattens as you move right. Moving "
        "from the global minimum-variance portfolio to point A might gain the same "
        "return as moving from A to D, but the extra risk taken in the second step is "
        "three to four times larger. Investors receive decreasing increases in return "
        "as they assume more risk.")

    d.h3("The two-fund separation theorem")
    d.key("Every investor, regardless of wealth, taste or risk aversion, holds a "
          "combination of just two things: the risk-free asset and the SAME optimal "
          "risky portfolio P. Only the proportions differ.")
    d.p("This splits the problem into two independent decisions. The investment decision "
        "- identifying P - is purely technical and identical for everybody. The "
        "financing decision - how much to lend or borrow - is where personal risk "
        "preference enters. Points left of P are lending portfolios; points right of P "
        "are borrowing (leveraged) portfolios, achieved by borrowing at R_f and "
        "investing more than 100% in P.")
    d.warn("A common error: assuming a highly risk-averse investor holds a different, "
           "safer risky portfolio. They do not. They hold the same portfolio P, just "
           "less of it, with the rest in the risk-free asset.")

    d.h3("Comprehensive worked example (the Lohrmanns)")
    d.p("Two risky assets: A returns 20% with 50% risk; B returns 15% with 33% risk; "
        "correlation zero. A risk-free asset returns 3%. The slope-maximising weight "
        "turns out to be 38.20% in A, which produces the capital allocation line:")
    d.formula("E(R_p) = 0.03 + 0.4978 σ_p",
              "0.4978 is the market price of risk - each extra 1% of standard deviation "
              "buys about 0.50% of extra expected return.")
    d.p("With a risk aversion coefficient of 2.5, computing utility at several points "
        "along this line gives 0.0300 at a 3% return, 0.0717 at 9%, 0.0774 at 15% and "
        "0.0546 at 20%. Utility rises and then falls, so the Lohrmanns' optimal "
        "portfolio is the 15% return / 24.1% risk point.")
    d.p("One detail worth noticing: on the CAL a 20% return can be obtained with 34.2% "
        "risk, whereas holding Asset A alone gives the same 20% return with 50% risk. "
        "Combining assets with the risk-free asset is simply a better deal than holding "
        "any single risky asset.")


# ======================================================================
def module2(d):
    d.h1(2, "Portfolio Risk and Return: Part II",
         "The Capital Asset Pricing Model: which risk gets paid, how beta measures it, "
         "and how to judge whether a manager actually added value.")

    d.h2("2.1  From the CAL to the Capital Market Line")
    d.p("The capital market line is a special case of the capital allocation line - the "
        "one where the risky portfolio is the market portfolio itself.")
    d.formula("E(R_p) = R_f + [ (E(R_m) − R_f) / σ_m ] × σ_p",
              "The x-axis is total risk (standard deviation). The CML applies only to "
              "efficient, well-diversified portfolios.")
    d.p("Points above the CML are unattainable; points below it are dominated. Note that "
        "although the CML combines two assets, it is a straight line - unlike a "
        "combination of two risky assets, which curves. The reason is arithmetic: the "
        "risk-free asset has zero standard deviation and zero covariance with everything, "
        "so two of the three terms in the portfolio variance formula disappear and "
        "σ_p reduces to (1 − w₁)σ_m.")

    d.h3("A worked case")
    d.p("T-bills at 5%; the market at 15% return with 20% risk. The CML is therefore "
        "E(R_p) = 5% + 0.50 σ_p.")
    make_table(d,
               ["% in market", "Expected return", "Risk"],
               [["0% (all T-bills)", "5.0%", "0%"],
                ["25%", "7.5%", "5%"],
                ["75%", "12.5%", "15%"],
                ["100%", "15.0%", "20%"],
                ["125% (borrow 25%)", "17.5%", "25%"],
                ["200% (borrow 100%)", "25.0%", "40%"]],
               widths=(44, 34, 24), align=("LEFT", "RIGHT", "RIGHT"))
    d.p("Leverage extends the line to the right. Negative investment in the risk-free "
        "asset - borrowing - raises both expected return and risk proportionally.")

    d.h3("When borrowing costs more than lending")
    d.p("Realistically you cannot borrow at the government's rate. If you lend at R_f but "
        "borrow at the higher R_b, the CML kinks at the market portfolio: it keeps the "
        "slope (R_m − R_f)/σ_m up to M, then flattens to (R_m − R_b)/σ_m "
        "beyond it. In the curriculum's example the slope drops from 0.50 to 0.40 - each "
        "1% of extra risk now buys only 0.40% of extra return. Leverage still works, but "
        "on worse terms, so only less risk-averse investors will choose it.")

    d.h3("Does a single optimal risky portfolio really exist?")
    d.p("Only under homogeneity of expectations - the assumption that everyone analyses "
        "securities identically and reaches identical valuations. The curriculum's "
        "Siemens illustration shows how fragile that is: the shares closed at EUR 111.84, "
        "but one analyst might value them at EUR 95 (overvalued, weight zero) and another "
        "at EUR 125 (undervalued, overweight). Different valuations mean different "
        "optimal portfolios.")
    d.p("The saving argument is that the market price reflects what the marginal, "
        "informed investor believes, so the market portfolio remains the natural "
        "benchmark against which everything else is judged - even if no individual "
        "actually holds it.")
    d.p("This distinction also defines passive versus active management. Passive "
        "investors accept market prices as unbiased and track an index cheaply. Active "
        "investors trust their own estimates, overweighting what they think is cheap, "
        "underweighting or shorting what they think is dear.")
    d.warn("What is 'the market'? Theoretically every risky asset with value, including "
           "human capital and the Taj Mahal. In practice a proxy such as the S&P 500 is "
           "used - which covers roughly 80% of US equity capitalisation but only about "
           "32% of world equity, and no bonds or property. Every CAPM result inherits "
           "that approximation. Roll's critique says this is why CAPM cannot truly be "
           "tested.")

    d.h2("2.2  Systematic and non-systematic risk")
    make_table(d,
               ["", "Systematic risk", "Non-systematic risk"],
               [["Also called", "Market, non-diversifiable", "Company-specific, idiosyncratic, diversifiable"],
                ["Sources", "Interest rates, inflation, economic cycles, political uncertainty, widespread natural disaster",
                 "A failed drug trial, an airliner crash, a management scandal"],
                ["Diversifiable?", "No", "Yes"],
                ["Is it paid?", "Yes", "No"]],
               widths=(24, 55, 59))
    d.formula("Total variance = Systematic variance + Non-systematic variance\n\n"
              "σ_i² = β_i² σ_m² + σ_e²\n"
              "σ_i  = √( β_i²σ_m² + σ_e² )",
              "The components add as VARIANCES, never as standard deviations. This is a "
              "classic exam trap.")

    d.h3("Why non-systematic risk earns nothing")
    d.p("Follow the argument through, because it is examinable as reasoning rather than "
        "as a fact to recall. Suppose diversifiable risk did pay a premium. You would "
        "buy assets loaded with it, then diversify it away by combining uncorrelated "
        "holdings. You would end up bearing only systematic risk while still collecting "
        "payment for non-systematic risk you no longer hold - a free lunch.")
    d.p("Every investor would do the same. Demand for such assets would rise, their "
        "prices would climb, and their expected returns would fall until the free lunch "
        "disappeared. Equilibrium is therefore reached only when the premium for "
        "diversifiable risk is exactly zero.")
    d.key("Only risk that cannot be avoided is compensated. This is the single most "
          "important conclusion in Module 2, and everything downstream - beta, the CAPM, "
          "the SML, the Treynor ratio, Jensen's alpha - is a consequence of it.")
    d.p("A caveat the curriculum adds: this does not mean non-systematic risk is "
        "harmless. It matters greatly to company management, to poorly diversified "
        "investors, and to analysts covering individual firms. And what looks like "
        "company-specific risk can turn out to be systematic - poor credit management "
        "at one bank became a global crisis because the bank was too big to fail.")

    d.h2("2.3  Return-generating models and beta")
    d.p("Building a true market portfolio is impractical - 1,000 assets would require "
        "1,000 return estimates, 1,000 standard deviations and 499,500 correlations. "
        "Return-generating models cut through this by estimating expected return from a "
        "small number of factors.")
    d.bullets([
        "Macroeconomic factor models - growth, interest rates, inflation, employment, "
        "consumer confidence.",
        "Fundamental factor models - earnings, growth, cash flow, R&D, patents.",
        "Statistical factor models - factors extracted from the data itself. The "
        "curriculum warns these can produce nonsense: the conference of the Super Bowl "
        "winner appears to explain US stock returns, with no economic link whatsoever. "
        "Data mining generates spurious factors, so analysts prefer the first two types.",
    ])
    d.p("The simplest version is the single-index model, E(R_i) − R_f = "
        "β_i[E(R_m) − R_f]. Its practical implementation is the market model, "
        "estimated by regression:")
    d.formula("R_i = α_i + β_i R_m + e_i",
              "α is the intercept, β the slope, e the company-specific error. "
              "Fitted by regressing historical security returns on market returns.")
    d.p("A worked case: Wal-Mart's regression gives α = 0.0001 and β = 0.90. On "
        "a day when the market rises 1%, the expected return is 0.0001 + 0.90 × 0.01 "
        "= 0.91%. If Wal-Mart actually rose 2%, the abnormal (company-specific) return "
        "is 2% − 0.91% = 1.09%.")

    d.h3("Calculating beta")
    d.formula("β_i = Cov(R_i, R_m) / σ_m² = ρ_i,m × (σ_i / σ_m)",
              "Two equivalent forms. Use the first when given covariance, the second "
              "when given correlation and standard deviations.")
    d.bullets([
        "Market beta = 1 by definition (its correlation with itself is 1).",
        "Risk-free asset beta = 0 (zero covariance with everything).",
        "The average beta of all assets in the market is 1.",
        "Positive beta means the asset moves with the market; negative beta means "
        "against it. Consistently negative betas are rare, because most stocks in "
        "developed markets correlate above 0.70 with the market.",
    ])
    d.p("Quick examples: correlation 0.70, asset SD 0.25, market SD 0.15 gives "
        "β = 0.70 × 0.25 / 0.15 = 1.17. Gold with a large SD but zero "
        "correlation has β = 0. An IPO with SD 40% and correlation 0.7 against a "
        "25% market has β = 1.12 - risky in total terms, but only modestly so "
        "systematically.")
    d.warn("High total risk does not imply high beta. Gold in the curriculum's example "
           "has the same standard deviation as the market but a beta of zero, because it "
           "is uncorrelated. Questions exploit this constantly.")
    d.p("On estimation: short windows (say 12 months) reflect current risk but are noisy "
        "and distorted by one-off events. Longer windows of three to five years are "
        "statistically steadier but may describe a company that no longer exists in that "
        "form. A three-year beta will differ from a five-year beta, and a beta from daily "
        "data will differ from one built on monthly data.")

    d.h2("2.4  The CAPM and the Security Market Line")
    d.formula("E(R_i) = R_f + β_i [ E(R_m) − R_f ]",
              "The market risk premium is E(R_m) − R_f, also called the excess "
              "market return. Portfolio beta is simply the weighted average of "
              "component betas: β_p = Σ w_iβ_i.")
    d.p("Two assets with the same beta have the same expected return, whatever they are "
        "- a bank, a gold mine, an emerging market fund. Under CAPM, beta is the only "
        "thing that matters. Assets with β > 1 are expected to beat the market; "
        "β < 1 to lag it; β < 0 to return LESS than the risk-free rate.")
    d.p("That last case is not a mistake. Insurance is the curriculum's example: it pays "
        "out precisely when your wealth is destroyed, so it reduces total portfolio risk "
        "and is valuable despite a negative expected return.")

    d.h3("The six assumptions")
    d.numbered([
        "Investors are risk-averse, utility-maximising and rational. They need not share "
        "the same degree of risk aversion, only the direction.",
        "Markets are frictionless - no transaction costs, no taxes, no restrictions on "
        "short selling, and borrowing and lending at R_f are both possible.",
        "All investors plan for the same single holding period.",
        "Investors have homogeneous expectations - the assumption that produces one "
        "market portfolio and one security market line.",
        "All investments are infinitely divisible.",
        "Investors are price takers; no single trader moves prices.",
    ])
    d.p("The purpose of all six is to create a marginal investor who chooses a "
        "mean-variance efficient portfolio predictably. Relaxing most of them changes "
        "little. The exception the curriculum highlights is short selling: costs or "
        "restrictions on shorting can introduce an upward bias in asset prices and do "
        "genuinely threaten CAPM's conclusions.")

    d.h3("SML versus CML - a distinction that is heavily tested")
    make_table(d,
               ["", "Capital Market Line", "Security Market Line"],
               [["X-axis", "Total risk (σ)", "Systematic risk (β)"],
                ["Applies to", "Efficient, well-diversified portfolios only",
                 "ANY security or portfolio, efficient or not"],
                ["Slope", "(R_m − R_f)/σ_m, the market price of risk",
                 "R_m − R_f, the market risk premium"],
                ["Used for", "Asset allocation between R_f and the market",
                 "Pricing securities; spotting mis-valuation"]],
               widths=(20, 60, 58))
    d.key("Total risk and systematic risk are equal ONLY for efficient portfolios, "
          "because those have no diversifiable risk left. For an individual security "
          "they differ, which is exactly why the SML - and not the CML - is the tool "
          "for pricing single securities.")

    d.h3("Worked examples")
    d.p("Risk-free 3%, market 13% with 23% risk. Bajaj Auto has 50% standard deviation "
        "but zero correlation with the market, so β = 0 and E(R) = 3% - the "
        "risk-free rate, despite being a volatile stock. Mueller Metals also has 50% "
        "risk but correlation 0.65, giving β = 1.41 and E(R) = 3% + 1.41 × 10% "
        "= 17.1%.")
    d.p("Portfolio example: 20% risk-free, 30% market, 50% in a stock with β = 2.0. "
        "β_p = (0.20 × 0) + (0.30 × 1.0) + (0.50 × 2.0) = 1.30, so "
        "E(R_p) = 4% + 1.30 × 12% = 19.6%.")

    d.h3("Using CAPM in capital budgeting")
    d.p("The GlaxoSmithKline case shows the model doing real work. Beta 2.3, risk-free "
        "2%, market 12%, so the required return is 2% + 2.3 × 10% = 25%. Discounting "
        "the probability-weighted cash flows at 25% gives an NPV of minus $147.07 "
        "million, so the project is rejected. A lower discount rate would have approved "
        "it - which is precisely why the risk adjustment matters.")

    d.h2("2.5  Where CAPM breaks down")
    d.h3("Theoretical limitations")
    d.bullets([
        "Single-factor: only beta is priced, so no other characteristic may be "
        "considered. Simple and prescriptive, but restrictive and inflexible.",
        "Single-period: it cannot capture factors that vary over time or span several "
        "periods, which can encourage myopic decisions.",
    ])
    d.h3("Practical limitations")
    d.bullets([
        "The true market portfolio includes non-investable assets such as human capital "
        "and is therefore unobservable - Roll's critique.",
        "Different proxies give different answers for the same asset, which the model "
        "does not permit.",
        "Beta estimates are unstable across periods and data frequencies.",
        "It predicts returns poorly. Empirical support is weak; realised returns are not "
        "determined by systematic risk alone.",
        "Homogeneous expectations plainly do not hold, so there is no unique optimal "
        "portfolio or single SML.",
    ])
    d.h3("What came next")
    d.p("Arbitrage Pricing Theory allows many factors, and the factors need not be "
        "common across assets. It is theoretically elegant and more flexible than CAPM, "
        "but it does not tell you what the factors are - which is why CAPM remains "
        "preferred in practice.")
    d.formula("Fama-French-Carhart four-factor model:\n\n"
              "E(R_it) = α_i + β_MKT·MKT + β_SMB·SMB\n"
              "                  + β_HML·HML + β_UMD·UMD",
              "MKT = excess market return; SMB = small minus big (size); HML = high "
              "minus low book-to-market (value versus growth); UMD = up minus down "
              "(momentum).")
    d.p("Historically the coefficient on MKT is not significantly different from zero - "
        "an uncomfortable result, since it implies stock returns are largely unrelated "
        "to the market factor. Size, value and momentum do the explanatory work. The "
        "model predicts far better than CAPM, but two caveats apply: it has no "
        "equilibrium theory behind it, and there is no assurance it will keep working.")

    d.h2("2.6  Performance appraisal")
    d.p("Performance evaluation answers three separate questions. Performance "
        "MEASUREMENT asks what the return and risk were. Performance ATTRIBUTION asks "
        "where the performance came from. Performance APPRAISAL asks whether it was "
        "skill or luck. The four ratios below belong to appraisal.")
    make_table(d,
               ["Measure", "Formula", "Risk used", "Key property"],
               [["Sharpe ratio", "(R_p − R_f) / σ_p", "Total",
                 "Slope of the CAL; must be compared with another portfolio to mean anything"],
                ["Treynor ratio", "(R_p − R_f) / β_p", "Systematic",
                 "Breaks down for negative-beta assets"],
                ["M²", "(R_p − R_f)(σ_m/σ_p) + R_f", "Total",
                 "Sharpe rescaled into a percentage return; ranks identically to Sharpe"],
                ["Jensen's alpha",
                 "R_p − [R_f + β_p(R_m − R_f)]", "Systematic",
                 "Meaningful on its own; the maximum you should pay a manager"]],
               widths=(24, 42, 20, 52))
    d.p("Both Sharpe and Treynor require a positive numerator to be meaningful. If the "
        "excess return is negative, a riskier portfolio produces a less negative ratio "
        "and the rankings invert - the measure becomes actively misleading.")
    d.p("M² answers the question 'what would this portfolio have returned if it had "
        "been levered or de-levered to exactly the market's volatility?' The gap between "
        "that figure and the market return is M² alpha. Worked example: R_f = 4%, "
        "R_p = 14%, σ_p = 25%, σ_m = 20%. Sharpe = 0.40, so M² = 0.40 "
        "× 0.20 + 0.04 = 12.0%. If the market returned 10%, the portfolio beat it by "
        "2.0% on a risk-adjusted basis.")

    d.h3("The three-manager case - and why it matters")
    make_table(d,
               ["Manager", "Return", "σ", "β", "Sharpe", "Treynor", "M² alpha", "Alpha"],
               [["X", "10.0%", "20.0%", "1.10", "0.35", "0.064", "0.65%", "0.40%"],
                ["Y", "11.0%", "10.0%", "0.70", "0.80", "0.114", "9.20%", "3.80%"],
                ["Z", "12.0%", "25.0%", "0.60", "0.36", "0.150", "0.84%", "5.40%"],
                ["Market", "9.0%", "19.0%", "1.00", "0.32", "0.060", "0.00%", "0.00%"]],
               widths=(20, 18, 16, 14, 18, 20, 22, 20),
               align=("LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"))
    d.p("All three managers beat the market on every measure, so the fund should be "
        "pleased. But Y and Z swap places depending on the measure used. On total-risk "
        "measures Y wins decisively (Sharpe 0.80 versus 0.36). On systematic-risk "
        "measures Z wins (Treynor 0.150 versus 0.114; alpha 5.40% versus 3.80%). Manager "
        "X is worst on every measure.")
    d.key("Choose the measure to match the situation. If the client's whole wealth is in "
          "this one portfolio, total risk is what they experience - use Sharpe or "
          "M², and hire Manager Y. If this is one sleeve of an already "
          "well-diversified fund, only systematic risk matters - use Treynor or Jensen's "
          "alpha, and hire Manager Z.")
    d.p("Note also that the risk-free asset has no Sharpe, Treynor or M² at all - "
        "each divides by a risk measure that is zero - but its alpha is defined and "
        "equals zero. The market's alpha and M² alpha are zero by construction.")

    d.h3("Security selection with the SML")
    d.p("Plot each security's estimated return against its beta. Points on the line are "
        "fairly valued. Points ABOVE the line offer more return than their risk "
        "warrants - undervalued, buy. Points BELOW are overvalued - avoid or short.")
    d.p("The security characteristic line makes the same point in regression form: plot "
        "the security's excess return against the market's excess return, and the "
        "intercept is Jensen's alpha while the slope is beta.")
    d.p("Positive alpha does not always mean mispricing. A security can have positive "
        "alpha simply because it is poorly correlated with your benchmark and its return "
        "is generous for the systematic risk it adds. For portfolio construction, weight "
        "each non-market security in proportion to α_i/σ_ei² - more "
        "weight for higher alpha, less for higher idiosyncratic risk. The information "
        "ratio α_i/σ_ei measures abnormal return per unit of added risk; "
        "higher is better.")
    d.p("Practical worked case: three stocks outside the Nikkei 225. P has alpha of "
        "minus 0.02 and is excluded. Q has alpha 0.04 with non-systematic variance "
        "0.0158, giving a relative weight of 2.53. R has alpha 0.03 with variance 0.0137, "
        "giving 2.19. Q therefore gets about 15.5% more weight than R.")
    d.p("Finally, on diversification: roughly 30 randomly selected securities across "
        "different asset classes remove most non-systematic risk. If the holdings are "
        "not randomly selected - thirty banks, say - the reduction is far smaller, and "
        "an index fund would serve better.")


def main():
    import sys, os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from _cfa_pc_part2 import module3, module4
    from _cfa_pc_part3 import module5, module6, appendix

    d = Guide()
    d.set_title("Portfolio Construction - CFA Level I Volume 9 Study Guide")
    d.set_author("Study guide")
    cover(d)
    how_to_use(d)
    module1(d)
    module2(d)
    module3(d)
    module4(d)
    module5(d)
    module6(d)
    appendix(d)
    d.output(OUT)
    print("Wrote:", OUT)
    print("Pages:", d.page_no())


if __name__ == "__main__":
    main()
