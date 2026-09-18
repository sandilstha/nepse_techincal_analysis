"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 3 - Corporate Finance

Run:  venv/Scripts/python.exe docs/make_cfa_v3.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V3-Corporate-Finance-Summary.pdf")

MODULES = [
    (1, "Organizational Forms, Corporate Issuer Features, and Ownership",
     "How businesses are structured and who owns them"),
    (2, "Investors and Other Stakeholders",
     "Debt against equity, and everyone with a claim on the firm"),
    (3, "Corporate Governance: Conflicts, Mechanisms, Risks, and Benefits",
     "Who watches management, and what happens when nobody does"),
    (4, "Working Capital and Liquidity",
     "The cash conversion cycle and surviving the short term"),
    (5, "Capital Investments and Capital Allocation",
     "NPV, IRR, ROIC, and the pitfalls that wreck good analysis"),
    (6, "Capital Structure",
     "How much debt, and what Modigliani-Miller really says"),
    (7, "Business Models",
     "How a firm actually makes money, and why network effects change it"),
]

STANDFIRST = ("All seven learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Corporate Finance at Level I is a small volume with a very uneven distribution of "
        "marks, and knowing where the weight sits saves a great deal of time.")
    d.numbered([
        "Modules 1 to 3 are descriptive: legal forms, who the stakeholders are, and how "
        "governance is supposed to restrain management. Almost no arithmetic, but a lot of "
        "vocabulary that must be exactly right.",
        "Modules 4 to 6 are the quantitative core: the cash conversion cycle, capital "
        "allocation, and the cost of capital. This is where the calculation questions live.",
        "Module 7 is descriptive again, and short.",
    ])
    d.p("The volume also has an unusual feature: it connects outward more than any other at "
        "Level I. The WACC from Module 6 reappears as the discount rate in Module 5, and "
        "again in equity valuation in Volume 5. The ratios in Module 4 reappear in Volume 4's "
        "financial analysis. Learning them once, properly, pays three times.")
    d.key("If you learn only two things from this volume, learn the cash conversion cycle and "
          "the WACC. Between them they account for the majority of the calculation marks, and "
          "both are formulas you can reproduce in under a minute with practice.")
    d.warn("Corporate governance questions are graded on precision, not on general good "
           "sense. An answer that sounds sensible but uses the wrong term scores nothing. "
           "Learn the difference between a shareholder mechanism and a board mechanism, and "
           "between an agency conflict and a stakeholder conflict, as vocabulary.")


def module1(d):
    d.h1(1, "Organizational Forms, Corporate Issuer Features, and Ownership",
         "Before you analyse a company you must know what kind of legal creature it is, "
         "because that decides who bears the losses and who pays the tax.")

    d.h2("The three forms")
    make_table(d,
               ["Form", "Owner liability", "Taxation", "Access to capital"],
               [["Sole proprietorship", "Unlimited; personal assets at risk",
                 "Taxed once, as the owner's income", "Very limited"],
                ["Partnership", "Unlimited for general partners; limited partners risk only "
                 "what they put in", "Taxed once, in the partners' hands", "Limited"],
                ["Limited company", "Limited to the amount invested",
                 "The company is taxed, and often the shareholder is taxed again on dividends",
                 "Wide"]],
               widths=(22, 30, 28, 20))
    d.key("The trade-off runs in one direction throughout. Limited liability and easy access "
          "to outside capital are bought at the price of double taxation and disclosure. "
          "Every question about why a firm chose a particular form is really a question about "
          "which side of that trade-off mattered more.")

    d.h2("What makes a corporation different")
    d.bullets([
        "Legal identity: the company is a person in law. It can own property, sue and be "
        "sued, and it outlives its owners.",
        "Separation of owner and manager: shareholders own, managers run. This separation is "
        "the source of nearly every governance problem in Module 3.",
        "Limited liability: a shareholder can lose the investment and nothing more.",
        "External financing: it can issue both debt and equity to strangers.",
        "Taxation: profits are taxed at the company, and distributions are often taxed again "
        "at the shareholder. Some jurisdictions relieve this; many do not.",
    ])

    d.h2("Public and private")
    make_table(d,
               ["", "Public", "Private"],
               [["Liquidity", "Shares trade continuously on an exchange",
                 "Sale requires finding a buyer and often board consent"],
                ["Price transparency", "A quoted price at all times",
                 "Value known only at a transaction"],
                ["Disclosure", "Heavy, continuous, regulated", "Light, mostly to lenders"],
                ["Share issuance", "Can raise capital from the public at short notice",
                 "Private placements only"]],
               widths=(22, 40, 38))
    d.p("Going public is usually done through an initial public offering, in which new shares "
        "are underwritten and sold. The alternatives are a direct listing, where existing "
        "shares simply begin trading and no new money is raised, and a merger with a special "
        "purpose acquisition company, which is faster but dilutes more.")
    d.p("Going private runs the other way: a leveraged buyout, a management buyout, or a "
        "straightforward acquisition. The common motive is escaping the cost and short-term "
        "pressure of public disclosure.")

    d.h2("The varieties of owner")
    d.p("Who holds the shares changes how a company behaves. The curriculum asks you to "
        "distinguish individual investors, institutional investors such as pension funds and "
        "insurers, other corporations holding strategic stakes, governments and sovereign "
        "funds, and private equity, whose horizon is deliberately finite.")
    d.warn("A common mistake is assuming a private company must be small. Many of the "
           "largest firms in the world are private, and a private company with a single "
           "family owner can be far larger than a small listed one. Public versus private is "
           "about how shares are traded, not about size.")


def module2(d):
    d.h1(2, "Investors and Other Stakeholders",
         "Everyone who has a claim on the firm, what each of them wants, and why lenders and "
         "shareholders end up on opposite sides.")

    d.h2("Debt against equity")
    make_table(d,
               ["", "Debt (lenders)", "Equity (shareholders)"],
               [["Return", "Fixed interest, contractually promised",
                 "Whatever is left over, if anything"],
                ["Upside", "Capped at the interest and principal",
                 "Unlimited"],
                ["Downside", "Loses only if the firm cannot pay", "Loses first, and entirely"],
                ["Priority", "Paid before equity in liquidation", "Last in the queue"],
                ["Control", "None, until a covenant is breached", "Votes, elects the board"],
                ["Maturity", "Finite; must be repaid", "Perpetual"]],
               widths=(18, 42, 40))
    d.key("A lender's position is economically the same as a short option on the firm's "
          "value: full payment in most states of the world, and a loss in the bad tail. A "
          "shareholder holds the opposite. That asymmetry, not bad faith, is what puts the "
          "two in conflict.")

    d.h2("The conflict between lenders and shareholders")
    d.p("Because shareholders take the upside and lenders do not, shareholders prefer more "
        "risk than lenders would choose. Three classic expressions of this appear in the "
        "curriculum.")
    d.bullets([
        "Asset substitution: after borrowing at a rate set for a safe business, the firm "
        "shifts into riskier projects. The upside is the shareholders'; the extra default "
        "risk is the lenders'.",
        "Underinvestment: when a firm is deeply indebted, shareholders may refuse to fund a "
        "worthwhile project because the gain would mostly go to repaying the lenders.",
        "Excessive dividends or buybacks: paying cash out to shareholders removes the assets "
        "that were backing the loan.",
    ])
    d.p("Lenders respond with covenants: promises in the loan agreement restricting further "
        "borrowing, asset sales, and distributions. Covenants are the cheap answer to a "
        "problem that would otherwise be priced into the interest rate.")

    d.h2("Stakeholders beyond the investors")
    make_table(d,
               ["Stakeholder", "Wants"],
               [["Shareholders", "Value, growth, and a say through voting"],
                ["Lenders", "To be repaid; stability rather than growth"],
                ["The board", "To represent shareholders and oversee management"],
                ["Managers", "Compensation, security, and the scope of their role"],
                ["Employees", "Pay, conditions, and continued employment"],
                ["Customers", "Value, quality, and continuity of supply"],
                ["Suppliers", "To be paid, and to keep the relationship"],
                ["Governments", "Tax, compliance, and employment"]],
               widths=(24, 76))

    d.h2("ESG in brief")
    d.p("Environmental, social and governance factors enter Level I as risks to be assessed "
        "rather than as ethics. Environmental factors include emissions, resource use and "
        "physical climate exposure. Social factors include labour practices, product safety "
        "and community relations. Governance factors overlap with Module 3 entirely.")
    d.warn("The examinable point is that ESG factors matter because they are financially "
           "material, not because they are virtuous. An environmental liability is a "
           "liability. Frame any ESG answer in terms of risk to cash flows and to the "
           "valuation, and it will be marked correct.")


def module3(d):
    d.h1(3, "Corporate Governance: Conflicts, Mechanisms, Risks, and Benefits",
         "Management runs a company it does not own. Governance is the whole apparatus built "
         "to make sure that goes well, and this module is mostly vocabulary.")

    d.h2("The conflicts")
    d.p("Three relationships generate almost all governance problems, and the exam expects "
        "you to name which one a scenario describes.")
    make_table(d,
               ["Conflict", "What goes wrong"],
               [["Shareholders against managers", "The principal-agent problem. Managers may "
                 "pursue empire-building, excessive pay, or a quiet life"],
                ["Controlling against minority shareholders", "A dominant holder extracts "
                 "value through related-party deals, or through dual-class shares that give "
                 "votes out of proportion to ownership"],
                ["Shareholders against creditors", "The risk-shifting problem from Module 2"]],
               widths=(30, 70))
    d.key("The principal-agent problem exists because of information asymmetry. Managers know "
          "more about the business than the owners do, so the owners cannot simply check "
          "whether decisions were good. Every governance mechanism in this module is an "
          "attempt to narrow that gap or to align incentives across it.")

    d.h2("The mechanisms")
    make_table(d,
               ["Group", "Mechanisms"],
               [["Shareholder", "Voting, proxy contests, the right to call a meeting, "
                 "shareholder activism, litigation"],
                ["Board and management", "Independent directors, separating the chair from "
                 "the chief executive, board committees, performance-linked pay"],
                ["Creditor", "Covenants, collateral, seniority, credit rating scrutiny"],
                ["Employee", "Contracts, works councils, employee share ownership"],
                ["Customer and supplier", "Contract terms, and the plain discipline of "
                 "losing the relationship"],
                ["Government", "Company law, securities regulation, listing rules, audit "
                 "requirements"]],
               widths=(26, 74))
    d.p("Three board committees appear repeatedly. The audit committee oversees financial "
        "reporting and the external auditor. The remuneration committee sets executive pay. "
        "The nominations committee controls who joins the board. Each should be composed of "
        "independent directors, because each concerns something management should not decide "
        "about itself.")

    d.h2("Risks and benefits")
    d.bullets([
        "Operational: weak governance produces poor decisions and weak control. Strong "
        "governance produces better capital allocation.",
        "Legal, regulatory and reputational: failures bring fines, litigation and lasting "
        "damage to the brand.",
        "Financial: poor governance raises the cost of capital, because lenders and equity "
        "investors both demand compensation for the risk of being expropriated.",
    ])
    d.warn("Dual-class share structures are an exam favourite. They let founders keep control "
           "with a small economic stake, which protects long-term strategy but entrenches "
           "management and disenfranchises minority holders. Be able to argue both sides; a "
           "question may ask for either.")


def module4(d):
    d.h1(4, "Working Capital and Liquidity",
         "A profitable company can still fail if it runs out of cash. This module is about "
         "the gap between paying for things and being paid for them.")

    d.h2("The cash conversion cycle")
    d.p("Money goes out when you buy inventory and comes back when your customer pays. The "
        "cycle measures how many days you are out of pocket in between.")
    d.formula("Days of inventory on hand  =  365 / inventory turnover\n"
              "  where inventory turnover  =  cost of goods sold / average inventory\n\n"
              "Days of sales outstanding  =  365 / receivables turnover\n"
              "  where receivables turnover  =  revenue / average receivables\n\n"
              "Days of payables  =  365 / payables turnover\n"
              "  where payables turnover  =  purchases / average payables\n\n"
              "Cash conversion cycle  =  DOH  +  DSO  -  days of payables")
    d.example("A company reports cost of goods sold of Rs 730m, revenue of Rs 1,095m, average "
              "inventory of Rs 120m, average receivables of Rs 150m and average payables of "
              "Rs 80m.\n\n"
              "  Inventory turnover = 730 / 120 = 6.08x    DOH = 365 / 6.08 = 60.0 days\n"
              "  Receivables turnover = 1,095 / 150 = 7.30x   DSO = 365 / 7.30 = 50.0 days\n"
              "  Payables turnover = 730 / 80 = 9.13x      Days payable = 40.0 days\n\n"
              "  Cash conversion cycle = 60 + 50 - 40 = 70 days\n\n"
              "The company funds 70 days of operations out of its own pocket. Cut DSO to 35 "
              "days by collecting faster and the cycle falls to 55, releasing cash without "
              "any new borrowing and without selling a single extra unit.")
    d.key("A shorter cycle is better, and it can be negative. A supermarket sells for cash in "
          "days, holds little inventory, and pays suppliers in sixty days, so its customers "
          "finance its operations. That is a structural advantage, not an accounting quirk.")
    d.warn("Payables turnover uses PURCHASES, not cost of goods sold. Many questions give "
           "only COGS and expect you to use it as an approximation, but if the question "
           "supplies purchases separately, using COGS is simply wrong. Read what is given.")

    d.h2("Liquidity")
    d.p("Primary sources are the ordinary ones: cash on hand, collections from customers, "
        "short-term investments, and committed credit lines. Secondary sources are the ones "
        "you use when the primary ones have failed: selling assets, renegotiating debt, "
        "filing for protection. Reaching for a secondary source is itself a warning sign, "
        "because each one damages the business.")
    d.p("Drags on liquidity delay money coming in: slow collections, obsolete inventory, "
        "tight credit limits. Pulls on liquidity accelerate money going out: suppliers "
        "shortening terms, lenders calling loans.")
    d.formula("Current ratio  =  current assets / current liabilities\n"
              "Quick ratio    =  (cash + short-term investments + receivables) / "
              "current liabilities\n"
              "Cash ratio     =  (cash + short-term investments) / current liabilities",
              "Each step down the list removes the less liquid assets. The quick ratio drops "
              "inventory; the cash ratio drops receivables too.")

    d.h2("Managing the working capital")
    d.bullets([
        "Inventory: hold enough to serve customers, not so much that cash is trapped.",
        "Receivables: tighten terms and chase collections, but not so hard that customers "
        "leave.",
        "Payables: take the full credit period, but never lose a worthwhile early-payment "
        "discount, which is usually far more valuable than it looks.",
    ])
    d.example("A company holds cash of Rs 40m, short-term investments of Rs 20m, receivables "
              "of Rs 150m and inventory of Rs 120m, against current liabilities of Rs 180m.\n\n"
              "  Current ratio = (40 + 20 + 150 + 120) / 180 = 330 / 180 = 1.83\n"
              "  Quick ratio   = (40 + 20 + 150) / 180 = 210 / 180 = 1.17\n"
              "  Cash ratio    = (40 + 20) / 180 = 60 / 180 = 0.33\n\n"
              "The current ratio looks comfortable, but more than a third of the current "
              "assets are inventory. If that inventory is slow-moving, the 1.17 quick ratio "
              "is the honest number. This is why the exam gives you all three.")
    d.warn("Trade credit discounts are deceptively expensive to forgo. Terms of 2/10 net 30 "
           "mean a 2% discount for paying 20 days early. That is roughly 2/98 = 2.04% for 20 "
           "days, which annualises to more than 44%. Almost no company can borrow that "
           "cheaply, so the discount should almost always be taken.")


def module5(d):
    d.h1(5, "Capital Investments and Capital Allocation",
         "How a firm decides which projects to fund. The arithmetic is straightforward; the "
         "marks are lost in the judgement around it.")

    d.h2("The four kinds of project")
    make_table(d,
               ["Type", "Nature", "Analysis required"],
               [["Going concern", "Maintenance and replacement", "Light; often mandatory"],
                ["Regulatory compliance", "Required by law", "Minimal; the alternative is "
                 "not operating"],
                ["Expansion of existing business", "More of what already works",
                 "Substantial"],
                ["New lines of business", "Genuinely new activity",
                 "The most, and the most uncertain"]],
               widths=(28, 34, 38))

    d.h2("Net present value")
    d.formula("NPV  =  sum of [ CF_t / (1 + r)^t ]  -  initial investment\n\n"
              "Accept if NPV > 0",
              "The discount rate r is the opportunity cost of the capital employed, which in "
              "practice is the WACC from Module 6, adjusted if the project is riskier than "
              "the firm as a whole.")
    d.example("A project costs Rs 1,000 today and returns Rs 400, Rs 500 and Rs 400 over "
              "three years. The required return is 10%.\n\n"
              "  PV = 400/1.10 + 500/1.21 + 400/1.331\n"
              "     = 363.6 + 413.2 + 300.5 = Rs 1,077.3\n"
              "  NPV = 1,077.3 - 1,000 = Rs 77.3\n\n"
              "Positive, so accept. The NPV is the amount by which shareholder wealth rises "
              "the moment the project is announced, which is why it is the theoretically "
              "correct rule.")

    d.h2("Internal rate of return")
    d.p("The IRR is the discount rate at which the NPV is exactly zero. Accept if it exceeds "
        "the required return. It is popular because it is a percentage and so feels "
        "comparable across projects, but it has three defects that the exam tests.")
    d.numbered([
        "Scale blindness. A 50% return on Rs 10 is worth less than a 12% return on Rs 1,000, "
        "but the IRR ranking prefers the first.",
        "Multiple IRRs. If the cash flows change sign more than once, several rates can set "
        "the NPV to zero, and none of them is meaningful.",
        "The reinvestment assumption. The IRR implicitly assumes intermediate cash flows are "
        "reinvested at the IRR itself, which is rarely available. The NPV assumes "
        "reinvestment at the required return, which is realistic.",
    ])
    d.example("Two mutually exclusive projects, with a required return of 10%.\n\n"
              "  Project A: costs Rs 100, returns Rs 150 in one year\n"
              "    NPV = 150/1.10 - 100 = Rs 36.4      IRR = 50%\n\n"
              "  Project B: costs Rs 1,000, returns Rs 1,250 in one year\n"
              "    NPV = 1,250/1.10 - 1,000 = Rs 136.4   IRR = 25%\n\n"
              "The IRR prefers A; the NPV prefers B. Take B. A percentage cannot be spent, "
              "and B adds Rs 100 more to shareholder wealth. This is scale blindness, and it "
              "is the most frequently examined defect of the IRR.")
    d.key("When NPV and IRR disagree about which of two mutually exclusive projects to "
          "choose, follow the NPV. Always. This is one of the few places in the curriculum "
          "where one method is simply declared superior, and the exam asks it directly.")

    d.h2("Return on invested capital")
    d.formula("ROIC  =  after-tax operating profit / average invested capital",
              "Compare it with the WACC. A firm creating value earns a ROIC above its cost "
              "of capital; one earning less is destroying value however fast it grows.")

    d.h2("Principles and pitfalls")
    d.bullets([
        "Use cash flows, not accounting earnings.",
        "Use incremental cash flows: only what changes because of the decision.",
        "Ignore sunk costs. Money already spent is irrelevant to what you should do now.",
        "Include opportunity costs, such as the market value of a building you already own.",
        "Include externalities, both cannibalisation of existing sales and any positive "
        "spillover.",
        "Ignore financing costs in the cash flows; they are already in the discount rate.",
    ])
    d.warn("Counting interest as a project cash flow AND discounting at the WACC is "
           "double-counting, and it is the single most common error in capital budgeting "
           "questions. The discount rate already charges the project for its financing.")
    d.p("Real options are the flexibility embedded in a project: to expand if it succeeds, "
        "to abandon if it fails, to delay until more is known, or to switch inputs. They "
        "always add value, because holding a choice is never worse than not holding it, so a "
        "plain NPV understates a project with genuine flexibility.")


def module6(d):
    d.h1(6, "Capital Structure",
         "How much of the firm should be financed with debt. The most theoretical module in "
         "the volume, and the most reliably examined.")

    d.h2("The cost of capital")
    d.formula("WACC  =  w_d x r_d x (1 - t)  +  w_e x r_e\n\n"
              "  w_d, w_e = weights of debt and equity, at MARKET value\n"
              "  r_d = cost of debt      r_e = cost of equity\n"
              "  t   = marginal tax rate",
              "Debt is multiplied by (1 - t) because interest is deductible. Dividends are "
              "not, so there is no such adjustment on the equity side.")
    d.example("A firm is 40% debt and 60% equity at market value. It borrows at 8%, its cost "
              "of equity is 14%, and the tax rate is 25%.\n\n"
              "  After-tax cost of debt = 8% x (1 - 0.25) = 6.0%\n"
              "  WACC = 0.40(6.0) + 0.60(14.0) = 2.40 + 8.40 = 10.4%\n\n"
              "Any project earning more than 10.4% adds value; anything below destroys it. "
              "Note that the tax shield alone cut the effective cost of the debt portion by "
              "two full percentage points.")
    d.warn("Use MARKET value weights, not book value. Book equity is a historical accounting "
           "figure with no bearing on what shareholders currently require. Questions supply "
           "book values precisely to see whether you will reach for them.")

    d.h2("Modigliani-Miller")
    d.p("Four propositions, learned as two pairs. The first pair assumes no taxes; the second "
        "adds them. Both assume no bankruptcy costs, no agency costs, and symmetric "
        "information.")
    make_table(d,
               ["Proposition", "Statement"],
               [["I, without taxes", "Capital structure is irrelevant. Firm value is set by "
                 "the assets, not by how they are financed"],
                ["II, without taxes", "The cost of equity rises exactly enough with leverage "
                 "to offset the cheaper debt, so the WACC is unchanged"],
                ["I, with taxes", "Firm value rises with debt by the value of the tax shield: "
                 "V_levered = V_unlevered + (t x D)"],
                ["II, with taxes", "The WACC falls as leverage rises, which taken literally "
                 "implies 100% debt"]],
               widths=(26, 74))
    d.key("The intuition behind Proposition I is a cake. Slicing it differently does not make "
          "it bigger. Debt is cheaper than equity, but adding debt makes the remaining equity "
          "riskier and therefore more expensive, and in a world without taxes the two effects "
          "cancel exactly.")
    d.example("An all-equity firm is worth Rs 500m. It borrows Rs 200m and uses the proceeds "
              "to buy back shares. The tax rate is 25%.\n\n"
              "  Tax shield = t x D = 0.25 x 200 = Rs 50m\n"
              "  V_levered = 500 + 50 = Rs 550m\n\n"
              "The assets did not change and the business did not improve. The firm is worth "
              "Rs 50m more purely because the government now collects less tax. That is the "
              "entire content of Proposition I with taxes, and it is why the theory, taken "
              "alone, points towards all-debt financing.")
    d.p("The absurd conclusion of Proposition II with taxes is the point, not a flaw. It "
        "shows that something has been left out, and what has been left out is the cost of "
        "financial distress.")

    d.h2("Where the optimum sits")
    d.p("Combine the two forces and you get the static trade-off theory. The tax shield rises "
        "steadily with debt. The expected cost of financial distress rises slowly at first "
        "and then very steeply. The optimal capital structure is where the marginal benefit "
        "of one more rupee of debt equals its marginal distress cost, and that is the point "
        "where the WACC is at its minimum and firm value at its maximum.")
    d.p("Costs of distress come in two forms. Direct costs are legal and administrative fees. "
        "Indirect costs are usually larger: customers leave, suppliers demand cash, good "
        "employees go, and management spends its time on the balance sheet instead of the "
        "business.")
    d.formula("Firm value is maximised where the WACC is minimised",
              "These are the same point, always. If a question asks for one, it is asking "
              "for the other.")

    d.h2("Pecking order and signalling")
    d.p("In practice firms do not aim straight at a target. The pecking order theory says "
        "they prefer internal funds first, then debt, and issue equity only as a last resort, "
        "because issuing equity signals that management thinks the shares are overvalued.")
    d.warn("Note the direction of the signal. Announcing a share issue usually pushes the "
           "price DOWN, because the market infers management would not sell cheap. "
           "Announcing new debt is generally read as confidence, because management is "
           "willing to commit to fixed payments.")


def module7(d):
    d.h1(7, "Business Models",
         "How a firm actually earns money. Short, descriptive, and easy marks if you have "
         "the vocabulary.")

    d.h2("What a business model has to answer")
    d.p("The curriculum frames it as four questions: who the customer is, what is offered, "
        "how it is delivered, and how much is charged. Together these are the value "
        "proposition.")
    d.bullets([
        "Who: the target customer and the segment.",
        "What: the product or service, and how it differs from alternatives.",
        "Where and how: the channel, the supply chain, and the assets needed.",
        "How much: the pricing and revenue model.",
    ])

    d.h2("Pricing and revenue models")
    make_table(d,
               ["Model", "How it charges"],
               [["Value-based", "On what the customer gains, not on what it cost to make"],
                ["Cost-based", "A margin added to cost"],
                ["Price discrimination", "Different prices to different customers for the "
                 "same thing"],
                ["Subscription", "A recurring fee for continuing access"],
                ["Freemium", "Free at the base tier, paid for more"],
                ["Razor and blade", "Cheap device, expensive consumables"],
                ["Auction", "The buyers set the price"],
                ["Bundling", "Several items sold together for less than the sum"]],
               widths=(28, 72))

    d.h2("Network effects and platforms")
    d.p("A network effect exists when the product becomes more valuable to each user as more "
        "people use it. A telephone network is the classic case. A platform business connects "
        "two groups and profits from the connection, and it usually shows cross-side network "
        "effects: more drivers make the service better for riders, and more riders attract "
        "more drivers.")
    d.key("Network effects produce winner-take-most markets, high margins once established, "
          "and very high barriers to entry, because a competitor must overcome the incumbent's "
          "installed base rather than merely match its product. This is why platform "
          "businesses can sustain returns far above their cost of capital for long periods, "
          "which is exactly the condition Module 5 said should attract competition.")
    d.warn("Do not confuse a network effect with an economy of scale. Scale lowers the "
           "producer's unit COST. A network effect raises the user's VALUE. A business can "
           "have one without the other, and questions are written to separate them.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place.")

    d.h2("Working capital and liquidity")
    d.formula("Inventory turnover   =  COGS / average inventory\n"
              "Receivables turnover =  revenue / average receivables\n"
              "Payables turnover    =  purchases / average payables\n"
              "Days  =  365 / the relevant turnover\n"
              "Cash conversion cycle  =  DOH + DSO - days of payables\n\n"
              "Current ratio  =  current assets / current liabilities\n"
              "Quick ratio    =  (cash + short-term investments + receivables) / CL\n"
              "Cash ratio     =  (cash + short-term investments) / CL")

    d.h2("Capital allocation")
    d.formula("NPV   =  sum of CF_t / (1 + r)^t  -  initial investment;  accept if > 0\n"
              "IRR   =  the rate at which NPV = 0;  accept if IRR > required return\n"
              "ROIC  =  after-tax operating profit / average invested capital\n\n"
              "When NPV and IRR conflict, follow the NPV")

    d.h2("Capital structure")
    d.formula("WACC  =  w_d x r_d x (1 - t)  +  w_e x r_e      (MARKET value weights)\n\n"
              "MM I without taxes:   value is independent of capital structure\n"
              "MM II without taxes:  the cost of equity rises; the WACC is unchanged\n"
              "MM I with taxes:      V_levered  =  V_unlevered  +  (t x D)\n"
              "MM II with taxes:     the WACC falls as leverage rises\n\n"
              "Optimum: where WACC is minimised, which is where firm value is maximised")

    d.h2("The things most often got wrong")
    d.bullets([
        "WACC weights are MARKET values, never book values.",
        "Never put interest in a project's cash flows and also discount at the WACC.",
        "Sunk costs are irrelevant; opportunity costs and cannibalisation are not.",
        "When NPV and IRR disagree, the NPV wins.",
        "Payables turnover uses purchases, not COGS, when purchases are given.",
        "Announcing an equity issue is a negative signal; announcing debt is not.",
        "A network effect raises user value; an economy of scale lowers producer cost.",
    ])


def build():
    d = Guide(volume=3, subject="Corporate Finance")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5, module6, module7):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
