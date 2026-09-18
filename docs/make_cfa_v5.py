"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 5 - Equity Investments

Run:  venv/Scripts/python.exe docs/make_cfa_v5.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402
from _cfa_v5_part2 import (module6, module7, module8, module9, module10,
                           module11, appendix)   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V5-Equities-Summary.pdf")

MODULES = [
    (1, "Equity Instrument Features", "What a share actually is"),
    (2, "Equity Jurisdictions, Classes, and the Voting Process", "Share classes and control"),
    (3, "Equity Issuance and Trading", "How shares reach the market and change hands"),
    (4, "Sources of Equity Returns", "Where a shareholder's return comes from"),
    (5, "Introduction to Equity Valuation", "The three families of valuation model"),
    (6, "Discounted Cash Flow (DCF) and Growth Models", "Dividend discount and free cash flow"),
    (7, "Relative Value Equity Valuation Approaches", "Multiples, and how to use them properly"),
    (8, "Financial Statement Forecasting in Equity Valuation", "Building the forecast"),
    (9, "Industry and Competitive Analysis", "The five forces and industry life cycle"),
    (10, "Company Analysis: Past, Present, and Future", "Judging one company in its industry"),
    (11, "Equity Analyst Research Reports", "Writing the conclusion up"),
]

STANDFIRST = ("All eleven learning modules in everyday English, with the formulas you must "
              "memorise, worked examples, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Equity Investments divides cleanly into three parts, and they are examined in very "
        "different ways.")
    d.numbered([
        "Modules 1 to 4 are the institutional background: what a share is, how it is issued "
        "and traded, and where the return comes from. Mostly descriptive.",
        "Modules 5 to 8 are the valuation core. This is where the calculation marks are, and "
        "the Gordon growth model in Module 6 is the single most examined formula in the "
        "volume.",
        "Modules 9 to 11 are the qualitative analysis that has to precede any valuation: the "
        "industry, the company, and the report that presents the conclusion.",
    ])
    d.p("The volume leans heavily on two others. The forecasting in Module 8 is Volume 4's "
        "financial statement analysis applied forward, and the discount rates come from "
        "Volume 3's cost of capital and Volume 9's CAPM. If any of those feel shaky, fix them "
        "before attempting the valuation modules here.")
    d.key("Almost every valuation question at Level I reduces to one of three things: a "
          "Gordon growth calculation, a justified multiple, or an enterprise value "
          "computation. Make those three automatic and the rest of the volume is reading.")
    d.warn("Be precise about which cash flow goes with which discount rate. Dividends and "
           "free cash flow to equity are discounted at the cost of equity and give the value "
           "of the EQUITY. Free cash flow to the firm is discounted at the WACC and gives the "
           "value of the whole ENTERPRISE, from which debt must then be subtracted. Mixing "
           "these is the most expensive error in the volume.")


def module1(d):
    d.h1(1, "Equity Instrument Features",
         "What a share is, what it entitles you to, and how it differs from the other claim "
         "on the same company.")

    d.h2("Common shares")
    d.p("A common share is a residual claim. The holder is entitled to whatever is left after "
        "everyone else has been paid, which is nothing in a bad year and everything in a good "
        "one. It carries voting rights, no maturity, and no promise of any payment.")
    d.bullets([
        "Residual claim on assets and income, ranking last in liquidation.",
        "Voting rights, exercised in person or by proxy.",
        "Dividends are discretionary. A company may cut or omit them without default.",
        "Limited liability: the most that can be lost is the amount invested.",
        "Perpetual: shares have no maturity date.",
    ])

    d.h2("Preference shares")
    d.p("Preference shares sit between debt and common equity. They carry a stated dividend "
        "paid before any common dividend, usually no vote, and a prior claim in liquidation, "
        "but they are still equity and the dividend can be skipped without triggering "
        "default.")
    make_table(d,
               ["Feature", "Meaning"],
               [["Cumulative", "Missed dividends accumulate and must be paid before any "
                 "common dividend"],
                ["Non-cumulative", "A missed dividend is simply lost"],
                ["Participating", "Receives the stated dividend AND shares in the upside"],
                ["Non-participating", "Receives the stated dividend only"],
                ["Convertible", "Can be exchanged for common shares on set terms"],
                ["Callable / putable", "The issuer can redeem, or the holder can require "
                 "redemption"]],
               widths=(26, 74))
    d.key("Preference shares behave like a bond in calm conditions and like equity in a "
          "crisis. They pay a fixed amount and are interest-rate sensitive, but there is no "
          "legal obligation to pay and no maturity forcing repayment. That asymmetry is why "
          "they are valued as equity and analysed as debt.")

    d.h2("Private against public equity")
    d.p("Private equity is not traded, is sold through private placements, carries far lower "
        "disclosure, and has no observable price. Venture capital funds early-stage "
        "companies, leveraged buyouts take mature companies private using debt, and private "
        "investment in public equity places a discounted block with a private investor.")
    d.warn("The absence of a quoted price is often mistaken for the absence of volatility. "
           "Private holdings appear smooth because they are marked infrequently, not because "
           "the underlying value moves less. The curriculum returns to this in Volume 8.")

    d.h2("Foreign equity")
    d.p("An investor can buy directly on a foreign exchange, buy a depository receipt, or buy "
        "a global registered share. A depository receipt is a domestically traded certificate "
        "representing shares held abroad by a depository bank. Sponsored receipts are created "
        "with the company's involvement and carry voting rights; unsponsored ones do not.")


def module2(d):
    d.h1(2, "Equity Jurisdictions, Classes, and the Voting Process",
         "Who really controls a company, and how the share structure can separate ownership "
         "from control.")

    d.h2("Share classes")
    d.p("A company may issue several classes of common share with different voting power. A "
        "dual-class structure typically gives founders shares with ten or more votes each "
        "while the public holds one-vote shares.")
    d.key("The consequence is that economic ownership and voting control come apart. A "
          "founder holding 10% of the shares can hold 55% of the votes, which means public "
          "shareholders cannot remove management however badly it performs. Whether this is "
          "good or bad is genuinely contested, and the exam may ask for either side.")
    d.p("The case for: management can pursue long-term strategy without responding to "
        "quarterly pressure or to a hostile bid. The case against: it entrenches "
        "underperformers, removes the discipline of the takeover market, and disenfranchises "
        "the people supplying most of the capital.")

    d.h2("Voting")
    make_table(d,
               ["Mechanism", "How it works"],
               [["Statutory voting", "One share, one vote, for each director separately. A "
                 "majority holder elects the entire board"],
                ["Cumulative voting", "Votes equal shares times seats, and may all be cast "
                 "for one candidate. This lets minorities elect at least one director"],
                ["Proxy voting", "The right to vote is delegated to someone attending"]],
               widths=(24, 76))
    d.warn("Cumulative voting PROTECTS minority shareholders and statutory voting does not. "
           "Candidates often reverse this. Under statutory voting a 51% holder wins every "
           "seat; under cumulative voting a minority can concentrate its votes and secure "
           "representation.")

    d.h2("Jurisdiction and shareholder protection")
    d.p("Legal systems differ in how strongly they protect minority shareholders. Common law "
        "jurisdictions generally give courts wider scope to protect investors against "
        "expropriation; civil law jurisdictions rely more on written statute. The examinable "
        "point is that stronger protection is associated with deeper equity markets, more "
        "dispersed ownership, and a lower cost of equity.")


def module3(d):
    d.h1(3, "Equity Issuance and Trading",
         "How shares come into existence, and the mechanics of the market where they "
         "subsequently trade.")

    d.h2("The primary market")
    make_table(d,
               ["Route", "Description"],
               [["Initial public offering", "The first sale to the public, underwritten by "
                 "investment banks"],
                ["Seasoned offering", "An already-listed company issuing more shares"],
                ["Rights issue", "Existing shareholders offered new shares pro rata, usually "
                 "at a discount"],
                ["Private placement", "Sold directly to a small number of investors"],
                ["Direct listing", "Existing shares simply begin trading; no new capital"]],
               widths=(26, 74))
    d.p("In a firm commitment underwriting the bank buys the whole issue and bears the risk "
        "of not reselling it. In a best efforts arrangement the bank merely tries, and the "
        "risk stays with the issuer.")
    d.warn("A rights issue dilutes any shareholder who does not participate. Because the new "
           "shares are offered below the market price, the share price mechanically falls to "
           "a theoretical ex-rights price. A holder who takes up the rights is unaffected in "
           "total value; one who does nothing loses. The right itself has value and can "
           "usually be sold.")

    d.h2("The secondary market")
    d.bullets([
        "Quote-driven markets: dealers post bid and ask prices and trade from inventory. "
        "Typical of bonds and currencies.",
        "Order-driven markets: buyers and sellers are matched by an order book, with rules "
        "of price and then time priority. Typical of modern equity exchanges.",
        "Brokered markets: a broker searches for a counterparty. Typical of illiquid, "
        "unique assets.",
    ])
    d.p("Order types matter. A market order executes immediately at the best available price "
        "and guarantees execution but not price. A limit order specifies a price and "
        "guarantees the price but not execution. A stop order becomes active only once a "
        "trigger price is reached, and is used to limit losses.")

    d.h2("Margin and short selling")
    d.formula("Leverage ratio  =  1 / initial margin requirement\n\n"
              "Margin call price  =  P0 x (1 - initial margin) / (1 - maintenance margin)",
              "The second formula gives the price at which a long position on margin will be "
              "called.")
    d.example("You buy a share at Rs 100 with 40% initial margin and a 25% maintenance "
              "requirement.\n\n"
              "  Leverage = 1 / 0.40 = 2.5 times\n"
              "  Margin call price = 100 x (1 - 0.40) / (1 - 0.25)\n"
              "                    = 100 x 0.60 / 0.75 = Rs 80\n\n"
              "A 20% fall in the share triggers the call. Note the leverage cuts both ways: "
              "the same 2.5 times that would have multiplied a gain has turned a 20% market "
              "move into a 50% loss of your own money.")
    d.p("A short sale borrows shares and sells them, hoping to buy them back cheaper. The "
        "short seller must pay any dividend to the lender, faces theoretically unlimited "
        "losses, and can be forced to close the position if the lender recalls the stock.")


def module4(d):
    d.h1(4, "Sources of Equity Returns",
         "Total return has only two components, and knowing which one is driving a result "
         "tells you a great deal about what to expect next.")

    d.formula("Total return  =  capital appreciation  +  income\n\n"
              "  Holding period return  =  (P1 - P0 + D1) / P0",
              "Nothing else. Every equity return decomposes into the price change and the "
              "cash distributed.")
    d.example("You buy at Rs 200, receive a Rs 12 dividend, and sell at Rs 226.\n\n"
              "  Total return = (226 - 200 + 12) / 200 = 38 / 200 = 19.0%\n"
              "    Capital appreciation = 26 / 200 = 13.0%\n"
              "    Dividend yield       = 12 / 200 =  6.0%\n\n"
              "If inflation over the period was 7%:\n"
              "  Real return = 1.19 / 1.07 - 1 = 11.2%\n\n"
              "Subtracting 7 from 19 would give 12%, which overstates the result by most of "
              "a percentage point.")

    d.h2("How companies return cash")
    make_table(d,
               ["Method", "Effect"],
               [["Cash dividend", "Cash to all shareholders; the share price falls by "
                 "roughly the dividend on the ex-date"],
                ["Share repurchase", "Cash to the sellers only; the share count falls, so "
                 "EPS rises"],
                ["Stock dividend", "More shares, each worth proportionately less. No cash, "
                 "no change in value"],
                ["Stock split", "The same, expressed differently. No change in value"]],
               widths=(24, 76))
    d.key("A share repurchase and a cash dividend of the same amount are equivalent in "
          "theory, before tax. The buyback concentrates ownership rather than distributing "
          "cash to everyone, so it raises EPS, but it does not create value on its own. A "
          "company buying back overvalued shares actively destroys value.")
    d.warn("A stock split and a stock dividend change nothing of substance. Two shares worth "
           "half as much each is the same wealth. Any question implying that a split created "
           "value is testing whether you know this.")

    d.h2("The dividend timeline")
    d.numbered([
        "Declaration date: the board announces the dividend.",
        "Ex-dividend date: buy on or after this date and you do NOT receive it.",
        "Record date: the company checks who is on the register.",
        "Payment date: the cash goes out.",
    ])


def module5(d):
    d.h1(5, "Introduction to Equity Valuation",
         "The three families of model, and the discipline of choosing the right one for the "
         "company in front of you.")

    d.h2("The three approaches")
    make_table(d,
               ["Family", "Asks", "Use when"],
               [["Present value", "What are the future cash flows worth today?",
                 "Cash flows are predictable and positive"],
                ["Relative value", "What do similar companies trade at?",
                 "Good comparables exist; a quick cross-check is wanted"],
                ["Asset based", "What are the net assets worth?",
                 "The firm is asset-heavy, in liquidation, or loss-making"]],
               widths=(22, 40, 38))
    d.key("The present value approach is the theoretically correct one, because value comes "
          "from future cash. Relative valuation is faster and reflects current market "
          "sentiment but carries whatever mispricing the comparables carry. Asset-based "
          "valuation sets a floor and badly understates any firm whose value is in "
          "intangibles.")

    d.h2("Intrinsic value and the market")
    d.p("Intrinsic value is what an asset is worth on full information. The market price is "
        "what it currently trades at. The difference is the analyst's entire proposition, "
        "and it rests on the assumption that the difference will eventually close.")
    d.warn("Two things can produce a gap between your value and the price: the market is "
           "wrong, or you are. A disciplined analyst states explicitly which assumption "
           "drives the difference and what the market must be assuming instead. A valuation "
           "that never asks what the market sees is an exercise in self-confirmation.")

    d.h2("Enterprise value")
    d.formula("Enterprise value  =  market capitalisation\n"
              "                     +  total debt\n"
              "                     +  preferred equity\n"
              "                     +  non-controlling interests\n"
              "                     -  cash and cash equivalents",
              "EV is what it would cost to buy the whole business free of debt. Cash is "
              "subtracted because the buyer gets it back immediately.")
    d.example("A company has 200m shares at Rs 150, debt of Rs 12bn, and cash of Rs 4bn.\n\n"
              "  Market capitalisation = 200m x 150 = Rs 30bn\n"
              "  Enterprise value = 30 + 12 - 4 = Rs 38bn\n\n"
              "If EBITDA is Rs 4.75bn, the EV/EBITDA multiple is 38 / 4.75 = 8.0x. Note that "
              "a company with a lot of cash looks cheaper on EV multiples than on P/E, which "
              "is exactly the distortion EV was designed to remove.")


def build():
    d = Guide(volume=5, subject="Equity Investments")
    cover(d, MODULES, STANDFIRST)
    how_to_use(d)
    for fn in (module1, module2, module3, module4, module5,
               module6, module7, module8, module9, module10, module11):
        fn(d)
    appendix(d)
    d.output(OUT)
    print("wrote", OUT, "(%d pages)" % d.page_no())


if __name__ == "__main__":
    build()
