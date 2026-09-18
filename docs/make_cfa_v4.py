"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 4 - Financial Statement Analysis

Run:  venv/Scripts/python.exe docs/make_cfa_v4.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402
from _cfa_v4_part2 import (module7, module8, module9, module10, module11,
                           module12, appendix)   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V4-Financial-Statement-Analysis-Summary.pdf")

MODULES = [
    (1, "Introduction to Financial Statement Analysis", "The statements, and how to read them"),
    (2, "Analyzing Income Statements", "Revenue, expenses, and earnings per share"),
    (3, "Analyzing Balance Sheets", "What is owned, what is owed, and what is missing"),
    (4, "Analyzing Statements of Cash Flows I", "Where the cash actually came from"),
    (5, "Analyzing Statements of Cash Flows II", "Free cash flow and common-size analysis"),
    (6, "Analysis of Inventories", "FIFO, LIFO, and why the choice changes everything"),
    (7, "Analysis of Long-Term Assets", "Capitalising, depreciating, and impairment"),
    (8, "Topics in Long-Term Liabilities and Equity", "Bonds, leases and pensions"),
    (9, "Analysis of Income Taxes", "Deferred tax, and the effective rate"),
    (10, "Financial Reporting Quality", "Telling aggressive from fraudulent"),
    (11, "Financial Analysis Techniques", "Ratios, and DuPont decomposition"),
    (12, "Introduction to Financial Statement Modeling", "Building a forecast"),
]

STANDFIRST = ("All twelve learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("This is the largest volume at Level I and it carries the largest share of the marks. "
        "It is also the volume that everything else depends on: you cannot value an equity in "
        "Volume 5 or assess a bond issuer in Volume 6 without the numbers this volume "
        "teaches you to read.")
    d.numbered([
        "Modules 1 to 5 are the statements themselves: income statement, balance sheet, and "
        "two modules on the cash flow statement. Learn these first and learn them cold.",
        "Modules 6 to 9 are the accounting choices that move the numbers: inventory, "
        "long-term assets, liabilities and tax. This is where IFRS and US GAAP diverge, and "
        "where most of the calculation questions live.",
        "Modules 10 to 12 are what an analyst does with all of it: judge the quality of the "
        "reporting, compute ratios, and build a forecast.",
    ])
    d.p("A single idea runs through the whole volume. Every accounting choice that flatters "
        "one statement usually damages another, and the analyst's job is to find where the "
        "compensation happened. Capitalising a cost raises profit now and lowers it later. "
        "Choosing an inventory method that lowers profit raises cash flow through the tax "
        "bill. Nothing is free.")
    d.key("Cash flow is the anchor. Earnings depend on dozens of judgements; cash paid and "
          "cash received do not. Whenever a question asks which company is healthier and the "
          "earnings say one thing while the cash flow says another, the cash flow is the "
          "signal and the earnings are the noise.")
    d.warn("Know which differences between IFRS and US GAAP are examinable, because there "
           "are only a handful and they recur constantly: LIFO is permitted under US GAAP "
           "and prohibited under IFRS; IFRS permits the revaluation of long-lived assets and "
           "US GAAP does not; IFRS allows reversal of impairments and US GAAP does not "
           "(except for assets held for sale); and the two differ on where interest and "
           "dividends sit in the cash flow statement.")


def module1(d):
    d.h1(1, "Introduction to Financial Statement Analysis",
         "What the statements are, what else comes with them, and the order in which a "
         "professional actually works through them.")

    d.h2("The statements")
    make_table(d,
               ["Statement", "Answers"],
               [["Income statement", "Did it make a profit over the period?"],
                ["Balance sheet", "What does it own and owe at one instant?"],
                ["Statement of cash flows", "Where did the cash come from and go?"],
                ["Statement of changes in equity", "How did the owners' stake move?"],
                ["Notes to the accounts", "What the four statements above do not say"]],
               widths=(32, 68))
    d.key("The notes are not supplementary reading. Accounting policies, segment detail, "
          "lease and pension obligations, contingent liabilities and the composition of major "
          "line items are all in the notes, and half the analysis in this volume is "
          "impossible without them. Candidates who treat the notes as optional lose marks "
          "throughout.")
    d.p("Beyond the audited statements, a filing carries management's commentary on the "
        "results, the auditor's report, and, for listed issuers, proxy material covering "
        "governance and pay.")

    d.h2("The auditor's opinion")
    make_table(d,
               ["Opinion", "Meaning"],
               [["Unqualified", "The statements are fairly presented. This is the clean and "
                 "normal outcome"],
                ["Qualified", "Fair, except for one identified issue"],
                ["Adverse", "Not fairly presented. A serious warning"],
                ["Disclaimer", "The auditor was unable to form an opinion at all"]],
               widths=(24, 76))
    d.warn("An unqualified opinion is the GOOD one. The word sounds like a criticism and "
           "catches candidates every year. It means the auditor attached no qualifications.")
    d.p("An audit gives reasonable assurance, not a guarantee, and it does not certify that "
        "the business is sound or that the reporting is free of aggressive but permissible "
        "choices. That judgement is Module 10's subject.")

    d.h2("The analysis framework")
    d.numbered([
        "State the purpose and the context: what decision is this analysis for?",
        "Collect the data: statements, notes, industry and economic information.",
        "Process the data: adjustments, ratios, common-size statements.",
        "Analyse and interpret.",
        "Report the conclusions.",
        "Update as new information arrives.",
    ])


def module2(d):
    d.h1(2, "Analyzing Income Statements",
         "Revenue at the top, profit at the bottom, and a great many judgements in between.")

    d.h2("Recognising revenue")
    d.p("Both IFRS and US GAAP now use a single converged five-step model, which makes this "
        "one of the few areas with no difference to memorise.")
    d.numbered([
        "Identify the contract with the customer.",
        "Identify the separate performance obligations in it.",
        "Determine the transaction price.",
        "Allocate that price across the obligations.",
        "Recognise revenue as each obligation is satisfied.",
    ])
    d.key("Revenue is recognised when CONTROL transfers to the customer, not when cash is "
          "received and not when the invoice is raised. A company can recognise revenue years "
          "before the cash arrives, or hold cash for years as deferred revenue before "
          "recognising anything. This gap is where most revenue manipulation lives.")

    d.h2("Expenses and the matching principle")
    d.p("Expenses are recognised in the period in which the related revenue is earned, not "
        "when the cash is paid. Cost of goods sold is matched against the sale. Costs with no "
        "identifiable revenue, such as administration, are expensed as incurred. Costs "
        "benefiting several periods, such as equipment, are capitalised and depreciated.")

    d.h2("Earnings per share")
    d.formula("Basic EPS  =  (net income - preferred dividends) / weighted average shares\n\n"
              "Diluted EPS  =  adjusted income / (weighted average shares + all dilutive "
              "potential shares)",
              "Preferred dividends are subtracted because basic EPS measures what is "
              "available to the ORDINARY shareholder.")
    d.example("A company earns Rs 500m and pays Rs 50m in preferred dividends. It had 100m "
              "shares for the first nine months and issued 40m more on 1 October.\n\n"
              "  Weighted average = 100 + 40 x (3/12) = 110m shares\n"
              "  Basic EPS = (500 - 50) / 110 = Rs 4.09\n\n"
              "Using the 140m closing count would give Rs 3.21, and using the opening 100m "
              "would give Rs 4.50. Neither is right: the new shares only had the company's "
              "money working for them for three months, so they count for three months.")
    d.p("Diluted EPS asks what EPS would be if every convertible instrument converted and "
        "every option were exercised. Options are handled by the treasury stock method: "
        "assume the proceeds from exercise are used to buy back shares at the average market "
        "price, and only the net new shares are added.")
    d.warn("A potential share is included in diluted EPS only if it is DILUTIVE, meaning it "
           "reduces EPS. An antidilutive instrument is ignored entirely. Diluted EPS can "
           "therefore never exceed basic EPS, and if your answer does, you included something "
           "you should have excluded.")

    d.h2("Below the operating line")
    d.p("Distinguish continuing operations from discontinued ones. A discontinued operation "
        "is a component being disposed of, and it is reported separately, net of tax, because "
        "it tells you nothing about future earnings. Non-recurring items within continuing "
        "operations are not separated in the same way, and finding them is the analyst's job.")
    d.p("Comprehensive income is net income plus items that bypass the income statement "
        "entirely: certain foreign currency translation effects, some pension adjustments, "
        "and gains and losses on particular investment categories.")


def module3(d):
    d.h1(3, "Analyzing Balance Sheets",
         "A photograph taken at one instant, showing what the company owns, what it owes, and "
         "what belongs to the shareholders.")

    d.formula("Assets  =  Liabilities  +  Equity",
              "This never fails to balance, because equity is defined as the residual. It "
              "balancing tells you nothing about whether the numbers are right.")

    d.h2("How assets are measured")
    make_table(d,
               ["Basis", "Applied to"],
               [["Historical cost", "Most property, plant and equipment, and inventory"],
                ["Amortised cost", "Debt securities held to maturity, loans"],
                ["Fair value", "Most marketable securities and derivatives"],
                ["Lower of cost or net realisable value", "Inventory under IFRS"]],
               widths=(38, 62))
    d.key("Different assets on the same balance sheet are measured on different bases, so the "
          "total is not a valuation of the company and was never intended to be. This is why "
          "market capitalisation and book equity routinely differ by a factor of several.")

    d.h2("What the balance sheet leaves out")
    d.bullets([
        "Internally generated intangibles: a brand built over decades appears at nothing, "
        "while a brand acquired by purchase appears at cost. Two identical companies can "
        "therefore look entirely different.",
        "Research costs, expensed as incurred under both frameworks. IFRS permits "
        "capitalising DEVELOPMENT costs once technical and commercial feasibility are "
        "established; US GAAP generally does not.",
        "Human capital, reputation and customer relationships, unless acquired.",
    ])
    d.p("Goodwill is the exception that proves the rule: it arises only in an acquisition, as "
        "the excess of the price paid over the fair value of the identifiable net assets. It "
        "is not amortised, but it is tested for impairment.")

    d.h2("Equity")
    d.p("Shareholders' equity comprises contributed capital, retained earnings, treasury "
        "shares as a deduction, and accumulated other comprehensive income. Non-controlling "
        "interests, the share of a consolidated subsidiary the parent does not own, sit "
        "within equity but separately from the parent's own.")
    d.warn("Treasury stock reduces equity; it is not an asset. A company cannot own itself. "
           "Questions sometimes present it as an asset to see whether you will accept it.")


def module4(d):
    d.h1(4, "Analyzing Statements of Cash Flows I",
         "The statement that is hardest to manipulate, and therefore the one an analyst "
         "trusts most.")

    d.h2("The three sections")
    make_table(d,
               ["Section", "Contains"],
               [["Operating", "Cash generated by the actual business: from customers, to "
                 "suppliers and employees, and tax"],
                ["Investing", "Buying and selling long-term assets and investments"],
                ["Financing", "Raising and repaying debt, issuing shares, dividends, buybacks"]],
               widths=(20, 80))
    d.warn("The classification of interest and dividends is a guaranteed exam question. "
           "Under US GAAP, interest paid and interest and dividends received are ALL "
           "operating, and only dividends paid are financing. Under IFRS the company may "
           "choose: interest and dividends paid may be operating or financing, and interest "
           "and dividends received may be operating or investing. The same company can "
           "therefore report different operating cash flow under the two frameworks with no "
           "change in its actual cash.")

    d.h2("Direct and indirect")
    d.p("The direct method lists actual cash receipts and payments. It is more informative "
        "and almost nobody uses it. The indirect method starts at net income and reconciles "
        "to cash, and is what you will almost always see.")
    d.formula("Cash flow from operations, indirect method:\n\n"
              "  Net income\n"
              "  + non-cash charges (depreciation, amortisation, impairment)\n"
              "  +/- losses/gains on asset sales (removed; they belong in investing)\n"
              "  - increases in operating assets (receivables, inventory)\n"
              "  + increases in operating liabilities (payables, accrued expenses)\n"
              "  =  cash flow from operations")
    d.example("Net income Rs 200m; depreciation Rs 60m; a Rs 10m gain on selling a machine; "
              "receivables up Rs 40m; inventory down Rs 15m; payables up Rs 25m.\n\n"
              "  200 + 60 - 10 - 40 + 15 + 25 = Rs 250m\n\n"
              "The gain is SUBTRACTED even though it increased net income, because the whole "
              "proceeds of the sale belong in investing. Leaving it in operating would count "
              "the same cash twice.")
    d.key("The sign rule in one line: an asset going UP consumes cash, and a liability going "
          "UP provides cash. Receivables rising means you sold but were not paid, so subtract "
          "it. Payables rising means you bought but have not paid, so add it. If you can "
          "state that sentence, you can do any indirect-method question.")


def module5(d):
    d.h1(5, "Analyzing Statements of Cash Flows II",
         "What to do with the cash flow statement once you have it.")

    d.h2("Free cash flow")
    d.p("Two versions, and using the wrong one is a common error because they discount at "
        "different rates and give different values.")
    d.formula("FCFF  =  CFO  +  interest x (1 - t)  -  capital expenditure\n"
              "  Free cash flow to the FIRM: available to all providers of capital.\n"
              "  Discount at the WACC.\n\n"
              "FCFE  =  CFO  -  capital expenditure  +  net borrowing\n"
              "  Free cash flow to EQUITY: what is left for shareholders.\n"
              "  Discount at the cost of equity.")
    d.example("CFO is Rs 300m, interest paid Rs 50m, the tax rate 25%, capital expenditure "
              "Rs 120m, and the company borrowed a net Rs 40m.\n\n"
              "  FCFF = 300 + 50(0.75) - 120 = 300 + 37.5 - 120 = Rs 217.5m\n"
              "  FCFE = 300 - 120 + 40 = Rs 220m\n\n"
              "Interest is added back for FCFF because lenders are among the capital "
              "providers being served, and it is added back after tax because the deduction "
              "already reduced the tax bill.")
    d.warn("Under US GAAP, interest paid is already inside CFO, so it must be added back to "
           "reach FCFF. Under IFRS, if the company classified interest as financing, it is "
           "NOT in CFO and must not be added again. Check the framework before adding "
           "anything back.")

    d.h2("Common-size and ratio analysis of cash flow")
    d.p("Express each line as a percentage of revenue, or of total cash inflows, to compare "
        "companies of different sizes and to see the shape of the cash generation.")
    d.formula("Cash flow to revenue    =  CFO / revenue\n"
              "Cash return on assets   =  CFO / average total assets\n"
              "Debt coverage           =  CFO / total debt\n"
              "Interest coverage       =  (CFO + interest paid + taxes paid) / interest paid\n"
              "Reinvestment            =  CFO / cash paid for long-term assets")
    d.key("The pattern across the three sections tells a story on its own. Positive operating, "
          "negative investing and negative financing is a mature, self-funding company paying "
          "down debt. Negative operating and positive financing is a young company living on "
          "raised capital, which is fine while the capital is available and fatal when it is "
          "not. Positive operating with large positive investing may mean the company is "
          "selling assets to stay afloat.")


def module6(d):
    d.h1(6, "Analysis of Inventories",
         "The same warehouse of goods produces very different profits depending on an "
         "accounting choice, and this module is about untangling that.")

    d.h2("What goes into inventory")
    d.p("Inventory carries all the costs of bringing goods to their present location and "
        "condition: purchase price, conversion costs, and inbound transport. Abnormal waste, "
        "most storage costs, administrative overhead and selling costs are expensed as "
        "incurred rather than capitalised.")

    d.h2("The cost flow methods")
    make_table(d,
               ["Method", "Assumes", "When prices are RISING"],
               [["FIFO", "The oldest units are sold first",
                 "Low COGS, high profit, high inventory on the balance sheet"],
                ["LIFO", "The newest units are sold first",
                 "High COGS, low profit, low and stale inventory value"],
                ["Weighted average", "Everything is blended", "Between the two"]],
               widths=(22, 30, 48))
    d.key("LIFO gives the most realistic income statement, because it matches current costs "
          "against current revenue, and the least realistic balance sheet, because the "
          "inventory left over is valued at ancient prices. FIFO does exactly the reverse. "
          "Neither is more honest; they are informative about different things.")
    d.example("A company buys 100 units at Rs 10, then 100 at Rs 14, and sells 100 for Rs 20 "
              "each.\n\n"
              "  FIFO: COGS = 100 x 10 = Rs 1,000;  gross profit = 2,000 - 1,000 = Rs 1,000\n"
              "        Ending inventory = 100 x 14 = Rs 1,400\n\n"
              "  LIFO: COGS = 100 x 14 = Rs 1,400;  gross profit = 2,000 - 1,400 = Rs 600\n"
              "        Ending inventory = 100 x 10 = Rs 1,000\n\n"
              "Same warehouse, same sales, same cash. The reported profit differs by Rs 400 "
              "and the balance sheet by Rs 400, in opposite directions.")
    d.p("LIFO is permitted under US GAAP and prohibited under IFRS. US companies using LIFO "
        "must disclose a LIFO reserve, the difference between the LIFO inventory and what it "
        "would be under FIFO, and that disclosure is what allows comparison.")
    d.formula("FIFO inventory  =  LIFO inventory  +  LIFO reserve\n"
              "FIFO COGS       =  LIFO COGS  -  increase in the LIFO reserve\n\n"
              "To convert equity:  add the LIFO reserve x (1 - t) to equity",
              "Always convert a LIFO company TO FIFO for comparison, never the reverse, "
              "because FIFO is the basis every IFRS company already uses.")
    d.warn("LIFO liquidation is the trap. If a LIFO company sells more than it produces, it "
           "dips into old, cheap inventory layers, and COGS falls artificially. Profit rises "
           "for a reason that has nothing to do with the business performing better, and it "
           "cannot be repeated. Treat the gain as non-recurring.")

    d.h2("Writing inventory down")
    d.p("Under IFRS, inventory is carried at the lower of cost and net realisable value, and "
        "a write-down may be REVERSED if the value recovers, up to the original cost. Under "
        "US GAAP the rule depends on the method, and reversals are generally prohibited.")


def build():
    d = Guide(volume=4, subject="Financial Statement Analysis")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5, module6,
               module7, module8, module9, module10, module11, module12):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
