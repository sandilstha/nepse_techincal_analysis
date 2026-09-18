"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 2 - Economics

Run:  venv/Scripts/python.exe docs/make_cfa_v2.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V2-Economics-Summary.pdf")

MODULES = [
    (1, "The Firm and Market Structures", "Competition, pricing power, and how to measure it"),
    (2, "Understanding Business Cycles", "Phases, inflation, unemployment, and the indicators"),
    (3, "Fiscal Policy", "Government spending, taxes, deficits and the multiplier"),
    (4, "Monetary Policy", "Central banks, interest rates, and where their power ends"),
    (5, "Introduction to Geopolitics", "Cooperation, conflict, and assessing political risk"),
    (6, "International Trade", "Why countries trade, and what happens when they restrict it"),
    (7, "Capital Flows and the FX Market", "Exchange rate regimes and the balance of payments"),
    (8, "Exchange Rate Calculations", "Quotes, cross rates, forwards and interest rate parity"),
]

STANDFIRST = ("All eight learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Economics at Level I is two subjects wearing one cover, and it helps enormously to "
        "notice where the join is.")
    d.numbered([
        "Module 1 is microeconomics: one firm, its costs, and how much pricing power its "
        "industry gives it. It stands almost entirely alone.",
        "Modules 2 to 4 are the domestic macro picture: where the economy is in its cycle, "
        "and the two levers governments and central banks pull in response.",
        "Modules 5 to 8 are the international picture: politics between countries, trade "
        "between them, money flowing between them, and the exchange rates that result.",
    ])
    d.p("The two halves are examined very differently. Micro and the exchange rate modules "
        "are calculation-heavy and reward practice. The business cycle, fiscal, monetary and "
        "geopolitics modules are almost entirely descriptive, and reward precise vocabulary "
        "rather than arithmetic.")
    d.key("Module 8 carries the densest calculation load in the volume and the most reliably "
          "examinable content. If time is short, make sure you can do cross rates and "
          "forward points in your sleep.")
    d.warn("The single biggest source of lost marks in this volume is currency notation. The "
           "curriculum writes a quote as price currency over base currency, so USD/EUR means "
           "dollars per euro. Read every exchange rate question twice before doing any "
           "arithmetic, and write down which currency is the base.")


def module1(d):
    d.h1(1, "The Firm and Market Structures",
         "How much can a firm charge? The answer depends almost entirely on how much "
         "competition it faces, and this module sorts industries into four types.")

    d.h2("Elasticity, and why it decides everything")
    d.p("Price elasticity of demand measures how much quantity responds when price changes. "
        "It is the number that decides whether raising a price raises revenue.")
    d.formula("Price elasticity  =  % change in quantity  /  % change in price",
              "Conventionally negative, because the two move in opposite directions. "
              "Candidates usually quote the absolute value.")
    make_table(d,
               ["Elasticity", "Name", "Raise the price and revenue..."],
               [["| E | > 1", "Elastic", "falls; quantity reacts more than price"],
                ["| E | = 1", "Unit elastic", "is unchanged"],
                ["| E | < 1", "Inelastic", "rises; quantity barely reacts"]],
               widths=(22, 26, 52))
    d.example("A company raises its price by 10% and sells 15% fewer units.\n\n"
              "  Elasticity = -15% / +10% = -1.5\n\n"
              "Demand is elastic, so revenue falls. Roughly, revenue changes by the sum of "
              "the two percentages: +10 - 15 = -5%. The price rise was a mistake.")
    d.p("Demand is more elastic when there are close substitutes, when the item is a large "
        "share of the buyer's budget, and when buyers have time to adjust. It is less "
        "elastic for necessities and for anything with no alternative.")

    d.h2("The four market structures")
    make_table(d,
               ["Structure", "Sellers", "Product", "Pricing power", "Barriers"],
               [["Perfect competition", "Very many", "Identical", "None; price taker", "None"],
                ["Monopolistic competition", "Many", "Differentiated", "Some", "Low"],
                ["Oligopoly", "Few", "Either", "Considerable", "High"],
                ["Monopoly", "One", "Unique", "Substantial", "Very high"]],
               widths=(26, 16, 18, 22, 18))
    d.p("Every firm maximises profit at the same place: where the revenue from one more unit "
        "equals the cost of one more unit. What differs is the demand curve each faces.")
    d.formula("Profit is maximised where  MR  =  MC",
              "In perfect competition the firm can sell any quantity at the market price, so "
              "marginal revenue equals price and the rule becomes P = MC.")
    d.key("In the long run, perfect competition and monopolistic competition both drive "
          "economic profit to zero, because new entrants arrive whenever profits are "
          "available. Oligopoly and monopoly can keep earning profit indefinitely, because "
          "the barriers keep entrants out. Barriers to entry, not the number of sellers, are "
          "what preserve profit.")

    d.h3("Oligopoly, the awkward one")
    d.p("With only a few sellers, each one's best move depends on what the others do, so "
        "there is no single model. The curriculum gives you several.")
    d.bullets([
        "Kinked demand curve: rivals match a price cut but ignore a rise, so prices stick.",
        "Cournot: firms choose quantities simultaneously and reach an equilibrium between "
        "the competitive and the monopoly outcome.",
        "Nash equilibrium: nobody can improve their position by changing strategy alone. The "
        "prisoner's dilemma is the standard illustration of why cartels break down.",
        "Stackelberg: one firm moves first and the others react.",
    ])

    d.h2("When to shut down")
    d.p("A loss-making firm does not always close. The decision differs between the short "
        "run, when some costs are already sunk, and the long run, when none are.")
    make_table(d,
               ["Condition", "Short run", "Long run"],
               [["Price above average total cost", "Operate, make a profit", "Stay"],
                ["Price between AVC and ATC", "Operate; losing money but covering variable "
                 "cost and part of fixed", "Exit"],
                ["Price below average variable cost", "Shut down immediately", "Exit"]],
               widths=(32, 40, 28))
    d.warn("The short-run rule compares price with average VARIABLE cost, not average total "
           "cost. If you are covering your variable costs and contributing something towards "
           "fixed costs you already owe, you lose less by staying open. Fixed costs are sunk "
           "and must not enter the decision.")

    d.h2("Measuring concentration")
    d.p("Two measures, and the exam usually asks you to explain why the second is better.")
    d.formula("N-firm concentration ratio  =  sum of the largest N market shares\n\n"
              "Herfindahl-Hirschman Index  =  sum of the SQUARED market shares",
              "Squaring is what makes the HHI useful: it gives disproportionate weight to "
              "the large firms, so it notices when one player dominates.")
    d.example("Four firms hold 40%, 30%, 20% and 10% of a market.\n\n"
              "  Four-firm concentration ratio = 100\n"
              "  HHI = 1,600 + 900 + 400 + 100 = 3,000\n\n"
              "Now suppose instead one firm holds 70% and three hold 10% each.\n\n"
              "  Four-firm concentration ratio = 100, exactly as before\n"
              "  HHI = 4,900 + 100 + 100 + 100 = 5,200\n\n"
              "The concentration ratio cannot tell the two markets apart. The HHI can, and "
              "that is precisely why competition regulators use it.")
    d.warn("Both measures ignore barriers to entry, which is their shared weakness. A market "
           "with one seller but no barriers may be far more competitive than the numbers "
           "suggest, because the threat of entry disciplines prices.")


def module2(d):
    d.h1(2, "Understanding Business Cycles",
         "Economies do not grow smoothly. This module is about the shape of the cycle, what "
         "moves at each stage, and the numbers used to measure it.")

    d.h2("The phases")
    d.p("The cycle is usually described in four stages, though the curriculum stresses that "
        "the boundaries are only clear afterwards.")
    make_table(d,
               ["Phase", "What is happening"],
               [["Expansion", "Output rising, unemployment falling, confidence building"],
                ["Peak", "Growth stalls; inflation pressure is usually at its highest"],
                ["Contraction", "Output falling; two consecutive quarters is the informal "
                 "definition of a recession"],
                ["Trough", "The low point, before recovery begins"]],
               widths=(24, 76))
    d.p("Inventories are the classic early signal. When sales slow unexpectedly, inventories "
        "pile up before anyone has decided there is a downturn, so the inventory-to-sales "
        "ratio rises at the start of a contraction and falls at the start of a recovery.")
    d.p("Employment lags. Firms cut hours and overtime before they cut people, because "
        "hiring back is expensive. Unemployment therefore keeps rising after the economy has "
        "already turned.")

    d.h2("Real and nominal output")
    d.p("Nominal GDP is measured at today's prices, so it rises when output rises and also "
        "when prices rise. Real GDP holds prices fixed at a base year, so it isolates the "
        "change in actual production. Only real GDP tells you whether an economy grew.")
    d.formula("GDP deflator  =  (nominal GDP / real GDP) x 100",
              "Rearranged, real GDP = nominal GDP x 100 / deflator. This is the standard "
              "one-line calculation the exam asks for.")
    d.example("Nominal GDP rises from Rs 800bn to Rs 900bn, and the deflator rises from 100 "
              "to 108.\n\n"
              "  Real GDP now = 900 x 100 / 108 = Rs 833.3bn\n"
              "  Real growth  = 833.3 / 800 - 1 = 4.2%\n\n"
              "Nominal growth was 12.5%, but 8 points of it was inflation. The economy grew "
              "4.2%, not 12.5%.")

    d.h2("Measuring unemployment")
    d.p("Three kinds of unemployment, and the distinction decides whether policy can help.")
    make_table(d,
               ["Type", "Cause", "Can policy fix it?"],
               [["Frictional", "People moving between jobs", "Never eliminated, and some is "
                 "healthy"],
                ["Structural", "Skills no longer match the jobs available", "Only slowly, "
                 "through training"],
                ["Cyclical", "Weak demand in a downturn", "Yes; this is what fiscal and "
                 "monetary policy target"]],
               widths=(20, 40, 40))
    d.p("Add frictional and structural together and you have the natural rate of "
        "unemployment: the level that persists even when the economy is running normally. "
        "Full employment does not mean zero unemployment.")
    d.bullets([
        "Labour force: people working or actively looking. Anyone not looking is outside it.",
        "Unemployment rate: the unemployed as a share of the labour force.",
        "Participation rate: the labour force as a share of the working-age population.",
        "Discouraged workers: people who have given up looking. They leave the labour force, "
        "which perversely lowers the unemployment rate.",
        "Underemployed: working part-time or below their skill level, counted as employed.",
    ])
    d.warn("A falling unemployment rate is not automatically good news. If people are leaving "
           "the labour force in despair, the rate falls because the denominator shrank. "
           "Always check the participation rate alongside it.")

    d.h2("Measuring inflation")
    make_table(d,
               ["Index", "Measures"],
               [["Consumer price index", "A fixed basket bought by households"],
                ["Producer price index", "Prices received by producers; often leads the CPI"],
                ["GDP deflator", "Everything produced domestically, with updating weights"]],
               widths=(30, 70))
    d.p("Headline inflation includes everything. Core inflation strips out food and energy, "
        "because those are volatile and often driven by supply shocks that reverse. Central "
        "banks watch core; households feel headline.")
    d.formula("Index level  =  (basket cost now / basket cost in the base period) x 100\n\n"
              "Inflation rate  =  (index_now / index_before)  -  1")
    d.key("A fixed-basket index such as the CPI overstates inflation, for three reasons the "
          "exam asks about by name. Substitution bias: people buy less of what has become "
          "expensive. Quality bias: goods improve, so part of a price rise buys more. New "
          "product bias: the basket updates slowly and misses cheaper new goods.")
    d.p("Inflation has two classic causes, and the distinction matters because the cure "
        "differs. Demand-pull inflation comes from too much spending chasing limited output, "
        "and raising interest rates addresses it. Cost-push inflation comes from rising input "
        "costs, and raising rates does not fix the cause while still slowing the economy.")

    d.h2("Economic indicators")
    make_table(d,
               ["Type", "Timing", "Examples"],
               [["Leading", "Turn before the economy", "Share prices, new orders, building "
                 "permits, the slope of the yield curve"],
                ["Coincident", "Turn with the economy", "Industrial production, personal "
                 "income, employees on payrolls"],
                ["Lagging", "Turn after the economy", "Duration of unemployment, the "
                 "inventory-to-sales ratio, the average prime rate"]],
               widths=(20, 26, 54))
    d.warn("Share prices are a LEADING indicator and unemployment is a LAGGING one. "
           "Candidates routinely reverse these, which makes an otherwise free mark "
           "disappear. The stock market is anticipating; the labour market is catching up.")


def module3(d):
    d.h1(3, "Fiscal Policy",
         "What governments do with spending and taxation, why the effect is larger than the "
         "amount spent, and why the timing usually goes wrong.")

    d.h2("The two objectives")
    d.p("Fiscal policy has a stabilisation purpose, smoothing the cycle, and a distributional "
        "purpose, changing who ends up with what. The curriculum is mostly concerned with the "
        "first, but expects you to know both exist.")
    d.bullets([
        "Expansionary: spend more or tax less. Used in a contraction. Raises the deficit.",
        "Contractionary: spend less or tax more. Used when the economy is overheating.",
    ])
    d.p("Some of this happens with nobody deciding anything. Automatic stabilisers are the "
        "parts of the budget that respond on their own: tax receipts fall in a downturn "
        "because incomes fall, and unemployment benefits rise because more people claim "
        "them. Both cushion the fall without any new legislation.")

    d.h2("The multiplier")
    d.p("A rupee of government spending raises national income by more than a rupee, because "
        "the recipient spends part of it, and so does the next person.")
    d.formula("Marginal propensity to consume, MPC  =  share of extra income that is spent\n"
              "Marginal propensity to save, MPS     =  1 - MPC\n\n"
              "Multiplier  =  1 / [ 1 - MPC(1 - t) ]\n\n"
              "  t = the marginal tax rate",
              "Tax dampens the multiplier because part of each round of income is taken out "
              "before it can be spent again.")
    d.example("Households spend 80% of extra income and the marginal tax rate is 25%.\n\n"
              "  Multiplier = 1 / [1 - 0.80(1 - 0.25)]\n"
              "             = 1 / [1 - 0.60] = 1 / 0.40 = 2.5\n\n"
              "Rs 100 of government spending eventually raises national income by Rs 250. "
              "With no tax at all the multiplier would be 1/(1 - 0.8) = 5, so taxation halves "
              "the effect. A higher saving rate does the same thing.")
    d.key("Spending has a bigger immediate effect than an equivalent tax cut, because all of "
          "the spending enters the economy while part of a tax cut is simply saved. This is "
          "the standard comparison question.")

    d.h2("Deficits and debt")
    d.p("A deficit is one year's shortfall; debt is the accumulation of all of them. The "
        "measure that matters is debt relative to the size of the economy, because a large "
        "economy can service a large debt.")
    d.p("Arguments that the debt matters: it may crowd out private investment by pushing up "
        "interest rates, higher future taxes will be needed to service it, and at some point "
        "lenders may refuse. Arguments that it matters less: much of it is owed domestically, "
        "borrowing to fund productive investment can pay for itself, and deficits shrink "
        "automatically as growth returns.")
    d.p("Ricardian equivalence is the proposition that people see through the whole exercise. "
        "If the government borrows today, taxpayers expect higher taxes later, so they save "
        "the difference and the stimulus has no effect. Whether this holds in practice is "
        "disputed, and the exam wants you to be able to state both the idea and the dispute.")

    d.h2("Why the timing goes wrong")
    d.numbered([
        "Recognition lag: it takes months of data to establish that a downturn has begun.",
        "Action lag: the budget process is slow, and spending needs legislation.",
        "Impact lag: once approved, construction and hiring take time to affect the economy.",
    ])
    d.warn("The lags are why fiscal stimulus so often arrives when the recovery is already "
           "under way, adding to a boom instead of cushioning a bust. Monetary policy has a "
           "much shorter action lag, which is the main practical argument for using it first.")


def module4(d):
    d.h1(4, "Monetary Policy",
         "What central banks actually control, how that control is transmitted, and the "
         "circumstances in which it stops working.")

    d.h2("Money and the central bank")
    d.p("Money serves three purposes: a medium of exchange, a store of value, and a unit of "
        "account. Commercial banks create most of it by lending: a loan credits a deposit "
        "that did not previously exist.")
    d.formula("Money multiplier  =  1 / reserve requirement",
              "A 10% reserve requirement implies a maximum multiplier of 10. In practice "
              "banks hold excess reserves and borrowers repay, so the realised figure is "
              "always lower.")
    d.p("A central bank typically has responsibility for the currency, for price stability, "
        "for supervising the banking system, for acting as lender of last resort, and for "
        "managing the government's accounts.")

    d.h2("The three tools")
    make_table(d,
               ["Tool", "How it works", "Used"],
               [["Policy rate", "The rate at which the central bank lends to banks; it "
                 "anchors every other short rate", "Constantly; the main lever"],
                ["Open market operations", "Buying or selling government securities to add "
                 "or drain reserves", "Routinely, to hold rates on target"],
                ["Reserve requirement", "The share of deposits banks must hold back",
                 "Rarely; too blunt"]],
               widths=(24, 50, 26))

    d.h2("Inflation targeting")
    d.p("Most modern central banks announce an inflation target, commonly around 2%, and set "
        "rates to meet it. Three features make it work: independence from the government, "
        "credibility so that expectations anchor to the target, and transparency so that "
        "markets can anticipate.")
    d.p("The target is not zero, deliberately. A small positive figure leaves room to push "
        "real rates below zero in a downturn, offsets measurement bias in the index, and "
        "keeps a safety margin against deflation, which is much harder to escape.")
    d.formula("Neutral rate  =  real trend growth  +  inflation target",
              "Above the neutral rate policy is restrictive; below it, stimulative. There is "
              "no way to observe the neutral rate directly, which is the practical "
              "difficulty with the whole framework.")
    d.key("Real interest rate = nominal rate - expected inflation. This one line explains why "
          "a central bank raising nominal rates from 2% to 4% while expected inflation goes "
          "from 1% to 6% has actually loosened policy, not tightened it. The exam tests this "
          "reasoning directly.")

    d.h2("Where monetary policy fails")
    d.bullets([
        "The liquidity trap: rates are already near zero, and cutting further does nothing "
        "because nobody wants to borrow at any price.",
        "Deflation: falling prices make people postpone purchases and raise the real burden "
        "of existing debt, and nominal rates cannot go far below zero.",
        "Bond market vigilantes: if investors doubt the bank's commitment to low inflation, "
        "long rates rise even as the policy rate falls.",
        "Banks unwilling to lend: reserves can be added without any new credit reaching "
        "borrowers.",
    ])
    d.p("Quantitative easing is the response to the first of these: buying longer-dated "
        "assets to push down long rates once short rates have run out of room.")
    d.warn("Monetary and fiscal policy interact, and an exam favourite is asking what happens "
           "under each combination. Both expansionary produces strong growth with inflation "
           "risk. Both contractionary slows the economy sharply. Tight monetary with loose "
           "fiscal tends to produce high interest rates alongside a larger public sector, and "
           "the opposite combination produces low rates with a smaller one.")


def module5(d):
    d.h1(5, "Introduction to Geopolitics",
         "A purely descriptive module, and an easy source of marks. Nothing to calculate; "
         "everything depends on using the right term for the right idea.")

    d.h2("Cooperation and the country's stance")
    d.p("The curriculum places any country on two axes: how much it cooperates with others, "
        "and how open it is to the movement of goods, capital, people and information.")
    make_table(d,
               ["Stance", "Description"],
               [["Globalisation", "Cooperative and open. Maximum interdependence"],
                ["Multilateralism", "Cooperative, working through shared institutions"],
                ["Bilateralism", "Cooperation arranged one country at a time"],
                ["Regionalism", "Cooperation within a bloc, much less so outside it"],
                ["Autarky", "Non-cooperative and closed. Self-sufficiency by choice"],
                ["Hegemony", "One dominant country setting the terms for others"]],
               widths=(26, 74))
    d.p("What pushes a country towards cooperation is its resource endowment, its "
        "standardisation with others, and how much it gains from access to foreign markets. "
        "What pushes it away is national security, protection of domestic industry, and "
        "political nationalism.")

    d.h2("The tools countries use on each other")
    d.bullets([
        "National security tools: military action, alliances, espionage.",
        "Economic tools: tariffs, quotas, sanctions, export controls, investment screening.",
        "Financial tools: currency arrangements, restricting access to payment systems, "
        "freezing reserves.",
    ])

    d.h2("Classifying the risk")
    make_table(d,
               ["Type", "Meaning"],
               [["Event risk", "A known date: an election, a treaty deadline, a referendum"],
                ["Exogenous risk", "A sudden unanticipated shock: an invasion, a coup"],
                ["Thematic risk", "A slow-building pressure: climate, migration, "
                 "demographics, technology rivalry"]],
               widths=(24, 76))
    d.p("Each is then assessed on three dimensions: how likely it is, how quickly it would "
        "bite, and how large the impact would be. Velocity is the one candidates forget. A "
        "high-impact risk that unfolds over a decade calls for a very different response from "
        "one that hits in a week.")

    d.h2("Globalisation and its consequences")
    d.p("Greater openness raises global growth, lowers prices for consumers, and moves "
        "production to wherever it is cheapest. It also increases inequality within "
        "countries, spreads shocks faster between them, and creates dependence on supply "
        "chains a country does not control.")
    d.p("Because of that last point, the curriculum stresses the recent shift away from pure "
        "cost efficiency and towards resilience: nearshoring, dual sourcing and strategic "
        "stockpiles all cost more, and are chosen anyway.")
    d.key("The practical investment consequence is that geopolitical risk raises required "
          "returns and lowers valuations, mostly through uncertainty rather than through any "
          "single realised event. Markets can price a known bad outcome; they struggle to "
          "price an unknown one.")


def module6(d):
    d.h1(6, "International Trade",
         "Why trade makes both sides better off even when one country is better at "
         "everything, and what happens when governments interfere.")

    d.h2("Absolute and comparative advantage")
    d.p("Absolute advantage means producing something with fewer resources than another "
        "country. Comparative advantage means producing it at a lower opportunity cost, "
        "measured in whatever else you gave up to make it.")
    d.key("Comparative advantage is the one that matters, and the point that confuses people "
          "is this: a country can hold an absolute advantage in everything and still gain "
          "from trade. It should specialise in whatever it gives up least to produce, and buy "
          "the rest. Being better at everything does not mean doing everything.")
    d.p("Two models explain where comparative advantage comes from. The Ricardian model "
        "attributes it to differences in labour productivity, driven by technology. The "
        "Heckscher-Ohlin model attributes it to differences in the supply of factors: a "
        "country with abundant labour exports labour-intensive goods, one with abundant "
        "capital exports capital-intensive goods.")

    d.h2("Restrictions on trade")
    make_table(d,
               ["Restriction", "What it does", "Who collects the gain"],
               [["Tariff", "A tax on imports", "The government"],
                ["Quota", "A limit on the quantity imported", "Whoever holds the licence; "
                 "foreign producers if licences go abroad"],
                ["Voluntary export restraint", "The exporting country limits itself",
                 "The foreign exporter"],
                ["Export subsidy", "A payment to domestic producers who export",
                 "Domestic producers, funded by taxpayers"]],
               widths=(28, 34, 38))
    d.p("The effects are always the same in direction. The domestic price rises, domestic "
        "producers gain, domestic consumers lose more than producers gain, and the country as "
        "a whole is worse off. That net loss is the deadweight loss, and it is why economists "
        "oppose protection even though particular groups genuinely benefit.")
    d.warn("A quota and a tariff can restrict imports by exactly the same amount and still "
           "differ in one crucial way: the tariff raises revenue for the government, while a "
           "quota hands that same amount to whoever holds the import licence. If the licences "
           "go to foreign exporters, the money leaves the country entirely.")

    d.h2("Trading blocs")
    d.p("Arrangements between countries come in increasing degrees of integration, and the "
        "exam expects you to place them in the right order.")
    d.numbered([
        "Free trade area: tariffs removed between members, each keeping its own external "
        "tariffs.",
        "Customs union: as above, plus a common external tariff.",
        "Common market: as above, plus free movement of labour and capital.",
        "Economic union: as above, plus common economic institutions and policy.",
        "Monetary union: as above, with a single currency.",
    ])
    d.p("A bloc CREATES trade when production shifts to the lower-cost member, which is "
        "beneficial. It DIVERTS trade when production shifts away from a more efficient "
        "non-member simply because that country still faces the tariff, which is harmful.")

    d.h2("The balance of payments")
    d.bullets([
        "Current account: trade in goods and services, income from abroad, and transfers.",
        "Capital account: transfers of capital assets, a small item in practice.",
        "Financial account: purchases and sales of financial assets, and direct investment.",
    ])
    d.formula("Current account  +  Capital account  +  Financial account  =  0",
              "By construction. A current account deficit must be financed by a financial "
              "account surplus: if a country buys more than it sells, it is selling assets or "
              "borrowing to make up the difference.")


def module7(d):
    d.h1(7, "Capital Flows and the FX Market",
         "Why currencies move, how countries choose to manage them, and what a persistent "
         "imbalance does to an economy.")

    d.h2("What the FX market is for")
    d.p("The market exists to settle trade, to let investors buy foreign assets, to hedge, "
        "and to speculate. By volume, trade is a small fraction of it. Capital flows dominate "
        "the market, and they dominate currency movements too.")
    d.p("Participants divide into the sell side, mainly large banks making prices, and the "
        "buy side: corporations, real money accounts such as pension funds, leveraged "
        "accounts such as hedge funds, governments and central banks.")

    d.h2("Exchange rate regimes")
    make_table(d,
               ["Regime", "How the rate is set", "Monetary independence"],
               [["Formal dollarisation", "Another country's currency is used", "None"],
                ["Currency board", "Fixed by law, fully backed by reserves", "None"],
                ["Conventional peg", "Fixed to a currency or a basket", "Very little"],
                ["Crawling peg", "Adjusted gradually along an announced path", "Little"],
                ["Managed float", "Market-determined, with intervention", "Some"],
                ["Independent float", "Market-determined", "Full"]],
               widths=(26, 44, 30))
    d.key("The impossible trinity: a country can have any two of a fixed exchange rate, free "
          "capital movement, and an independent monetary policy, but never all three. Every "
          "row of the table above is a different choice about which one to give up.")

    d.h2("What moves an exchange rate")
    d.bullets([
        "Relative interest rates: higher real rates attract capital and support the currency, "
        "at least in the short run.",
        "Relative inflation: persistently higher inflation erodes a currency over time. This "
        "is purchasing power parity, which holds only over long horizons.",
        "Growth and productivity: faster growth attracts investment.",
        "The current account position: a persistent deficit is a persistent supply of the "
        "currency onto the market.",
        "Risk sentiment: in a crisis, capital moves to safe-haven currencies regardless of "
        "the fundamentals.",
    ])
    d.p("Capital flows swamp trade flows in the short run, which is why a currency can "
        "strengthen for years while the country runs a trade deficit.")

    d.h2("Current account imbalances")
    d.p("A deficit is not automatically a problem. It may mean a country is investing more "
        "than it saves, which is normal for a fast-growing economy. It becomes a problem when "
        "it funds consumption rather than investment, or when the financing is short-term and "
        "can leave quickly.")
    d.p("Imbalances correct through three channels. The exchange rate falls, making exports "
        "cheaper. Interest rates rise, cooling domestic demand. And domestic prices adjust "
        "relative to foreign ones.")
    d.warn("The J-curve is a standard question. When a currency depreciates, the trade balance "
           "usually gets WORSE before it gets better: import contracts are already signed and "
           "now cost more in domestic currency, while export volumes take time to respond. "
           "The improvement arrives only once quantities have adjusted.")


def module8(d):
    d.h1(8, "Exchange Rate Calculations",
         "The most calculation-heavy module in the volume, and the most reliably examined. "
         "All of it rests on reading the quote correctly.")

    d.h2("Reading a quote")
    d.p("The curriculum always writes a rate as price currency over base currency. In USD/EUR "
        "the euro is the base, and the number tells you how many dollars one euro costs.")
    d.formula("A/B  =  units of A required to buy one unit of B\n\n"
              "  B is the BASE currency  - the thing being priced\n"
              "  A is the PRICE currency - what you pay in",
              "If the number rises, the base currency has strengthened. Fix this sentence in "
              "your memory; almost every error in this module comes from getting it backwards.")
    d.p("A direct quote gives the domestic price of one unit of foreign currency. An indirect "
        "quote is its reciprocal. Which is which depends on where you are standing, so the "
        "question must tell you.")
    d.p("Dealers quote two prices. The bid is what the dealer pays for the base currency; the "
        "ask is what the dealer sells it for. The ask is always higher, and the gap is the "
        "spread. You always trade at the price that is worse for you.")

    d.h2("Cross rates")
    d.p("When two currencies are each quoted against a third, you can derive the rate between "
        "them.")
    d.example("USD/EUR = 1.1000 and USD/GBP = 1.2500. What is EUR/GBP?\n\n"
              "You want euros per pound. One pound buys 1.25 dollars, and each dollar buys "
              "1/1.10 euros.\n\n"
              "  EUR/GBP = 1.2500 / 1.1000 = 1.1364\n\n"
              "One pound is worth 1.1364 euros. Sanity-check it: the pound is worth more "
              "dollars than the euro is, so it must be worth more than one euro. If your "
              "answer had come out below 1, you inverted something.")
    d.warn("Always sanity-check a cross rate against which currency you expect to be the "
           "stronger. Inverting a quote is the most common error in the entire volume, and "
           "the inverted answer is always among the choices offered.")

    d.h2("Forward rates")
    d.p("A forward rate is agreed today for settlement later. It is not a forecast: it is "
        "forced by the two interest rates, because otherwise there would be free money.")
    d.formula("F  =  S  x  (1 + r_price)  /  (1 + r_base)\n\n"
              "  F = forward rate        S = spot rate\n"
              "  r_price = interest rate of the price currency\n"
              "  r_base  = interest rate of the base currency",
              "Adjust both rates for the actual period. For a 90-day forward use r x 90/360, "
              "following whichever convention the question gives.")
    d.example("Spot USD/EUR = 1.1000. The one-year US rate is 5%, the euro rate 3%.\n\n"
              "  F = 1.1000 x (1.05 / 1.03) = 1.1000 x 1.019417 = 1.12136\n\n"
              "  Forward points = (1.12136 - 1.10000) x 10,000 = 213.6 points\n\n"
              "The euro, the base currency, is worth more dollars forward than spot, so the "
              "euro trades at a forward premium and the dollar at a forward discount. The "
              "dollar had the higher interest rate, and that is the rule: the currency with "
              "the higher interest rate always trades at a forward DISCOUNT.")
    d.key("Why it must be so. Lending dollars at 5% for a year, or converting to euros, "
          "lending at 3% and converting back at the agreed forward rate, must give the same "
          "result. If they differed you would borrow in one and lend in the other and take "
          "the difference risk-free. This is covered interest rate parity, and it holds "
          "tightly in practice because banks arbitrage it continuously.")
    d.p("Forward points are simply the difference between the forward and the spot, scaled. "
        "They are quoted in the last decimal place of the spot rate, so the scaling factor "
        "depends on the pair.")
    d.warn("Covered interest rate parity is enforced by arbitrage and holds. UNCOVERED "
           "interest rate parity, which claims the spot rate will move to offset the interest "
           "differential, is only a theory about expectations and is repeatedly violated in "
           "practice. That violation is what makes the carry trade profitable, and the exam "
           "expects you to know the difference between the two.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place. Economics has far fewer "
        "formulas than Quantitative Methods, so there is no excuse for missing any of them.")

    d.h2("Microeconomics")
    d.formula("Price elasticity  =  %change in Q / %change in P\n"
              "Profit is maximised where  MR = MC\n"
              "Perfect competition:  P = MR = MC\n"
              "Shut down in the short run if P < AVC; exit in the long run if P < ATC\n"
              "N-firm concentration ratio  =  sum of the largest N market shares\n"
              "HHI  =  sum of (market share) squared")

    d.h2("Business cycles and inflation")
    d.formula("GDP deflator   =  (nominal GDP / real GDP) x 100\n"
              "Real GDP       =  nominal GDP x 100 / deflator\n"
              "Index level    =  (basket cost now / basket cost in base) x 100\n"
              "Inflation      =  index_now / index_before - 1\n"
              "Unemployment rate   =  unemployed / labour force\n"
              "Participation rate  =  labour force / working-age population\n"
              "Natural rate        =  frictional + structural")

    d.h2("Fiscal and monetary policy")
    d.formula("MPC  =  share of extra income spent;   MPS  =  1 - MPC\n"
              "Multiplier        =  1 / [1 - MPC(1 - t)]\n"
              "Money multiplier  =  1 / reserve requirement\n"
              "Neutral rate      =  real trend growth + inflation target\n"
              "Real rate         =  nominal rate - expected inflation")

    d.h2("Exchange rates and external accounts")
    d.formula("A/B  =  units of A per one unit of B   (B is the BASE)\n"
              "Cross rate:  A/C  =  (A/B) x (B/C)\n"
              "Forward:     F  =  S x (1 + r_price) / (1 + r_base)\n"
              "Forward points  =  (F - S) x 10,000\n"
              "Balance of payments:  current + capital + financial  =  0")

    d.h2("The things most often got wrong")
    d.bullets([
        "The base currency is the SECOND one in the curriculum's notation.",
        "The higher-interest-rate currency trades at a forward DISCOUNT.",
        "Share prices lead the cycle; unemployment lags it.",
        "The short-run shutdown rule uses average VARIABLE cost, not average total cost.",
        "A quota's gain goes to the licence holder; a tariff's goes to the government.",
        "Comparative advantage, not absolute advantage, is what drives trade.",
        "Covered interest rate parity holds; uncovered parity does not.",
    ])


def build():
    d = Guide(volume=2, subject="Economics")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5, module6, module7, module8):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
