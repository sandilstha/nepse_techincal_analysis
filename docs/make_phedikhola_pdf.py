"""Generate the Phedikhola Hydropower investment assessment PDF (v3).

Sources: audited FY2079/80 accounts, NEA Grid Connection Agreement (13 Apr 2023),
CARE Ratings Nepal press release December 2025 (rating REVISED to BB-), company
website, public reporting.

Core PDF fonts are latin-1 only, so all text stays ASCII.
"""
from fpdf import FPDF

NAVY = (16, 42, 74)
RED = (176, 42, 42)
GREEN = (22, 110, 68)
AMBER = (150, 96, 8)
GREY = (110, 118, 132)
LINE = (205, 212, 222)


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, "Phedikhola Hydropower Company Limited - Investment Assessment", align="L")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GREY)
        self.cell(0, 4, "Analysis only - not investment advice. Sources: audited FY2079/80 accounts; "
                        "NEA Grid Connection Agreement 13 Apr 2023;", align="C")
        self.ln(3.4)
        self.cell(0, 4, "CARE Ratings Nepal press release Dec 2025; company website; public reporting.",
                  align="C")
        self.ln(3.4)
        self.cell(0, 4, f"Page {self.page_no()} of {{nb}}", align="C")


def UW(p):
    return p.w - p.l_margin - p.r_margin - 2


def h2(p, t, colour=NAVY):
    p.ln(2); p.set_x(p.l_margin)
    p.set_font("Helvetica", "B", 10.5); p.set_text_color(*colour)
    p.cell(0, 5.5, t); p.ln(6)
    p.set_draw_color(*LINE); p.set_line_width(0.3)
    p.line(p.l_margin, p.get_y() - 1, p.w - p.r_margin, p.get_y() - 1)
    p.ln(1)


def body(p, t, colour=(35, 40, 50)):
    p.set_x(p.l_margin)
    p.set_font("Helvetica", "", 9); p.set_text_color(*colour)
    p.multi_cell(UW(p), 4.4, t); p.ln(0.5)


def bullet(p, t, colour=(35, 40, 50)):
    p.set_x(p.l_margin)
    p.set_font("Helvetica", "", 9); p.set_text_color(*colour)
    p.cell(4, 4.4, "-")
    p.set_x(p.l_margin + 4)
    p.multi_cell(UW(p) - 4, 4.4, t)


def table(p, rows, widths):
    tot = sum(widths)
    widths = [w * (UW(p) - 2) / tot for w in widths]
    p.set_x(p.l_margin)
    for i, r in enumerate(rows):
        if i == 0:
            p.set_fill_color(238, 242, 248); p.set_text_color(*NAVY)
            p.set_font("Helvetica", "B", 8.5)
        else:
            p.set_fill_color(255, 255, 255); p.set_text_color(35, 40, 50)
            p.set_font("Helvetica", "", 8.5)
        p.set_x(p.l_margin)
        for w, cell in zip(widths, r):
            p.cell(w, 5.2, str(cell), border="B", fill=True)
        p.ln(5.2)
    p.ln(1)


p = PDF(format="A4")
p.set_margins(14, 14, 14)
p.alias_nb_pages()
p.set_auto_page_break(auto=True, margin=20)
p.add_page()

p.set_font("Helvetica", "B", 17); p.set_text_color(*NAVY)
p.multi_cell(UW(p), 7.5, "Phedikhola Hydropower Company Limited (PKHCL)")
p.set_font("Helvetica", "", 9.5); p.set_text_color(*GREY)
p.multi_cell(UW(p), 4.8, "Investment Assessment | 4.3 MW run-of-river, Bhojpur | "
                         "Updated to CARE Ratings press release of December 2025")
p.ln(2)

p.set_fill_color(255, 248, 235); p.set_draw_color(*AMBER); p.set_line_width(0.5)
y0 = p.get_y()
p.rect(p.l_margin, y0, p.w - p.l_margin - p.r_margin, 26, style="DF")
p.set_xy(p.l_margin + 3, y0 + 2.5)
p.set_font("Helvetica", "B", 11); p.set_text_color(*AMBER)
p.cell(0, 5, "VERDICT: SPECULATIVE - DO NOT COMMIT YET, BUT NO LONGER A REJECT"); p.ln(5)
p.set_x(p.l_margin + 3)
p.set_font("Helvetica", "", 8.5); p.set_text_color(70, 55, 30)
p.multi_cell(UW(p) - 6, 4,
             "The project is far more advanced than earlier public information suggested: 64% financial "
             "progress, debt fully closed, 96% of equity injected, and the credit rating UPGRADED to BB-. "
             "But the required commercial operation date expired in April 2025, penalties and tariff-"
             "escalation restrictions are now live, and power cannot be evacuated until a second project "
             "finishes. Wait for the IPO prospectus.")
p.set_y(y0 + 28)

h2(p, "1. What changed - and a correction to my earlier view", GREEN)
body(p, "An earlier draft of this assessment concluded 'not investable', based partly on the company "
        "website still describing tender preparation and access-road work as ongoing. That website was "
        "out of date. The CARE Ratings press release of December 2025 shows a materially different "
        "picture, and the earlier conclusion was too harsh on execution progress.")
table(p, [
    ["Measure", "Oct 2024 (prior review)", "Jun-Dec 2025 (current)"],
    ["Credit rating", "CARE-NP B+", "CARE-NP BB- (UPGRADED)"],
    ["Financial progress", "about 25%", "about 64% (as at 5 Jun 2025)"],
    ["Debt", "not tied up", "financial closure ACHIEVED"],
    ["Equity injected", "partial", "about 96%, Rs 402 million"],
    ["Company status", "private limited", "PUBLIC limited (Dec 2024)"],
], [40, 42, 48])
body(p, "The conversion to a public limited company in December 2024 is the formal step that precedes an "
        "IPO. The rating agency attributes the upgrade to 'satisfactory pace of progress', substantial "
        "equity infusion and full debt tie-up, which together lower funding risk.")

h2(p, "2. Project and financing structure")
table(p, [
    ["Item", "Detail"],
    ["Capacity / type", "4.3 MW run-of-river, BOOT, Salpasilicho, Bhojpur"],
    ["Total project cost", "Rs 939 million (Rs 218 million per MW)"],
    ["Debt : equity", "53 : 47 (Rs 500m debt / Rs 439m equity)"],
    ["Lender facility", "Term loan Rs 500 million, rated CARE-NP BB-"],
    ["Catchment area", "58.26 sq km, perennial river"],
    ["Turbines / generators", "2 x Pelton 2.22 MW (91% eff) / 2 x 2.53 MVA (97% eff)"],
    ["Net head / discharge", "171.58 m / 1.455 cumecs per unit"],
], [40, 130])

h2(p, "3. The PPA - the strongest asset, with one caveat")
table(p, [
    ["Item", "Detail"],
    ["PPA signed", "7 October 2018, with NEA"],
    ["Contracted capacity", "3.52 MW  (NOT the full 4.3 MW)"],
    ["Contracted energy / PLF", "20.68 million units / 67.06%"],
    ["Tariff", "Rs 8.40/kWh dry, Rs 4.80/kWh wet"],
    ["Escalation", "3% annually on base tariff, for 8 years"],
    ["Dry energy mix", "32%"],
    ["Term", "30 years from COD, or licence validity if earlier"],
    ["Generation licence", "27 February 2020, valid 35 years"],
], [40, 130])
body(p, "CAVEAT: the PPA covers 3.52 MW. The incremental 0.78 MW from the capacity upgrade is the portion "
        "subject to the 16 dispatch-restriction clauses in the NEA grid agreement (see section 6). "
        "Counterparty risk on NEA is assessed as moderate, given full Government of Nepal ownership.")

p.add_page()

h2(p, "4. Live risk: the required COD has already expired", RED)
body(p, "The Required Commercial Operation Date (RCOD) was 12 April 2025 and has passed. The company "
        "applied for an extension in January 2025 after infrastructure was damaged by a flood on "
        "30 July 2024. Two consequences are contractual, not hypothetical:", RED)
bullet(p, "DELAY PENALTY: 5% of the revenue that could have been generated between RCOD and actual COD.", RED)
bullet(p, "TARIFF ESCALATION LOSS: any delay beyond 6 months from RCOD restricts the number of tariff "
          "escalations available. Since the tariff escalates 3% per year for 8 years, losing escalations "
          "permanently reduces lifetime revenue - the rating agency states this diminishes return "
          "indicators and adversely impacts the revenue profile.", RED)
body(p, "The 6-month mark passed in October 2025, so this restriction is very likely already engaged. "
        "The extension application had not been confirmed as granted at the date of the rating release.", RED)

h2(p, "5. Power evacuation depends on a second project by the same promoter", RED)
body(p, "From the NEA Grid Connection Agreement (13 April 2023), confirmed by CARE:")
bullet(p, "Power is evacuated via a 5 km 33 kV line to the switchyard of the UNDER-CONSTRUCTION Upper "
          "Irkhuwa Hydropower Project (14.5 MW), developed by Aarati Power Company Limited "
          "(also rated CARE-NP BB-/A4).")
bullet(p, "It then shares an 18 km 132 kV line to NEA's UNDER-CONSTRUCTION Khandbari substation.")
bullet(p, "Grid agreement clause 18 lists both the 132 kV line from Upper Irkhuwa and the 220 kV "
          "Tumlingtar-Basantapur-Inaruwa line as 'deemed critical and must be completed before "
          "commissioning'.")
body(p, "Prakash Dulal is Executive Director of Phedikhola AND a director of Aarati Power. The project "
        "therefore cannot sell a single unit until a second, separately financed project run by the same "
        "person is finished - and NEA must also complete its substation. Three parties must all deliver. "
        "CARE calls timely completion of these lines 'crucial from a revenue generation perspective'.", RED)

h2(p, "6. Curtailment exposure on the incremental 0.78 MW")
body(p, "Clauses 6-17 of the grid agreement each bind the developer to NEA Load Dispatch Center "
        "instructions. The PPA fixes a tariff; it does not guarantee dispatch.")
table(p, [
    ["Constrained line / condition", "Period of restriction"],
    ["Dhalkebar-Muzaffarpur 400 kV, wet peak and off-peak", "FY2025/26 - FY2028/29"],
    ["Dhalkebar-Muzaffarpur 400 kV, N-1 wet off-peak", "FY2025/26 - FY2033/34"],
    ["Khandbari-Baneshwor-Basantapur 220 kV, N-1", "FY2026/27 onwards"],
    ["Basantapur-New Duhabi 220 kV, N-1", "FY2026/27 onwards"],
    ["If four cross-border 400 kV lines are not built", "FY2025/26 - FY2029/30 on"],
], [105, 65])

h2(p, "7. Management and governance")
body(p, "Chandra Prasad Bastola (Chairman) has over a decade in banks and financial institutions. "
        "Prakash Dulal (Executive Director) has more than a decade in hydropower and is a director of "
        "Aarati Power [BB-/A4], Nilganga Hydropower, Sewa Hydro [B+/A4] and Himalayan Urja Bikash.")
body(p, "Two observations. First, the promoter group is genuinely experienced and rated across several "
        "entities - but none is investment grade; all sit in the B+ to BB- band. Second, the FY2079/80 "
        "audited accounts showed Rs 5.39m of advances to individuals against only Rs 613,788 of cash, "
        "including Rs 389,808 to the Managing Director himself and Rs 3,100,000 to Ramesh Prasad Dulal. "
        "That audit predates the current build phase, but the practice is worth testing in the prospectus.")

h2(p, "8. Sector tailwinds (per CARE)")
bullet(p, "Full income tax exemption for 10 years, then 50% for 5 years, for projects in commercial "
          "operation before mid-April 2028.")
bullet(p, "Nepal Rastra Bank mandates a minimum share of bank lending to the energy sector.")
bullet(p, "National energy demand growing about 11% per year over 2020-2025.")
bullet(p, "Nepal-India treaty to export 10,000 MW over 10 years supports long-term demand.")
body(p, "Note the tax incentive is time-limited: commercial operation must be achieved before mid-April "
        "2028 to capture the full 10-year exemption. Further slippage puts that benefit at risk too.", AMBER)

p.add_page()

h2(p, "9. Balance of the argument")
table(p, [
    ["Against", "In favour"],
    ["RCOD expired Apr 2025; penalty live", "Rating UPGRADED B+ to BB- (Dec 2025)"],
    ["Tariff escalations likely restricted", "64% financial progress (Jun 2025)"],
    ["Cannot evacuate until Upper Irkhuwa done", "Debt fully closed; 96% equity (Rs 402m)"],
    ["NEA substation still under construction", "PPA signed 30 yr; licence valid 35 yr"],
    ["16 curtailment clauses to FY2033/34", "Now a public limited company (IPO path)"],
    ["PPA covers 3.52 MW, not 4.3 MW", "10-yr tax holiday if COD before Apr 2028"],
    ["Flood damage July 2024", "Experienced multi-project promoter group"],
    ["Related-party advances in older accounts", "NEA counterparty risk only moderate"],
], [86, 86])

h2(p, "10. Recommendation")
bullet(p, "Do NOT commit capital yet - but this is no longer a project to dismiss. The upgrade to BB-, "
          "full debt closure and 96% equity infusion are real, verifiable improvements.")
bullet(p, "WAIT FOR THE IPO PROSPECTUS. Conversion to public limited in December 2024 means it is coming. "
          "The prospectus will carry current audited accounts, actual construction progress and a "
          "regulated entry price.")
bullet(p, "Before subscribing, get answers to five questions:")
p.set_x(p.l_margin + 8)
p.set_font("Helvetica", "", 9); p.set_text_color(35, 40, 50)
p.multi_cell(UW(p) - 8, 4.4,
             "1. Was the RCOD extension granted, and on what terms?\n"
             "2. How many tariff escalations have been forfeited, and what does that do to project IRR?\n"
             "3. What is the current status of Upper Irkhuwa's switchyard and the 132 kV line?\n"
             "4. When will NEA's Khandbari substation be energised?\n"
             "5. What is the revised COD, and can it beat the mid-April 2028 tax-holiday deadline?")
p.ln(1)
bullet(p, "Treat this as a SPECULATIVE, high-risk holding if you do subscribe. BB- is below investment "
          "grade, and the single largest risk - power evacuation - is outside the company's control.")

h2(p, "11. Limitations of this assessment")
body(p, "The audited accounts available are for FY2079/80 (year ended 16 July 2023), when the company had "
        "no revenue, Rs 40m of project work in progress and no borrowings. They describe roughly 4% of "
        "the eventual project and should not be used to value it. The progress figures here come from the "
        "CARE release and are dated 5 June 2025; construction status at the date of reading may differ. "
        "Whether the project is now near completion or has slipped further cannot be verified from the "
        "documents reviewed.", GREY)

out = r"c:\Users\Admin\Desktop\nepse_analytics_platform\docs\Phedikhola-Investment-Assessment-v3.pdf"
p.output(out)
print("written:", out)
