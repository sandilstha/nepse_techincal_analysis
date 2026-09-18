"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 7 - Derivatives

Run:  venv/Scripts/python.exe docs/make_cfa_v7.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402
from _cfa_v7_part2 import (module6, module7, module8, module9, module10,
                           appendix)   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V7-Derivatives-Summary.pdf")

MODULES = [
    (1, "Derivative Instrument and Derivative Market Features", "What a derivative is"),
    (2, "Forward Commitment and Contingent Claim Features", "Obligations against rights"),
    (3, "Derivative Benefits, Risks, and Issuer and Investor Uses", "Why anyone uses them"),
    (4, "Arbitrage, Replication, and the Cost of Carry", "The one principle behind all pricing"),
    (5, "Pricing and Valuation of Forward Contracts", "Forwards, and varying maturities"),
    (6, "Pricing and Valuation of Futures Contracts", "Futures, and why they differ"),
    (7, "Pricing and Valuation of Interest Rate and Other Swaps", "Swaps as a series of forwards"),
    (8, "Pricing and Valuation of Options", "Intrinsic value, time value, and the drivers"),
    (9, "Option Replication Using Put-Call Parity", "The identity that ties it all together"),
    (10, "Valuing a Derivative Using a One-Period Binomial Model", "Pricing by replication"),
]

STANDFIRST = ("All ten learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Derivatives frightens more candidates than any other volume and deserves to "
        "frighten fewer. It is short, and almost all of it follows from a single idea "
        "introduced in Module 4.")
    d.numbered([
        "Modules 1 to 3 are descriptive: what derivatives are, the two families they fall "
        "into, and who uses them for what. Straightforward marks.",
        "Module 4 is the conceptual centre of the volume. Arbitrage, replication and the cost "
        "of carry generate every pricing formula that follows. Do not move past it until it "
        "is genuinely clear.",
        "Modules 5 to 7 apply that principle to forward commitments: forwards, futures and "
        "swaps.",
        "Modules 8 to 10 cover options, which are harder because the payoff is asymmetric. "
        "Put-call parity in Module 9 is the most examined single relationship in the volume.",
    ])
    d.key("The one idea: if two things produce identical future cash flows, they must cost "
          "the same today. If they do not, someone can buy the cheap one, sell the dear one, "
          "and collect the difference with no risk and no capital. Every derivative price in "
          "this volume is derived by constructing exactly such a pair and setting them equal.")
    d.warn("Keep the distinction between PRICE and VALUE absolutely firm. The forward price "
           "is the rate agreed in the contract, and it is fixed at inception. The forward "
           "value is what the contract is worth to you today, and it starts at zero and moves "
           "afterwards. Questions ask for one and offer the other among the choices.")


def module1(d):
    d.h1(1, "Derivative Instrument and Derivative Market Features",
         "A derivative derives its value from something else. That is the whole definition, "
         "and everything else is detail about the arrangement.")

    d.h2("The basic structure")
    d.bullets([
        "The underlying: the asset, rate, index or event the contract refers to.",
        "The notional: the quantity of the underlying the contract covers. It is usually not "
        "exchanged, which is why derivatives are so capital-efficient.",
        "The expiration: when the contract settles.",
        "Settlement: physical delivery of the underlying, or a cash payment of the "
        "difference.",
    ])
    d.key("The notional is a reference quantity, not an amount invested. A swap with a "
          "notional of Rs 100m may involve net payments of a few hundred thousand rupees. "
          "This is the source of both the efficiency of derivatives and their capacity for "
          "damage: a small amount of capital controls a very large exposure.")

    d.h2("Exchange-traded and over the counter")
    make_table(d,
               ["", "Exchange-traded", "Over the counter"],
               [["Terms", "Standardised", "Customised to the parties"],
                ["Counterparty", "A central clearing house", "The other party directly"],
                ["Credit risk", "Minimal; the clearing house guarantees", "Real, and borne "
                 "by each party"],
                ["Collateral", "Margin, marked to market daily", "Negotiated, often "
                 "collateralised"],
                ["Liquidity", "Generally high", "Generally low"],
                ["Transparency", "Prices are public", "Private"]],
               widths=(20, 38, 42))
    d.warn("The central clearing house does not eliminate credit risk from the system; it "
           "concentrates it in one institution and manages it with margin. The exam wants you "
           "to say that exchange trading REDUCES counterparty credit risk through "
           "novation and daily margining, not that it removes risk altogether.")


def module2(d):
    d.h1(2, "Forward Commitment and Contingent Claim Features and Instruments",
         "Every derivative is one of two things: an obligation, or a right. This distinction "
         "governs everything that follows.")

    d.h2("The two families")
    make_table(d,
               ["", "Forward commitment", "Contingent claim"],
               [["Nature", "Both parties MUST perform", "One party MAY choose to perform"],
                ["Examples", "Forwards, futures, swaps", "Options, and option-like features"],
                ["Payoff", "Symmetric: linear gains and losses on both sides",
                 "Asymmetric: limited on one side, open on the other"],
                ["Cost at inception", "Usually zero", "The buyer pays a premium"]],
               widths=(20, 40, 40))
    d.key("Symmetric against asymmetric is the distinction to hold on to. A forward's payoff "
          "diagram is a straight line through the agreed price. An option's is a hockey "
          "stick, bent at the strike. Almost every conceptual question in the volume turns on "
          "which shape applies.")

    d.h2("The instruments")
    d.bullets([
        "Forward: an agreement to buy or sell at a set price on a set date. Customised, "
        "over the counter, settled at expiry.",
        "Futures: the same economic idea, standardised, exchange-traded, and marked to "
        "market daily.",
        "Swap: an agreement to exchange a series of cash flows. Equivalent to a package of "
        "forwards with staggered dates.",
        "Call option: the right, not the obligation, to BUY at the strike price.",
        "Put option: the right, not the obligation, to SELL at the strike price.",
        "Credit default swap: protection against a specified credit event, which behaves "
        "like an insurance contract and is treated as a contingent claim.",
    ])
    d.p("An American option may be exercised at any time up to expiry; a European option only "
        "at expiry. An American option is therefore worth at least as much as an otherwise "
        "identical European one, and never less.")


def module3(d):
    d.h1(3, "Derivative Benefits, Risks, and Issuer and Investor Uses",
         "Why the market exists. The same instrument can reduce risk or magnify it, and only "
         "the intention differs.")

    d.h2("What derivatives are good for")
    d.bullets([
        "Risk transfer: moving an exposure to someone better placed to carry it. This is the "
        "primary economic function.",
        "Price discovery: derivative prices reveal the market's expectation of future prices.",
        "Efficiency: exposure can be adjusted far more cheaply and quickly than by trading "
        "the underlying itself.",
        "Access: exposure to assets that are hard to trade directly, such as a commodity or "
        "an index.",
    ])

    d.h2("What they risk")
    d.bullets([
        "Leverage: a small outlay controls a large notional, so losses scale accordingly.",
        "Counterparty credit risk, particularly over the counter.",
        "Liquidity risk in customised contracts.",
        "Basis risk: the hedge and the exposure do not move exactly together.",
        "Complexity, and the associated risk that the user does not understand the position.",
    ])
    d.key("Hedging and speculation use identical instruments. The difference is whether you "
          "already hold an offsetting exposure. A farmer selling wheat futures is hedging; a "
          "trader selling the same contract with no wheat is speculating. Nothing about the "
          "contract distinguishes them.")

    d.h2("Issuer and investor uses")
    d.p("An issuer, meaning a corporation, uses derivatives to manage the risks its business "
        "creates: interest rate swaps to convert floating debt to fixed, currency forwards to "
        "hedge foreign revenue, commodity futures to fix input costs. The accounting notion "
        "of hedge effectiveness applies to how closely the hedge tracks the exposure.")
    d.p("An investor uses them to modify portfolio exposure: to hedge a holding, to gain "
        "exposure cheaply, to express a view on volatility, or to alter the return "
        "distribution deliberately, as when writing covered calls to convert uncertain upside "
        "into certain premium income.")
    d.warn("Do not describe derivatives as inherently risky in an exam answer. The curriculum's "
           "position is that they are risk TRANSFER instruments, and that the risk lies in how "
           "they are used, in the leverage embedded, and in the counterparty. A hedged "
           "position using derivatives is less risky than the unhedged position.")


def module4(d):
    d.h1(4, "Arbitrage, Replication, and the Cost of Carry in Pricing Derivatives",
         "The conceptual heart of the volume. Master this module and the rest becomes "
         "arithmetic.")

    d.h2("The law of one price")
    d.p("Two positions producing identical cash flows in every future state must have the "
        "same price today. If they do not, an arbitrageur buys the cheaper and sells the "
        "dearer, locking a profit with no net investment and no risk. Such opportunities are "
        "eliminated as soon as they appear, which is why we can assume they do not exist.")
    d.key("Derivative pricing does not require any forecast of where the underlying is going. "
          "This surprises people and it is the most important single point in the volume. The "
          "forward price is not a prediction; it is the only price at which no arbitrage is "
          "possible, given today's spot price and the cost of holding the asset.")

    d.h2("Replication")
    d.p("A derivative can be reproduced with a combination of the underlying and borrowing or "
        "lending. Since the replicating portfolio and the derivative pay the same amounts, "
        "they must cost the same, and that equality IS the pricing formula.")
    d.formula("Long forward  =  buy the asset with borrowed money\n\n"
              "  Buying the asset today costs S0, financed by borrowing.\n"
              "  At expiry you owe S0 x (1 + r)^T and you hold the asset.\n"
              "  That is precisely the payoff of a long forward struck at\n"
              "  F0 = S0 x (1 + r)^T.")

    d.h2("Cost of carry")
    d.formula("F0  =  S0  x  (1 + r)^T   +  (costs of carrying)  -  (benefits of carrying)\n\n"
              "  Costs: storage, insurance, financing\n"
              "  Benefits: dividends, coupons, convenience yield",
              "Holding the asset costs money and may earn income. The forward price adjusts "
              "so that holding the asset and holding the forward come out the same.")
    d.example("A share trades at Rs 500. The risk-free rate is 6% and the share will pay a "
              "Rs 20 dividend in six months. What is the fair one-year forward price?\n\n"
              "  Future value of the dividend at expiry = 20 x (1.06)^0.5 = Rs 20.59\n"
              "  F0 = 500 x 1.06 - 20.59 = 530.00 - 20.59 = Rs 509.41\n\n"
              "The dividend is SUBTRACTED because the holder of the share receives it and the "
              "holder of the forward does not. Now suppose the forward actually trades at "
              "Rs 520. Borrow Rs 500, buy the share, sell the forward at 520. At expiry you "
              "deliver the share for 520, repay 530, and you collected 20.59 from the "
              "dividend: 520 + 20.59 - 530 = Rs 10.59 of riskless profit per share. That "
              "profit is exactly the mispricing, and pursuing it is what forces the price "
              "back to 509.41.")
    d.warn("Benefits of carry reduce the forward price; costs of carry raise it. Get the sign "
           "backwards and the answer will still look plausible, which is why the wrong-sign "
           "result is always among the choices. Reason it out each time: the forward holder "
           "misses the dividend, so the forward must be cheaper.")

    d.h2("Convenience yield")
    d.p("For commodities there is a further benefit: the value of physically holding the "
        "goods, for instance being able to keep a factory running. This convenience yield "
        "behaves like a dividend and lowers the forward price. When it is large enough, the "
        "forward price falls BELOW the spot, a condition called backwardation. The opposite, "
        "where forwards trade above spot, is contango.")


def module5(d):
    d.h1(5, "Pricing and Valuation of Forward Contracts and for an Underlying with "
            "Varying Maturities",
         "Applying Module 4 to the simplest forward commitment, and keeping price and value "
         "distinct throughout.")

    d.h2("Price at inception")
    d.formula("F0(T)  =  S0  x  (1 + r)^T\n\n"
              "With carry:  F0(T)  =  (S0 - PV of benefits + PV of costs) x (1 + r)^T",
              "This is the price WRITTEN INTO the contract. It is set so that the contract is "
              "worth nothing to either party at the start, which is why no money changes "
              "hands at inception.")

    d.h2("Value during the life")
    d.p("Once the contract exists, the spot price moves and the contract acquires a value. "
        "For the long party, the contract is worth the present value of the difference "
        "between what the asset is now worth forward and what was agreed.")
    d.formula("Value to the LONG at time t\n"
              "     =  (F_t  -  F_0)  /  (1 + r)^(T - t)\n\n"
              "Equivalently:  V_t  =  S_t  -  F0 / (1 + r)^(T - t)\n"
              "               (for an underlying with no carry costs or benefits)",
              "The value to the short is the negative of the value to the long. Between them "
              "the contract always sums to zero.")
    d.example("You entered a one-year forward to buy a share at Rs 509. Six months later the "
              "share trades at Rs 540 and the risk-free rate is still 6%.\n\n"
              "  The new six-month forward price is 540 x (1.06)^0.5 = Rs 555.97\n"
              "  Value to you = (555.97 - 509) / (1.06)^0.5\n"
              "               = 46.97 / 1.02956 = Rs 45.62\n\n"
              "You agreed to pay 509 for something now worth substantially more, so the "
              "contract has become an asset to you worth Rs 45.62 and a liability of exactly "
              "the same amount to the counterparty. No money has yet changed hands.")
    d.key("At inception the value is zero and the price is whatever makes it zero. During the "
          "life the price agreed is frozen while the value moves. At expiry the value is "
          "simply S_T minus F0 for the long. If you can state those three sentences, you can "
          "answer any forward question.")

    d.h2("Varying maturities")
    d.p("With a term structure of interest rates, each maturity has its own discount rate, so "
        "the forward price for each date is computed using the rate for that date rather than "
        "a single flat rate. The principle is unchanged; only the discounting becomes more "
        "careful.")
    d.warn("For a forward on a bond, remember to handle accrued interest and any coupon paid "
           "during the contract's life as a benefit of carry. The coupon accrues to the "
           "holder of the bond, not to the holder of the forward, so it reduces the forward "
           "price exactly as a dividend does.")


def build():
    d = Guide(volume=7, subject="Derivatives")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5,
               module6, module7, module8, module9, module10):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
