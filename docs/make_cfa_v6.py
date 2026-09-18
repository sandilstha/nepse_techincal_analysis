"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 6 - Fixed Income

Run:  venv/Scripts/python.exe docs/make_cfa_v6.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402
from _cfa_v6_part2 import (module6, module7, module8, module9, module10,
                           module11, module12, module13)   # noqa: E402
from _cfa_v6_part3 import (module14, module15, module16, module17, module18,
                           module19, appendix)   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V6-Fixed-Income-Summary.pdf")

MODULES = [
    (1, "Fixed-Income Instrument Features", "What a bond promises"),
    (2, "Fixed-Income Cash Flows and Types", "Amortising, floating, and the rest"),
    (3, "Fixed-Income Issuance and Trading", "Primary and secondary markets"),
    (4, "Fixed-Income Markets for Corporate Issuers", "How companies borrow"),
    (5, "Fixed-Income Markets for Government Issuers", "How states borrow"),
    (6, "Bond Valuation: Prices and Yields", "Discounting the promised cash flows"),
    (7, "Yield and Yield Spread Measures for Fixed-Rate Bonds", "YTM and the spreads"),
    (8, "Yield and Yield Spread Measures for Floating-Rate Instruments", "Quoted margins"),
    (9, "The Term Structure of Interest Rates", "Spot, par and forward curves"),
    (10, "Interest Rate Risk and Return", "Price risk against reinvestment risk"),
    (11, "Yield-Based Bond Duration Measures and Properties", "Measuring sensitivity"),
    (12, "Yield-Based Bond Convexity and Portfolio Properties", "The second-order correction"),
    (13, "Curve-Based and Empirical Fixed-Income Risk Measures", "Effective duration"),
    (14, "Credit Risk", "The chance of not being paid"),
    (15, "Credit Analysis for Government Issuers", "Sovereign and municipal"),
    (16, "Credit Analysis for Corporate Issuers", "The four Cs and the ratios"),
    (17, "Fixed-Income Securitization", "Turning loans into securities"),
    (18, "Asset-Backed Security Features", "Structures and credit enhancement"),
    (19, "Mortgage-Backed Security Features", "Prepayment risk and tranching"),
]

STANDFIRST = ("All nineteen learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("This is the longest volume in the curriculum, but it is far more repetitive than its "
        "length suggests. Nearly everything follows from one relationship, stated in Module 6 "
        "and then examined from nineteen angles.")
    d.numbered([
        "Modules 1 to 5 are institutional background: what bonds are and who issues them. "
        "Read them once, carefully, and move on.",
        "Modules 6 to 9 are valuation: price, yield, spreads and the yield curve. This is the "
        "foundation and it must be solid.",
        "Modules 10 to 13 are interest rate risk: duration and convexity. Along with Module "
        "6 this carries most of the calculation marks in the volume.",
        "Modules 14 to 16 are credit: the risk that you are not paid at all.",
        "Modules 17 to 19 are securitisation: pooling loans and slicing the result.",
    ])
    d.key("The one relationship that generates the whole volume: price and yield move in "
          "OPPOSITE directions. A bond's promised payments are fixed, so if the market "
          "demands a higher return, the only thing that can adjust is the price. Every "
          "duration, convexity and spread measure in Modules 10 to 13 is a way of quantifying "
          "how much the price moves when the yield does.")
    d.warn("Be careful with the word 'yield'. Current yield, yield to maturity, yield to "
           "call, yield to worst, discount margin and the various spreads are all different "
           "numbers measuring different things, and questions frequently give you one and ask "
           "for another. Read which one is being requested before you start.")


def module1(d):
    d.h1(1, "Fixed-Income Instrument Features",
         "A bond is a contractual loan with the terms written down. Those terms are the "
         "entire subject of this module.")

    d.h2("The basic terms")
    make_table(d,
               ["Term", "Meaning"],
               [["Issuer", "The borrower: a government, a company, a special vehicle"],
                ["Par or face value", "The amount repaid at maturity"],
                ["Coupon rate", "The stated interest rate, applied to par"],
                ["Maturity", "When the principal is repaid"],
                ["Currency", "The currency of the payments, which may not be the issuer's own"],
                ["Seniority", "Where the holder ranks if the issuer fails"]],
               widths=(24, 76))
    d.p("The indenture, or trust deed, is the legal contract setting all of this out, along "
        "with the covenants. Affirmative covenants require the issuer to do things: maintain "
        "the assets, supply audited accounts, keep ratios within limits. Negative covenants "
        "forbid things: further borrowing beyond a level, selling key assets, paying "
        "excessive dividends.")
    d.key("Covenants exist because of the lender-shareholder conflict from Volume 3. Once the "
          "money is lent, the shareholders' incentive is to take more risk with it, and the "
          "lender's only protection is what was written down beforehand. A bond with weak "
          "covenants must pay a higher yield to compensate.")

    d.h2("Where the bond sits in the queue")
    d.p("Secured debt is backed by identified collateral and is paid from it first. Unsecured "
        "debt ranks by seniority: senior, then subordinated, then junior subordinated. Equity "
        "is behind all of it. The same issuer can have bonds at several points in this queue, "
        "and they will trade at different yields for that reason alone.")

    d.h2("Embedded options")
    make_table(d,
               ["Option", "Held by", "Effect on value to the investor"],
               [["Call", "The ISSUER, who may redeem early", "Negative; investor demands a "
                 "higher yield"],
                ["Put", "The INVESTOR, who may demand repayment", "Positive; investor "
                 "accepts a lower yield"],
                ["Conversion", "The INVESTOR, who may convert to shares", "Positive"]],
               widths=(18, 34, 48))
    d.warn("Work out who holds the option and the pricing follows automatically. An issuer "
           "calls when rates have FALLEN, which is exactly when the investor least wants the "
           "money back, so a callable bond must yield more than an otherwise identical "
           "straight bond. A putable bond protects the investor and therefore yields less.")


def module2(d):
    d.h1(2, "Fixed-Income Cash Flows and Types",
         "Not every bond pays a coupon twice a year and the principal at the end. This module "
         "catalogues the alternatives.")

    d.h2("Principal repayment structures")
    make_table(d,
               ["Structure", "How the principal is repaid"],
               [["Bullet", "Entirely at maturity. The standard case"],
                ["Amortising", "In instalments over the life, alongside the interest"],
                ["Partially amortising", "Instalments plus a large balloon payment at the end"],
                ["Sinking fund", "The issuer retires a portion each year, reducing the "
                 "amount outstanding at maturity"]],
               widths=(24, 76))
    d.key("An amortising bond is safer for the lender than a bullet of the same size and "
          "maturity, because the principal is returned gradually rather than depending on the "
          "issuer's condition on one distant day. It also has a shorter duration, for the "
          "same reason, which matters from Module 11 onward.")

    d.h2("Coupon structures")
    d.bullets([
        "Fixed rate: the same coupon throughout.",
        "Floating rate: a reference rate plus a fixed quoted margin, reset periodically.",
        "Zero coupon: no coupons at all, issued at a deep discount to par.",
        "Step-up: the coupon rises on a set schedule, often linked to a rating downgrade.",
        "Deferred coupon: no payments for an initial period, then a higher rate.",
        "Payment-in-kind: the issuer may pay in more bonds rather than in cash. A sign of a "
        "stressed borrower.",
        "Index-linked: principal, coupon or both adjust with an inflation index.",
    ])
    d.warn("A floating-rate note has very little interest rate risk, because the coupon "
           "resets to the market. But it has full CREDIT risk, because the quoted margin is "
           "fixed at issue. If the issuer deteriorates, the market demands a wider margin than "
           "the note pays, and the price falls. Floating rate does not mean price-stable.")


def module3(d):
    d.h1(3, "Fixed-Income Issuance and Trading",
         "How bonds are brought to market and where they change hands afterwards.")

    d.h2("The primary market")
    d.bullets([
        "Underwritten offering: an investment bank buys the issue and resells it, bearing "
        "the risk.",
        "Best efforts: the bank distributes without guaranteeing the outcome.",
        "Auction: used by governments. Bids are submitted and filled from the best price "
        "down, with a single price typically paid by all successful bidders.",
        "Shelf registration: the issuer registers once and issues in tranches when "
        "conditions suit.",
        "Private placement: sold directly to institutional investors without a public "
        "offering.",
    ])

    d.h2("The secondary market")
    d.p("Most bond trading is over the counter, negotiated with dealers rather than matched "
        "on an exchange. The consequences matter: liquidity is far lower than for equities, "
        "bid-ask spreads are wider, prices are less transparent, and many bonds do not trade "
        "at all on a given day.")
    d.key("The vast majority of a bond's life is spent not trading. That is why valuation in "
          "Module 6 is done by discounting contractual cash flows rather than by observing a "
          "price, and why matrix pricing exists: estimating the yield of an untraded bond "
          "from those of similar traded ones.")
    d.p("Settlement is typically the trade date plus one day for government bonds and plus "
        "two for corporates, though conventions vary by market.")


def module4(d):
    d.h1(4, "Fixed-Income Markets for Corporate Issuers",
         "The range of instruments a company uses to borrow, from overnight to thirty years.")

    d.h2("Short-term funding")
    make_table(d,
               ["Instrument", "Description"],
               [["Commercial paper", "Unsecured short-term notes, usually under 270 days, "
                 "issued by high-quality borrowers at a discount"],
                ["Bank line of credit", "A committed or uncommitted facility to draw on"],
                ["Repurchase agreement", "Selling a security with an agreement to buy it "
                 "back. Economically a secured loan"]],
               widths=(26, 74))
    d.p("A repo's interest is the difference between the sale and repurchase prices, and the "
        "lender protects itself with a haircut: lending less than the collateral is worth. "
        "The repo rate is lower when the collateral is high quality, the term is short, and "
        "the collateral is in demand.")
    d.warn("Commercial paper carries rollover risk. It matures constantly and must be "
           "refinanced, so a borrower who loses market access can face an immediate funding "
           "crisis despite being solvent. This is why issuers back their programmes with "
           "committed bank lines.")

    d.h2("Longer-term funding")
    d.p("Corporate bonds are issued in the domestic market, in a foreign market, or in the "
        "eurobond market, which is issued outside the jurisdiction of any single country and "
        "is typically less regulated. Medium-term note programmes allow continuous issuance "
        "in varying sizes and maturities.")
    d.p("Syndicated bank loans sit alongside bonds: several banks lend together, usually at a "
        "floating rate, with tighter covenants and more ability to renegotiate than a bond "
        "held by dispersed investors.")


def module5(d):
    d.h1(5, "Fixed-Income Markets for Government Issuers",
         "Sovereigns, agencies and local authorities, and why the sovereign sets the floor "
         "for everything else.")

    d.h2("Sovereign debt")
    d.p("A government borrowing in its OWN currency is in a materially different position "
        "from one borrowing in a foreign currency, because it controls the currency in which "
        "the debt is denominated. Default in the local currency is therefore a policy "
        "decision rather than an inability to pay; default in a foreign currency can be "
        "forced by running out of reserves.")
    d.key("This distinction explains why a sovereign's local currency rating is usually "
          "higher than its foreign currency rating, and why the local currency sovereign "
          "yield is treated as the risk-free benchmark for that market. Every other yield in "
          "the market is quoted as a spread over it.")
    d.p("Instruments run from Treasury bills, issued at a discount with no coupon and a "
        "maturity under a year, through notes and bonds to inflation-linked issues where the "
        "principal is indexed to consumer prices.")

    d.h2("Non-sovereign and supranational")
    d.bullets([
        "Agency and quasi-government bonds: issued by entities with explicit or implicit "
        "state support, yielding slightly more than the sovereign.",
        "Municipal and local authority bonds: backed either by the general taxing power of "
        "the issuer or by the revenue of a specific project. The second is riskier, because "
        "it depends on that project performing.",
        "Supranational bonds: issued by bodies such as the World Bank, backed by member "
        "states and typically very highly rated.",
    ])


def build():
    d = Guide(volume=6, subject="Fixed Income")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5,
               module6, module7, module8, module9, module10, module11, module12,
               module13, module14, module15, module16, module17, module18, module19):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
