"""Modules 3 and 4 of the Portfolio Construction study guide.

Imported from make_cfa_pc_pdf.py at run time (inside main(), so there is no
circular-import problem: part 1 is fully loaded before this module is read).
"""
from make_cfa_pc_pdf import make_table


def module3(d):
    d.h1(3, "Portfolio Management: An Overview",
         "Why the portfolio - not the security - is the right unit of analysis, the "
         "three-step management process, who the investors are, and what the industry "
         "sells them.")

    d.h2("3.1  The case for a portfolio approach")
    d.p("The whole volume rests on one decision: do you evaluate securities in "
        "isolation, or by what they contribute to the portfolio as a whole? The "
        "curriculum makes the case with a real disaster rather than with algebra.")
    d.h3("Enron")
    d.p("Through the 1990s Enron returned over 27% a year against 13% for the S&P 500 "
        "and was one of the most admired companies in America. Employees held it through "
        "their 401(k). By January 2001 those accounts were worth over USD 2 billion, of "
        "which USD 1.3 billion - 62% - was Enron stock.")
    d.p("The detail that matters: only about USD 150 million of that USD 1.3 billion was "
        "actually restricted from sale. Employees were free to sell the rest and chose "
        "not to. One 67-year-old retiree held all USD 2 million of his retirement savings "
        "in Enron shares. Between January 2001 and January 2002 the price went from about "
        "USD 90 to zero.")
    d.key("The loss was not simply large - it was correlated with everything else these "
          "employees owned. Their wages, their job security and their savings all "
          "depended on the same company. When Enron failed they lost their income and "
          "their retirement at the same moment. The same pattern appeared at Owens "
          "Corning, Northern Telecom, Corning and ADC Telecommunications, where employees "
          "held more than 25% of assets in employer stock while prices fell almost 90%.")

    d.h3("Portfolios reduce risk more than they change returns")
    d.p("The Hong Kong example quantifies it. Five HKSE-listed shares over 16 quarters: "
        "picking one at random gave an average return of 15.1% with 24.9% risk. An "
        "equally weighted portfolio of all five gave the same 15.1% return with only "
        "17.9% risk.")
    d.formula("Diversification ratio = 17.9% / 24.9% = 71.9%",
              "The portfolio's risk is about 72% of the average individual stock's risk. "
              "Lower is better. And this was achieved with five companies from a similar "
              "industry group - across genuinely different industries the ratio would "
              "have been lower still.")
    d.p("Composition also matters, not just the act of diversifying. The equally weighted "
        "portfolio gave 15.1% return at 17.9% risk. An optimised mix - 25% Yue Yuen, 3% "
        "Cathay Pacific, 52% Hutchison Whampoa, 20% Li & Fung, 0% COSCO - gave the same "
        "15.1% return at just 15.6% risk.")

    d.h3("The honest caveat: diversification fails when you need it most")
    make_table(d,
               ["Period", "Mean return", "Diversification ratio"],
               [["Q4 1993 - Q3 2000", "12.6%", "75.1%"],
                ["Q1 2006 - Q1 2009", "−4.7%", "95.8%"],
                ["Q4 2007 - Q1 2009", "−48.5%", "99.4%"]],
               widths=(52, 32, 44), align=("LEFT", "RIGHT", "RIGHT"))
    d.p("Read the third row carefully. A ratio of 99.4% means the diversified portfolio "
        "was almost exactly as risky as a single randomly chosen index. Correlations "
        "converged on one and every market fell together. Diversification did protect "
        "against picking the very worst market, but that was nearly all it did.")
    d.warn("The examinable conclusion: portfolios are most likely to provide RISK "
           "REDUCTION. They do not guarantee downside protection and they do not "
           "eliminate risk. In the face of a worldwide contagion, the curriculum says "
           "flatly, diversification is a false promise.")
    d.p("Modern portfolio theory dates from Markowitz's 1952 article. Its central "
        "conclusion is not merely 'hold portfolios' but 'focus on how the holdings relate "
        "to one another'. Sharpe, Lintner and Treynor then established that only the "
        "non-diversifiable portion of an asset's risk should affect its price - the "
        "insight that becomes the CAPM.")

    d.h2("3.2  The three-step process")
    d.numbered([
        "PLANNING. Understand the client's objectives and constraints, and write the "
        "investment policy statement. It may name a benchmark for later evaluation, and "
        "should be reviewed roughly every three years or whenever circumstances change "
        "materially.",
        "EXECUTION. First set the target asset allocation, then analyse securities, then "
        "construct the portfolio, then trade. Analysis may be top-down (macro to industry "
        "to company) or bottom-up (company specifics first, less concerned with the "
        "economic cycle).",
        "FEEDBACK. Monitor and rebalance as weights drift or the client's needs change; "
        "measure performance against the benchmark and report it. Findings may send you "
        "back to revise the IPS.",
    ])
    d.key("Order matters and is examined directly. Objectives and constraints are set in "
          "PLANNING. Asset allocation and security selection happen in EXECUTION. "
          "Rebalancing and performance reporting happen in FEEDBACK. Of all the decisions "
          "taken, asset allocation is commonly viewed as having the greatest impact on "
          "performance.")

    d.h3("Two portfolios, same theory, opposite answers")
    make_table(d,
               ["Asset class", "Yale endowment", "MassMutual (life insurer)"],
               [["Public equity", "19.1%", "9% (preferred + common)"],
                ["Fixed income", "4.6%", "56% bonds"],
                ["Private equity", "14.2%", "5% partnerships"],
                ["Real assets / real estate", "18.7%", "1% + 14% mortgages"],
                ["Absolute return / hedge funds", "25.1%", "—"],
                ["Cash", "1.2%", "2%"],
                ["Other", "17.2%", "13% (policy loans, other)"]],
               widths=(48, 40, 50))
    d.p("Yale holds under 5% in fixed income; MassMutual holds about 80% in bonds, "
        "mortgages, loans and cash. Neither is wrong. Yale has a perpetual horizon and no "
        "fixed liabilities; the insurer must pay unpredictable claims and faces "
        "regulatory constraints. Identical theory, opposite portfolios, because the "
        "constraints differ. This is the best single argument in Module 3 for why the IPS "
        "must come first.")

    d.h2("3.3  Types of investor")
    d.h3("Individuals and pension plans")
    make_table(d,
               ["", "Defined contribution (DC)", "Defined benefit (DB)"],
               [["What is fixed", "The contribution going in", "The benefit coming out"],
                ["Who bears investment risk", "THE EMPLOYEE", "THE EMPLOYER"],
                ["Who bears inflation risk", "The employee", "The employer"],
                ["Examples",
                 "401(k) US, group personal pension UK, superannuation Australia",
                 "Traditional corporate and public pension schemes"],
                ["Trend", "Growing", "Shrinking - lower cost and risk to the company"]],
               widths=(38, 50, 50))
    d.p("Global pension assets exceeded USD 41 trillion at the end of 2017, with the US, "
        "UK and Japan accounting for over 76%. The DC/DB split varies sharply by country: "
        "Australia is 87% DC and the US 60% DC, while Japan is 96% DB, Canada 95%, the "
        "Netherlands 94% and the UK 82%.")
    d.warn("If a trustee has a fiduciary duty to beneficiaries and the sponsor's "
           "interests conflict with theirs - the sponsor wanting more risk to lower "
           "future funding costs, the beneficiaries wanting safety - the trustee must act "
           "in the BENEFICIARIES' best interests.")

    d.h3("Institutional investors compared")
    make_table(d,
               ["Investor", "Horizon", "Risk tolerance", "Income need", "Liquidity need"],
               [["Individuals", "Varies", "Varies", "Varies", "Varies"],
                ["DB pension plans", "Long", "Quite high",
                 "High if mature, low if growing", "Varies with maturity"],
                ["Endowments & foundations", "Very long (perpetual)", "High",
                 "To meet spending rule", "Quite low"],
                ["Banks", "Short", "Quite low", "To pay depositors", "HIGH"],
                ["Insurance companies", "Short (P&C) / long (life)", "Quite low",
                 "Typically low", "High - to meet claims"],
                ["Investment companies", "Varies by fund", "Varies", "Varies",
                 "High - to meet redemptions"],
                ["Sovereign wealth funds", "Varies", "Varies", "Varies", "Varies"]],
               widths=(34, 30, 22, 32, 32))
    d.p("Endowments and foundations differ in kind: endowments fund the operations of a "
        "non-profit institution, while foundations make grants. US endowments hold about "
        "54% in alternatives, reflecting their perpetual horizon and the influence of the "
        "Yale model. Yale's spending rule illustrates the balancing act: a 5.25% "
        "long-term target with smoothing, so that spending in any year is 80% of last "
        "year's spending plus 20% of the target rate applied to the market value two "
        "years prior. The Wellcome Trust instead targets a 4.5% real return.")
    d.p("Insurance companies split their assets in two. The GENERAL account holds "
        "premiums and is invested conservatively in fixed income under regulatory "
        "guidance. The SURPLUS account is the excess of assets over liabilities and can "
        "target higher returns in equities, real estate, infrastructure and hedge funds. "
        "Life insurers hold longer assets than property and casualty insurers because "
        "their liabilities are longer and far more predictable.")

    d.h2("3.4  The asset management industry")
    d.p("About USD 79 trillion under management at the end of 2017, with roughly 80% in "
        "North America and Europe, but the fastest growth in Asia and Latin America. A "
        "manager is a BUY-SIDE firm because it buys research and execution from SELL-SIDE "
        "broker-dealers.")
    make_table(d,
               ["Category", "Assets", "Revenue", "% of assets", "% of revenue"],
               [["Actively managed", "$64trn", "$258bn", "80%", "94%"],
                ["   of which alternatives", "$12trn", "$117bn", "15%", "43%"],
                ["Passively managed", "$16trn", "$17bn", "20%", "6%"]],
               widths=(52, 24, 24, 26, 26),
               align=("LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"))
    d.key("The asset and revenue columns tell two completely different stories. Passive "
          "management holds a fifth of the world's assets but earns only 6% of the "
          "industry's revenue, because its fees are a fraction of active fees. "
          "Alternatives are the mirror image: 15% of assets producing 43% of revenue, "
          "because they charge both management and performance fees.")
    d.p("SMART BETA sits between the two: simple, transparent, rules-based strategies "
        "tilted toward factors such as size, value, momentum or dividends, with fees and "
        "turnover higher than plain market-cap indexing but below full active management.")
    d.h3("Three industry trends")
    d.bullets([
        "Growth of passive investing. Concentrated among a few providers - the top three "
        "ETF managers hold about 70% of ETF assets. Driven by low cost and by the "
        "difficulty of generating alpha in efficient markets such as US large-cap.",
        "Big data. Social media sentiment, satellite imagery and geolocation data - "
        "retailer car-park occupancy, cargo ship movements - analysed with machine "
        "learning. An information arms race requiring heavy investment in data scientists "
        "and infrastructure.",
        "Robo-advisers. About USD 180 billion by end-2017. Roughly 0.20% a year against "
        "about 1% for a traditional adviser, serving younger and mass-affluent clients "
        "who were previously underserved.",
    ])

    d.h2("3.5  Pooled investment products")
    d.p("A mutual fund is a commingled pool in which each investor has a pro-rata claim "
        "on income and value. Net asset value is computed daily from closing prices.")
    d.h3("Open-end versus closed-end")
    make_table(d,
               ["", "Open-end fund", "Closed-end fund"],
               [["New money", "Accepted; new shares created at NAV",
                 "Not accepted; fixed share count"],
                ["Trades at", "Exactly NAV", "Premium or discount to NAV"],
                ["Growth", "Easy", "Limited"],
                ["Main drawback",
                 "Must hold cash and may be forced to sell assets to meet redemptions",
                 "Cannot easily grow"],
                ["Share of US MF assets", "About 99%", "About 1%"]],
               widths=(30, 54, 54))
    d.p("The curriculum's worked example: a fund starts at USD 10 million with 100,000 "
        "shares at USD 100. Later NAV per share is USD 120. Investor F invests USD "
        "960,000, creating 8,000 new shares; Investor E redeems 5,000 shares for USD "
        "600,000. Net effect: USD 360,000 of new money and 3,000 new shares. Every other "
        "investor's holding and share value is completely unaffected.")
    d.p("Separately, LOAD funds charge a percentage fee on purchase or redemption on top "
        "of the annual fee and are usually sold through brokers who take part of it. "
        "NO-LOAD funds charge only the annual fee. Load funds have declined in "
        "importance.")
    d.h3("Fund types by underlying asset")
    d.bullets([
        "Money market funds - very short instruments; constant or variable NAV; NOT "
        "insured like bank deposits, despite being used as a substitute for them.",
        "Bond funds - maturities from one year to thirty-plus, versus overnight to ninety "
        "days for money market funds. Categories include global, government, corporate, "
        "high yield, inflation-protected and national tax-free.",
        "Stock funds - historically the largest category. Active funds charge more and "
        "trade more, which in many jurisdictions realises more taxable capital gains; "
        "index funds are cheaper and buy-and-hold. The first index fund was launched by "
        "Vanguard in 1976.",
        "Hybrid / balanced funds - both stocks and bonds. More common in Europe than the "
        "US, and growing through lifecycle or target-date funds that automatically shift "
        "from equities to bonds as retirement approaches.",
    ])
    d.h3("Other products")
    make_table(d,
               ["Product", "What distinguishes it"],
               [["Separately managed account (SMA)",
                 "You own the assets directly, not a share of a pool. Fully customisable "
                 "for tax position and ESG exclusions. Drawback: a much higher minimum "
                 "investment."],
                ["Exchange-traded fund (ETF)",
                 "Trades intraday on an exchange like a stock; can be shorted or bought on "
                 "margin; dividends are paid out rather than reinvested; low minimum; NO "
                 "capital gain distributions. Grew from $428bn in 2005 to $4.9trn by "
                 "mid-2018."],
                ["Hedge fund",
                 "Short selling, leverage, absolute return objective, low correlation, and "
                 "a two-part fee - traditionally 2% management plus up to 20% incentive, "
                 "subject to a high-water mark. High minimums and restricted liquidity."],
                ["Private equity / venture capital",
                 "7-10 year life; hands-on involvement in portfolio companies; exit by "
                 "merger, sale or IPO. Fees: management, transaction, carried interest "
                 "(typically 20%, usually only after LPs recover their capital), and "
                 "investment income."]],
               widths=(48, 96))
    d.warn("Buyout funds make a FEW LARGE investments in private companies expecting most "
           "to work. Venture capital funds make MANY SMALL investments expecting most to "
           "fail and a few to pay off spectacularly. Also remember: ETFs are the product "
           "least likely to make a capital gain distribution, and hedge funds are the "
           "pooled vehicle subject to the LEAST regulation.")


def module4(d):
    d.h1(4, "Basics of Portfolio Planning and Construction",
         "Turning a client's life into a written plan: the investment policy statement, "
         "the five constraints, and how the strategic asset allocation is built from it.")

    d.h2("4.1  Why the IPS exists")
    d.p("Portfolio planning is the programme developed BEFORE constructing a portfolio "
        "that defines the client's investment objectives. The investment policy statement "
        "is the written document that governs it. It is the starting point of the entire "
        "management process, and without a full understanding of the client's situation "
        "success is unlikely.")
    d.p("Success here has a specific meaning: the client achieves their important goals "
        "by means they are comfortable with. Both halves matter. A plan that reaches the "
        "target through risks the client cannot stomach will be abandoned halfway - "
        "usually at the worst possible moment.")
    d.p("In several jurisdictions an IPS or equivalent is a legal requirement. UK pension "
        "schemes must have a statement of investment principles under the Pensions Act "
        "1995; the UK regulator suggests reviewing it at least every three years. MiFID "
        "requires firms to categorise clients as eligible counterparties, institutional or "
        "retail, which determines the protections they receive.")
    d.warn("A written IPS is best practice and is sometimes legally required, but it does "
           "NOT ensure that objectives will be achieved. The examinable description is "
           "that it communicates a plan for TRYING to achieve investment success, and "
           "that it works best as a COLLABORATIVE effort between client and manager.")

    d.h3("Structure of an IPS")
    d.bullets([
        "Introduction - describes the client",
        "Statement of purpose",
        "Statement of duties and responsibilities - client, custodian, managers",
        "Procedures - keeping the IPS current and handling contingencies",
        "INVESTMENT OBJECTIVES - risk and return",
        "INVESTMENT CONSTRAINTS - the five categories below",
        "Investment guidelines - how policy is executed: leverage, derivatives, excluded "
        "assets",
        "Evaluation and review",
        "Appendices - strategic asset allocation and rebalancing policy",
    ])
    d.key("The objectives and constraints sections are the ones most closely linked to "
          "the client's distinctive needs. The strategic asset allocation and rebalancing "
          "policy are typically APPENDICES. The statement of duties and responsibilities "
          "is an integral part of the main document, not an appendix - a distinction that "
          "has been tested directly.")

    d.h2("4.2  Risk objectives")
    d.bullets([
        "ABSOLUTE - self-standing, unrelated to any market. 'Do not lose more than 4% of "
        "capital in any 12 months.' Better expressed as a probability: 'with 95% "
        "probability, do not lose more than 4% in any 12 months.' Measured by standard "
        "deviation, variance, or value at risk.",
        "RELATIVE - measured against a benchmark. 'Stay within 4% of the TOPIX return.' "
        "Measured by tracking risk, also called tracking error - the standard deviation "
        "of the differences between portfolio and benchmark returns.",
        "LIABILITY-DRIVEN (LDI) - where the size and timing of future obligations are "
        "known. A pension plan's risk objective becomes minimising the probability of "
        "failing to meet payments as they fall due.",
    ])
    d.p("A note on interpreting tracking error: because it is a one standard deviation "
        "measure, an expected tracking error of 2% means returns fall within roughly 4% "
        "of the index about 95% of the time, assuming normality.")

    d.h2("4.3  Risk tolerance: ability versus willingness")
    make_table(d,
               ["", "Ability BELOW average", "Ability ABOVE average"],
               [["Willingness BELOW average", "Below-average risk tolerance",
                 "Conflict - resolution needed"],
                ["Willingness ABOVE average", "Conflict - resolution needed",
                 "Above-average risk tolerance"]],
               widths=(46, 50, 48))
    d.bullets([
        "ABILITY to bear risk is OBJECTIVE. Time horizon, stability and level of income, "
        "and wealth relative to liabilities. A 20-year horizon allows more scope to "
        "recover from losses than a 2-year horizon. Assets comfortably exceeding "
        "liabilities means high ability.",
        "WILLINGNESS to take risk is SUBJECTIVE - psychology, self-esteem, independence of "
        "thought, financial knowledge and decision style. Assessed by discussion or by a "
        "psychometric questionnaire such as Grable and Joo's five-item instrument, scored "
        "5 to 20, where the sample mean was 12.86 and the median 13.",
    ])
    d.key("When ability and willingness conflict, adopt the LOWER of the two and document "
          "the decision. You may educate a client whose willingness rests on a "
          "miscalculation or misperception. You must NOT try to change a client's "
          "personality - modifying elements of personality is not within the investment "
          "adviser's role.")
    d.h3("The two Gascon cases")
    make_table(d,
               ["", "Marie Gascon", "Jacques Gascon"],
               [["Income", "EUR 250,000, stable, secure job",
                 "EUR 40,000 average, volatile, self-employed"],
                ["Obligations", "None material; owns flat outright",
                 "EUR 10,000/yr to ex-wife and children; EUR 100,000 mortgage"],
                ["Assets", "EUR 1,000,000 savings", "EUR 10,000 savings"],
                ["Horizon", "20 years to retirement at 50",
                 "2-6 years (children aged 12-16 to university)"],
                ["Questionnaire", "Risk tolerant", "Risk tolerant"],
                ["ABILITY", "HIGH", "LOW"],
                ["WILLINGNESS", "HIGH", "HIGH"],
                ["Conclusion", "High risk tolerance overall",
                 "Conflict - adopt the lower; invest relatively cautiously"]],
               widths=(30, 56, 58))
    d.p("The Jacques case is the instructive one. His questionnaire answers and market "
        "views suggest an aggressive investor, but his finely balanced finances and short "
        "horizon say otherwise. The adviser's job is to explain the position honestly and "
        "then recommend a relatively cautious portfolio anyway.")

    d.h2("4.4  Return objectives")
    d.p("Return objectives may be absolute or relative, nominal or real, gross or net of "
        "fees, and pre- or post-tax. Whichever is chosen must be stated explicitly and "
        "agreed - a nominal objective is easier to measure, a real objective usually "
        "relates better to what the client actually wants.")
    d.p("Peer-group objectives - 'top quartile among private equity managers' - are "
        "problematic. You rarely know peers' strategies or return methodology, not all "
        "investors can be above average, and a good benchmark should be INVESTABLE, which "
        "a peer group is not.")
    d.p("Above all the objective must be realistic and consistent with the risk "
        "objective. A 15% nominal return may be achievable when inflation is 10%; it is "
        "unlikely when inflation is 3%. Where expectations are unrealistic, the adviser "
        "must counsel the client on what is actually achievable.")
    d.h3("Worked example - Marie Gascon's required return")
    d.formula("Step 1 - inflate the target to money of the day:\n"
              "  EUR 2,000,000 × (1.02)²⁰ = EUR 2,971,895\n\n"
              "Step 2 - solve for the required growth rate:\n"
              "  EUR 2,971,895 / EUR 900,000 = (1 + X)²⁰\n"
              "  X ≈ 6.2% per year",
              "The EUR 100,000 emergency reserve is EXCLUDED from the calculation - only "
              "the EUR 900,000 retirement portfolio has to reach the target. Watch for "
              "this in the exam: money set aside for liquidity is not part of the growth "
              "problem.")

    d.h2("4.5  The five constraints")
    d.numbered([
        "LIQUIDITY. Expected withdrawals - school fees, healthcare, endowment spending "
        "rules, insurance claims, pension payments. Cover them with liquid, low-risk "
        "assets whose value is known with reasonable certainty at the time the money is "
        "needed. Progressive Corporation, an auto insurer facing unpredictable claim "
        "timing, holds about 77% in fixed maturities plus 10% short-term investments.",
        "TIME HORIZON. The period until assets are drawn on or until circumstances change "
        "materially. A 55-year-old retiring at 65 has a 10-year horizon even though the "
        "portfolio is not liquidated then - its structure must change as income begins. "
        "Long horizons support illiquid and risky assets; short horizons do not, because "
        "there is no time to recover.",
        "TAX. Some investors pay tax, others do not. Income is usually taxed more heavily "
        "than gains, and gains are typically taxed only on realisation, which gives a "
        "time-value benefit. Taxable investors may favour capital gains and, in the US, "
        "municipal bonds. Tax-exempt investors such as pension funds are indifferent "
        "between income and gains.",
        "LEGAL AND REGULATORY. Pension allocation limits vary widely - Switzerland caps "
        "listed equity at 50% and real estate at 30%; Japan permits 100% equity but "
        "prohibits real estate; South Africa allows 75% equity and 25% foreign currency. "
        "Self-investment limits cap holdings of the sponsor's own securities. If a client "
        "is a director subject to closed-period trading restrictions, the IPS must note "
        "it so the manager does not inadvertently trade that stock.",
        "UNIQUE CIRCUMSTANCES AND ESG. Faith-based restrictions - Shari'a prohibits "
        "gambling and interest, so casinos and conventional bonds are excluded. Personal "
        "objections to weapons, tobacco, gambling or particular labour and environmental "
        "practices. And critically, risks the client already carries outside the "
        "portfolio.",
    ])
    d.key("The unique-circumstances constraint is where the enterprise view enters "
          "personal investing. An oil executive should not hold significant oil stocks - "
          "his human capital is already an oil exposure. A stockbroker should underweight "
          "equities, because his earning power falls exactly when equities do. An "
          "entrepreneur should avoid competitors and businesses sharing her risk "
          "exposures. This is the Enron lesson written into policy.")
    d.h3("Six ESG implementation approaches")
    make_table(d,
               ["Approach", "What it does"],
               [["Negative screening",
                 "Excludes companies or sectors on business activity or ESG concerns"],
                ["Positive / best-in-class",
                 "Includes companies with the best ESG performance relative to peers"],
                ["ESG integration",
                 "Systematically considers material ESG factors in allocation, selection "
                 "and construction"],
                ["Thematic investing", "Invests in themes or assets tied to ESG factors"],
                ["Engagement / active ownership",
                 "Uses shareholder power - voting, proposals, dialogue - to change "
                 "corporate behaviour"],
                ["Impact investing",
                 "Invests with the intention of generating measurable social or "
                 "environmental impact alongside a financial return"]],
               widths=(50, 94))
    d.p("Screening narrows the investable universe, which changes expected risk and "
        "return, so an off-the-shelf benchmark may no longer be appropriate - screened "
        "index variants exist to address this. ESG integration is different in kind: "
        "because it is a process enhancement rather than a restriction, asset owners "
        "increasingly expect managers to beat the STANDARD benchmark while applying it.")
    d.p("The Mountain Materials case shows integration changing a decision. Carbon "
        "regulation costs 1% of operating margin, cleaner fuel another 2%, the dividend "
        "is cut from 2% to 0%, and weak safety performance implies multiple contraction. "
        "The base-case IRR falls from 15% to 5%, and the analyst cuts the position from "
        "1.5% to 0.5% while engaging with management. ESG is one input among many, not an "
        "automatic veto.")

    d.h2("4.6  Building the strategic asset allocation")
    d.formula("IPS objectives and constraints  +  capital market expectations\n"
              "         → optimisation / simulation →  Strategic Asset Allocation",
              "Capital market expectations are the risk, return and correlation forecasts "
              "for each asset class. They are kept separate from the IPS because they "
              "require different analysis, different sources and different review cycles.")
    d.p("Two principles justify the focus on asset allocation. First, systematic risk "
        "accounts for most of a portfolio's change in value over the long run. Second, "
        "returns to groups of similar assets predictably reflect exposure to particular "
        "sets of systematic factors. The SAA is therefore the mechanism for buying "
        "exposure to systematic risks in the proportions the client needs.")
    d.h3("What makes a good asset class")
    d.bullets([
        "Assets within it are relatively homogeneous, with similar risk-return "
        "expectations",
        "Paired correlations are HIGH within the class and LOWER against other classes",
        "Classes are mutually exclusive",
        "Together they approximate the whole investable universe, so no opportunity is "
        "overlooked",
    ])
    d.p("Correlation data over December 2000 to August 2018 shows how hard this is for "
        "equities: US against European 0.88, US against US small-cap 0.89, US against "
        "emerging markets 0.78. Japan is the least correlated at 0.59. Against US "
        "Treasuries, however, US equities run at minus 0.37, European at minus 0.28, "
        "emerging markets at minus 0.24.")
    d.key("Bonds - not another flavour of equity - are the real diversifier. So why do "
          "investors still split equities into so many classes? Partly regulation, but "
          "mainly organisation: managers specialise by region, size and style, so aligning "
          "asset class definitions with available products simplifies implementation.")
    d.h3("The optimisation")
    d.formula("U_p = E(R_p) − λ σ_p²\n\n"
              "E(R_p) = Σ w_i E(R_i)\n"
              "σ_p = √( Σ Σ w_i w_j Cov(R_i,R_j) )\n"
              "Cov(R_i,R_j) = ρ_i,j σ_i σ_j",
              "λ measures risk aversion. The optimal allocation is where the "
              "efficient frontier just touches the highest attainable indifference curve.")
    d.p("If expectations improve, the frontier shifts up and the tangency point moves, so "
        "the allocation should change. If the client's objectives or constraints change, "
        "the indifference curves change shape and the tangency point moves again. Neither "
        "the frontier nor the client is static.")
    d.p("The Gottschalk case shows how it plays out in practice. A former homebuilder "
        "excludes real estate (his income already depends on it) and tobacco (family "
        "values). The tobacco screen costs 0.2% of expected European equity return and "
        "adds 0.1% of volatility. His objectives are 5% return at 10% risk. No portfolio "
        "delivers both exactly - the best available at 10% risk returns 4.9% - and adviser "
        "and client agree the shortfall is acceptable. The allocation is 16% European "
        "equity, 38% emerging market equity, 46% government bonds. Real plans involve "
        "compromise.")

    d.h2("4.7  Risk budgeting, drift and rebalancing")
    d.p("Total portfolio risk comes from three sources, and each should have its own "
        "limits and expected payoff:")
    make_table(d,
               ["Source", "What it is", "Rewarded long-run?"],
               [["Strategic asset allocation",
                 "Chosen exposure to systematic risk factors", "YES"],
                ["Tactical asset allocation",
                 "Deliberate short-term deviation from policy weights", "Only if skilled"],
                ["Security selection",
                 "Picking securities to beat the class benchmark", "ZERO-SUM"]],
               widths=(46, 66, 32))
    d.p("Security selection is a zero-sum game before costs. All investors in an asset "
        "class collectively earn the market return, so one investor's gain is another's "
        "loss. After trading costs and salaries, the AVERAGE active manager must "
        "underperform. This does not mean skilled managers do not exist, nor that passive "
        "managers automatically match their index - a high-turnover index is expensive to "
        "track.")
    d.p("Where skill is likeliest to pay is in less efficient markets. US large-cap "
        "equity is highly efficient and demands exceptional skill; some regional markets "
        "lack the technical and regulatory infrastructure for timely information "
        "dissemination, leaving inefficiencies to exploit. Sometimes the choice is made "
        "implicitly - non-listed real estate and infrastructure are so illiquid that you "
        "cannot buy diversified exposure at all, so participation requires selection.")
    d.h3("Drift and the rebalancing policy")
    d.p("As markets move, weights drift from their targets. The rebalancing policy is the "
        "set of rules for restoring them - typically a corridor around each policy "
        "weight.")
    d.h3("Worked example - a European charity")
    d.p("Policy weights: 30% European equity, 15% international equity, 20% government "
        "bonds, 20% corporate bonds, 15% cash. Corridor plus or minus 2%.")
    make_table(d,
               ["Asset class", "Policy", "H1 return", "H1 end weight", "H2 return"],
               [["European equities", "30%", "+15.0%", "32.4% BREACH", "−9.0%"],
                ["International equities", "15%", "+10.0%", "15.5%", "−6.0%"],
                ["Government bonds", "20%", "+0.5%", "18.9%", "+4.0%"],
                ["Corporate bonds", "20%", "+1.5%", "19.1%", "+4.0%"],
                ["Cash", "15%", "+1.0%", "14.2%", "+2.0%"],
                ["TOTAL", "100%", "+6.6%", "100%", "−2.0%"]],
               widths=(42, 20, 24, 34, 24),
               align=("LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"))
    d.p("After six months European equity had breached its 32% ceiling. The committee "
        "chose not to rebalance fully back to policy, believing the rally would continue, "
        "and merely trimmed to the 32% limit. It did not continue - equities fell while "
        "bonds recovered.")
    d.formula("TAA contribution = Σ (actual weight − policy weight) "
              "× period return\n\n"
              "European equity:  (32.0% − 30.0%) × (−9.0%)  =  −0.18%\n"
              "International:    (15.5% − 15.0%) × (−6.0%)  =  −0.03%\n"
              "Government bonds: (18.9% − 20.0%) × (+4.0%)  =  −0.05%\n"
              "Corporate bonds:  (19.1% − 20.0%) × (+4.0%)  =  −0.04%\n"
              "Cash:             (14.6% − 15.0%) × (+2.0%)  =  −0.01%\n"
              "                                        TOTAL  =  −0.30%",
              "The tactical decision to stay overweight equities cost 30 basis points. "
              "This calculation - actual minus policy weight, times the period return - is "
              "a standard exam question.")
    d.h3("Two newer developments")
    d.bullets([
        "ETFs combined with robo-advice have made cheap, liquid, well-diversified "
        "portfolios available to retail investors at a fraction of former costs.",
        "Risk parity weights asset classes by RISK contribution rather than capital, on "
        "the argument that a conventional 60% equity allocation contributes far more than "
        "60% of the risk. Critics note its strong post-2009 record coincided with a long "
        "decline in interest rates that flattered bonds.",
    ])
