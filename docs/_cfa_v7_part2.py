"""Volume 7, modules 6 to 10 and the formula sheet. Imported by make_cfa_v7.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module6(d):
    d.h1(6, "Pricing and Valuation of Futures Contracts",
         "Economically a forward, institutionally very different, and the difference is "
         "entirely about when the money moves.")

    d.h2("Marking to market")
    d.p("A futures position is settled every day. Gains are paid into the account and losses "
        "taken out, so the accumulated profit is realised continuously rather than at expiry. "
        "The contract's value therefore returns to zero at the end of each day.")
    make_table(d,
               ["", "Forward", "Futures"],
               [["Settlement of gains", "All at expiry", "Daily, in cash"],
                ["Value between settlements", "Accumulates", "Resets to zero each day"],
                ["Credit risk", "Builds up over the life", "Limited to one day's move"],
                ["Terms", "Customised", "Standardised"],
                ["Margin", "Negotiated", "Initial and maintenance, enforced daily"]],
               widths=(26, 34, 40))
    d.example("You are long one futures contract on 100 units, entered at Rs 250. Initial "
              "margin is Rs 3,000 and the maintenance margin is Rs 2,200.\n\n"
              "  Day 1: settles at 248. Loss = 100 x 2 = Rs 200. Balance Rs 2,800.\n"
              "  Day 2: settles at 244. Loss = 100 x 4 = Rs 400. Balance Rs 2,400.\n"
              "  Day 3: settles at 241. Loss = 100 x 3 = Rs 300. Balance Rs 2,100.\n\n"
              "The balance is now below the Rs 2,200 maintenance level, so a margin call is "
              "issued. Note what must be deposited: enough to restore the INITIAL margin of "
              "Rs 3,000, not merely the maintenance level, so Rs 900 is required.")
    d.warn("A margin call must be met back up to the INITIAL margin, not to the maintenance "
           "margin. Restoring only to the maintenance level is the standard wrong answer and "
           "it appears in every question of this type.")

    d.h2("Do futures and forward prices differ?")
    d.key("If interest rates are constant, or uncorrelated with the underlying's price, "
          "futures and forward prices are identical. They differ only when rates and the "
          "underlying price are correlated, because daily settlement means gains are "
          "reinvested and losses financed at prevailing rates. Positive correlation favours "
          "the long futures holder, so futures prices exceed forward prices slightly.")
    d.p("At Level I this difference is a conceptual point rather than a calculation. The "
        "examinable statement is that the two prices are equal absent that correlation.")


def module7(d):
    d.h1(7, "Pricing and Valuation of Interest Rate and Other Swaps",
         "A swap looks complicated and is not. It is a series of forwards bundled together "
         "and priced so that the bundle is worth nothing at the start.")

    d.h2("The plain vanilla interest rate swap")
    d.p("One party pays a fixed rate and receives a floating rate; the other does the "
        "reverse. Payments are netted, and the notional is never exchanged. It exists so that "
        "a borrower with floating-rate debt can convert it to fixed without refinancing.")
    d.formula("Net payment to the fixed payer, per period\n"
              "     =  notional  x  (floating rate  -  fixed rate)  x  (days / 360)\n\n"
              "  Positive when floating exceeds fixed; negative otherwise.",
              "Only the difference changes hands, which is why the credit exposure of a swap "
              "is far smaller than its notional suggests.")
    d.example("A Rs 100,000,000 notional swap, quarterly, fixed rate 5%. In one quarter the "
              "floating reference sets at 6.2%, with 90 days in the period.\n\n"
              "  Net = 100,000,000 x (0.062 - 0.050) x (90/360)\n"
              "      = 100,000,000 x 0.012 x 0.25 = Rs 300,000\n\n"
              "The fixed payer receives Rs 300,000. Note the scale: a Rs 100m notional "
              "produced a Rs 300,000 cash flow. The notional measures exposure, not "
              "investment.")

    d.h2("Pricing and valuing a swap")
    d.key("Two equivalent ways of seeing a swap, and either will answer an exam question. "
          "First, it is a package of forward rate agreements, one per settlement date. "
          "Second, it is a long position in a floating-rate bond and a short position in a "
          "fixed-rate bond, both on the same notional. The second view makes the valuation "
          "immediate.")
    d.formula("Value to the fixed payer\n"
              "     =  value of the floating bond  -  value of the fixed bond\n\n"
              "At inception these are equal, so the value is zero, and the fixed rate\n"
              "chosen to make them equal is the SWAP RATE.",
              "A floating rate bond is worth par at every reset date, which simplifies the "
              "floating leg enormously.")
    d.p("As rates move, the swap acquires value. If rates rise, the floating leg is worth "
        "more and the fixed payer gains; if rates fall, the fixed payer loses. A fixed payer "
        "therefore benefits from rising rates, which is the whole point of using a swap to "
        "hedge floating-rate borrowing.")
    d.warn("The swap rate is set at inception so the swap's initial value is zero. It is not "
           "a forecast of future rates, and it does not change over the contract's life. What "
           "changes is the swap's VALUE, exactly as with a forward. The same price-against-"
           "value discipline from Module 5 applies here.")

    d.h2("Other swaps")
    d.bullets([
        "Currency swap: exchanges payments in two currencies, and here the notionals usually "
        "ARE exchanged, at the start and again at the end.",
        "Equity swap: one leg pays the return on an equity or index, the other a fixed or "
        "floating rate.",
        "Commodity swap: fixes the price of a commodity over a series of dates.",
    ])


def module8(d):
    d.h1(8, "Pricing and Valuation of Options",
         "Options are harder than forwards because the payoff bends. Everything here follows "
         "from that asymmetry.")

    d.h2("The four positions")
    make_table(d,
               ["Position", "Right or obligation", "Maximum gain", "Maximum loss"],
               [["Long call", "Right to buy", "Unlimited", "The premium paid"],
                ["Short call", "Obligation to sell if exercised", "The premium received",
                 "Unlimited"],
                ["Long put", "Right to sell", "Strike minus zero, less premium",
                 "The premium paid"],
                ["Short put", "Obligation to buy if exercised", "The premium received",
                 "Strike less premium"]],
               widths=(18, 34, 24, 24))
    d.warn("A short call has theoretically UNLIMITED loss, because the underlying can rise "
           "without bound. A short put's loss is large but bounded, because the underlying "
           "cannot fall below zero. This asymmetry between the two short positions is "
           "examined regularly.")

    d.h2("Intrinsic and time value")
    d.formula("Option value  =  intrinsic value  +  time value\n\n"
              "  Call intrinsic  =  max(0,  S - X)\n"
              "  Put intrinsic   =  max(0,  X - S)\n\n"
              "  S = spot price of the underlying,  X = strike price",
              "Intrinsic value is what the option would pay if exercised immediately. It can "
              "never be negative, because the holder would simply not exercise.")
    d.example("A share trades at Rs 340. A call with a Rs 320 strike costs Rs 28; a put with "
              "the same strike costs Rs 6.\n\n"
              "  Call intrinsic = max(0, 340 - 320) = Rs 20, so time value = 28 - 20 = Rs 8\n"
              "  Put intrinsic  = max(0, 320 - 340) = Rs 0,  so time value = Rs 6\n\n"
              "The call is in the money and the put is out of the money. The put has no "
              "intrinsic value at all, and its entire Rs 6 price is the possibility that the "
              "share falls below 320 before expiry. At expiry that possibility is gone, and "
              "every option is worth exactly its intrinsic value.")
    d.key("Time value decays to zero at expiry, always, and the decay accelerates as expiry "
          "approaches. This is why a long option position loses money as time passes even if "
          "the underlying does not move at all, and why selling options is a business of "
          "collecting that decay.")

    d.h2("What drives an option's value")
    make_table(d,
               ["An increase in", "Call value", "Put value"],
               [["Price of the underlying", "Rises", "Falls"],
                ["Strike price", "Falls", "Rises"],
                ["Volatility", "RISES", "RISES"],
                ["Time to expiry", "Rises (usually)", "Rises (usually)"],
                ["Risk-free rate", "Rises", "Falls"],
                ["Benefits of holding the asset (dividends)", "Falls", "Rises"]],
               widths=(38, 31, 31))
    d.key("Volatility raises BOTH a call and a put, which is the one row people find "
          "counterintuitive. The reason is the asymmetry: greater dispersion increases the "
          "chance of a large favourable move, while the unfavourable side is already capped "
          "at the premium. More uncertainty is unambiguously good for an option holder.")


def module9(d):
    d.h1(9, "Option Replication Using Put-Call Parity",
         "One identity, exactly true, that ties calls, puts, the underlying and a bond "
         "together. The most examined relationship in the volume.")

    d.formula("c  +  X / (1 + r)^T   =   p  +  S0\n\n"
              "  c  = price of a European call\n"
              "  p  = price of a European put, same strike and expiry\n"
              "  X  = strike price\n"
              "  S0 = current price of the underlying\n"
              "  T  = time to expiry",
              "Left side is the fiduciary call: a call plus a risk-free bond maturing at the "
              "strike. Right side is the protective put: a put plus the underlying. Both are "
              "worth max(S_T, X) at expiry, so they must cost the same today.")
    d.p("The logic is worth seeing directly. At expiry, if the share finishes above the "
        "strike, the fiduciary call exercises and holds the share while the protective put "
        "expires worthless and still holds the share. If it finishes below, the call expires "
        "and the bond pays X, while the put is exercised for X. Identical in every state, so "
        "identical in price today.")
    d.example("A share trades at Rs 400. A six-month call struck at Rs 390 costs Rs 34. The "
              "risk-free rate is 6% a year. What must the put cost?\n\n"
              "  p = c + X/(1+r)^T - S0\n"
              "    = 34 + 390/(1.06)^0.5 - 400\n"
              "    = 34 + 390/1.02956 - 400\n"
              "    = 34 + 378.80 - 400\n"
              "    = Rs 12.80\n\n"
              "If the put actually trades at Rs 15, it is expensive relative to the call. Sell "
              "the put, sell the share short, buy the call, and lend the difference: the "
              "position costs nothing at expiry in any state and you banked Rs 2.20 today.")
    d.key("Rearrange the identity to synthesise any of the four instruments from the other "
          "three. A synthetic call is a put plus the underlying minus a bond. A synthetic "
          "underlying is a call minus a put plus a bond. Questions often describe a portfolio "
          "in words and ask what it is equivalent to, and the answer is always one of these "
          "rearrangements.")
    d.warn("Put-call parity holds strictly for EUROPEAN options only. American options can be "
           "exercised early, which breaks the equality into an inequality. If a question "
           "mentions American options and asks you to apply parity exactly, the point being "
           "tested is that you cannot.")


def module10(d):
    d.h1(10, "Valuing a Derivative Using a One-Period Binomial Model",
         "The simplest possible option pricing model, and it demonstrates the entire "
         "no-arbitrage method in one page of arithmetic.")

    d.h2("The setup")
    d.p("Assume the underlying can take only two values at expiry: up by a factor u, or down "
        "by a factor d. Build a portfolio of the underlying and borrowing that reproduces the "
        "option's payoff in both states. Since it matches in every state, its cost today is "
        "the option's price.")
    d.formula("Risk-neutral probability\n"
              "     pi  =  [ (1 + r)  -  d ]  /  ( u  -  d )\n\n"
              "Option value\n"
              "     c0  =  [ pi x c_up  +  (1 - pi) x c_down ]  /  (1 + r)",
              "The option value is the expected payoff under the risk-neutral probability, "
              "discounted at the risk-free rate.")
    d.example("A share is at Rs 100. In one year it will be either Rs 130 (u = 1.30) or "
              "Rs 80 (d = 0.80). The risk-free rate is 5%. Value a call struck at Rs 110.\n\n"
              "  Payoffs:  c_up = max(0, 130 - 110) = Rs 20\n"
              "            c_down = max(0, 80 - 110) = Rs 0\n\n"
              "  pi = (1.05 - 0.80) / (1.30 - 0.80) = 0.25 / 0.50 = 0.50\n\n"
              "  c0 = [0.50 x 20 + 0.50 x 0] / 1.05 = 10 / 1.05 = Rs 9.52\n\n"
              "Check it by replication. A portfolio holding 0.4 shares financed with Rs 30.48 "
              "of borrowing pays 0.4(130) - 32 = 20 in the up state and 0.4(80) - 32 = 0 in "
              "the down state, matching the call exactly. It costs 0.4(100) - 30.48 = Rs 9.52 "
              "today. The two methods agree because they are the same argument.")
    d.key("The risk-neutral probability is NOT the real probability of the share rising, and "
          "the real probability never enters the calculation. This is the deepest point in "
          "the volume: two investors who disagree completely about where the share is going "
          "must still agree on the option's price, because disagreeing would create an "
          "arbitrage between them.")
    d.warn("Because the actual probability is irrelevant, a question that supplies one is "
           "supplying a distractor. If you are told the share has a 70% chance of rising, "
           "that number does not appear anywhere in the binomial calculation. Candidates who "
           "use it instead of pi arrive at a wrong answer that is offered among the choices.")

    d.h2("The hedge ratio")
    d.formula("Hedge ratio (delta)  =  (c_up  -  c_down)  /  (S_up  -  S_down)",
              "The number of units of the underlying needed to replicate one option. In the "
              "example above: (20 - 0) / (130 - 80) = 0.4, which is where the 0.4 shares came "
              "from.")
    d.p("Extending the model to many short periods produces increasingly realistic prices, "
        "and in the limit it converges on the continuous-time models used in practice. Level "
        "I requires only the single period.")


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place.")

    d.h2("Forwards and futures")
    d.formula("F0(T)  =  S0 x (1 + r)^T\n"
              "With carry:  F0(T)  =  (S0 - PV benefits + PV costs) x (1 + r)^T\n\n"
              "Value to the long at time t  =  (F_t - F0) / (1 + r)^(T-t)\n"
              "Value at expiry to the long  =  S_T - F0\n\n"
              "Benefits of carry LOWER the forward price; costs RAISE it.\n"
              "Futures and forward prices are equal unless rates and the\n"
              "underlying price are correlated.")

    d.h2("Swaps")
    d.formula("Net payment to the fixed payer\n"
              "   =  notional x (floating - fixed) x (days / 360)\n\n"
              "Value to the fixed payer\n"
              "   =  value of the floating bond - value of the fixed bond\n\n"
              "A swap is a package of forwards. The swap rate makes its\n"
              "initial value zero. Rising rates benefit the fixed payer.")

    d.h2("Options")
    d.formula("Call intrinsic  =  max(0, S - X)\n"
              "Put intrinsic   =  max(0, X - S)\n"
              "Option value    =  intrinsic value + time value\n\n"
              "PUT-CALL PARITY (European only)\n"
              "   c  +  X / (1 + r)^T   =   p  +  S0\n\n"
              "Volatility raises BOTH calls and puts.")

    d.h2("Binomial model")
    d.formula("pi  =  [ (1 + r) - d ] / ( u - d )\n\n"
              "c0  =  [ pi x c_up + (1 - pi) x c_down ] / (1 + r)\n\n"
              "Hedge ratio  =  (c_up - c_down) / (S_up - S_down)\n\n"
              "The REAL probability of an up move is never used.")

    d.h2("The things most often got wrong")
    d.bullets([
        "Price is fixed at inception; value starts at zero and moves afterwards.",
        "Benefits of carry such as dividends LOWER the forward price.",
        "A margin call must restore the INITIAL margin, not the maintenance margin.",
        "Volatility raises the value of a call AND a put.",
        "Put-call parity holds exactly for European options only.",
        "The real probability of an up move never enters the binomial model.",
        "A short call has unlimited loss; a short put's loss is bounded.",
        "Hedging and speculating use identical instruments; only the exposure differs.",
        "Notional is a reference quantity, not an amount invested.",
    ])
