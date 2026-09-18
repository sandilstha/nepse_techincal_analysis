"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 8 - Alternative Investments

Run:  venv/Scripts/python.exe docs/make_cfa_v8.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V8-Alternative-Investments-Summary.pdf")

MODULES = [
    (1, "Alternative Investment Features, Methods, and Structures", "What makes them different"),
    (2, "Alternative Investment Performance and Returns", "Fees, and why reported returns mislead"),
    (3, "Investments in Private Capital: Equity and Debt", "Private equity and private debt"),
    (4, "Real Estate and Infrastructure", "Property and long-lived public assets"),
    (5, "Natural Resources", "Commodities, timber and farmland"),
    (6, "Hedge Funds", "Strategies, and what the label actually means"),
    (7, "Introduction to Digital Assets", "Blockchain, tokens and the investment case"),
]

STANDFIRST = ("All seven learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Alternative Investments is the shortest technical volume and one of the most "
        "straightforward, provided you resist one temptation: accepting reported performance "
        "at face value.")
    d.numbered([
        "Modules 1 and 2 are the general framework: what counts as an alternative, how they "
        "are structured, how fees work, and why the reported returns and risks are "
        "systematically flattering.",
        "Modules 3 to 7 work through the categories one at a time: private capital, real "
        "assets, natural resources, hedge funds and digital assets.",
    ])
    d.p("Module 2 is worth more attention than its length suggests. The fee calculation "
        "appears on the exam almost every sitting, and the biases in reported returns are "
        "asked about repeatedly in conceptual questions across the whole volume.")
    d.key("The recurring theme: alternatives appear to offer higher returns with lower "
          "volatility and low correlation to equities. Much of that appearance is an artefact "
          "of how they are valued and reported. Infrequent, appraisal-based pricing smooths "
          "the series, and funds that fail stop reporting. Neither the volatility nor the "
          "correlation is as low as the data suggests.")
    d.warn("Illiquidity is the defining feature of most alternatives, and it cuts both ways. "
           "It may earn a genuine premium, because investors must be paid to give up access "
           "to their money. It also means you cannot exit when you want to, valuations are "
           "estimates rather than prices, and the reported risk is understated. Any answer "
           "that treats low reported volatility as low risk is wrong.")


def module1(d):
    d.h1(1, "Alternative Investment Features, Methods, and Structures",
         "What distinguishes an alternative investment from a traditional one, and the legal "
         "arrangements through which they are held.")

    d.h2("The common features")
    d.bullets([
        "Illiquidity, often with a lock-up period during which no withdrawal is possible.",
        "Limited regulation and disclosure compared with public markets.",
        "Complex, often leveraged structures.",
        "Specialised expertise required, and a wide dispersion of manager results.",
        "Valuation that is estimated rather than observed, and done infrequently.",
        "High fees, typically including a share of the profits.",
    ])
    d.key("The dispersion between the best and worst managers is far wider in alternatives "
          "than in public equities. In a traditional asset class, manager selection changes "
          "the result by a little; in private equity or hedge funds it can change it "
          "entirely. This is why due diligence occupies so much of the curriculum's attention "
          "here.")

    d.h2("Three ways to invest")
    make_table(d,
               ["Method", "Description", "Trade-off"],
               [["Fund investment", "Commit capital to a manager's pooled vehicle",
                 "Least work, least control, full fees"],
                ["Co-investment", "Invest alongside the fund in a specific deal",
                 "Lower fees and some control; requires capability to assess the deal"],
                ["Direct investment", "Buy the asset outright",
                 "No fees and full control; needs substantial in-house expertise"]],
               widths=(22, 38, 40))

    d.h2("The partnership structure")
    d.p("The standard vehicle is a limited partnership. The general partner manages the fund, "
        "makes the investment decisions, and bears unlimited liability. The limited partners "
        "supply the capital and have liability limited to their commitment, but no say in "
        "decisions.")
    d.p("Capital is not paid in at once. Limited partners make a commitment, and the general "
        "partner issues capital calls, or drawdowns, as investments are made. Money returns "
        "as distributions when investments are realised. The resulting pattern of negative "
        "then positive cash flows is called the J-curve: early fees and write-downs produce "
        "negative returns before the profitable exits arrive.")
    d.warn("Because capital is committed rather than invested, a return measured on committed "
           "capital and one measured on invested capital are very different numbers. The "
           "internal rate of return quoted by private funds is calculated on drawn capital "
           "and on the general partner's timing decisions, which is why it is not directly "
           "comparable with a public market return.")


def module2(d):
    d.h1(2, "Alternative Investment Performance and Returns",
         "The most examinable module in the volume. Fees are calculable, and the biases in "
         "reported returns are asked about constantly.")

    d.h2("The fee structure")
    d.formula("Management fee  =  a percentage of assets (or of committed capital)\n"
              "Incentive fee   =  a percentage of PROFITS\n\n"
              "The common arrangement, '2 and 20', means a 2% management fee\n"
              "and a 20% share of the profits.")
    make_table(d,
               ["Provision", "Effect"],
               [["Hurdle rate", "No incentive fee until the return exceeds a threshold"],
                ["Hard hurdle", "The incentive fee applies only to the return ABOVE the "
                 "hurdle"],
                ["Soft hurdle", "Once the hurdle is cleared, the fee applies to the ENTIRE "
                 "return"],
                ["High water mark", "No incentive fee until previous losses have been "
                 "recovered, so investors are not charged twice for the same gain"],
                ["Clawback", "Requires the manager to return incentive fees already paid if "
                 "later losses occur"]],
               widths=(24, 76))
    d.example("A fund begins the year with Rs 100m. It charges 2% of year-END assets and 20% "
              "of profits above a 5% HARD hurdle. Gross return is 25%.\n\n"
              "  Year-end gross value = 100 x 1.25 = Rs 125m\n"
              "  Management fee = 2% x 125 = Rs 2.5m\n"
              "  Gross profit = Rs 25m;  hurdle = 5% x 100 = Rs 5m\n"
              "  Incentive fee = 20% x (25 - 5) = 20% x 20 = Rs 4.0m\n\n"
              "  Total fees = Rs 6.5m\n"
              "  Investor's net value = 125 - 6.5 = Rs 118.5m\n"
              "  Net return = 18.5%\n\n"
              "The investor earned 18.5% of the 25% the fund produced. The manager took 6.5 "
              "percentage points, or 26% of the gross return.\n\n"
              "Had the hurdle been SOFT, the incentive fee would be 20% x 25 = Rs 5m, giving "
              "total fees of Rs 7.5m and a net return of 17.5%. One word in the term sheet is "
              "worth a full percentage point.")
    d.warn("Read the terms with great care, because each variation changes the arithmetic. "
           "Is the management fee on beginning or ending assets, and is it deducted before "
           "the incentive fee is computed? Is the hurdle hard or soft? Is there a high water "
           "mark, and where is it? Questions vary exactly these details.")
    d.key("A high water mark protects the investor from paying twice. If a fund gains 20%, "
          "loses 20%, then gains 20%, the investor is roughly back where they started, but "
          "without a high water mark the manager would have collected an incentive fee in "
          "both up years. With one, no fee is due in the third year until the previous peak "
          "is exceeded.")

    d.h2("Why reported returns mislead")
    d.bullets([
        "Survivorship bias: funds that fail close and leave the index, so the surviving "
        "average overstates the experience of an investor who picked at the start.",
        "Backfill bias: a fund joins a database and its past record is added retrospectively. "
        "Funds only do this when the record is good.",
        "Smoothing: infrequent, appraisal-based valuation dampens the reported series, "
        "understating volatility and correlation.",
        "Self-selection: reporting is voluntary, and poor performers stop.",
    ])
    d.key("Smoothing has a specific consequence worth stating precisely: it understates "
          "standard deviation, which INFLATES the Sharpe ratio, and it understates "
          "correlation with equities, which overstates the diversification benefit. The two "
          "headline attractions of alternatives are both partly measurement artefacts.")


def module3(d):
    d.h1(3, "Investments in Private Capital: Equity and Debt",
         "Financing companies outside the public markets, on both sides of the balance sheet.")

    d.h2("Private equity")
    make_table(d,
               ["Strategy", "Target", "Method"],
               [["Venture capital", "Early-stage companies", "Minority stakes, no leverage, "
                 "very high failure rate offset by rare large successes"],
                ["Growth equity", "Established but expanding companies",
                 "Minority stakes, modest or no leverage"],
                ["Leveraged buyout", "Mature, cash-generative companies",
                 "Control acquired using substantial debt"],
                ["Distressed", "Companies in or near default",
                 "Debt bought cheaply, often converted to control"]],
               widths=(22, 30, 48))
    d.p("A leveraged buyout creates value in three ways: improving the operations, reducing "
        "the debt with the company's own cash flow, and selling at a higher multiple than was "
        "paid. The curriculum expects all three to be named.")
    d.p("Exit routes are the trade sale to a strategic buyer, the secondary sale to another "
        "financial buyer, the initial public offering, and the recapitalisation, in which the "
        "company borrows to pay a dividend while the sponsor retains ownership.")
    d.warn("Leverage is what makes a buyout's equity returns large, and it is also what makes "
           "them fragile. A company bought at five times leverage that misses its plan can "
           "wipe out the equity entirely while the same business unleveraged would simply "
           "have had a poor year. Attributing buyout returns to operational skill alone "
           "ignores the mechanism actually producing most of them.")

    d.h2("Private debt")
    d.bullets([
        "Direct lending: loans made straight to mid-sized companies, usually floating rate "
        "and senior secured.",
        "Mezzanine debt: subordinated, often with equity warrants attached, higher yielding.",
        "Venture debt: lending to young companies that have equity backing but little cash "
        "flow.",
        "Distressed debt: buying the obligations of troubled companies at a discount.",
    ])
    d.key("Private debt's attraction over public bonds is a yield premium, tighter covenants "
          "and direct negotiation with the borrower. Its cost is illiquidity and the absence "
          "of a market price, so a deteriorating loan may be carried at par far longer than a "
          "traded bond would be.")


def module4(d):
    d.h1(4, "Real Estate and Infrastructure",
         "Long-lived physical assets producing contracted income, and the two ways of owning "
         "them.")

    d.h2("Real estate")
    make_table(d,
               ["", "Equity", "Debt"],
               [["Private", "Direct ownership of buildings; private funds",
                 "Mortgages, whole loans"],
                ["Public", "REITs and listed property companies",
                 "Mortgage-backed securities"]],
               widths=(16, 44, 40))
    d.p("Property is valued three ways. The income approach capitalises the net operating "
        "income. The cost approach asks what it would cost to rebuild. The comparable sales "
        "approach looks at what similar buildings fetched.")
    d.formula("Net operating income  =  rental income  -  operating expenses\n"
              "  (before financing costs and before tax)\n\n"
              "Capitalisation rate  =  NOI / property value\n\n"
              "Value  =  NOI / capitalisation rate")
    d.example("A building generates Rs 24m of rent and incurs Rs 7.5m of operating costs. "
              "Comparable buildings trade at a 7.5% capitalisation rate.\n\n"
              "  NOI = 24 - 7.5 = Rs 16.5m\n"
              "  Value = 16.5 / 0.075 = Rs 220m\n\n"
              "Note how sensitive this is. If capitalisation rates move to 8.5%, purely "
              "because interest rates rose and nothing about the building changed, the value "
              "falls to 16.5 / 0.085 = Rs 194m, a 12% loss with the tenants still in place "
              "paying the same rent.")
    d.key("The capitalisation rate is the property equivalent of the inverse of a P/E "
          "multiple, and it moves with interest rates. This is why property is far more "
          "rate-sensitive than its stable rental income suggests, and why the diversification "
          "benefit against bonds is weaker than it appears.")
    d.p("A REIT holds property in a listed vehicle and is generally required to distribute "
        "most of its income to avoid tax at the entity level. It offers liquidity and "
        "diversification, at the cost of correlating with the equity market in the short run "
        "far more closely than direct property does.")

    d.h2("Infrastructure")
    d.p("Roads, airports, utilities, pipelines, telecommunications towers. The appeal is long "
        "life, often regulated or contracted revenue, frequently inflation-linked, and low "
        "sensitivity to the economic cycle.")
    make_table(d,
               ["Category", "Meaning", "Risk"],
               [["Brownfield", "An existing, operating asset", "Lower; the cash flow exists"],
                ["Greenfield", "To be built", "Higher; construction and demand risk"]],
               widths=(22, 36, 42))
    d.warn("Infrastructure's dominant risk is regulatory and political, not operational. A "
           "regulated utility's returns are set by a regulator who can change them, and a "
           "concession can be renegotiated by a new government. Long contracted cash flows "
           "are only as good as the counterparty's willingness to honour them.")


def module5(d):
    d.h1(5, "Natural Resources",
         "Commodities, timberland and farmland: assets that are produced and consumed rather "
         "than held for a stream of income.")

    d.h2("Commodities")
    d.p("A commodity produces no cash flow. It has no dividend, no coupon and no earnings, "
        "which means it cannot be valued by discounting anything. Its return comes purely "
        "from the price and from the mechanics of holding a futures position.")
    d.formula("Total return on a commodity futures position\n"
              "     =  spot return  +  roll return  +  collateral return\n\n"
              "  Spot return: the change in the commodity's price\n"
              "  Roll return: gain or loss from rolling an expiring contract forward\n"
              "  Collateral return: interest on the cash backing the position")
    make_table(d,
               ["Curve shape", "Futures price", "Roll return"],
               [["Contango", "Above the spot price", "NEGATIVE: you sell the cheap near "
                 "contract and buy a dearer far one"],
                ["Backwardation", "Below the spot price", "POSITIVE: you sell the dearer near "
                 "contract and buy a cheaper far one"]],
               widths=(24, 26, 50))
    d.warn("Contango and backwardation are reversed by candidates constantly. Contango is the "
           "upward-sloping curve and produces a NEGATIVE roll return for a long investor. An "
           "index fund holding commodity futures in a persistently contangoed market can lose "
           "money over years while the spot price is unchanged, which is the single most "
           "practically important point in this module.")
    d.key("Commodities are held for two reasons that have nothing to do with expected return: "
          "they have historically provided an inflation hedge, because they are an input to "
          "the prices being measured, and their correlation with equities is low in normal "
          "conditions. Note the qualifier: correlations rise sharply in a crisis, when "
          "diversification is most wanted.")

    d.h2("Timberland and farmland")
    d.bullets([
        "Timberland returns come from biological growth, the change in timber prices, and the "
        "land value. Growth continues regardless of the market, and harvesting can be delayed "
        "if prices are poor, which is a valuable form of flexibility.",
        "Farmland returns come from the crop yield, commodity prices, and the land value. "
        "Income may come from farming directly or from renting the land out.",
        "Both are exposed to weather, disease and climate change, and both are highly "
        "illiquid with appraisal-based valuation.",
    ])


def module6(d):
    d.h1(6, "Hedge Funds",
         "A fee structure and a legal form rather than a strategy. The label says almost "
         "nothing about what the fund actually does.")

    d.h2("Common features")
    d.bullets([
        "Few restrictions on what may be held, including short positions and derivatives.",
        "Leverage, often substantial.",
        "Performance fees, typically with a high water mark.",
        "Lock-up periods, notice periods, and sometimes gates limiting withdrawals.",
        "Limited disclosure, and offered only to qualified investors.",
    ])

    d.h2("The strategy families")
    make_table(d,
               ["Family", "Approach"],
               [["Equity hedge", "Long and short equity positions. Includes long/short, "
                 "market neutral and dedicated short bias"],
                ["Event driven", "Positions around corporate events: merger arbitrage, "
                 "distressed securities, activist campaigns"],
                ["Relative value", "Exploiting price differences between related securities: "
                 "convertible arbitrage, fixed income arbitrage"],
                ["Macro and CTA", "Directional positions on rates, currencies, commodities "
                 "and indices, often systematic and trend-following"]],
               widths=(22, 78))
    d.key("Market neutral means the long and short exposures offset so that the fund's return "
          "does not depend on the market's direction. It does NOT mean low risk. Such funds "
          "typically use heavy leverage to make small spreads worthwhile, so a modest adverse "
          "move in the relationships they trade can produce a very large loss.")
    d.warn("Relative value strategies characteristically show long periods of small, steady "
           "gains punctuated by rare severe losses. The return distribution is negatively "
           "skewed with fat tails, which means standard deviation understates the risk and "
           "the Sharpe ratio flatters it. Do not assess these strategies on mean and variance "
           "alone; the curriculum is explicit about this.")

    d.h2("Fund of funds")
    d.p("A fund of hedge funds allocates across managers, offering diversification, access to "
        "funds that are closed, and professional due diligence. It charges a second layer of "
        "fees on top of the underlying managers', which is a substantial drag and the main "
        "argument against the structure.")


def module7(d):
    d.h1(7, "Introduction to Digital Assets",
         "The newest section of the curriculum, treated descriptively and with considerable "
         "caution.")

    d.h2("Distributed ledger technology")
    d.p("A blockchain is a shared record maintained across many computers rather than by one "
        "central authority. Entries are grouped into blocks, each cryptographically linked to "
        "the one before, which makes altering history impracticable. Participants agree on "
        "the state of the ledger through a consensus mechanism.")
    d.bullets([
        "Proof of work: participants compete to solve a computational puzzle. Secure, and "
        "extremely energy-intensive.",
        "Proof of stake: the right to validate is allocated in proportion to holdings pledged "
        "as security. Far less energy-intensive.",
        "Permissionless: anyone may participate. Permissioned: participation is restricted, "
        "which suits enterprise uses.",
    ])
    d.p("A smart contract is code stored on the ledger that executes automatically when "
        "conditions are met, removing the need for an intermediary to enforce the agreement.")

    d.h2("The asset types")
    make_table(d,
               ["Type", "Description"],
               [["Cryptocurrency", "Intended as a medium of exchange or store of value"],
                ["Stablecoin", "Pegged to a currency or asset, typically by holding reserves"],
                ["Non-fungible token", "A unique record of ownership of a specific item"],
                ["Security token", "A traditional security represented on a ledger"],
                ["Utility token", "Access to a particular service or network"],
                ["Central bank digital currency", "A digital form of sovereign money"]],
               widths=(28, 72))
    d.key("The valuation difficulty is fundamental, not merely practical. A cryptocurrency "
          "produces no cash flow, so there is nothing to discount, and unlike a commodity it "
          "has no industrial use establishing a floor. Value rests entirely on what the next "
          "buyer will pay, which is why the curriculum discusses these assets descriptively "
          "and offers no valuation model.")
    d.warn("The claimed diversification benefit is weaker than early data suggested. "
           "Correlation with risk assets has risen substantially as institutional ownership "
           "has grown, and it tends to rise further in stressed conditions. Add extreme "
           "volatility, evolving and inconsistent regulation, custody and operational risk, "
           "and thin liquidity in stress, and the case for a material allocation is not one "
           "the curriculum makes.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place. There are few formulas "
        "here, which means the ones that exist are almost certain to be examined.")

    d.h2("Fees")
    d.formula("Management fee  =  rate x assets  (check: beginning or ending?)\n"
              "Incentive fee   =  rate x profit above the hurdle\n\n"
              "HARD hurdle:  fee applies only to the return ABOVE the hurdle\n"
              "SOFT hurdle:  once cleared, fee applies to the ENTIRE return\n\n"
              "High water mark: no incentive fee until the previous peak is exceeded\n"
              "Clawback: previously paid incentive fees may be reclaimed")

    d.h2("Real estate")
    d.formula("NOI  =  rental income - operating expenses\n"
              "        (before financing and before tax)\n\n"
              "Capitalisation rate  =  NOI / value\n"
              "Value                =  NOI / capitalisation rate")

    d.h2("Commodities")
    d.formula("Total return  =  spot return + roll return + collateral return\n\n"
              "CONTANGO:       futures above spot   ->  NEGATIVE roll return\n"
              "BACKWARDATION:  futures below spot   ->  POSITIVE roll return")

    d.h2("The things most often got wrong")
    d.bullets([
        "Contango gives a NEGATIVE roll return to a long investor.",
        "A soft hurdle charges the fee on the entire return once cleared, not just the excess.",
        "A margin call on a fee question is not the issue; read whether the management fee "
        "is on beginning or ending assets.",
        "Market neutral does not mean low risk; leverage makes it otherwise.",
        "Smoothed valuations understate volatility, inflating the Sharpe ratio.",
        "Survivorship and backfill bias both flatter reported index returns.",
        "Low reported correlation rises sharply in a crisis, exactly when it matters.",
        "A commodity and a cryptocurrency both produce no cash flow, so neither can be "
        "valued by discounting.",
    ])


def build():
    d = Guide(volume=8, subject="Alternative Investments")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5, module6, module7):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
