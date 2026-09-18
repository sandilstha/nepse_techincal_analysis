"""Volume 4, modules 7 to 12 and the formula sheet. Imported by make_cfa_v4.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module7(d):
    d.h1(7, "Analysis of Long-Term Assets",
         "Buildings, machines, patents and goodwill. The recurring question is whether a cost "
         "belongs on the balance sheet or the income statement.")

    d.h2("Capitalise or expense")
    d.p("A cost that creates a future benefit is capitalised and written off over the years "
        "it benefits. A cost consumed now is expensed now. The choice does not change the "
        "total expense over the asset's life, only its timing, but the timing changes "
        "everything an analyst looks at.")
    make_table(d,
               ["", "Capitalising", "Expensing"],
               [["Profit in year 1", "Higher", "Lower"],
                ["Profit in later years", "Lower, as depreciation runs", "Higher"],
                ["Total assets and equity", "Higher", "Lower"],
                ["Cash from operations", "Higher; the outflow sits in investing", "Lower"],
                ["Total cash flow", "Identical", "Identical"]],
               widths=(28, 38, 34))
    d.key("Capitalising shifts cash outflow from the operating section to the investing "
          "section of the cash flow statement. Total cash does not move by a rupee, but "
          "reported operating cash flow does, and so does every ratio built on it. A company "
          "with suspiciously strong CFO and heavy capital expenditure deserves a closer look "
          "at what it is capitalising.")
    d.p("Interest incurred while constructing an asset for the company's own use is "
        "capitalised into that asset's cost under both frameworks. Research is expensed under "
        "both. Development may be capitalised under IFRS once feasibility is demonstrated, "
        "but generally not under US GAAP, which makes an IFRS technology company look more "
        "profitable and more asset-heavy than an identical US one.")

    d.h2("Depreciation methods")
    d.formula("Straight line  =  (cost - residual value) / useful life\n\n"
              "Double declining balance  =  2 / useful life  x  beginning book value\n"
              "  Residual value is IGNORED in the calculation, but you stop\n"
              "  depreciating once book value reaches it.\n\n"
              "Units of production  =  (cost - residual) x units this period / total units")
    d.example("An asset costs Rs 100,000, has a residual value of Rs 10,000 and a five-year "
              "life.\n\n"
              "  Straight line: (100,000 - 10,000) / 5 = Rs 18,000 every year\n\n"
              "  Double declining, rate = 2/5 = 40%:\n"
              "    Year 1: 40% of 100,000 = Rs 40,000, book value Rs 60,000\n"
              "    Year 2: 40% of 60,000  = Rs 24,000, book value Rs 36,000\n"
              "    Year 3: 40% of 36,000  = Rs 14,400, book value Rs 21,600\n\n"
              "Accelerated depreciation reports Rs 40,000 of expense in year 1 against "
              "Rs 18,000 under straight line. The asset is identical; only the profile of "
              "reported profit differs.")
    d.warn("Under double declining balance, residual value is not subtracted before applying "
           "the rate. You apply the rate to the full book value and simply stop when book "
           "value reaches the residual. Subtracting first is the standard error.")
    d.p("Estimates matter as much as methods. Lengthening a useful life or raising an assumed "
        "residual value lowers annual depreciation and raises profit, with no operational "
        "change whatever. Compare a company's assumed lives against its peers.")

    d.h2("Revaluation and impairment")
    d.p("IFRS permits a company to carry long-lived assets at a revalued fair value. Increases "
        "generally go to other comprehensive income; decreases below original cost go to the "
        "income statement. US GAAP does not permit revaluation at all.")
    d.p("Impairment is recognised when an asset's carrying amount exceeds what it can "
        "realistically recover. Under IFRS the write-down may be reversed if the asset "
        "recovers. Under US GAAP it may not, except for assets held for sale.")
    d.warn("Impairment is a non-cash charge, so it does not touch the cash flow statement. It "
           "also lowers the asset base, which mechanically RAISES return on assets in every "
           "subsequent year. An analyst should be sceptical of a company whose returns "
           "improved immediately after a large write-off.")


def module8(d):
    d.h1(8, "Topics in Long-Term Liabilities and Equity",
         "Bonds, leases and pensions: three obligations that are easy to understand "
         "individually and easy to misread on a balance sheet.")

    d.h2("Bonds payable")
    d.p("A bond is recorded at the amount actually received, which equals the present value "
        "of its promised payments at the market rate on the day of issue. If the coupon is "
        "below the market rate it is issued at a discount; above, at a premium.")
    d.formula("Interest EXPENSE  =  carrying value at the start of the period\n"
              "                     x  the MARKET rate at issuance\n\n"
              "Interest PAID     =  face value  x  the COUPON rate\n\n"
              "The difference amortises the discount or premium into the carrying value.")
    d.example("A Rs 1,000 bond with a 6% coupon is issued to yield 8%, for proceeds of "
              "Rs 920.\n\n"
              "  Year 1 interest expense = 920 x 8% = Rs 73.6\n"
              "  Year 1 cash paid        = 1,000 x 6% = Rs 60.0\n"
              "  Discount amortised      = Rs 13.6\n"
              "  New carrying value      = 920 + 13.6 = Rs 933.6\n\n"
              "The expense exceeds the cash paid every year, and the carrying value climbs "
              "towards Rs 1,000 by maturity. For a bond issued at a premium, both effects run "
              "the other way.")
    d.warn("Interest expense uses the market rate AT ISSUANCE applied to the carrying value, "
           "not the coupon rate and not the current market rate. The rate is locked in on day "
           "one for accounting purposes even though the market moves afterwards.")

    d.h2("Leases")
    d.p("A lease gives the right to use an asset for a period. Under IFRS a lessee recognises "
        "a right-of-use asset and a lease liability for essentially every lease. US GAAP "
        "splits them into finance leases and operating leases, and although both now appear "
        "on the balance sheet, the income statement treatment differs.")
    make_table(d,
               ["", "Finance lease (and all IFRS leases)", "US GAAP operating lease"],
               [["Income statement", "Depreciation plus interest; front-loaded",
                 "A single straight-line lease expense"],
                ["EBITDA", "Higher, because depreciation and interest sit below it",
                 "Lower, because the whole expense is operating"],
                ["Cash flow", "Principal in financing, interest per the framework",
                 "Entirely operating"]],
               widths=(22, 42, 36))
    d.key("The reason leases matter to an analyst is comparability. A company that leases and "
          "one that borrows to buy have very similar economics, and before the current rules "
          "one showed a clean balance sheet and the other a leveraged one. Both now appear, "
          "which is precisely why the rules changed.")

    d.h2("Pensions")
    d.p("A defined contribution plan commits the employer to pay a fixed amount into a fund. "
        "The expense equals the contribution, and all investment risk is the employee's. "
        "There is nothing to analyse.")
    d.p("A defined benefit plan promises a specified retirement income. The employer bears the "
        "investment risk, and the balance sheet carries the funded status.")
    d.formula("Funded status  =  fair value of plan assets  -  the benefit obligation\n\n"
              "  Positive: overfunded, and reported as an asset\n"
              "  Negative: underfunded, and reported as a liability")
    d.warn("A defined benefit obligation depends on assumptions the company chooses: the "
           "discount rate, expected salary growth, and life expectancy. Raising the discount "
           "rate shrinks the obligation and improves the funded status without anything "
           "changing in reality. Always compare a company's assumptions with its peers "
           "before accepting the reported figure.")


def module9(d):
    d.h1(9, "Analysis of Income Taxes",
         "Companies keep two sets of books quite legally: one for shareholders and one for "
         "the tax authority. Deferred tax is the bridge between them.")

    d.h2("Why the two differ")
    d.p("Accounting profit follows IFRS or US GAAP. Taxable profit follows the tax code. The "
        "differences are of two kinds, and the distinction decides whether deferred tax "
        "arises at all.")
    d.bullets([
        "Temporary differences: the same item is recognised in both, but in different "
        "periods. Accelerated tax depreciation is the classic case. These reverse over time "
        "and create deferred tax.",
        "Permanent differences: an item recognised in one and never in the other, such as a "
        "permanently non-deductible fine or tax-exempt interest income. These never reverse "
        "and create NO deferred tax; they change the effective tax rate instead.",
    ])
    d.formula("Deferred tax LIABILITY  arises when accounting profit exceeds taxable profit\n"
              "  (tax is being deferred to later years)\n\n"
              "Deferred tax ASSET      arises when taxable profit exceeds accounting profit\n"
              "  (tax has been paid early, or a loss is carried forward)")
    d.example("An asset costing Rs 1,000 is depreciated straight line over four years for "
              "reporting but over two years for tax. The tax rate is 25%.\n\n"
              "  Year 1 accounting depreciation = Rs 250\n"
              "  Year 1 tax depreciation        = Rs 500\n"
              "  Taxable profit is Rs 250 LOWER than accounting profit\n"
              "  Deferred tax liability = 250 x 25% = Rs 62.5\n\n"
              "By year 3 the tax depreciation is exhausted while the accounting charge "
              "continues, so the difference reverses and the liability unwinds to zero by "
              "year 4. Nothing was avoided; it was only postponed.")
    d.key("Remember the direction with one sentence: if you are paying the tax authority LESS "
          "than your accounts suggest you should, you owe the difference later, so it is a "
          "liability. Reason it out from that each time rather than memorising a table.")

    d.h2("Valuation allowance and the effective rate")
    d.p("A deferred tax asset is only worth something if there will be future profits to use "
        "it against. If that is doubtful, a valuation allowance reduces it. Increasing the "
        "allowance lowers reported profit; releasing it raises profit, and a release is a "
        "judgement call that deserves scrutiny.")
    d.formula("Effective tax rate  =  income tax expense / pre-tax accounting income",
              "Compare it with the statutory rate. The gap is explained by permanent "
              "differences, foreign rates, and changes in the valuation allowance, and the "
              "reconciliation is given in the notes.")
    d.warn("A falling effective tax rate is a common source of earnings growth that has "
           "nothing to do with the business. Before crediting a company with improving "
           "profitability, check whether the improvement came from the tax line, and whether "
           "the cause is repeatable.")


def module10(d):
    d.h1(10, "Financial Reporting Quality",
         "Two separate questions: are the numbers a faithful picture, and are the underlying "
         "results any good? A company can score well on one and badly on the other.")

    d.h2("The quality spectrum")
    make_table(d,
               ["Level", "Description"],
               [["High quality reporting, high quality earnings",
                 "Faithful reporting of genuinely strong, sustainable results"],
                ["High quality reporting, low quality earnings",
                 "An honest account of a poor business. Useful to an analyst"],
                ["Within GAAP, but biased", "Choices and estimates consistently flattering"],
                ["Within GAAP, but earnings management",
                 "Deliberate structuring of transactions to hit a target"],
                ["Non-compliant, or fictitious", "Outside the rules; fraud"]],
               widths=(34, 66))
    d.key("Reporting quality concerns the information; earnings quality concerns the "
          "business. A faithful report of bad results is high quality reporting. Candidates "
          "who conflate the two get these questions wrong even when their instincts about "
          "the company are right.")

    d.h2("The conditions that produce poor reporting")
    d.numbered([
        "Motivation: pressure to meet a target, a covenant, an analyst forecast, or a "
        "compensation threshold.",
        "Opportunity: weak internal controls, a passive board, accounting standards with "
        "wide latitude.",
        "Rationalisation: a way for the individuals involved to justify it to themselves.",
    ])

    d.h2("What to look for")
    d.bullets([
        "Net income persistently exceeding cash from operations. Profits that never turn "
        "into cash are the single most reliable warning sign.",
        "Receivables growing much faster than revenue, suggesting sales booked early or to "
        "weak customers.",
        "Inventory growing faster than sales, suggesting an impending write-down.",
        "Capitalising costs that peers expense.",
        "Frequent 'one-off' charges that appear every year and are therefore not one-off.",
        "Changes in estimates, useful lives or residual values that happen to raise profit.",
        "A falling effective tax rate with no explanation in the notes.",
    ])
    d.warn("The accruals ratio operationalises the first point. Accruals are the gap between "
           "accounting profit and cash generated. A large and growing gap means an increasing "
           "share of reported profit rests on judgement rather than on cash, and academic "
           "evidence consistently links high accruals with weaker subsequent returns.")


def module11(d):
    d.h1(11, "Financial Analysis Techniques",
         "The ratios themselves, and the discipline of decomposing them so that a number "
         "becomes an explanation.")

    d.h2("The five families")
    d.formula("ACTIVITY - how efficiently assets are used\n"
              "  Inventory turnover  =  COGS / average inventory\n"
              "  Receivables turnover = revenue / average receivables\n"
              "  Total asset turnover = revenue / average total assets\n\n"
              "LIQUIDITY - can it meet the next twelve months?\n"
              "  Current  =  CA / CL     Quick  =  (cash + ST inv + receivables) / CL\n\n"
              "SOLVENCY - can it survive its long-term debt?\n"
              "  Debt to equity  =  total debt / total equity\n"
              "  Interest coverage  =  EBIT / interest expense\n\n"
              "PROFITABILITY\n"
              "  Gross margin = gross profit / revenue;  Net margin = NI / revenue\n"
              "  ROA = NI / average assets;  ROE = NI / average equity\n\n"
              "VALUATION\n"
              "  P/E = price / EPS;   P/B = price / book value per share")

    d.h2("DuPont decomposition")
    d.p("Return on equity on its own tells you the result but not the reason. Decomposing it "
        "tells you which of three levers produced it, and whether the answer is reassuring.")
    d.formula("Three-part:\n"
              "  ROE  =  net margin  x  asset turnover  x  financial leverage\n"
              "       =  (NI/revenue) x (revenue/assets) x (assets/equity)\n\n"
              "Five-part:\n"
              "  ROE  =  tax burden x interest burden x operating margin\n"
              "          x asset turnover x financial leverage\n"
              "       =  (NI/EBT) x (EBT/EBIT) x (EBIT/revenue)\n"
              "          x (revenue/assets) x (assets/equity)")
    d.example("Two companies each report an ROE of 18%.\n\n"
              "  Company A: margin 12%, turnover 1.5x, leverage 1.0x\n"
              "             0.12 x 1.5 x 1.0 = 18%\n\n"
              "  Company B: margin 3%, turnover 1.2x, leverage 5.0x\n"
              "             0.03 x 1.2 x 5.0 = 18%\n\n"
              "The same headline number. Company A earns it from the business; Company B "
              "earns it from the balance sheet, and a modest downturn will do to B what it "
              "will not do to A. The decomposition is the whole point: identical ROE, "
              "entirely different risk.")
    d.key("The five-part version separates the two burdens. A tax burden near 1 means little "
          "tax is being paid; an interest burden near 1 means little debt is being serviced. "
          "If ROE improved, these two ratios tell you immediately whether it came from "
          "operations or from financing and tax.")
    d.warn("Ratios mean nothing in isolation. They must be compared against the same "
           "company's history, against close peers, or against an industry benchmark. A "
           "current ratio of 1.2 is comfortable for a supermarket and alarming for a "
           "shipbuilder, and a question that gives you one number and no context is usually "
           "testing whether you know that.")


def module12(d):
    d.h1(12, "Introduction to Financial Statement Modeling",
         "Turning the historical analysis into a forecast, which is what every valuation in "
         "Volumes 5 and 6 ultimately requires.")

    d.h2("How a model is built")
    d.numbered([
        "Forecast revenue first. Everything else follows from it, so this is the assumption "
        "that deserves the most work. Build it from volume and price, or from market size and "
        "share, rather than from a growth rate pulled out of the air.",
        "Forecast the operating costs, usually as a margin or as a percentage of revenue, "
        "separating the genuinely variable from the fixed.",
        "Forecast the working capital using the turnover ratios from Module 11, which links "
        "the balance sheet to the revenue forecast.",
        "Forecast capital expenditure and the resulting depreciation.",
        "Forecast the financing: debt, interest, and the share count.",
        "Let the three statements link, and check that the balance sheet balances.",
    ])
    d.key("The three statements must be connected, not forecast separately. Net income flows "
          "into retained earnings; capital expenditure flows into the asset base and then "
          "into depreciation; the change in working capital flows into cash. If your balance "
          "sheet does not balance, a link is missing, and the error is almost always in "
          "working capital or in the cash sweep.")

    d.h2("The behaviour of margins")
    d.p("Competition erodes abnormal profitability. A company earning returns far above its "
        "cost of capital attracts entrants, and margins revert towards the industry over "
        "time. A forecast that holds a 40% margin flat for a decade is making an implicit "
        "claim about barriers to entry, and the model should say what those barriers are.")
    d.p("The exception is a structural advantage that entrants cannot replicate: a network "
        "effect, a regulatory licence, a genuinely superior cost position. Volume 3's "
        "business models module is where those are catalogued.")

    d.h2("Inflation and the competitive environment")
    d.p("Inflation affects revenue and costs at different rates and with different lags. A "
        "company with pricing power passes cost increases through and its margin survives; "
        "one without absorbs them and its margin compresses. The examinable point is that "
        "inflation is not neutral across a model.")
    d.warn("Behavioural bias infects forecasting more than any other analytical task. "
           "Overconfidence produces ranges that are too narrow. Anchoring holds the forecast "
           "near the last reported figure or near the consensus. Confirmation bias finds the "
           "evidence that supports the conclusion already reached. The defence is to state "
           "the assumptions explicitly and to test what happens when each is wrong.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place. This is the longest "
        "formula sheet at Level I, and it is the one most worth reproducing from memory.")

    d.h2("Income statement")
    d.formula("Basic EPS    =  (net income - preferred dividends) / weighted avg shares\n"
              "Diluted EPS  =  adjusted income / (weighted avg shares + dilutive shares)\n"
              "  Include a potential share only if it REDUCES EPS")

    d.h2("Cash flow")
    d.formula("CFO (indirect)  =  net income + non-cash charges -/+ gains/losses\n"
              "                   - increases in operating assets\n"
              "                   + increases in operating liabilities\n\n"
              "FCFF  =  CFO + interest x (1 - t) - capital expenditure   (discount at WACC)\n"
              "FCFE  =  CFO - capital expenditure + net borrowing        (discount at r_e)")

    d.h2("Inventory")
    d.formula("FIFO inventory  =  LIFO inventory + LIFO reserve\n"
              "FIFO COGS       =  LIFO COGS - the increase in the LIFO reserve\n"
              "Equity adjustment  =  + LIFO reserve x (1 - t)\n\n"
              "Rising prices:  FIFO gives lower COGS and higher profit than LIFO")

    d.h2("Long-term assets")
    d.formula("Straight line  =  (cost - residual) / useful life\n"
              "Double declining  =  (2 / life) x beginning book value   (ignore residual)\n"
              "Units of production  =  (cost - residual) x units / total units")

    d.h2("Liabilities and tax")
    d.formula("Interest expense  =  carrying value x market rate at issuance\n"
              "Interest paid     =  face value x coupon rate\n"
              "Funded status     =  plan assets - benefit obligation\n"
              "Effective tax rate  =  tax expense / pre-tax accounting income")

    d.h2("Ratios and DuPont")
    d.formula("ROA  =  net income / average total assets\n"
              "ROE  =  net income / average equity\n\n"
              "ROE  =  net margin x asset turnover x leverage\n"
              "ROE  =  tax burden x interest burden x operating margin\n"
              "        x asset turnover x leverage")

    d.h2("The things most often got wrong")
    d.bullets([
        "An UNQUALIFIED audit opinion is the clean one.",
        "Revenue is recognised when control transfers, not when cash arrives.",
        "Diluted EPS can never exceed basic EPS.",
        "An asset rising consumes cash; a liability rising provides cash.",
        "Gains on asset sales are SUBTRACTED in the indirect method.",
        "Under rising prices, LIFO gives higher COGS and lower profit than FIFO.",
        "Double declining balance ignores residual value when applying the rate.",
        "Impairment is non-cash and mechanically raises later return on assets.",
        "Bond interest expense uses the market rate at ISSUANCE, not the coupon.",
        "Permanent differences create no deferred tax; temporary differences do.",
        "Capitalising moves cash outflow from operating to investing; total cash is unchanged.",
    ])
