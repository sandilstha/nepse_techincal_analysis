"""Modules 5 and 6 plus the appendices of the Portfolio Construction study guide."""
from make_cfa_pc_pdf import make_table, MUTED
from fpdf.enums import XPos, YPos


def module5(d):
    d.h1(5, "The Behavioral Biases of Individuals",
         "Traditional theory assumes people consider all available information and act "
         "rationally. They do not. Module 5 catalogues how they actually behave and what "
         "to do about it.")

    d.h2("5.1  The two families of bias")
    make_table(d,
               ["", "COGNITIVE ERRORS", "EMOTIONAL BIASES"],
               [["Source",
                 "Faulty reasoning: statistical, information-processing or memory errors",
                 "Impulse, intuition and feelings"],
                ["Arise", "Through flawed conscious thinking",
                 "Spontaneously; may even be unwanted by the person feeling them"],
                ["Response",
                 "MODERATE - reduce or eliminate through better information, education and "
                 "process",
                 "ADAPT - recognise, accept and design around them"],
                ["Why", "Better data and discipline can fix reasoning",
                 "You cannot argue somebody out of a feeling"]],
               widths=(24, 58, 62))
    d.key("Cognitive errors can be corrected; emotional biases can usually only be "
          "accommodated. To MODERATE a bias is to reduce or eliminate it. To ADAPT to a "
          "bias is to accept it and adjust the plan around it. Which verb applies to "
          "which family is examined directly and frequently.")
    d.p("Cognitive errors divide further into BELIEF PERSEVERANCE biases - clinging to "
        "what you already think - and PROCESSING ERRORS - using information illogically. "
        "Belief perseverance is rooted in COGNITIVE DISSONANCE, the mental discomfort "
        "that arises when new information contradicts an existing belief. To relieve it, "
        "people ignore or distort the conflicting information.")

    d.h2("5.2  Cognitive errors: belief perseverance")
    d.h3("Conservatism bias")
    d.p("Maintaining prior views by inadequately incorporating new, conflicting "
        "information. In Bayesian terms, overweighting the prior and underweighting the "
        "new evidence, so beliefs UNDERREACT.")
    d.bullets([
        "Worst where information is technical, abstract or statistical, because the "
        "COGNITIVE COST of processing it is higher.",
        "Fix: apply Bayes' rule deliberately. Ask 'how does this information change my "
        "forecast?' Seek help interpreting information you do not understand rather than "
        "quietly discounting it.",
        "Curriculum example: through the 1990s analysts took years to lower Japanese GDP "
        "forecasts despite growth having decelerated sharply from 1990.",
    ])
    d.h3("Confirmation bias")
    d.p("Noticing what confirms existing beliefs and ignoring or undervaluing what "
        "contradicts them - a predisposition to justify what we want to believe.")
    d.bullets([
        "Consequences: seeing only positive news about a holding; building screens that "
        "ignore evidence against their own validity; UNDER-DIVERSIFIED portfolios; and "
        "over-concentration in employer stock, because acknowledging bad news would make "
        "going to work uncomfortable.",
        "Fix: actively seek the opposing case and corroborate from a different source or "
        "method.",
        "Example: a portfolio manager whose stock is collapsing calls the analyst who "
        "recommended it - who still rates it a buy - rather than an analyst with a sell "
        "rating, or researching the competitor taking its market share.",
    ])
    d.h3("Representativeness bias")
    d.p("Classifying new information by what it resembles. Two forms:")
    d.bullets([
        "BASE-RATE NEGLECT - ignoring how often something happens in the wider population "
        "in favour of vivid specific information. In the APM case, very few auto parts "
        "makers failed in 50 years even in hard times, but alarming headlines lead the "
        "analyst to predict failure anyway.",
        "SAMPLE-SIZE NEGLECT - treating a small sample as representative of the whole "
        "population, also called neglecting the law of small numbers.",
        "Fix: ask explicitly 'what is the probability this belongs to the group it "
        "RESEMBLES versus the group it statistically BELONGS to?' Research the base rate; "
        "widen the sample.",
    ])
    d.h3("Illusion of control bias")
    d.p("Believing you can control or influence outcomes you cannot. The classic tell is "
        "preferring to choose your own lottery numbers.")
    d.bullets([
        "Consequences: concentrated positions in companies people feel they influence, "
        "especially employers; OVERTRADING, and research shows portfolio turnover is "
        "negatively correlated with returns; and excessively detailed forecasting models, "
        "as though more detail controlled uncertainty. Understanding is useful; model "
        "complexity does not reduce inherent risk.",
        "Fix: accept that investing is a PROBABILISTIC activity. Ask what the downside "
        "is, what could go wrong, and when you would sell. Speak to someone with an "
        "opposing view.",
    ])
    d.h3("Hindsight bias")
    d.p("Remembering past events as having been predictable, and remembering your own "
        "forecasts as more accurate than they were - because outcomes that happened are "
        "more available than those that did not. Badly reasoned decisions with good "
        "outcomes get remembered as brilliance; well-reasoned decisions with bad outcomes "
        "get remembered as avoidable errors.")
    d.key("The fix for hindsight bias is mechanical and it works: WRITE DOWN each "
          "investment decision and the reasons for it, at the time you make it. Consult "
          "the record rather than your memory. Memory will reliably rewrite history in "
          "your favour.")

    d.h2("5.3  Cognitive errors: processing errors")
    d.h3("Anchoring and adjustment")
    d.p("Relying on an initial number and then adjusting insufficiently from it. Closely "
        "related to conservatism. The Industrial Lift case: last year's EPS was GBP 1.00 "
        "in strong conditions; non-residential construction has since collapsed and a "
        "recession is feared; the analyst forecasts GBP 0.90 - a 10% trim from an anchor "
        "that conditions have already invalidated.")
    d.p("Fix: ask whether you are holding a position on rational analysis or to reach a "
        "price you are anchored to, such as your purchase price or a previous high. Ask "
        "whether a forecast is built from past observed quantities or from expected "
        "future conditions. Remember that a company's past earnings reflect PAST "
        "conditions, and that your own cost basis is irrelevant to the security's future.")
    d.h3("Mental accounting")
    d.p("Dividing money into separate mental accounts that influence decisions, even "
        "though money is FUNGIBLE. Statman's observation is that investors build "
        "portfolios as a layered pyramid, each layer serving a different goal.")
    d.bullets([
        "Consequences: missing chances to reduce risk by combining low-correlation "
        "assets, because each account is examined separately; irrationally separating "
        "income from capital gains and chasing yield while unwittingly risking principal; "
        "and treating gains as 'house money' that can be gambled more freely.",
        "Example: Kendra Liu sells half a position that doubled overnight and puts the "
        "proceeds into a high-risk biotech she would never otherwise buy, because it is "
        "money she 'did not expect to have anyway'.",
        "Fix: aggregate. Put every account onto ONE spreadsheet with no headings or "
        "labels and look at the true overall allocation. The result is often surprising.",
    ])
    d.h3("Framing bias")
    d.p("Answering the same question differently depending on how it is presented. One in "
        "four start-ups succeeds; three in four fail. Same fact, different decisions.")
    d.bullets([
        "GAIN framing tends to produce more risk-averse choices; LOSS framing produces "
        "more risk-seeking ones.",
        "NARROW FRAMING is judging on one or two points - a charismatic CEO - while "
        "losing sight of industry conditions, fundamentals and valuation.",
        "The uncomfortable implication: your own risk-tolerance questionnaire can bias "
        "the answer. Showing a 95% return RANGE versus showing a standard deviation, or "
        "reordering the risk and return columns, changes which portfolio clients pick.",
        "Fix: ask whether the decision rests on a net gain or net loss position. Strip out "
        "references to gains and losses already incurred and focus on future prospects.",
    ])
    d.h3("Availability bias")
    d.p("Estimating probability by how easily something comes to mind. Four sources:")
    d.bullets([
        "RETRIEVABILITY - the first answer to surface is taken as correct.",
        "CATEGORIZATION - searching only within familiar categories.",
        "NARROW RANGE OF EXPERIENCE - generalising from your own limited exposure. The "
        "hedge fund employee who concludes 'most CFA charterholders work at hedge funds'.",
        "RESONANCE - being swayed by how closely something mirrors your own situation.",
    ])
    d.p("Consequences: a limited opportunity set; choosing funds by advertising volume or "
        "news coverage; and failing to diversify away from your own industry. Fix: build a "
        "proper policy strategy, research before deciding, use long-term historical data, "
        "and ask directly how the candidate list was assembled.")

    d.h2("5.4  Emotional biases")
    d.h3("Loss aversion and the disposition effect")
    d.p("Losses hurt considerably more than equivalent gains please. The value function "
        "is S-shaped and asymmetric around a reference point, which produces RISK-SEEKING "
        "behaviour in the domain of losses and RISK-AVOIDANCE in the domain of gains - the "
        "opposite of rational behaviour, which would accept more risk to increase gains "
        "rather than to avoid losses.")
    d.key("The DISPOSITION EFFECT: holding losers too long and selling winners too soon. "
          "The consequence is not merely poor returns - the portfolio becomes RISKIER than "
          "the client's objectives justify, because the deteriorating positions are kept "
          "and the improving ones are sold.")
    d.h3("Overconfidence bias")
    d.p("Unwarranted faith in one's own abilities. Two forms:")
    d.bullets([
        "PREDICTION overconfidence - confidence intervals set far too narrow, with too "
        "little variation allowed around a forecast.",
        "CERTAINTY overconfidence - probabilities assigned to outcomes set too high. The "
        "analyst who says 'there is no credible downside case' when asked what happens if "
        "oil falls another 10%.",
    ])
    d.p("Amplified by SELF-ATTRIBUTION BIAS: taking credit for successes "
        "(self-enhancing) while blaming others for failures (self-protecting). "
        "Consequences are underestimated risk, overestimated return, and poorly "
        "diversified portfolios with significant downside.")
    d.p("Fix: review your actual trading record over at least two years, winners AND "
        "losers, and count the trades. Separate decisions that were genuinely good from "
        "those that were merely lucky. Look for repeated patterns in the losses. As the "
        "old Wall Street line has it - do not confuse brains with a bull market.")
    d.h3("Self-control bias")
    d.p("Failing to act on long-term goals because of short-term satisfaction, worsened by "
        "HYPERBOLIC DISCOUNTING - a strong preference for small payoffs now over larger "
        "payoffs later. Consequences: saving too little, then taking excessive portfolio "
        "risk to make up the shortfall; and borrowing too much to fund present "
        "consumption. Fix: a written plan and a budget, reviewed regularly, with a "
        "strategic asset allocation to anchor decisions.")
    d.h3("Status quo bias")
    d.p("Doing nothing when change is warranted - through INERTIA rather than any "
        "conscious choice. The distinction matters: endowment and regret-aversion biases "
        "also produce inaction, but through conscious, if mistaken, decisions.")
    d.p("The Choi et al. study of automatic 401(k) enrolment is the evidence. Enrolment "
        "jumped from 26-43% at six months and 57-69% at three years to over 85% at all "
        "three firms. But more than 65% of employees simply contributed the employer's "
        "default of 2% or 3% and stayed in the default investment option, and after two "
        "years over 40% were still on the default. Defaults are extraordinarily powerful.")
    d.h3("Endowment bias")
    d.p("Valuing an asset more simply because you own it, so that the minimum price you "
        "would sell at exceeds the maximum you would pay to buy the same thing. It applies "
        "to purchased as well as inherited holdings.")
    d.key("The single most effective question in Module 5: 'Would you buy this security "
          "TODAY at the current price?' If the honest answer is no, endowment bias is "
          "driving the holding. For inherited assets, ask whether the deceased's intent "
          "was to leave that specific portfolio, or simply to leave resources that benefit "
          "the heirs. Most people conclude the latter, and become open to changing the "
          "allocation.")
    d.h3("Regret-aversion bias")
    d.p("Avoiding decisions for fear they turn out badly. Regret is more intense for "
        "actions TAKEN than for actions NOT taken, so inaction becomes the default.")
    d.bullets([
        "Being too conservative after past losses, leading to long-run underperformance "
        "and missed goals.",
        "HERDING - crowding into popular, well-known names because unfamiliar choices feel "
        "riskier and carry more personal responsibility. Keynes: 'worldly wisdom teaches "
        "that it is better for reputation to fail conventionally than to succeed "
        "unconventionally'.",
        "Fix: quantify the benefits of diversification and proper allocation. Accept that "
        "losses happen to everyone; keep long-term objectives in view to avoid being "
        "either too cautious or swept into a bubble.",
    ])

    d.h2("5.5  Biases at the market level: anomalies")
    d.p("An ANOMALY is a persistent abnormal return that is predictable in direction. But "
        "not every apparent deviation is genuine. Three sources of false positives:")
    d.numbered([
        "The asset pricing model chosen. If a reasonable change in how you estimate "
        "normal returns makes the anomaly vanish, it was an illusion - Fama places the IPO "
        "puzzle and post-stock-split returns in this category. Persistent high returns may "
        "simply be compensation for risk.",
        "Statistical problems - small samples, selection or survivorship bias, and data "
        "mining that treats spurious correlations as real. Benchmark choice alone can "
        "change the size of any measured out- or underperformance.",
        "Temporary disequilibrium. Publication draws attention and arbitrage removes the "
        "pattern. The small-company January effect does not survive risk adjustment, and "
        "the weekend effect has faded in the US and UK.",
    ])
    d.h3("Momentum")
    d.p("Future prices correlate with the recent past, typically for up to two years "
        "before reversing. The London Business School study of 52 years of UK data found "
        "the best performers of the prior 12 months went on to return 18.3% annualised "
        "while the worst returned 6.8%, against a market return of 13.5%. The effect "
        "appeared in all 16 other international markets studied.")
    d.p("Behavioural explanations: AVAILABILITY in the form of the RECENCY EFFECT - recent "
        "events are recalled vividly and extrapolated, with private investors more prone "
        "to this while professionals more often expect mean reversion. And REGRET, an "
        "expression of HINDSIGHT BIAS - investors who feel they should have foreseen a "
        "move buy in to remedy the regret, which also contributes to overtrading.")
    d.h3("Bubbles and crashes")
    d.p("Some elements are rational. Investors may expect a crash without knowing its "
        "timing; shorting may be costly, capital may be unwilling to bear extended losses, "
        "or suitable instruments may not exist. And managers judged on short-term "
        "performance face real commercial and career risk for standing aside.")
    d.p("The curriculum's paired example is the sharpest illustration in the volume. The "
        "manager of Hedge Fund A knew technology stocks were overvalued by December 1999 "
        "but misjudged the timing - 'we thought it was the eighth inning, and it was the "
        "ninth' - and resigned in April 2000 despite a strong 12-year record. The manager "
        "of Hedge Fund B refused to buy technology stocks in 1998 and 1999 because he "
        "correctly judged them overvalued, and after 17 years of strong performance the "
        "fund was DISSOLVED in 2000 because its returns could not keep up.")
    d.warn("Being right is not sufficient. Fund B's manager made the correct call and lost "
           "his fund for it. This is why career risk is treated as a RATIONAL explanation "
           "for bubble participation, not merely a behavioural one.")
    d.p("The biases at work during bubbles: OVERCONFIDENCE above all - overtrading, "
        "underestimating risk, failing to diversify, rejecting contradictory information. "
        "In a rising market almost every sale is profitable, so CONFIRMATION and "
        "SELF-ATTRIBUTION biases convert luck into perceived skill. REGRET AVERSION draws "
        "in those who feel they are missing out. As the bubble unwinds, ANCHORING makes "
        "markets underreact, cognitive dissonance leads investors to rationalise losses, "
        "and eventual capitulation accelerates the decline.")
    d.h3("Value versus growth")
    d.p("Fama and French found value stocks - high book-to-market, low P/E, low "
        "price-to-dividend - beat growth stocks in 12 of 13 major markets over 1975-1995. "
        "But the anomaly DISAPPEARS in a three-factor model, suggesting size and "
        "book-to-market are compensation for risk, such as greater vulnerability to "
        "distress in downturns.")
    d.p("The behavioural counter-explanation is the HALO EFFECT, a form of "
        "representativeness: a favourable evaluation of one characteristic spreads to "
        "others, so a company with a good growth record and strong past share performance "
        "is assumed to be a good investment with higher expected returns than its risk "
        "warrants. Overconfidence in growth forecasts compounds it.")
    d.p("Related is HOME BIAS - a preference for domestic securities, and even for "
        "companies headquartered near the investor. Explanations include a perceived "
        "informational advantage, comfort from access to management, and a desire to "
        "invest locally. Note also the perverse finding that a more positive emotional "
        "rating leads investors to perceive a stock as LESS risky: CAPM says risk and "
        "expected return move together, but many investors behave as though they move in "
        "opposite directions.")


def module6(d):
    d.h1(6, "Introduction to Risk Management",
         "Risk management is not risk minimisation. It is choosing risks deliberately, "
         "sizing them, measuring them continuously, and keeping them aligned with a "
         "tolerance decided in advance.")

    d.h2("6.1  What risk management actually is")
    d.formula("Risk management is the process by which an organisation or individual\n"
              "defines the level of risk to be taken, measures the level of risk being\n"
              "taken, and adjusts the latter toward the former - with the goal of\n"
              "maximising the entity's value or the individual's utility.",
              "Note the three verbs: DEFINE, MEASURE, ADJUST. Nothing in the definition "
              "mentions reducing or avoiding risk.")
    d.key("A company that shied away from all risk would find it could not operate. Risk "
          "management is not about avoiding risk any more than a practical diet is about "
          "avoiding calories.")
    d.h3("Three meanings of the word 'risk'")
    d.p("The curriculum separates them carefully, using a yen example. An announcement "
        "will move the yen up or down by 1%, and you hold JPY 1,000,000.")
    make_table(d,
               ["Term", "In this example", "Meaning"],
               [["Risk driver", "The uncertain ±1% move", "The underlying uncertainty"],
                ["Risk position", "JPY 1,000,000 held", "The size of the risky action taken"],
                ["Risk exposure", "±JPY 10,000", "The potential valuation change"]],
               widths=(30, 42, 66))
    d.p("Here exposure is simply position times driver. In practice all three get called "
        "'risk', which is why questions often turn on which one is meant.")
    d.h3("The Doctrine of No Surprises")
    d.p("A risk manager is not expected to predict the crisis. They are expected to have "
        "already quantified what the crisis would cost. Before 2008 a good bank risk "
        "manager would not have known a real estate crisis was coming, but would have told "
        "the board that such a crisis could destroy 60% of capital, forced a governance "
        "discussion about whether that was tolerable, and hedged the portion that was not. "
        "The only surprise should be the market shock itself.")
    d.key("In a good risk management process most of the work happens BEFORE the event. "
          "In a poor one just as much work gets done - but all of it afterwards, once the "
          "damage is already done.")
    d.p("The benefits of doing it well: fewer surprises and a known cost when they occur; "
        "better decision discipline and risk-return trade-offs; faster response through "
        "active monitoring; fewer operational errors; more trust between the board and "
        "management, which supports effective delegation; and a better reputation with "
        "analysts and investors. Together these raise enterprise value.")

    d.h2("6.2  The risk management framework")
    d.numbered([
        "RISK GOVERNANCE - the top-down foundation. Board-level. Sets goals, defines risk "
        "tolerance, provides oversight.",
        "RISK IDENTIFICATION AND MEASUREMENT - the analytical core. Analysing risk "
        "drivers, tracking exposures, computing metrics under scenarios and stresses. "
        "Includes qualitative assessment, not only quantitative.",
        "RISK INFRASTRUCTURE - the people and systems. Risk capture, databases, models, a "
        "stress engine, reporting, and skilled staff. With heavier reliance on technology, "
        "more testing is needed to avoid the irony of errors originating inside the risk "
        "system itself.",
        "POLICIES AND PROCESSES - governance extended into daily operations. Limits, "
        "constraints, due diligence, escalation procedures, checklists.",
        "RISK MONITORING, MITIGATION AND MANAGEMENT - the day-to-day work. Recognising "
        "when exposure has drifted outside tolerance and acting.",
        "COMMUNICATION - continual, across all levels, with a feedback loop back to the "
        "governing body. Reporting matters MORE, not less, when limits are breached.",
        "STRATEGIC ANALYSIS AND INTEGRATION - the offensive use. Sorting out which "
        "activities add value and which do not, and feeding that back into decisions.",
    ])
    d.p("For an individual the same framework applies in reduced form: set goals; choose "
        "investments and identify their risks; evaluate exposure; consider ways to modify "
        "it; implement; and review periodically. The individual acts as their own "
        "governing body while an adviser performs the management role. The curriculum's "
        "warning is that individuals often decide risk management is too complicated and "
        "skip it - at essentially the same cost as a corporation would face, only with "
        "less money involved.")
    d.p("When risk is genuinely integrated into every decision rather than bolted on "
        "afterwards, the organisation has an effective RISK CULTURE.")

    d.h2("6.3  Risk governance and risk tolerance")
    d.p("ENTERPRISE RISK MANAGEMENT means focusing risk activity on the objectives, health "
        "and value of the WHOLE organisation, using the entire economic balance sheet "
        "rather than assets alone.")
    d.h3("Why the enterprise view matters - the pension case")
    d.p("A pension fund manager maximising only the fund's ASSETS may ruin the sponsor. "
        "Pension liabilities are bond-like, so an all-equity fund faces a market collapse "
        "and falling interest rates simultaneously: assets fall while liabilities rise in "
        "value, and the fund becomes insolvent.")
    d.p("A true enterprise view goes further still and considers the PARENT COMPANY. In "
        "that same collapse the sponsor is probably in recession, so demands for extra "
        "contributions arrive exactly when they are hardest to meet. Factoring in the "
        "corporate risk profile lowers the appropriate risk tolerance again.")
    d.p("For individuals the equivalent is total wealth, not just the portfolio. Someone "
        "with a career in real estate should hold fewer real estate securities. And three "
        "retirees - one with an inflation-linked pension, one with a fixed pension, one "
        "with no pension at all - require completely different solutions. Because of the "
        "variability of an individual life cycle and the discreteness of personal goals, "
        "the curriculum argues the enterprise view is EVEN MORE important for individuals "
        "than for institutions.")
    d.h3("Governance structures")
    d.bullets([
        "A RISK MANAGEMENT COMMITTEE gives senior decision-makers a regular forum, "
        "paralleling the board's deliberations at an operational level. It does NOT "
        "approve the governing body's policies.",
        "A CHIEF RISK OFFICER builds and runs the framework and participates in strategic "
        "decisions - this is not purely a policing role. The curriculum's argument: it "
        "makes no more sense for the CEO to act as CRO than to act as CFO.",
    ])
    d.h3("Setting risk tolerance")
    d.p("Risk tolerance identifies the extent to which the organisation is willing to "
        "experience losses or opportunity costs and to fail in meeting its objectives. It "
        "requires two analyses combined:")
    d.bullets([
        "The INSIDE view - what shortfalls would cause us to fail, or to miss critical "
        "goals?",
        "The OUTSIDE view - what uncertain forces are we exposed to? What are our risk "
        "drivers?",
    ])
    d.p("The Spanish construction equipment example makes it concrete. Inside: a 5-10% "
        "revenue drop is survivable, but a 20% drop triggers debt covenants and imperils a "
        "flagship product launch; EUR 40 million of annual cash flow is needed for "
        "critical capital expenditure and almost none of it can be at risk. Outside: three "
        "uncontrollable drivers - the US dollar, interest rates, and industrial sector "
        "equity returns. The board therefore caps cash flow variation at EUR 10 million a "
        "year and revenue exposure at minus 10% in a global recession, which then shapes "
        "financing choices and drives a hedging programme.")
    d.warn("Risk tolerance must be decided and communicated BEFORE a crisis. Many "
           "organisations only hold the discussion afterwards, which the curriculum "
           "compares to buying insurance after the loss has occurred.")
    make_table(d,
               ["Factors that SHOULD drive risk tolerance",
                "Factors that often do but SHOULD NOT"],
               [["Goals and strategy",
                 "Personal motivations and beliefs of board members (the agency problem)"],
                ["Areas of genuine expertise", "Company size"],
                ["Ability to respond dynamically to adverse events",
                 "Whether markets currently seem stable"],
                ["Loss the firm can sustain as a going concern", "Short-term pressures"],
                ["Competitive and regulatory landscape",
                 "Management compensation arrangements"]],
               widths=(70, 74))
    d.p("Good governance also steers WHERE risk is taken. Pursue risk in areas of core "
        "competence, where the firm is positioned to create value; limit or hedge non-core "
        "risks where it has no comparative advantage. Companies that take risk in areas "
        "where they have no expertise put their core value creation - and sometimes the "
        "whole organisation - at peril.")
    d.p("It is easy to find strategies producing outsized short-term returns at extreme "
        "risk. Selling put options on your own equity raises short-term profits and "
        "dramatically increases the chance of failure in a market decline; excessive "
        "leverage does the same. A formal risk tolerance naturally steers the discussion "
        "away from strategies that simply trade ruin for return.")

    d.h2("6.4  Risk budgeting")
    d.p("Where risk tolerance says HOW MUCH, risk budgeting says HOW AND WHERE. It "
        "quantifies and allocates the tolerable risk using specific metrics, bridging the "
        "gap between one high-level board decision and thousands of operating choices.")
    d.p("The key shift is to view a portfolio by risk characteristics rather than by "
        "product labels. A portfolio described as 20% hedge funds, 30% private equity and "
        "50% stocks and bonds might equally be described as 70% driven by global equity "
        "returns, 20% by domestic equity and 10% by interest rates, with 45% illiquid. The "
        "two descriptions coexist, and the risk view is usually more informative - some "
        "equities are low risk and some hedge funds are very high risk, so the product "
        "label tells you little.")
    d.bullets([
        "Single-dimension budgets: standard deviation, beta, value at risk, or scenario "
        "loss. Even the simplest measure delivers real benefits.",
        "Multi-dimensional budgets: allocation by underlying risk class, or by factor "
        "exposures - a beta target with value and momentum tilts layered on top.",
    ])
    d.key("The hidden benefit of risk budgeting is that it forces trade-offs into every "
          "decision. Once the budget binds, you must choose where return per unit of risk "
          "is highest, and you must compare each active bet against simply buying the "
          "market and hedging. Every risky decision is measured against a passive "
          "alternative on a risk-equivalent basis - so the framework pushes you to add "
          "value in each decision rather than merely to be paid for risk.")
    d.p("Individuals frequently fail here without noticing. The classic case is holding "
        "employer stock in a personal portfolio, which concentrates the total wealth "
        "budget - financial plus human capital - into one firm and one industry. It almost "
        "never comes from a formal plan; it comes from inaction.")

    d.h2("6.5  Identifying risks")
    d.h3("Financial risks - arising from the financial markets")
    make_table(d,
               ["Risk", "Definition and notes"],
               [["Market risk",
                 "Movements in interest rates, stock prices, exchange rates and commodity "
                 "prices. The most visible risk, with abundant data - risk management "
                 "knowledge is most advanced here."],
                ["Credit risk",
                 "Loss if a counterparty fails to pay an obligation. Also called default "
                 "or counterparty risk. With swaps and forwards either party can end up "
                 "owing, so credit risk is BILATERAL. Defaults have far longer-lasting "
                 "consequences than price falls, which can reverse."],
                ["Liquidity risk",
                 "A significant downward valuation adjustment when selling. Note "
                 "carefully: a known bid-ask spread is a COST, not a risk. The RISK is the "
                 "UNCERTAINTY of that spread - it could be called transaction cost risk."]],
               widths=(30, 114))
    d.p("Liquidity risk has two sources: market liquidity varies over time, and the cost "
        "and uncertainty of liquidation rise with position size relative to normal trading "
        "volume. In extreme cases there may be no price above zero at which the asset can "
        "be sold.")
    d.h3("Non-financial risks")
    d.bullets([
        "SETTLEMENT RISK - you pay, the counterparty goes bankrupt before delivering. Also "
        "called Herstatt risk, after the German bank that failed in 1974 after receiving "
        "overnight payments. Often arises from time zone differences.",
        "LEGAL RISK - being sued, or a contract not being upheld. Even a seemingly weak "
        "case can prevail in court.",
        "REGULATORY, ACCOUNTING and TAX RISK - collectively compliance risk. Rules always "
        "lag financial innovation, so updates bring unexpected costs, back taxes, "
        "restatements and penalties.",
        "MODEL RISK - valuation error from using the wrong model, or the right model "
        "wrongly. Assuming constant dividend growth when growth is not constant is the "
        "curriculum's simplest example.",
        "TAIL RISK - more extreme events than probability models predict. Ignoring tail "
        "risk is itself a form of model risk, arising from internal modelling choices.",
        "OPERATIONAL RISK - inadequate or failed people, systems and internal processes, "
        "plus external events affecting operations.",
        "SOLVENCY RISK - running out of cash, even while otherwise solvent.",
    ])
    d.h3("How badly the normal distribution fails")
    d.p("S&P 500 monthly returns, January 1950 to October 2018: mean 0.70%, standard "
        "deviation 4.10%. Under a normal distribution:")
    make_table(d,
               ["Month", "Return", "Expected frequency under normality"],
               [["October 1987", "−21.76%", "Once every 2,199,935 years"],
                ["October 2008", "−16.94%", "Once every 6,916 years"],
                ["August 1998", "−14.58%", "Once every 654 years"],
                ["October 1974", "+16.30%", "Once every 888 years"]],
               widths=(38, 26, 80))
    d.warn("All three of those crashes occurred inside a single 68-year window. If the "
           "normal distribution described returns, they should never have happened. It is "
           "safe to reject normality for at least another two million years - yet option "
           "models, portfolio construction and asset allocation routinely assume it. This "
           "is why market risk is so often dealt with in an oversimplified way.")
    d.h3("Operational risk in detail")
    d.bullets([
        "Employees - theft, but also honest mistakes. Crediting USD 100,000 for a USD 100 "
        "deposit is an innocent error that can lose money very fast. Accounting fraud has "
        "often been committed to make a company look better rather than for personal gain.",
        "Rogue traders - personified by Nick Leeson, whose speculative trades destroyed "
        "the 200-year-old Barings Bank in 1995. The defining feature is trading without "
        "regard for the organisation's limits or controls.",
        "Business interruption - floods, earthquakes, hurricanes. External and "
        "uncontrollable, but that does NOT excuse failing to prepare. Generators, backup "
        "facilities and remote working are cheap.",
        "Cyber risk - hackers succeed only where systems are vulnerable, so security is "
        "the organisation's responsibility. Under GDPR, breaches of sensitive personal "
        "data must be notified within 72 hours, with fines of several million euros for "
        "failure - and this applies to organisations outside the EU that target European "
        "citizens.",
        "Terrorism - after the 1993 World Trade Center attacks many firms established "
        "distant backup facilities, which proved decisive in 2001.",
    ])
    d.h3("Solvency risk")
    d.p("The most underappreciated risk before 2008. Lehman Brothers is usually described "
        "as a leverage failure, and leverage certainly contributed, but what actually "
        "forced the bankruptcy was solvency: funding disappeared almost overnight once "
        "counterparties refused Lehman's credit risk. Even a day of large market GAINS "
        "would not have saved it - it had already been destroyed by solvency risk.")
    d.p("Solvency risk is the clearest argument for the enterprise view. A university "
        "endowment might hold a perfectly balanced portfolio in isolation, but in a deep "
        "recession tuition revenue, grants and donations all fall at the same time as "
        "portfolio values and distributions - forcing emergency actions that impair the "
        "endowment purely because the wider enterprise needs cash.")
    d.p("It is easily mitigated but never eliminated, and none of the safeguards is free: "
        "less leverage, more stable financing, better transparency, holding more cash "
        "equivalents and fewer illiquid assets.")
    d.h3("Risks specific to individuals")
    d.bullets([
        "HEALTH RISK - direct costs, reduced income through disability, reduced lifespan "
        "or quality of life.",
        "MORTALITY RISK - dying young, ending the income stream a family depends on.",
        "LONGEVITY RISK - outliving your resources. Insurers and DB plans only need "
        "reliable GROUP averages from mortality tables; an individual has no idea which "
        "side of the average they will fall on, which is why DC investors face a genuinely "
        "harder problem.",
        "PROPERTY AND CASUALTY - fire, natural disaster, liability from harming others.",
    ])

    d.h2("6.6  Risks interact - and they compound")
    d.key("Market risk begets credit risk, which begets operational risk. Risks are almost "
          "never independent, and the combined risk is practically always worse than the "
          "sum of the parts. Most risk models do not capture the interaction, which makes "
          "the consequence worse still.")
    d.h3("Wrong-way risk")
    d.p("You buy an out-of-the-money put with a JPY 1,000 strike from Counterparty C. "
        "Assuming a 2% default probability INDEPENDENT of the market, the contract prices "
        "at about JPY 98 rather than JPY 100.")
    d.p("But C's default probability is not independent. It is far higher precisely when "
        "the equity market has collapsed - which is exactly when the put pays. The real "
        "default probability in that state might be 10% or more. In the extreme event "
        "where you should receive JPY 1,000, you will very likely receive nothing. You "
        "bore far more risk than you thought and you OVERPAID for the contract.")
    d.p("This pattern was widespread in 2008, when holders of mortgage credit securities "
        "believed their risks were well diversified when in truth they were systematic.")
    d.h3("Non-linearity")
    make_table(d,
               ["Baseline loss", "Outcome for a 2× levered firm with liquidity strain"],
               [["1%", "2% - simple leverage, as expected"],
                ["10%", "25% rather than 20% - liquidity and funding stress begins to bite"],
                ["30%", "Failure - the toxic interplay of leverage and liquidity"]],
               widths=(34, 110))
    d.p("This is what happened to many banks and funds in 2008 and to Long-Term Capital "
        "Management in 1998: leverage manifesting as higher market risk, interacting "
        "toxically with liquidity and solvency risk. It is also why up-front SCENARIO "
        "PLANNING is so valuable - linear models simply do not capture it.")
    d.p("The individual equivalent is employer stock again: market risk and human capital "
        "risk interacting so that a single event takes the job and the savings together.")

    d.h2("6.7  Measuring risk")
    d.p("Risk drivers originate in the global and domestic macroeconomy, in industries, "
        "and in individual companies. Risk management can influence some of this but not "
        "all of it - a risk manager can reduce the chance their own firm defaults, but "
        "cannot control interest rates. For the latter, the job is to position the firm so "
        "its exposure matches its tolerance.")
    make_table(d,
               ["Measure", "What it captures"],
               [["Probability",
                 "Relative frequency of an outcome. Necessary but far from sufficient on "
                 "its own."],
                ["Standard deviation",
                 "Dispersion. Widely used but may not exist for fat-tailed distributions, "
                 "and overstates risk in a diversified context."],
                ["Beta",
                 "Systematic risk - how much market risk an asset adds to a diversified "
                 "portfolio."],
                ["Delta",
                 "First-order: derivative price sensitivity to a SMALL move in the "
                 "underlying."],
                ["Gamma",
                 "Second-order: how delta itself changes. Captures LARGE moves."],
                ["Vega", "First-order sensitivity to the volatility of the underlying."],
                ["Rho",
                 "Sensitivity to interest rates. Low for most options, high for interest "
                 "rate options."],
                ["Duration",
                 "First-order interest rate sensitivity of a fixed-income instrument - the "
                 "bond analogue of delta."]],
               widths=(34, 110))
    d.h3("Value at risk")
    d.formula("\"Our VaR is GBP 3 million at 5% for one day.\"\n\n"
              "= we expect to lose AT LEAST GBP 3 million in one day, 5% of the time\n"
              "= a minimum loss of GBP 3 million about once every 20 business days",
              "Three components: an amount, a time period, a probability.")
    d.warn("VaR is a MINIMUM extreme loss, not a maximum. The word 'minimum' is the most "
           "frequently overlooked word in the definition and the most frequently tested. "
           "There is no maximum in a VaR measure - the true maximum is the entire equity "
           "of the organisation.")
    d.p("VaR is simple, accepted by most banking regulators, approved for accounting "
        "disclosure - and controversial. Different estimation methods give widely "
        "different answers. It is subject to model risk: wrong distributional assumption "
        "or wrong inputs, wrong VaR. Critics argue naive users are lulled into false "
        "security by a tolerable-looking number while the real risk is uncontrolled. "
        "Always supplement it.")
    d.bullets([
        "CVaR (conditional VaR) - the weighted average of ALL loss outcomes exceeding the "
        "VaR loss. It tells you how bad the tail is, not merely where it begins.",
        "EXPECTED LOSS GIVEN DEFAULT - the credit analogue: if this issuer defaults, how "
        "much do we lose on average?",
        "EXTREME VALUE THEORY - statistics devoted to the tails, long used by insurers.",
        "SCENARIO ANALYSIS - a package of related stress tests under a common theme, such "
        "as a sharp rate rise combined with a currency collapse.",
        "STRESS TESTING - specific extreme price moves, rare but potentially "
        "destabilising for the whole organisation. Now required of major banks by the US "
        "Federal Reserve and other central banks.",
    ])
    d.h3("Measuring credit and operational risk")
    d.p("Credit analysis leans on rating agencies but also on liquidity ratios such as the "
        "current ratio, solvency ratios such as interest coverage, profitability measures "
        "such as return on assets, and leverage measures such as debt to total assets - "
        "plus the strength and cyclicality of the industry.")
    d.p("The structural difficulty is that credit events are RARE for any one issuer. Very "
        "few companies that default have a history of defaulting. Lehman Brothers had "
        "operated since 1850 without one - imagine assigning it a default probability in "
        "2007. Risk managers therefore pool similar companies, which is essentially what a "
        "credit rating does. Market prices of CREDIT DEFAULT SWAPS, options and insurance "
        "contracts provide a valuable second signal: the market's own ex ante price of the "
        "risk.")
    d.p("Operational risk is harder still. Assessing the probability of an event such as "
        "the 2014 Home Depot card breach - and the years of litigation risk that follow - "
        "is close to impossible from internal data alone, so third parties aggregate "
        "events across many companies and publish statistics. Regulatory, accounting and "
        "political risks often admit no numeric measure at all and revert to subjective "
        "judgement.")

    d.h2("6.8  Modifying risk")
    d.p("Modification is not always reduction. A portfolio targeting 50/50 equity and cash "
        "drifts toward cash when cash outperforms, and beyond a point its risk becomes "
        "unacceptably LOW given the return target - so rebalancing means INCREASING risk.")
    make_table(d,
               ["Method", "What it means", "Typical tool"],
               [["Prevention and avoidance", "Do not take the risk at all",
                 "Strategy, exclusions, governance limits"],
                ["Acceptance", "Bear it, but efficiently",
                 "Self-insurance, reserves, capital, DIVERSIFICATION"],
                ["Transfer", "Pass it to another party",
                 "INSURANCE, surety and fidelity bonds, reinsurance, catastrophe bonds"],
                ["Shifting", "Change the shape of the payoff distribution", "DERIVATIVES"]],
               widths=(38, 50, 56))
    d.h3("Prevention and avoidance")
    d.p("Rarely as simple as it sounds, because avoiding risk usually means avoiding the "
        "benefit too. You could eliminate car accident risk by never travelling by car; "
        "you could protect children from all harm at the cost of preparing them poorly for "
        "adult life; you could hold only cash and forgo inflation protection and long-term "
        "growth.")
    d.p("Nearly every risk has an upside as perceived by the risk taker - which is why "
        "people gamble, smoke or skydive despite the apparent costs. These are simply "
        "cases of choosing to bear risk, conceptually identical to an investor accepting a "
        "high degree of portfolio risk. In organisations this is a strategic, board-level "
        "decision, often used to exclude areas so management can concentrate on where it "
        "can add value.")
    d.h3("Acceptance: self-insurance and diversification")
    d.p("Self-insurance means bearing a risk considered undesirable but too costly to "
        "remove - sometimes simply bearing it, sometimes establishing a reserve. A young, "
        "healthy adult without dependants who declines health insurance and sets money "
        "aside is fully self-insuring. Banks self-insure through capital and loan loss "
        "reserves.")
    d.warn("There is a fine line between self-insurance and DENIAL. Reserving against a "
           "loss that sits inside your risk tolerance is good governance. An investment "
           "firm with a EUR 1 billion loss tolerance that leaves a EUR 3 billion rogue "
           "trader exposure unhedged and calls it 'self-insuring' is simply ignoring the "
           "risk and violating its own governance.")
    d.h3("Transfer: insurance")
    d.p("Insurance works through POOLING of low-correlation risks. The insurer charges a "
        "premium covering expected aggregate losses, operating costs and profit, using "
        "actuarial data that is generally readily available. A well-diversified insurer "
        "does not care if one policyholder claims more than average, provided claims are "
        "uncorrelated.")
    d.bullets([
        "Insurers manage their own risk by limiting concentration - not writing too much "
        "Gulf Coast hurricane cover - and by REINSURANCE, selling risk to another insurer. "
        "A Midwest tornado insurer may happily accept some hurricane risk in exchange.",
        "CATASTROPHE BONDS pass insurance risk to bond investors, who may lose principal "
        "or interest if claims exceed a threshold.",
        "DEDUCTIBLES serve three purposes: they cut the number of small claims, each of "
        "which carries a fixed processing cost; they encourage good risk management by the "
        "insured; and they let the insured combine transfer with self-insurance for a "
        "better overall trade-off.",
        "Where risks CANNOT be pooled - one Olympics, one volatile film star - specialist "
        "cover through Lloyd's syndicates is required, with investors bearing losses "
        "directly. Because such risks are uncorrelated with each other, writing several of "
        "them still achieves some diversification.",
        "SURETY BONDS pay if a third party fails to perform; FIDELITY BONDS cover employee "
        "dishonesty. In this context 'bond' means an assurance, not a debt security.",
    ])
    d.h3("Shifting: derivatives")
    d.p("Risk transfer passes risk to another party; risk SHIFTING changes the "
        "distribution of outcomes - adjusting the payoff diagram itself. A company willing "
        "to make slightly less profit if markets rise, in exchange for not losing more "
        "than 20% if they fall, is shifting risk. This is the bulk of hedging and the most "
        "common form of risk modification for financial firms.")
    make_table(d,
               ["", "Forward commitments", "Contingent claims (options)"],
               [["Examples", "Forwards, futures, swaps", "Calls and puts"],
                ["Obligation", "BOTH parties obligated",
                 "Buyer has the right, not the obligation"],
                ["Cash at inception", "NONE", "Premium paid up front"],
                ["Outcome", "Locks in a price or rate; no flexibility",
                 "Keeps the upside, caps the downside"],
                ["Trade-off", "Free, but you give up favourable moves",
                 "Flexible, but you pay for it"]],
               widths=(32, 54, 58))
    d.h3("Worked hedging example")
    d.p("A UK investor holds 60% FTSE 100 and 40% US Treasuries. Unhedged, the portfolio "
        "expects 3.9% with 8.9% risk. Hedging 100% of the currency exposure with a "
        "one-year forward:")
    make_table(d,
               ["", "Unhedged", "Currency hedged"],
               [["Expected return", "3.90%", "3.87%"],
                ["Risk (standard deviation)", "8.9%", "7.6%"]],
               widths=(56, 44, 44), align=("LEFT", "RIGHT", "RIGHT"))
    d.p("Risk falls by 1.3 percentage points for 3 basis points of return - because the "
        "one-year forward price of USD in GBP, 0.7038, is 0.03% below the spot of 0.7040, "
        "and 40% of the portfolio is hedged.")
    d.warn("The hedge is NOT perfect and this detail is examinable. As the Treasury "
           "investment changes value it will be worth more or less than the USD amount "
           "sold forward, leaving the portfolio over- or under-hedged. Because the "
           "investment is expected to GROW, being under-hedged is the likely outcome. "
           "Managing it means comparing the forward's notional value against the "
           "investment at intervals - and how often to do so is itself a trade-off between "
           "monitoring cost, transaction cost and residual risk.")
    d.h3("Choosing a method")
    d.p("No method has a clear advantage; they are not mutually exclusive, and most "
        "organisations use all four. Some airlines hedge fuel and some do not; among those "
        "that do, some prefer the certainty of forwards and swaps and others the "
        "flexibility of options. Some manufacturers hedge currency with derivatives while "
        "others build plants abroad or match currency assets against liabilities.")
    d.numbered([
        "PREVENT AND AVOID first, for risks offering few benefits against potentially "
        "extreme costs - especially those outside core competence. But avoidance may not "
        "be good value, and avoiding risk often means avoiding opportunity.",
        "SELF-INSURE where you can afford it. It avoids external monitoring costs and "
        "gives the greatest flexibility. Few organisations have enough cash to self-insure "
        "everything, and some risks can imperil the entire capital base.",
        "TRANSFER where risks pool effectively and the premium is less than the expected "
        "benefit. Many risks are not insurable cost-effectively, particularly those "
        "affecting many parties at once.",
        "SHIFT with derivatives for financial risks beyond appetite - the most common "
        "choice in that category, though not every risk has a derivative available.",
    ])
    d.key("The methods leave DIFFERENT RISK PROFILES behind, not merely different amounts "
          "of risk. A contingent claim hedge and a forward commitment hedge produce "
          "genuinely different shapes of outcome. Ultimately the decision is always "
          "balancing costs against benefits while producing a risk profile consistent with "
          "the organisation's risk tolerance and governance objectives.")


def appendix(d):
    d.h1("", "Appendix A - Formula sheet",
         "Everything from Volume 9 you may need to compute under exam conditions.")

    d.h3("Module 1 - Portfolio risk and return")
    d.formula("Expected return build-up\n"
              "  1 + E(R) = (1 + r_rF) × [1 + E(π)] × [1 + E(RP)]\n\n"
              "Utility\n"
              "  U = E(r) − ½ A σ²\n\n"
              "Two-asset portfolio return\n"
              "  R_p = w₁R₁ + (1 − w₁)R₂\n\n"
              "Two-asset portfolio risk\n"
              "  σ_p = √( w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρ₁₂σ₁σ₂ )\n\n"
              "Covariance\n"
              "  Cov(R₁,R₂) = ρ₁₂ σ₁ σ₂\n\n"
              "Three-asset portfolio risk\n"
              "  σ_p = √( w₁²σ₁² + w₂²σ₂² + w₃²σ₃²\n"
              "         + 2ρ₁,₂w₁w₂σ₁σ₂ + 2ρ₁,₃w₁w₃σ₁σ₃ + 2ρ₂,₃w₂w₃σ₂σ₃ )\n\n"
              "Equally weighted N-asset portfolio\n"
              "  σ_p² = σ̄²/N + [(N−1)/N] × Cov̄\n\n"
              "Capital allocation line\n"
              "  E(R_p) = R_f + [ (E(R_i) − R_f) / σ_i ] × σ_p\n\n"
              "Test for adding a new asset\n"
              "  [E(R_new) − R_f]/σ_new  >  {[E(R_p) − R_f]/σ_p} × ρ_new,p\n\n"
              "Foreign asset return in domestic currency\n"
              "  R_D = (1 + R_lc) × (1 + R_FX) − 1")

    d.h3("Module 2 - CAPM and performance")
    d.formula("Capital market line\n"
              "  E(R_p) = R_f + [ (E(R_m) − R_f) / σ_m ] × σ_p\n\n"
              "Kinked CML with a higher borrowing rate R_b\n"
              "  w₁ ≥ 0:  E(R_p) = R_f + [(E(R_m) − R_f)/σ_m] σ_p\n"
              "  w₁ < 0:  E(R_p) = R_b + [(E(R_m) − R_b)/σ_m] σ_p\n\n"
              "Risk decomposition\n"
              "  σ_i² = β_i²σ_m² + σ_e²\n\n"
              "Beta\n"
              "  β_i = Cov(R_i,R_m)/σ_m² = ρ_i,m × (σ_i/σ_m)\n\n"
              "Market model\n"
              "  R_i = α_i + β_i R_m + e_i\n\n"
              "CAPM / security market line\n"
              "  E(R_i) = R_f + β_i[E(R_m) − R_f]\n\n"
              "Portfolio beta\n"
              "  β_p = Σ w_i β_i\n\n"
              "Sharpe ratio      (R_p − R_f) / σ_p\n"
              "Treynor ratio     (R_p − R_f) / β_p\n"
              "M²                (R_p − R_f)(σ_m/σ_p) + R_f\n"
              "M² alpha          M² − R_m\n"
              "Jensen's alpha    α_p = R_p − [R_f + β_p(R_m − R_f)]\n\n"
              "Security characteristic line\n"
              "  R_i − R_f = α_i + β_i(R_m − R_f)\n\n"
              "Non-market security weighting: proportional to α_i / σ_ei²\n"
              "Information ratio: α_i / σ_ei")

    d.h3("Modules 3 to 6")
    d.formula("Diversification ratio\n"
              "  SD of equally weighted portfolio / SD of a randomly selected security\n\n"
              "Utility used in asset allocation\n"
              "  U_p = E(R_p) − λ σ_p²\n\n"
              "Multi-asset expected return\n"
              "  E(R_p) = Σ w_i E(R_i)\n\n"
              "Multi-asset risk\n"
              "  σ_p = √( Σ Σ w_i w_j Cov(R_i,R_j) )\n\n"
              "Inflating a return target to money of the day\n"
              "  FV = PV × (1 + inflation)ⁿ\n\n"
              "Required rate of return\n"
              "  FV / PV = (1 + X)ⁿ   →  solve for X\n\n"
              "Tactical asset allocation contribution\n"
              "  Σ (actual weight − policy weight) × period return")

    # ------------------------------------------------------------------
    d.h1("", "Appendix B - The distinctions most often confused",
         "If you lose marks in Volume 9, it will almost certainly be on one of these.")
    make_table(d,
               ["Confusion", "The distinction that resolves it"],
               [["Risk aversion vs risk tolerance",
                 "Opposites. High tolerance = low aversion = low A."],
                ["Ability vs willingness to take risk",
                 "Ability is objective (horizon, income, wealth vs liabilities). "
                 "Willingness is psychological. On conflict, adopt the LOWER and document "
                 "it."],
                ["CML vs SML",
                 "CML: total risk (σ) on the x-axis, efficient portfolios only. "
                 "SML: systematic risk (β), ANY security. Equal only for "
                 "efficient portfolios."],
                ["Sharpe / M² vs Treynor / alpha",
                 "Total risk vs systematic risk. Not diversified → Sharpe or "
                 "M². Well diversified → Treynor or Jensen's alpha."],
                ["Total risk = systematic + non-systematic",
                 "These add as VARIANCES, never as standard deviations."],
                ["High standard deviation vs high beta",
                 "Unrelated. Gold in the curriculum has market-level SD and a beta of "
                 "ZERO, because correlation is zero."],
                ["Sharpe ratio vs Jensen's alpha",
                 "Sharpe is meaningless alone and must be compared. Alpha is interpretable "
                 "on its own - positive means outperformance."],
                ["Cognitive errors vs emotional biases",
                 "Cognitive: faulty reasoning, MODERATE them. Emotional: feelings, ADAPT "
                 "to them."],
                ["Status quo vs endowment vs regret aversion",
                 "All produce inaction. Status quo is INERTIA; the other two are conscious "
                 "but mistaken choices."],
                ["Conservatism vs anchoring",
                 "Conservatism = under-updating a BELIEF. Anchoring = adjusting "
                 "insufficiently from a starting NUMBER."],
                ["Base-rate vs sample-size neglect",
                 "Both are representativeness. Base-rate ignores population frequency; "
                 "sample-size over-trusts a small sample."],
                ["Liquidity risk vs solvency risk",
                 "Liquidity: uncertainty of the price concession on SELLING an asset. "
                 "Solvency: running out of CASH to operate. Practitioners often call the "
                 "second one liquidity risk too."],
                ["Credit risk vs settlement risk",
                 "Credit: the counterparty cannot pay. Settlement: you paid first and they "
                 "failed before delivering (Herstatt risk)."],
                ["VaR minimum vs maximum",
                 "VaR is a MINIMUM extreme loss at a given probability. There is no "
                 "maximum short of total equity."],
                ["Risk transfer vs risk shifting",
                 "Transfer = insurance, works by POOLING. Shifting = derivatives, works by "
                 "changing the shape of the payoff."],
                ["Forward commitments vs options",
                 "Forwards: no cash up front, both obligated, outcome locked. Options: "
                 "premium up front, buyer has a right only, upside retained."],
                ["Risk tolerance vs risk budgeting",
                 "Tolerance = HOW MUCH risk is acceptable. Budgeting = HOW and WHERE that "
                 "risk gets taken."],
                ["Open-end vs closed-end funds",
                 "Open-end always trades at NAV. Closed-end trades at a premium or "
                 "discount."],
                ["Buyout vs venture capital",
                 "Buyout: a FEW LARGE investments expected to work. VC: MANY SMALL "
                 "investments, most expected to fail."],
                ["DC vs DB pension plans",
                 "DC: the EMPLOYEE bears investment and inflation risk. DB: the EMPLOYER "
                 "does."]],
               widths=(50, 94))

    # ------------------------------------------------------------------
    d.h1("", "Appendix C - The volume in one page",
         "The thread that ties the six modules together.")
    d.p("Volume 9 is not six topics. It is one argument, and if you can state the argument "
        "you can reconstruct most of the detail.")
    d.numbered([
        "SOME RISK IS PAID FOR AND SOME IS NOT. Combining assets that do not move together "
        "lowers risk without lowering return, so any risk you could have diversified away "
        "earns nothing. Only systematic risk - measured by beta - is compensated. "
        "(Modules 1 and 2)",
        "THEREFORE THE PORTFOLIO, NOT THE SECURITY, IS THE UNIT OF ANALYSIS. Judge every "
        "holding by what it contributes to the whole. Enron's employees did not, and lost "
        "their job and their savings in the same event. (Module 3)",
        "BUT 'THE PORTFOLIO' MEANS ALL OF SOMEONE'S WEALTH, NOT JUST THE ACCOUNT YOU "
        "MANAGE. Human capital, pensions, property and liabilities all belong in the "
        "picture. This is why an IPS starts with the person and not the market, and why "
        "the same theory produces a 5%-bond portfolio for Yale and an 80%-bond portfolio "
        "for an insurer. (Module 4)",
        "PEOPLE WILL NOT FOLLOW THE PLAN. They will hold losers, sell winners, ignore "
        "contradictory evidence, anchor on their purchase price, keep employer stock and "
        "do nothing out of inertia. Cognitive errors can be corrected with better process; "
        "emotional biases can only be designed around. (Module 5)",
        "SO YOU NEED MACHINERY TO HOLD THE LINE. Decide the tolerance in advance and in "
        "writing, budget the risk across allocation, tactical bets and selection, measure "
        "exposure continuously, and modify it by avoidance, acceptance, transfer or "
        "shifting when it drifts out of line. (Module 6)",
    ])
    d.key("Risk is not the enemy. Unmeasured, unchosen, unmanaged risk is. Every formula, "
          "every bias and every governance structure in this volume exists to keep the "
          "risk you actually hold lined up with the risk you deliberately chose.")
    d.ln(6)
    d.set_font("DejaVu", "I", 9)
    d.set_text_color(*MUTED)
    d.multi_cell(d.epw, 5,
                 "Prepared as a study companion to the CFA Program Curriculum 2027, "
                 "Level I, Volume 9. The explanations, tables and groupings here are "
                 "original work; the underlying curriculum, its examples and its data are "
                 "the copyright of CFA Institute. Use this alongside the official readings "
                 "and the CFA Institute Learning Ecosystem, not instead of them. "
                 "Candidates report averaging more than 300 hours of preparation per exam "
                 "level.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
