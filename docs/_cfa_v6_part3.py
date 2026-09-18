"""Volume 6, modules 14 to 19 and the formula sheet. Imported by make_cfa_v6.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module14(d):
    d.h1(14, "Credit Risk",
         "Everything so far assumed the issuer pays. This module is about the possibility "
         "that it does not.")

    d.h2("The components")
    d.formula("Expected loss  =  probability of default  x  loss given default\n\n"
              "Loss given default  =  exposure  x  (1 - recovery rate)",
              "Two separate questions: how likely is a default, and how much is lost if one "
              "happens. A bond can have a high default probability and a small expected loss "
              "if it is well secured.")
    d.example("A bond has a 4% probability of default over the year, an exposure of "
              "Rs 10,000,000, and an expected recovery of 60%.\n\n"
              "  Loss given default = 10,000,000 x (1 - 0.60) = Rs 4,000,000\n"
              "  Expected loss = 0.04 x 4,000,000 = Rs 160,000\n\n"
              "That is 1.6% of the exposure, so the bond must yield at least 1.6% more than "
              "the risk-free rate simply to break even on expected credit losses, before any "
              "compensation for bearing the risk itself.")
    d.bullets([
        "Default risk: the issuer fails to pay.",
        "Loss severity: how much is lost when it does.",
        "Spread risk: the spread widens without any default, and the price falls.",
        "Downgrade risk: a rating agency lowers the rating, usually widening the spread.",
        "Market liquidity risk: the bond can only be sold at a concession.",
    ])

    d.h2("Ratings")
    make_table(d,
               ["Grade", "Moody's", "S&P and Fitch"],
               [["Investment grade", "Aaa down to Baa3", "AAA down to BBB-"],
                ["High yield", "Ba1 and below", "BB+ and below"]],
               widths=(28, 32, 40))
    d.key("The boundary between BBB- and BB+ matters far more than one notch should, because "
          "many institutions are mandated to hold only investment grade. A downgrade across "
          "that line forces selling by investors who have no choice, which is why a 'fallen "
          "angel' often falls much further than the change in credit quality alone justifies.")
    d.warn("Rating agencies rate the ISSUE, not only the issuer. A senior secured bond and a "
           "subordinated bond from the same company carry different ratings, through notching. "
           "Ratings are also lagging indicators: the market usually moves the spread well "
           "before the agency moves the rating.")

    d.h2("Spread and price")
    d.formula("Yield  =  risk-free rate  +  credit spread\n\n"
              "Approximate % price change from a spread move\n"
              "     =  - modified duration  x  change in spread",
              "The same duration arithmetic applies: a spread widening hurts the price "
              "exactly as a yield rise does, because for the holder they are the same thing.")


def module15(d):
    d.h1(15, "Credit Analysis for Government Issuers",
         "Assessing a borrower that writes the laws, and in its own currency prints the money.")

    d.h2("Sovereign analysis")
    d.p("The curriculum frames it around two questions: is the government ABLE to pay, and is "
        "it WILLING to pay? The second is genuine, not rhetorical. Sovereign default is often "
        "a political choice rather than an arithmetic necessity.")
    make_table(d,
               ["Dimension", "What is examined"],
               [["Institutional", "Stability, rule of law, policy credibility, corruption, "
                 "the record of honouring debts"],
                ["Economic", "Growth, income per head, diversification, competitiveness"],
                ["External", "Current account, reserves, external debt, currency regime"],
                ["Fiscal", "Deficit, debt to GDP, interest burden, the revenue base"],
                ["Monetary", "Inflation record, central bank independence, depth of the "
                 "domestic market"]],
               widths=(22, 78))
    d.key("Local currency debt and foreign currency debt from the same sovereign are "
          "different credits. Local currency debt can, in the last resort, be serviced by "
          "creating money, which is why ratings on it are typically higher. Foreign currency "
          "debt requires reserves the government cannot create, so the reserve position and "
          "the current account matter far more.")
    d.warn("A high debt-to-GDP ratio is not on its own evidence of distress. What matters is "
           "the interest burden relative to revenue, who holds the debt, what currency it is "
           "in, and the average maturity. A country with high debt held domestically in its "
           "own currency at long maturities is in a very different position from one with "
           "less debt owed abroad in dollars at short maturities.")

    d.h2("Non-sovereign government debt")
    d.p("Local authority debt splits into two kinds, and the distinction decides the analysis "
        "entirely.")
    d.bullets([
        "General obligation bonds: backed by the issuer's full taxing power. Analyse the "
        "local economy, the tax base, the employment mix, and the pension obligations.",
        "Revenue bonds: backed only by the revenue of a specific project, such as a toll road "
        "or a utility. Analyse the project. There is no recourse to the taxpayer, so these "
        "are riskier and yield more.",
    ])
    d.formula("Debt service coverage ratio  =  net project revenue / debt service",
              "The central ratio for a revenue bond. Below 1.0 the project cannot service "
              "its own debt from its own cash.")


def module16(d):
    d.h1(16, "Credit Analysis for Corporate Issuers",
         "The framework for a company, and the ratios that put numbers behind it.")

    d.h2("The four Cs")
    make_table(d,
               ["C", "Question"],
               [["Capacity", "Can it generate enough cash to service the debt? The industry, "
                 "the competitive position, and the operating performance"],
                ["Collateral", "What is the quality of the assets backing the claim, "
                 "including intangibles that may be worth nothing in a liquidation"],
                ["Covenants", "What do the terms permit the issuer to do to the lender's "
                 "position"],
                ["Character", "Management's record, strategy, accounting aggressiveness, and "
                 "history of honouring obligations"]],
               widths=(18, 82))
    d.key("Capacity is where most of the analysis goes, and it is Volume 4 applied to a "
          "credit question rather than an equity one. The difference in mindset matters: an "
          "equity analyst asks how good the upside is, a credit analyst asks how bad the "
          "downside can get before the interest stops being paid.")

    d.h2("The ratios")
    d.formula("LEVERAGE\n"
              "  Debt / EBITDA           - the headline measure; lower is safer\n"
              "  Debt / capital          - the balance sheet view\n"
              "  FFO / debt              - funds from operations against debt\n\n"
              "COVERAGE\n"
              "  EBIT / interest expense      - the standard interest coverage ratio\n"
              "  EBITDA / interest expense    - more generous, ignores depreciation\n\n"
              "PROFITABILITY AND CASH\n"
              "  Operating margin,  free cash flow after dividends / debt")
    d.example("A company reports EBITDA of Rs 2,400m, EBIT of Rs 1,600m, interest expense of "
              "Rs 400m and total debt of Rs 7,200m.\n\n"
              "  Debt / EBITDA = 7,200 / 2,400 = 3.0x\n"
              "  EBIT / interest = 1,600 / 400 = 4.0x\n"
              "  EBITDA / interest = 2,400 / 400 = 6.0x\n\n"
              "Three times leverage with four times interest cover is a solid investment "
              "grade profile for most industries. But notice how much more comfortable the "
              "EBITDA coverage looks: EBITDA ignores the depreciation, and a company that "
              "must eventually replace its assets cannot ignore it forever. Where the two "
              "coverage ratios diverge widely, the business is capital-intensive and the EBIT "
              "figure is the honest one.")
    d.warn("EBITDA is not cash flow. It ignores capital expenditure, working capital "
           "movements, interest and tax. For a capital-intensive issuer it substantially "
           "overstates the cash available to service debt, and the curriculum is explicit "
           "that leverage measured on EBITDA alone flatters exactly the issuers least able to "
           "afford it.")

    d.h2("Yields and the industry")
    d.p("Two companies with identical ratios in different industries deserve different "
        "leverage. A regulated utility with predictable, contracted cash flows can carry debt "
        "that would be reckless for a cyclical manufacturer. Always assess leverage against "
        "the volatility of the cash flow, not against an absolute standard.")
    d.p("Seniority within the structure matters as much as the issuer's quality. The same "
        "company's senior secured and subordinated bonds can differ by several hundred basis "
        "points, because the recovery rates differ enormously.")


def module17(d):
    d.h1(17, "Fixed-Income Securitization",
         "Pooling many loans into one security, and why the result can be safer than any of "
         "the loans in it.")

    d.h2("How it works")
    d.numbered([
        "An originator, typically a bank, holds a pool of loans: mortgages, car loans, credit "
        "card receivables.",
        "It sells them to a special purpose entity, legally separate from itself.",
        "The special purpose entity issues securities backed by the cash flows from that pool.",
        "Investors buy those securities and receive the pool's payments.",
    ])
    d.key("The legal separation is the whole point. Because the special purpose entity owns "
          "the loans outright, investors are exposed to the POOL and not to the originator. "
          "The securities can therefore carry a higher rating than the bank that created "
          "them, and the bank frees up capital to lend again. This is called bankruptcy "
          "remoteness.")

    d.h2("Tranching")
    d.p("The securities issued are divided into tranches with a defined order of priority. "
        "Senior tranches are paid first and absorb losses last; junior and equity tranches "
        "are paid last and absorb losses first.")
    make_table(d,
               ["Tranche", "Paid", "Losses", "Yield"],
               [["Senior", "First", "Last", "Lowest"],
                ["Mezzanine", "Second", "Second", "Middle"],
                ["Junior / equity", "Last", "First", "Highest"]],
               widths=(26, 22, 22, 30))
    d.warn("Tranching redistributes risk; it does not reduce it. The total credit risk of the "
           "pool is unchanged, and every rupee of loss still falls somewhere. What tranching "
           "does is concentrate the loss in the junior tranches so that the senior ones can "
           "be rated highly. Any question implying that securitisation creates safety out of "
           "nothing is testing this point.")

    d.h2("Credit enhancement")
    d.bullets([
        "Internal: subordination through tranching, overcollateralisation (the pool is worth "
        "more than the securities issued), and excess spread (the pool yields more than the "
        "securities pay).",
        "External: a third-party guarantee, a letter of credit, or bond insurance. External "
        "enhancement introduces the guarantor's own credit risk.",
    ])


def module18(d):
    d.h1(18, "Asset-Backed Security (ABS) Instrument and Market Features",
         "Securitisation applied to loans other than mortgages, and the structures that "
         "result.")

    d.h2("Amortising and non-amortising pools")
    make_table(d,
               ["Type", "Example", "Structure"],
               [["Amortising", "Car loans, equipment leases",
                 "Principal returns steadily; the pool shrinks over time"],
                ["Non-amortising", "Credit card receivables",
                 "Balances revolve, so a lockout period reinvests principal in new "
                 "receivables before amortisation begins"]],
               widths=(22, 26, 52))
    d.p("A credit card structure therefore has two phases. During the revolving period, "
        "principal collected is used to buy more receivables and investors receive interest "
        "only. In the amortisation period, principal is passed through to investors.")
    d.key("Early amortisation is the protective trigger. If the pool's performance "
          "deteriorates past defined thresholds, the revolving period ends immediately and "
          "principal is returned to investors early. It protects the investor but shortens "
          "the security's life at precisely the moment reinvestment is least attractive.")

    d.h2("Collateralised debt obligations")
    d.p("A CDO pools debt obligations, which may be corporate bonds, loans, or other "
        "structured securities, and tranches the result. Unlike a conventional ABS, a CDO has "
        "an active manager who trades the underlying portfolio, and the cash flows are not "
        "simply passed through.")
    d.warn("Where a CDO's collateral is itself made of other structured securities, the "
           "correlation between the underlying assets becomes the dominant risk and it is "
           "extremely difficult to estimate. Tranching only works if losses are dispersed; if "
           "everything in the pool defaults together, the senior tranche is not protected by "
           "anything. This is the specific mechanism that failed in 2008, and the curriculum "
           "treats it as the cautionary case.")


def module19(d):
    d.h1(19, "Mortgage-Backed Security (MBS) Instrument and Market Features",
         "The largest securitisation market, and the one with a risk found nowhere else: the "
         "borrower's right to repay early.")

    d.h2("The underlying mortgage")
    d.p("A residential mortgage is a loan secured on property, usually amortising over twenty "
        "to thirty years. Two measures define its risk: the loan-to-value ratio, which "
        "determines how much equity cushions a fall in house prices, and the debt service "
        "coverage of the borrower's income.")
    d.p("A recourse loan allows the lender to pursue the borrower's other assets if the "
        "property does not cover the debt. A non-recourse loan does not, so the borrower "
        "holds what amounts to a put option on the house, and default becomes rational "
        "whenever the property is worth less than the loan.")

    d.h2("Prepayment risk")
    d.p("Borrowers can repay early, and they do so mainly when rates fall and refinancing "
        "becomes attractive. The investor then receives principal back at exactly the moment "
        "when it can only be reinvested at lower rates.")
    d.key("This is why a mortgage-backed security displays NEGATIVE convexity. When rates "
          "fall, an ordinary bond rises in price; an MBS rises far less, because prepayments "
          "accelerate and return the principal. When rates rise, prepayments slow, the "
          "expected life extends, and the price falls much as any bond would. The investor "
          "gets the bad half of both outcomes.")
    make_table(d,
               ["", "When rates FALL", "When rates RISE"],
               [["Prepayments", "Accelerate", "Slow down"],
                ["Average life", "Shortens", "Extends"],
                ["The risk is called", "Contraction risk", "Extension risk"],
                ["Effect on the investor", "Cash returned to reinvest at lower rates",
                 "Stuck holding a below-market coupon for longer"]],
               widths=(24, 38, 38))
    d.warn("Contraction and extension risk are frequently confused. Remember that rates "
           "falling CONTRACTS the life, because borrowers refinance. Both outcomes are "
           "unfavourable, which is exactly the definition of negative convexity and the "
           "reason MBS yields exceed government yields of similar duration.")

    d.h2("Types of MBS")
    d.bullets([
        "Pass-through: principal and interest are collected and passed to investors pro "
        "rata, after a servicing fee. Every holder faces the same prepayment experience.",
        "Collateralised mortgage obligation: the same cash flows are redistributed into "
        "tranches with different prepayment exposure, so that some investors bear contraction "
        "risk and others bear extension risk according to preference.",
        "Commercial MBS: backed by income-producing commercial property. These are typically "
        "non-recourse and carry prepayment penalties or lockouts, so prepayment risk is much "
        "reduced and the analysis shifts to the debt service coverage of the properties.",
    ])
    d.formula("Debt service coverage ratio  =  net operating income / debt service\n\n"
              "  The central ratio for commercial MBS. Above 1.0 the property services\n"
              "  its own debt; the higher the figure, the greater the cushion.",
              "Note the contrast with residential MBS, where prepayment dominates. In "
              "commercial MBS the prepayment is restricted, so credit quality returns to the "
              "centre of the analysis.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place. Fixed income has the "
        "heaviest formula load at Level I; this page is worth reproducing from memory.")

    d.h2("Price and yield")
    d.formula("Price  =  sum of [ coupon / (1+r)^t ]  +  par / (1+r)^n\n\n"
              "Current yield  =  annual coupon / price\n"
              "Full price     =  flat price + accrued interest\n"
              "Accrued interest  =  coupon x (days since last coupon / days in period)\n\n"
              "Coupon > yield  ->  premium      Coupon < yield  ->  discount\n"
              "Discount bond:  coupon rate < current yield < YTM\n"
              "Premium bond:   coupon rate > current yield > YTM")

    d.h2("Term structure")
    d.formula("(1 + z_n)^n  =  (1 + z_m)^m  x  (1 + f)^(n-m)\n\n"
              "Quick check: the one-year forward one year out is approximately\n"
              "   2 x (two-year spot)  -  (one-year spot)")

    d.h2("Duration and convexity")
    d.formula("Modified duration  =  Macaulay duration / (1 + yield per period)\n\n"
              "% price change  =  (- mod duration x delta y)\n"
              "                   + (0.5 x convexity x (delta y)^2)\n\n"
              "Money duration  =  modified duration x full price\n"
              "PVBP            =  money duration x 0.0001\n\n"
              "Portfolio duration  =  sum of (market-value weight x duration)\n\n"
              "Effective duration  =  (PV_down - PV_up) / (2 x PV_0 x delta curve)\n"
              "Effective convexity =  (PV_down + PV_up - 2 PV_0) / (PV_0 x (delta curve)^2)")

    d.h2("Credit")
    d.formula("Expected loss  =  probability of default x loss given default\n"
              "Loss given default  =  exposure x (1 - recovery rate)\n"
              "Yield  =  risk-free rate + credit spread\n"
              "% price change from a spread move  =  - modified duration x delta spread\n\n"
              "Debt service coverage  =  net operating income / debt service\n"
              "Leverage  =  debt / EBITDA;   Coverage  =  EBIT / interest")

    d.h2("The things most often got wrong")
    d.bullets([
        "Price and yield always move in opposite directions. The minus sign is not optional.",
        "Duration is a sensitivity measure, not a time to maturity.",
        "Lower coupon and lower yield both LENGTHEN duration.",
        "A zero coupon bond's Macaulay duration equals its maturity exactly.",
        "Horizon = Macaulay duration is where price and reinvestment risk cancel.",
        "Convexity is always positive for a straight bond and beneficial to the holder.",
        "A callable bond has negative convexity at low yields; so does an MBS.",
        "Falling rates cause CONTRACTION risk in an MBS, not extension.",
        "Use effective duration whenever cash flows are uncertain, never modified duration.",
        "A floater's duration is roughly the time to the next reset.",
        "For a callable bond, OAS is less than the Z-spread.",
        "Tranching redistributes credit risk; it does not reduce it.",
        "EBITDA is not cash flow, and it flatters capital-intensive issuers.",
    ])
