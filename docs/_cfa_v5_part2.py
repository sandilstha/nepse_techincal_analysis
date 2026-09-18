"""Volume 5, modules 6 to 11 and the formula sheet. Imported by make_cfa_v5.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module6(d):
    d.h1(6, "Discounted Cash Flow (DCF) and Growth Models",
         "The heart of the volume. A share is worth the present value of what it will pay "
         "you, and everything here is a way of making that statement operational.")

    d.h2("The dividend discount model")
    d.formula("V0  =  sum of  D_t / (1 + r)^t\n\n"
              "  D_t = the dividend in year t\n"
              "  r   = the required return on equity, usually from the CAPM",
              "The general form. In practice nobody forecasts dividends forever, so a growth "
              "assumption is imposed after a few years.")

    d.h3("The Gordon growth model")
    d.formula("V0  =  D1 / (r - g)\n\n"
              "  D1 = next year's dividend  =  D0 x (1 + g)\n"
              "  g  = the constant growth rate, forever\n\n"
              "Requires g < r, strictly.")
    d.example("A company just paid a dividend of Rs 8. Dividends are expected to grow at 5% "
              "forever, and the required return is 13%.\n\n"
              "  D1 = 8 x 1.05 = Rs 8.40\n"
              "  V0 = 8.40 / (0.13 - 0.05) = 8.40 / 0.08 = Rs 105.00\n\n"
              "Now change growth to 6%, a single percentage point:\n"
              "  V0 = 8.48 / 0.07 = Rs 121.14, a rise of 15%\n\n"
              "The model is extraordinarily sensitive to the denominator, because the two "
              "numbers being subtracted are close together. This sensitivity is not a bug to "
              "be hidden; it is the reason every DCF should be presented as a range.")
    d.warn("If g is greater than or equal to r the model returns a negative or infinite "
           "value, which is meaningless rather than merely wrong. No company can grow faster "
           "than its required return forever, because it would eventually exceed the size of "
           "the economy. If a question produces g > r, the intended answer is that the model "
           "cannot be applied.")
    d.formula("Sustainable growth rate  =  b  x  ROE\n\n"
              "  b = the retention ratio  =  1 - payout ratio",
              "This is where g comes from. A company grows by retaining earnings and earning "
              "a return on them; it cannot grow faster than that without raising new capital.")
    d.example("A company earns an ROE of 15% and pays out 40% of its earnings.\n\n"
              "  Retention ratio b = 1 - 0.40 = 0.60\n"
              "  g = 0.60 x 0.15 = 9.0%\n\n"
              "If it paid out 70% instead, g would fall to 0.30 x 0.15 = 4.5%. The trade-off "
              "is explicit: a higher dividend today buys slower growth in every year after.")

    d.h2("Multistage models")
    d.p("Few companies grow at one constant rate. A two-stage model forecasts a high growth "
        "period explicitly, then applies the Gordon formula to a mature terminal rate. The "
        "terminal value is discounted back along with the individual dividends.")
    d.formula("Terminal value at year n  =  D_(n+1) / (r - g_long)\n\n"
              "V0  =  sum of the explicit dividends discounted\n"
              "      +  TV_n / (1 + r)^n",
              "The terminal value is calculated as at year n and must then be discounted back "
              "n years, not n+1.")
    d.warn("The terminal value routinely accounts for 60% to 80% of a DCF result, which means "
           "the answer is mostly driven by an assumption about the distant future rather than "
           "by the detailed forecast. Sanity-check the terminal growth rate against long-run "
           "nominal GDP growth. Anything materially above it is untenable.")

    d.h2("Free cash flow models")
    d.p("Many companies pay no dividend, which makes the dividend discount model unusable. "
        "Free cash flow models value the cash a company COULD distribute.")
    make_table(d,
               ["Model", "Discount at", "Gives"],
               [["FCFE", "Cost of equity", "The value of the equity directly"],
                ["FCFF", "WACC", "The value of the whole firm; subtract debt for equity"]],
               widths=(18, 30, 52))
    d.key("Use a dividend model when dividends are stable and reflect earning power. Use FCFE "
          "when they do not, or when there are none. Use FCFF when the capital structure is "
          "changing or leverage is high, because the WACC handles the changing mix more "
          "gracefully than a cost of equity that must be re-levered every year.")


def module7(d):
    d.h1(7, "Relative Value Equity Valuation Approaches",
         "Valuation by comparison. Faster than a DCF, easier to get wrong, and far more "
         "widely used in practice.")

    d.h2("The main multiples")
    make_table(d,
               ["Multiple", "Definition", "Suits"],
               [["P/E", "Price / earnings per share", "Profitable, stable companies"],
                ["P/B", "Price / book value per share", "Banks and asset-heavy firms"],
                ["P/S", "Price / sales per share", "Loss-making or cyclical firms"],
                ["P/CF", "Price / cash flow per share",
                 "Where earnings quality is doubtful"],
                ["EV/EBITDA", "Enterprise value / EBITDA",
                 "Comparing across different capital structures"]],
               widths=(18, 34, 48))
    d.p("A trailing multiple uses the last twelve months of reported results; a forward "
        "multiple uses the next twelve months of forecasts. Forward multiples are more "
        "relevant to a valuation and more prone to forecast error.")

    d.h2("The justified P/E")
    d.p("A multiple can be derived from the Gordon growth model rather than taken from "
        "comparables, which turns it from a comparison into a valuation.")
    d.formula("Justified leading P/E   =  payout ratio / (r - g)\n\n"
              "Justified trailing P/E  =  payout ratio x (1 + g) / (r - g)",
              "Leading uses next year's earnings, trailing uses last year's. The difference "
              "is one factor of (1 + g).")
    d.example("A company pays out 45% of earnings, requires a 12% return, and grows at 5%.\n\n"
              "  Justified leading P/E = 0.45 / (0.12 - 0.05) = 0.45 / 0.07 = 6.4x\n\n"
              "If the share actually trades at 11x forward earnings, the market is not using "
              "your assumptions. Solve for the growth the market must be assuming:\n\n"
              "  11 = 0.45 / (0.12 - g)   so   0.12 - g = 0.0409   and   g = 7.9%\n\n"
              "This is far more useful than arguing about whether 11x is 'expensive'. It "
              "converts the price into a testable statement: does 7.9% growth forever look "
              "plausible for this business?")
    d.key("Three things raise a justified P/E: higher growth, lower required return, and a "
          "higher payout. But growth and payout pull against each other through the "
          "sustainable growth relationship, so a company cannot simply raise both. Any "
          "question offering that as an option is testing whether you noticed.")

    d.h2("Using comparables properly")
    d.numbered([
        "Choose genuine peers: the same industry, similar size, similar growth, similar risk "
        "and similar capital structure.",
        "Use the same definition for every company. A P/E built on adjusted earnings for one "
        "and reported earnings for another compares nothing.",
        "Prefer the median to the mean, because one extreme multiple distorts an average.",
        "Explain the differences rather than assuming they are errors. A company trading "
        "below its peers may deserve to.",
    ])
    d.warn("The fundamental weakness of relative valuation is that it is only relative. If "
           "the entire sector is overvalued, a company that is cheap against its peers is "
           "still overvalued in absolute terms. Relative and absolute methods answer "
           "different questions, and a good analysis uses both.")
    d.p("Two mechanical traps recur. A P/E on negative earnings is meaningless, not "
        "negative, which is why P/S is used for loss-making firms. And EV/EBITDA is the right "
        "multiple when capital structures differ, because EBITDA is measured before interest "
        "and EV includes the debt, so both sides of the ratio are consistent.")


def module8(d):
    d.h1(8, "Financial Statement Forecasting in Equity Valuation",
         "Volume 4's analysis pointed backwards. Here the same machinery is pointed forwards, "
         "because every model in Module 6 needs numbers that do not exist yet.")

    d.h2("The order of the forecast")
    d.numbered([
        "Revenue. Build it from volume and price, or from market size multiplied by expected "
        "share. A single growth percentage is an assumption disguised as an answer.",
        "Operating margin, separating fixed costs from variable, because operating leverage "
        "means margins move more than revenue does.",
        "Working capital, driven off the revenue forecast using the turnover ratios.",
        "Capital expenditure, split between maintenance and growth, and the depreciation "
        "that follows from it.",
        "Capital structure, interest and the share count.",
    ])
    d.key("Operating leverage is the idea that ties the first two steps together. When fixed "
          "costs are a large share of the total, a small change in revenue produces a large "
          "change in operating profit, in both directions. A forecast that moves margin in "
          "lockstep with revenue has not understood the cost structure.")

    d.h2("Where forecasts go wrong")
    d.bullets([
        "Straight-line extrapolation of a cyclical business at the top of its cycle.",
        "Holding a high margin flat for a decade without saying what prevents competition.",
        "Forgetting that growth consumes cash: more revenue needs more working capital and "
        "usually more capacity.",
        "Terminal growth above long-run nominal GDP.",
        "Anchoring on the consensus forecast and adjusting only slightly from it.",
    ])
    d.warn("A forecast is not a single number. Build a base case, an upside and a downside, "
           "and state which assumption moves the valuation most. If a one-point change in "
           "terminal growth moves the answer by 20%, that fact belongs in the conclusion, not "
           "buried in the spreadsheet.")

    d.h2("Scenario and sensitivity")
    d.p("Sensitivity analysis changes one variable at a time to see how much the answer "
        "moves. Scenario analysis changes a coherent set of variables together, because in a "
        "recession revenue, margin and the discount rate all move at once rather than "
        "independently.")


def module9(d):
    d.h1(9, "Industry and Competitive Analysis",
         "You cannot value a company without understanding the industry it competes in, "
         "because the industry sets the ceiling on what any participant can earn.")

    d.h2("Defining the industry")
    d.p("Classify by what a company does, not by what it is called. The standard approach "
        "groups by principal business activity, using published classification systems, but "
        "the analyst must check that the peer group actually competes for the same customers. "
        "A useful cross-check is whether the companies' results move together.")

    d.h2("The five forces")
    make_table(d,
               ["Force", "Strong when"],
               [["Threat of new entrants", "Barriers are low: little capital needed, no "
                 "regulation, no brand loyalty"],
                ["Bargaining power of suppliers", "Few suppliers, unique inputs, high "
                 "switching costs"],
                ["Bargaining power of buyers", "Few large buyers, undifferentiated product, "
                 "easy to switch"],
                ["Threat of substitutes", "Alternatives meet the same need acceptably"],
                ["Rivalry among existing firms", "Many similar competitors, slow growth, "
                 "high fixed costs, high exit barriers"]],
               widths=(30, 70))
    d.key("The five forces determine industry profitability, and industry profitability sets "
          "the range within which any single company's returns will sit. A superb operator in "
          "a terrible industry usually earns less than a mediocre one in a good industry, "
          "which is why the industry analysis comes before the company analysis.")

    d.h2("The industry life cycle")
    make_table(d,
               ["Stage", "Growth", "Profitability", "Competition"],
               [["Embryonic", "Slow, from a tiny base", "Negative", "Little"],
                ["Growth", "Rapid", "Improving", "Rising but tolerable"],
                ["Shakeout", "Slowing", "Falling", "Intense; weaker firms exit"],
                ["Mature", "In line with the economy", "Stable, defended", "Stable, often "
                 "consolidated"],
                ["Decline", "Negative", "Deteriorating", "Price-driven"]],
               widths=(20, 26, 26, 28))
    d.warn("Do not assume the growth stage is the most profitable one to invest in. Growth "
           "stages attract capital and competition, and many entrants do not survive the "
           "shakeout. Mature, consolidated industries frequently offer better risk-adjusted "
           "returns, which is the opposite of the intuitive answer.")

    d.h2("External influences")
    d.p("The curriculum uses the acronym PESTLE: political, economic, social, technological, "
        "legal and environmental. Technology is the one most often decisive, because it can "
        "dissolve an entire industry's barriers to entry within a few years.")


def module10(d):
    d.h1(10, "Company Analysis: Past, Present, and Future",
         "Having judged the industry, judge the company within it: what it does, how well it "
         "does it, and whether the advantage will last.")

    d.h2("The elements")
    d.numbered([
        "The business model: what it sells, to whom, and how it makes money. Volume 3, "
        "Module 7 is the reference.",
        "The competitive position: cost leadership, differentiation, or focus on a niche.",
        "The financial performance: growth, margins, returns and the balance sheet, using "
        "Volume 4's ratios.",
        "The outlook: whether the position is defensible and what would break it.",
    ])
    d.p("Porter's three generic strategies give the vocabulary. Cost leadership means being "
        "the low-cost producer and competing on price. Differentiation means offering "
        "something customers will pay more for. Focus means doing either of those for a "
        "narrow segment rather than the whole market.")
    d.warn("A company attempting both cost leadership and differentiation across the whole "
           "market is described as 'stuck in the middle', and the curriculum treats that as a "
           "weak position: too expensive to win on price and too undifferentiated to command "
           "a premium.")

    d.h2("Judging the numbers")
    d.p("Growth alone proves nothing. A company growing revenue rapidly while its returns on "
        "capital fall below its cost of capital is destroying value at increasing speed. The "
        "combination to look for is growth ACCOMPANIED by returns above the cost of capital, "
        "and a credible reason why competition has not already eliminated it.")
    d.key("Look for the source of the advantage, not the evidence of it. High margins are "
          "evidence; a patent, a network effect, a regulatory licence, a genuinely lower cost "
          "position or high switching costs are sources. Evidence without an identifiable "
          "source usually means the advantage is temporary.")

    d.h2("Quality of management")
    d.p("Assess the capital allocation record above all else: what management did with the "
        "cash it generated, whether acquisitions earned their cost of capital, and whether "
        "buybacks were made at sensible prices. Look also at incentive alignment, the "
        "candour of past disclosures, and whether previous guidance was met.")


def module11(d):
    d.h1(11, "Equity Analyst Research Reports",
         "The output. A valuation nobody can follow is worth nothing, and the curriculum is "
         "specific about what a report must contain.")

    d.h2("What a report should contain")
    d.bullets([
        "The recommendation and the target price, stated up front.",
        "The investment thesis in a few sentences: why the market is wrong.",
        "The business description and industry context.",
        "The valuation, with the method stated and the key assumptions visible.",
        "The risks: what would make the thesis fail, specifically.",
        "Disclosures of any conflict of interest.",
    ])
    d.key("The single most important element is the explicit assumption set. A reader must be "
          "able to disagree with one input, change it, and see what happens to the "
          "conclusion. A report that hides its assumptions cannot be argued with, and is "
          "therefore useless as analysis however good the conclusion happens to be.")

    d.h2("Common failings")
    d.numbered([
        "A conclusion reached first and evidence assembled afterwards.",
        "A target price with no stated horizon.",
        "Risks listed generically, so that they apply to any company in any industry.",
        "Precision that the inputs do not support: a target of Rs 247.63 implies a "
        "confidence no DCF can deliver.",
        "No discussion of what the market is currently assuming.",
    ])
    d.warn("Ethics applies directly here, and Volume 10 will examine it. Standard V requires "
           "a reasonable and adequate basis for any recommendation, the distinction between "
           "fact and opinion, and disclosure of the basic format and general principles of "
           "the process used. A research report is the most common setting for those "
           "questions.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place.")

    d.h2("Returns and trading")
    d.formula("Holding period return  =  (P1 - P0 + D1) / P0\n"
              "Leverage ratio         =  1 / initial margin requirement\n"
              "Margin call price      =  P0 x (1 - initial margin) / (1 - maint. margin)")

    d.h2("Discounted cash flow")
    d.formula("Gordon growth:  V0  =  D1 / (r - g)      where  D1 = D0 x (1 + g)\n"
              "                Requires g < r, strictly\n\n"
              "Sustainable growth:  g  =  b x ROE       where  b = 1 - payout\n\n"
              "Terminal value at year n  =  D_(n+1) / (r - g_long)\n"
              "  then discount back n years, not n+1\n\n"
              "Preferred share value  =  D / r          (no growth)")

    d.h2("Relative value")
    d.formula("Justified leading P/E   =  payout / (r - g)\n"
              "Justified trailing P/E  =  payout x (1 + g) / (r - g)\n\n"
              "Enterprise value  =  market cap + debt + preferred + NCI - cash\n"
              "EV/EBITDA is the multiple to use when capital structures differ")

    d.h2("Matching cash flow to discount rate")
    d.formula("Dividends  ->  cost of equity  ->  value of EQUITY\n"
              "FCFE       ->  cost of equity  ->  value of EQUITY\n"
              "FCFF       ->  WACC            ->  value of the FIRM\n"
              "                                   then subtract debt for equity")

    d.h2("The things most often got wrong")
    d.bullets([
        "Gordon growth uses NEXT year's dividend, D1, not the one just paid.",
        "If g is greater than or equal to r, the model cannot be used at all.",
        "A terminal value must be discounted back n years, not n+1.",
        "Cumulative voting protects minorities; statutory voting does not.",
        "A stock split or stock dividend changes nothing of substance.",
        "FCFF discounted at the WACC gives the FIRM, not the equity.",
        "A P/E on negative earnings is meaningless, not negative.",
        "Growth and payout cannot both be raised freely; g = b x ROE links them.",
    ])
