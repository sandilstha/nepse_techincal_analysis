"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 1 - Quantitative Methods

Modules 1-5 live here; 6-11 and the formula appendix are in _cfa_v1_part2.py.

Run:  venv/Scripts/python.exe docs/make_cfa_v1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V1-Quantitative-Methods-Summary.pdf")

MODULES = [
    (1, "Returns of Financial Assets and Instruments", "What a return is, and what return you should demand"),
    (2, "Types of Financial Returns", "Price and income, averaging, annualising, real and leveraged"),
    (3, "Benchmarking Returns", "Money- vs time-weighted, and how an index is built"),
    (4, "The Time Value of Money in Finance", "Valuing cash flows, implied returns, no arbitrage"),
    (5, "Statistical Characteristics of Asset Returns", "Centre, spread, shape, and how two assets move together"),
    (6, "Statistical Distributions for Prices and Returns", "Moments, the key distributions, conditional thinking, Bayes"),
    (7, "Estimation and Hypothesis Testing", "Samples, confidence intervals, and testing a claim"),
    (8, "The Return and Risk of a Financial Portfolio", "Portfolio maths, the efficient frontier, the CAL and CML"),
    (9, "Simulation of Asset Prices and Returns", "Historical simulation, bootstrapping, Monte Carlo"),
    (10, "Applications of Simple Linear Regression", "Fitting a line, testing it, and using it to predict"),
    (11, "Introduction to Financial Data Science", "Big data, machine learning and AI in investing"),
]

STANDFIRST = ("All eleven learning modules explained in everyday English, with the formulas "
              "you must memorise, worked examples in the style of the curriculum, and the "
              "traps that catch candidates in the exam.")


# ======================================================================
def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Eleven modules, but only five ideas. Read it in order the first time.")
    d.p("Quantitative Methods looks like a pile of unrelated maths. It is not. It is five "
        "questions asked in sequence, and once you can see them the volume becomes much "
        "easier to hold in your head:")
    d.numbered([
        "Modules 1 to 3 ask: what exactly is a return, and did I measure it correctly? "
        "This sounds trivial and is not. Most of the marks here come from choosing the "
        "right kind of average and the right kind of weighting.",
        "Module 4 asks: what is a stream of future cash worth today? This is the engine "
        "underneath every valuation you will meet in Volumes 5 and 6, so it repays more "
        "time than its page count suggests.",
        "Modules 5 to 7 ask: how do I describe uncertainty, and how do I test a claim "
        "about it? Describing comes first (centre, spread, shape), then the distributions "
        "that model it, then formal testing.",
        "Module 8 asks: what happens when I hold assets together rather than alone? This "
        "is where the volume pays off, and it reappears almost unchanged in Volume 9.",
        "Modules 9 to 11 ask: what do I do when the maths gets too hard for a formula? "
        "The answer is simulate it, fit a line to it, or hand it to a machine.",
    ])
    d.key("If you are short of time, Modules 4, 5, 7, 8 and 10 carry the most examinable "
          "content. Modules 9 and 11 are largely descriptive and can be learned quickly, "
          "but do not skip them: descriptive modules produce easy marks.")

    d.h2("A note on the mathematics")
    d.p("You will not derive anything in this volume. You will be asked to put numbers into "
        "perhaps thirty formulas quickly and correctly, and far more often to say in words "
        "what a number means. The examiners test interpretation harder than arithmetic.")
    d.p("Three habits save marks repeatedly across the whole volume:")
    d.bullets([
        "Check the time period. Almost every error in Modules 1 to 4 is a periodic rate "
        "used where an annual one belonged, or the reverse.",
        "Check whether the question is about a sample or a population. It changes the "
        "denominator, the formula, and sometimes the whole test.",
        "Check whether the question wants total risk or only the part of risk the market "
        "pays for. Standard deviation and beta are not interchangeable.",
    ])
    d.warn("The calculator is where most lost marks actually happen. Learn your financial "
           "calculator's cash flow and statistics functions until they are automatic, and "
           "always clear the memory between questions. A stale cash flow register has "
           "cost more candidates marks than any concept in this volume.")


# ======================================================================
def module1(d):
    d.h1(1, "Returns of Financial Assets and Instruments",
         "What a return actually is, where it comes from, and how to work out what return "
         "you are entitled to demand before you invest.")

    d.h2("Where a return comes from")
    d.p("An investment pays you in two ways, and the curriculum insists you keep them "
        "separate because they behave very differently.")
    d.bullets([
        "Price return, sometimes called capital gain. The asset is worth more when you "
        "sell it than when you bought it. This part is uncertain for almost every asset.",
        "Income return, from the cash the asset hands you while you hold it: a dividend on "
        "a share, a coupon on a bond, rent on a property. This part is often fixed or at "
        "least far more predictable.",
    ])
    d.p("Add the two and you have the total return, which is the only number that describes "
        "what actually happened to your money.")
    d.formula("Total return  =  (P₁ − P₀ + I₁) / P₀\n\n"
              "  P₀ = price paid\n"
              "  P₁ = price received\n"
              "  I₁ = income received during the holding period",
              "The whole numerator is the money you ended up with beyond what you put in. "
              "The denominator is what you put in. Nothing more complicated is happening.")
    d.example("You buy a share at Rs 100. A year later it is worth Rs 112 and it has paid "
              "a dividend of Rs 4.\n\n"
              "Total return = (112 − 100 + 4) / 100 = 16 / 100 = 16.0%\n\n"
              "Of that, 12 points are price return and 4 points are income return. Now "
              "suppose inflation over the year was 9%.\n\n"
              "Real return = 1.16 / 1.09 − 1 = 6.42%\n\n"
              "Your money grew 16%, but your purchasing power grew only 6.42%. Subtracting "
              "9 from 16 would have given 7%, which is wrong by more than half a point.")
    d.key("A share that goes nowhere but pays a 5% dividend has earned you 5%. A share that "
          "rises 5% and pays nothing has also earned you 5%. The market does not care which "
          "pocket the money came from, and neither should your return calculation.")

    d.h2("The return you should demand")
    d.p("The return you earned is history. The return you should demand before committing "
        "money is a different question, and it is built in layers.")
    d.formula("Required return  =  real risk-free rate\n"
              "                  + expected inflation\n"
              "                  + risk premium",
              "Read it as three separate payments for three separate things: giving up the "
              "use of your money, losing purchasing power, and bearing uncertainty.")
    d.p("The first two layers together are the nominal risk-free rate, which is what you "
        "see quoted on a short-dated government security. The third layer is where all the "
        "interesting work in finance happens.")
    d.p("The risk premium is itself a stack. Candidates are expected to name its "
        "components and say what each one compensates for.")
    make_table(d,
               ["Premium", "Compensates you for"],
               [["Default risk", "The borrower may not pay you back at all"],
                ["Liquidity risk", "You may not be able to sell quickly at a fair price"],
                ["Maturity risk", "Longer promises are more sensitive to rate changes"]],
               widths=(32, 68))
    d.warn("The exact relationship is multiplicative, not additive. Adding the layers is an "
           "approximation that examiners accept only when they say so. If a question gives "
           "you precise figures, use (1 + real)(1 + inflation) − 1 and expect the additive "
           "answer to appear among the distractors.")

    d.h2("Nominal against real")
    d.p("A nominal return is the number on your statement. A real return is what you can "
        "actually buy with it. When inflation is high the difference stops being academic.")
    d.formula("(1 + nominal)  =  (1 + real) × (1 + inflation)\n\n"
              "so    real  =  (1 + nominal) / (1 + inflation) − 1",
              "A 12% nominal return with 9% inflation is a real return of 2.75%, not 3%. "
              "In a high-inflation market the gap between the two answers is examinable.")

    d.h2("Simple against compound")
    d.p("Simple interest pays only on the original sum. Compound interest pays on the "
        "interest too. Over one period they are identical, which is why the distinction is "
        "easy to miss, and over many periods they diverge enormously.")
    d.formula("Future value, simple    =  PV × (1 + r × n)\n"
              "Future value, compound  =  PV × (1 + r)ⁿ",
              "Every valuation in the CFA curriculum assumes compounding unless it says "
              "otherwise. Simple interest appears mainly in money-market conventions.")
    d.key("Continuous compounding is the limit of this process: FV = PV × e^(r×n). The "
          "continuously compounded return is ln(P₁/P₀), and it has one property worth "
          "remembering — these returns add across time, whereas ordinary returns must be "
          "multiplied. That is why option pricing and much of risk modelling uses them.")


# ======================================================================
def module2(d):
    d.h1(2, "Types of Financial Returns",
         "The same investment can produce half a dozen different 'returns' depending on how "
         "you measure it. This module is about choosing the right one and not being caught "
         "by the wrong average.")

    d.h2("Holding period return")
    d.p("The holding period return is the total return over however long you held the "
        "asset, with no annualising and no averaging. It is the honest starting point.")
    d.formula("HPR  =  (P₁ − P₀ + I₁) / P₀",
              "The same formula as total return. The name simply emphasises that the period "
              "is whatever you actually held it for, not a calendar year.")
    d.p("To chain several periods together you compound them. You never add them.")
    d.formula("HPR over n periods  =  (1 + r₁)(1 + r₂) … (1 + rₙ) − 1")

    d.h2("The three averages, and when each one is right")
    d.p("This is the highest-yielding section in the first three modules. Candidates lose "
        "marks here every year by reaching for the arithmetic mean out of habit.")
    make_table(d,
               ["Average", "Use it when", "Property"],
               [["Arithmetic", "Estimating the return of a single future period",
                 "Always the highest of the three"],
                ["Geometric", "Describing what actually happened over several periods",
                 "The true compound growth rate"],
                ["Harmonic", "Averaging ratios such as P/E, or cost per share when buying "
                 "a fixed rupee amount each period", "Always the lowest of the three"]],
               widths=(22, 48, 30))
    d.formula("Geometric mean  =  [(1 + r₁)(1 + r₂) … (1 + rₙ)]^(1/n)  −  1\n\n"
              "Harmonic mean   =  n / Σ(1 / xᵢ)")
    d.p("The ordering is fixed and worth memorising: harmonic ≤ geometric ≤ arithmetic. "
        "They are equal only when every observation is identical. The more the values vary, "
        "the wider the gaps.")
    d.example("A fund returns +30% in year 1, −20% in year 2, and +15% in year 3.\n\n"
              "Arithmetic mean = (30 − 20 + 15) / 3 = 8.33%\n\n"
              "Geometric mean  = (1.30 × 0.80 × 1.15)^(1/3) − 1\n"
              "                = (1.196)^(1/3) − 1 = 6.15%\n\n"
              "Check which one is true: Rs 100 grows to 130, falls to 104, then rises to "
              "119.60. Compounding 6.15% for three years also gives 119.60. Compounding "
              "8.33% would give 127.13, which never happened. The geometric mean is the "
              "one that matches the account.")
    d.key("Why the geometric mean is lower: losses hurt more than equal-sized gains help. "
          "Lose 50% then gain 50% and you are down 25%, not flat. The arithmetic mean says "
          "zero; the geometric mean says −13.4% a year, and the geometric mean is the one "
          "that matches your bank balance.")
    d.example("You invest Rs 12,000 on the first of each month for three months. The "
              "share costs Rs 400, then Rs 500, then Rs 600.\n\n"
              "Shares bought: 30 + 24 + 20 = 74\n"
              "Total invested: Rs 36,000\n"
              "Average cost per share = 36,000 / 74 = Rs 486.49\n\n"
              "The harmonic mean gives the same: 3 / (1/400 + 1/500 + 1/600) = Rs 486.49. "
              "The arithmetic mean of the three prices is Rs 500, which overstates what you "
              "actually paid. Fixed rupee amounts buy more shares when the price is low, "
              "and that pulls your average cost down.")
    d.warn("Cost averaging is the classic harmonic-mean question. If you invest the same "
           "rupee amount each month, your average cost per share is the harmonic mean of "
           "the prices, not the arithmetic mean. If you buy the same number of shares each "
           "month, it is the arithmetic mean. Read which one the question describes.")

    d.h2("Annualising")
    d.p("To compare a three-month return with a two-year one you must put them on the same "
        "footing. Annualising compounds a periodic return up to a year.")
    d.formula("Annualised return  =  (1 + r_period)^(periods per year)  −  1",
              "A 4% quarterly return annualises to 1.04⁴ − 1 = 16.99%, not 16%.")
    d.warn("Annualising a short period assumes the rate repeats all year, which for a "
           "one-week return is close to meaningless. The curriculum expects you to "
           "calculate it when asked and to say why it may mislead.")

    d.h2("Gross, net, and after tax")
    d.p("Returns are quoted at different points in the chain of deductions, and comparing "
        "across those points is a standard trap.")
    d.bullets([
        "Gross return is before management fees and expenses, but after trading costs. It "
        "is the right measure of the manager's skill.",
        "Net return is after fees. It is what the investor actually receives, and the right "
        "measure for comparing funds.",
        "After-tax return deducts tax on income and on realised gains, and depends on the "
        "investor rather than the asset.",
    ])

    d.h2("Leveraged returns")
    d.p("Borrowing to invest multiplies both the gain and the loss, and the cost of "
        "borrowing has to come out of the result.")
    d.formula("Leveraged return  =  r_portfolio + (borrowed / equity) × (r_portfolio − r_borrow)",
              "The second term is the whole story: you keep the spread between what the "
              "assets earned and what the debt cost, scaled by how much you borrowed. When "
              "that spread is negative, leverage works against you just as hard.")


# ======================================================================
def module3(d):
    d.h1(3, "Benchmarking Returns",
         "Two questions: how well did the money do, and how well did the manager do? They "
         "have different answers and different formulas. Then, what exactly is the index "
         "you are comparing against?")

    d.h2("Money-weighted against time-weighted")
    d.p("This is the single most examinable idea in the module, and the reasoning matters "
        "more than the arithmetic.")
    d.p("The money-weighted rate of return is simply the internal rate of return of the "
        "investor's own cash flows. It answers: what did this investor earn? It is affected "
        "by when money was paid in and taken out, which the manager usually does not "
        "control.")
    d.p("The time-weighted rate of return breaks the period at every cash flow, works out "
        "the return of each sub-period, and compounds them. Cash flow timing drops out "
        "entirely. It answers: how well did the manager invest the money they had?")
    d.formula("TWR  =  [(1 + r₁)(1 + r₂) … (1 + rₙ)]  −  1\n\n"
              "where each rᵢ is the return of a sub-period between cash flows",
              "If the sub-periods are not equal in length, compound them and then annualise "
              "by taking the appropriate root.")
    d.example("You buy one share at Rs 100. After a year it is worth Rs 110 and pays a "
              "Rs 5 dividend, and you buy a second share at Rs 110. After the second year "
              "each share is worth Rs 120 and each pays Rs 5, and you sell both.\n\n"
              "TIME-WEIGHTED\n"
              "  Year 1: (110 − 100 + 5) / 100 = 15.00%\n"
              "  Year 2: (120 − 110 + 5) / 110 = 13.64%\n"
              "  TWR = (1.15 × 1.1364)^(1/2) − 1 = 14.32% a year\n\n"
              "MONEY-WEIGHTED\n"
              "  t0: −100      t1: +5 − 110 = −105      t2: +10 + 240 = +250\n"
              "  The rate that makes these balance is 14.10% a year.\n\n"
              "The money-weighted figure is lower because you put more money in just "
              "before the weaker of the two years. The manager did not choose that timing, "
              "which is exactly why performance is reported time-weighted.")
    d.key("Time-weighted is the industry standard for reporting manager performance, and it "
          "is required under the Global Investment Performance Standards, precisely because "
          "it strips out the effect of client contributions the manager did not choose.")
    d.warn("When a large amount is added just before a good period, the money-weighted "
           "return exceeds the time-weighted one. When a large amount is added just before "
           "a bad period, it falls below. Examiners love asking which is higher and why, "
           "without asking you to compute either.")

    d.h2("How an index is weighted")
    d.p("An index is a portfolio with rules. The rule that matters most is how much weight "
        "each constituent gets, because it changes the index's behaviour completely.")
    make_table(d,
               ["Method", "Weight is based on", "Bias it introduces"],
               [["Price weighted", "Share price", "High-priced shares dominate, regardless "
                 "of company size"],
                ["Equal weighted", "Nothing; every member is the same", "Tilts to small "
                 "companies; needs constant rebalancing"],
                ["Market-cap weighted", "Total market value", "Largest and most expensive "
                 "companies dominate"],
                ["Float-adjusted cap", "Market value of freely traded shares only",
                 "The most widely used; reflects what is actually investable"],
                ["Fundamental weighted", "Sales, earnings, book value or similar",
                 "A deliberate value tilt"]],
               widths=(26, 36, 38))
    d.p("A price-weighted index is the simplest and the least defensible: a share priced at "
        "1,000 rupees moves it ten times as much as one priced at 100, even if the second "
        "company is far larger. The divisor must be adjusted whenever there is a split or a "
        "change of constituent, so the index does not jump for a reason that has nothing to "
        "do with the market.")
    d.key("A market-cap weighted index rebalances itself. As a share rises its weight rises "
          "automatically, so no trading is needed. An equal-weighted index does the "
          "opposite and must be traded back into line, which is why it costs more to track.")

    d.h2("Rebalancing and reconstitution")
    d.p("Two words that sound similar and are not.")
    d.bullets([
        "Rebalancing puts the existing members back to their intended weights.",
        "Reconstitution changes who the members are: some companies leave the index and "
        "others join.",
    ])
    d.warn("Float adjustment is the concept most often tested by a calculation. If a "
           "company has 100 million shares but 40 million are held by founders and the "
           "state, only 60 million count. Free float is about what the public can actually "
           "buy, not what exists.")


# ======================================================================
def module4(d):
    d.h1(4, "The Time Value of Money in Finance",
         "The engine underneath every valuation you will ever do. Learn this module "
         "properly and Volumes 5 and 6 become much shorter.")

    d.h2("The one idea")
    d.p("A rupee today is worth more than a rupee next year, because today's rupee can be "
        "put to work. Everything in this module is that sentence with different cash flow "
        "patterns attached.")
    d.formula("PV  =  FV / (1 + r)ⁿ            FV  =  PV × (1 + r)ⁿ",
              "Discounting and compounding are the same operation pointed in opposite "
              "directions.")

    d.h2("Valuing a bond")
    d.p("A fixed-coupon bond is a stream of identical payments plus a lump sum at the end. "
        "Its value is the present value of both parts.")
    d.formula("PV_bond  =  Σ [ coupon / (1 + r)ᵗ ]  +  face value / (1 + r)ⁿ",
              "The first term is an annuity, the second a single future amount. Your "
              "calculator handles both at once through the bond or cash flow keys.")
    d.example("A three-year bond with a face value of Rs 1,000 pays an 8% annual coupon. "
              "The market demands 10%.\n\n"
              "  PV = 80/1.10 + 80/1.10² + 1,080/1.10³\n"
              "     = 72.73 + 66.12 + 811.42\n"
              "     = Rs 950.26\n\n"
              "It trades below face value because its coupon is below the market yield. A "
              "bond whose coupon exceeds the market yield trades above face value, and one "
              "whose coupon equals it trades exactly at face value. You should be able to "
              "state which of the three applies without calculating anything.")
    d.p("Turn the question round and you get the implied return. Given the price and the "
        "cash flows, the discount rate that makes them equal is the yield to maturity. "
        "There is no closed-form solution; the calculator iterates to find it.")

    d.h2("Valuing a share")
    d.p("A share has no maturity, so the stream never ends. If dividends grow at a constant "
        "rate forever, the infinite sum collapses into one line.")
    d.formula("PV  =  D₁ / (r − g)\n\n"
              "  D₁ = next year's dividend\n"
              "  r  = required return\n"
              "  g  = constant growth rate, which must be below r",
              "Known as the constant growth or Gordon growth model. It reappears in Volume 5 "
              "almost word for word.")
    d.p("Rearranged, the same equation gives you the implied growth the market is assuming, "
        "or the return the current price offers:")
    d.formula("r  =  D₁ / P₀  +  g            g  =  r  −  D₁ / P₀",
              "The first term of r is the dividend yield and the second is capital growth. "
              "A required return is a yield plus a growth rate, which is worth remembering "
              "in words as well as symbols.")
    d.example("A company will pay a dividend of Rs 5 next year, expected to grow at 4% "
              "a year forever. You require 12%.\n\n"
              "  Value = 5 / (0.12 − 0.04) = 5 / 0.08 = Rs 62.50\n\n"
              "If the share actually trades at Rs 80, the market is not using your numbers. "
              "Solve backwards for the growth it must be assuming:\n\n"
              "  g = 0.12 − 5/80 = 0.12 − 0.0625 = 5.75%\n\n"
              "That is often the more useful question. Rather than arguing about whether "
              "Rs 80 is right, you can ask whether 5.75% growth forever is believable.")
    d.warn("If g is greater than or equal to r the formula returns a negative or infinite "
           "value and is simply not applicable. Growth above the required return cannot be "
           "sustained forever, and an exam question with that setup is testing whether you "
           "notice rather than whether you can divide.")

    d.h2("Cash flow additivity and no arbitrage")
    d.p("Cash flow additivity says the value of a set of cash flows equals the sum of their "
        "individual values. It sounds too obvious to name, and it is the foundation of "
        "arbitrage-free pricing.")
    d.p("If two packages of cash flows are identical, they must cost the same. If they do "
        "not, you buy the cheap one, sell the dear one, and pocket a risk-free profit. "
        "Because traders do exactly that, prices are forced back into line, and we can "
        "price almost anything by building a copy of it.")
    d.key("This principle is how forward rates are derived. Investing for two years must "
          "give the same result as investing for one year and then rolling into a one-year "
          "rate agreed today. If not, there is free money on the table.")
    d.formula("(1 + r₂)²  =  (1 + r₁) × (1 + f₁,₁)\n\n"
              "  r₂    = today's two-year spot rate\n"
              "  r₁    = today's one-year spot rate\n"
              "  f₁,₁  = the one-year rate, one year from now, implied by the other two",
              "Rearrange to find the forward rate. The same logic gives forward exchange "
              "rates in Volume 2 and forward prices in Volume 7.")

    d.example("The one-year spot rate is 5% and the two-year spot rate is 6%. What "
              "one-year rate, one year from now, is the market already implying?\n\n"
              "  (1.06)² = (1.05) × (1 + f)\n"
              "  1.1236  = 1.05 × (1 + f)\n"
              "  1 + f   = 1.0701      so f = 7.01%\n\n"
              "Nobody quoted that number. It is forced by the fact that the two routes "
              "must pay the same, otherwise you could borrow one way, lend the other, and "
              "collect the difference for nothing.")

    d.h2("Compounding frequency")
    d.p("A rate quoted annually but paid more often is worth more than it looks. The stated "
        "rate must be converted before it can be compared.")
    d.formula("Effective annual rate  =  (1 + stated / m)^m  −  1\n\n"
              "  m = compounding periods per year",
              "10% compounded quarterly is an effective 10.38%. Compounded continuously it "
              "is e^0.10 − 1 = 10.52%, which is the ceiling.")
    d.warn("Always convert to an effective annual rate before comparing two quoted rates. "
           "Comparing a semi-annual quote with a monthly quote directly is the single most "
           "common error in this module.")


# ======================================================================
def module5(d):
    d.h1(5, "Statistical Characteristics of Asset Returns",
         "Describing a set of returns: where the centre is, how spread out they are, what "
         "shape they make, and how two assets move in relation to each other.")

    d.h2("The centre")
    d.p("Three measures of centre, each answering a slightly different question.")
    d.bullets([
        "Mean: the arithmetic average. Uses every observation, which is its strength and "
        "its weakness, because one extreme value drags it.",
        "Median: the middle value once sorted. Unaffected by extremes, which makes it the "
        "honest choice for skewed data such as income or fund size.",
        "Mode: the most frequent value. Rarely useful for continuous returns, occasionally "
        "useful for categorical data.",
    ])
    d.p("Location measures divide the data instead: quartiles into four parts, quintiles "
        "into five, deciles into ten, percentiles into a hundred. The interquartile range, "
        "the third quartile minus the first, is a spread measure that ignores the tails.")

    d.h2("The spread")
    d.p("Spread is risk in this curriculum, so these formulas matter.")
    d.formula("Population variance  σ²  =  Σ(xᵢ − μ)²  /  N\n"
              "Sample variance      s²  =  Σ(xᵢ − x̄)²  /  (n − 1)",
              "The sample version divides by n − 1, not n. This is Bessel's correction and "
              "it exists because using the sample mean rather than the true mean makes the "
              "deviations slightly too small.")
    d.p("Standard deviation is the square root of variance, and is preferred for reporting "
        "because it is in the same units as the returns themselves.")
    d.example("Five yearly returns: 10%, −5%, 15%, 20%, −10%.\n\n"
              "  Mean = 30 / 5 = 6%\n"
              "  Deviations: 4, −11, 9, 14, −16\n"
              "  Squared:    16, 121, 81, 196, 256   →   sum 670\n"
              "  Sample variance = 670 / 4 = 167.5\n"
              "  Standard deviation = √167.5 = 12.94%\n"
              "  Coefficient of variation = 12.94 / 6 = 2.16\n\n"
              "Divide by 5 instead of 4 and you get 11.57%, which is the population answer "
              "to a sample question. Read the wording before you touch the calculator.")
    d.warn("Getting n versus n − 1 wrong is the most common arithmetic slip in the whole "
           "volume. Ask yourself whether you have every observation that exists (population) "
           "or a sample drawn from a larger set (almost always the case with returns).")

    d.h3("Two refinements")
    d.p("Standard deviation punishes upside and downside equally, which investors do not. "
        "Semi-deviation fixes that by counting only the observations below the mean, or "
        "below any target you choose. It is the more honest risk measure when returns are "
        "not symmetric.")
    d.formula("Coefficient of variation  =  s / x̄",
              "Risk per unit of return, so you can compare the riskiness of two assets with "
              "very different average returns. Lower is better. It has no units, which is "
              "the whole point.")

    d.h2("The shape")
    d.p("Two numbers describe how a distribution departs from the neat symmetric bell.")
    make_table(d,
               ["Measure", "What it says", "For investors"],
               [["Skewness = 0", "Symmetric", "The normal distribution's assumption"],
                ["Positive skew", "A long right tail; mean above median",
                 "Occasional large gains. Investors like it"],
                ["Negative skew", "A long left tail; mean below median",
                 "Occasional large losses. This is what most asset returns actually do"],
                ["Kurtosis = 3", "Normal tails, called mesokurtic", "The benchmark"],
                ["Excess kurtosis > 0", "Fat tails, leptokurtic",
                 "Extreme outcomes far more likely than a normal model predicts"]],
               widths=(26, 34, 40))
    d.key("Real asset returns are usually negatively skewed with fat tails. Both make a "
          "normal-distribution risk model too optimistic, which is exactly what went wrong "
          "in 2008. If an exam question mentions fat tails, it is asking you to say that "
          "the probability of an extreme loss is understated.")

    d.h2("How two assets move together")
    d.p("Covariance measures whether two assets tend to move in the same direction. Its "
        "problem is that its size is meaningless on its own, because it depends on the "
        "units.")
    d.formula("Cov(X,Y)  =  Σ (xᵢ − x̄)(yᵢ − ȳ)  /  (n − 1)\n\n"
              "Corr(X,Y)  =  ρ  =  Cov(X,Y) / (s_X × s_Y)",
              "Correlation is covariance scaled by the two standard deviations, which "
              "forces it between −1 and +1 and makes it comparable across any pair.")
    d.bullets([
        "ρ = +1: they move together in exact proportion. No diversification benefit at all.",
        "ρ = 0: no linear relationship.",
        "ρ = −1: they move exactly opposite. Risk can in principle be eliminated entirely.",
    ])
    d.warn("Correlation captures only straight-line relationships. Two variables can be "
           "perfectly related through a curve and still show a correlation near zero. It is "
           "also badly distorted by a single outlier, and it never establishes causation.")


# ======================================================================
def build():
    from _cfa_v1_part2 import main as part2
    d = Guide(volume=1, subject="Quantitative Methods")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    module1(d)
    module2(d)
    module3(d)
    module4(d)
    module5(d)
    part2(d)
    d.output(OUT)
    print("wrote", OUT, f"({d.page_no()} pages)")


if __name__ == "__main__":
    build()
