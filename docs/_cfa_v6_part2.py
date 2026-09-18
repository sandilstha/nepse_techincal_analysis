"""Volume 6, modules 6 to 13. Imported by make_cfa_v6.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module6(d):
    d.h1(6, "Fixed-Income Bond Valuation: Prices and Yields",
         "The foundation of the volume. A bond is worth the present value of what it "
         "promises, and everything later is an elaboration of that sentence.")

    d.formula("Price  =  sum of  [ coupon / (1 + r)^t ]  +  par / (1 + r)^n\n\n"
              "  r = the market discount rate, per period\n"
              "  n = the number of periods",
              "For a semi-annual bond, halve the coupon and the yield and double the number "
              "of periods.")
    d.example("A three-year bond, par Rs 1,000, annual coupon 7%, market yield 9%.\n\n"
              "  70/1.09 + 70/1.09^2 + 1,070/1.09^3\n"
              "  = 64.22 + 58.92 + 826.15\n"
              "  = Rs 949.29\n\n"
              "It trades below par because its 7% coupon is below the 9% the market demands. "
              "The Rs 50.71 discount is precisely the compensation for receiving a "
              "below-market coupon for three years.")

    d.h2("The three relationships")
    make_table(d,
               ["Condition", "Price", "Called"],
               [["Coupon rate > market yield", "Above par", "Premium bond"],
                ["Coupon rate = market yield", "Exactly par", "Par bond"],
                ["Coupon rate < market yield", "Below par", "Discount bond"]],
               widths=(34, 24, 42))
    d.key("You should be able to state whether a bond trades at a premium or a discount "
          "without any calculation, purely by comparing the coupon with the yield. Questions "
          "often ask only for the direction, and doing the arithmetic wastes time you need "
          "elsewhere.")
    d.p("A bond's price converges on par as maturity approaches, whatever it started at. A "
        "premium bond drifts down and a discount bond drifts up, purely through the passage "
        "of time. This is called the constant-yield price trajectory, or pull to par.")

    d.h2("Clean and dirty price")
    d.formula("Full (dirty) price  =  flat (clean) price  +  accrued interest\n\n"
              "Accrued interest  =  coupon x (days since last coupon / days in period)",
              "Quoted prices are clean. The buyer actually pays the dirty price, because the "
              "seller is entitled to the interest earned since the last coupon date.")
    d.warn("Day count conventions differ and the exam tests them. Government bonds typically "
           "use actual/actual; corporate and municipal bonds typically use 30/360. Using the "
           "wrong convention gives an accrued interest figure that is close but wrong, which "
           "is exactly what the distractor answers are built from.")

    d.h2("Matrix pricing")
    d.p("Most bonds do not trade on most days. Matrix pricing estimates a yield for an "
        "untraded bond by interpolating from the yields of traded bonds with similar credit "
        "quality and maturity. It is an estimate, and it is only as good as the "
        "comparability of the bonds used.")


def module7(d):
    d.h1(7, "Yield and Yield Spread Measures for Fixed-Rate Bonds",
         "Several different numbers are all called 'yield'. This module distinguishes them.")

    d.h2("The yield measures")
    d.formula("Current yield  =  annual coupon / current price\n"
              "  Ignores any gain or loss to maturity. Crude.\n\n"
              "Yield to maturity  =  the single rate that makes the present value of ALL\n"
              "  the promised cash flows equal the current price.\n\n"
              "Yield to call  =  the same calculation, run to the call date and call price.\n\n"
              "Yield to worst  =  the LOWEST of the yield to maturity and every yield to call.")
    d.example("A bond priced at Rs 950 with an 8% annual coupon on Rs 1,000 par.\n\n"
              "  Current yield = 80 / 950 = 8.42%\n\n"
              "The yield to maturity is higher still, because the holder also collects a "
              "Rs 50 gain when the bond redeems at par. For a bond trading at a PREMIUM the "
              "ordering reverses: current yield exceeds the yield to maturity, because the "
              "holder faces a capital loss on the way to par.\n\n"
              "  Discount bond:  coupon rate  <  current yield  <  YTM\n"
              "  Premium bond:   coupon rate  >  current yield  >  YTM")
    d.key("The three assumptions buried in the yield to maturity, and the exam asks for them "
          "by name. The bond is held to maturity; the issuer makes every payment in full and "
          "on time; and every coupon is reinvested at the yield to maturity itself. The third "
          "is the one that almost never holds, and Module 10 is about what happens when it "
          "does not.")
    d.warn("For a callable bond trading at a premium, the yield to call is usually below the "
           "yield to maturity, so yield to worst equals the yield to call. Quoting the yield "
           "to maturity for such a bond overstates what an investor will actually earn, which "
           "is exactly why the yield to worst convention exists.")

    d.h2("Spreads")
    make_table(d,
               ["Spread", "Measured against"],
               [["G-spread", "The yield of a government bond of comparable maturity, "
                 "interpolated"],
                ["I-spread", "The swap rate of comparable maturity"],
                ["Z-spread", "The constant amount added to EVERY spot rate on the government "
                 "curve that makes the present value equal the price"],
                ["Option-adjusted spread", "The Z-spread with the value of any embedded "
                 "option removed"]],
               widths=(28, 72))
    d.key("The OAS is the one to compare bonds on when options are involved, because it "
          "strips out the option and leaves only the compensation for credit and liquidity. "
          "For a CALLABLE bond, OAS is less than Z-spread, because part of the apparent "
          "spread was really payment for the call option the investor sold. For a PUTABLE "
          "bond the relationship reverses.")


def module8(d):
    d.h1(8, "Yield and Yield Spread Measures for Floating-Rate Instruments",
         "A floater resets its coupon, so 'yield to maturity' does not mean much. The "
         "equivalent measure is the margin.")

    d.formula("Coupon  =  reference rate  +  quoted margin\n\n"
              "  The QUOTED margin is fixed at issue.\n"
              "  The REQUIRED margin is what the market demands now.",
              "The reference rate is typically a short-term market rate, reset every quarter "
              "or every six months.")
    make_table(d,
               ["If the required margin is", "The floater trades", "Because"],
               [["Equal to the quoted margin", "At par", "It pays exactly what is demanded"],
                ["Above the quoted margin", "Below par",
                 "The issuer's credit has deteriorated since issue"],
                ["Below the quoted margin", "Above par", "The issuer's credit has improved"]],
               widths=(30, 24, 46))
    d.p("The discount margin is the floater's equivalent of a yield to maturity: the margin "
        "over the reference rate that makes the present value of the expected cash flows "
        "equal the price. For a floater trading at par, the discount margin simply equals the "
        "quoted margin.")
    d.key("A floater's price barely moves when the general level of interest rates changes, "
          "because the coupon follows. It moves substantially when the issuer's CREDIT "
          "changes, because the quoted margin cannot follow. Interest rate risk is nearly "
          "absent; credit risk is entirely present.")
    d.warn("A floater is only price-stable at the reset dates. Between resets the coupon is "
           "fixed, so the price does respond to rate moves over that short window. The "
           "duration of a floater is roughly the time remaining to the next reset, not zero "
           "and not its maturity.")


def module9(d):
    d.h1(9, "The Term Structure of Interest Rates: Spot, Par, and Forward Curves",
         "There is not one interest rate but a whole curve of them, and the three ways of "
         "expressing that curve all contain the same information.")

    d.h2("The three curves")
    make_table(d,
               ["Curve", "Shows"],
               [["Spot curve", "The rate today for a single payment at each future date. "
                 "Built from zero coupon bonds"],
                ["Par curve", "The coupon rate at which a bond of each maturity would trade "
                 "at exactly par"],
                ["Forward curve", "The rate agreed today for borrowing over a future period"]],
               widths=(22, 78))
    d.key("All three carry the same information expressed differently, and each can be "
          "derived from the others. If a question gives you spot rates and asks for a forward "
          "rate, or gives par rates and asks for spots, it is testing whether you can move "
          "between them, not whether you have extra data.")

    d.h2("Forward rates from spot rates")
    d.formula("(1 + z_n)^n  =  (1 + z_m)^m  x  (1 + f_(m, n-m))^(n-m)\n\n"
              "  z = spot rate,  f = the implied forward rate",
              "The principle: investing for n years directly must give the same result as "
              "investing for m years and rolling into the forward. Otherwise there is "
              "arbitrage.")
    d.example("The one-year spot rate is 4% and the two-year spot rate is 5%. What one-year "
              "rate, one year forward, is implied?\n\n"
              "  (1.05)^2 = (1.04) x (1 + f)\n"
              "  1.1025   = 1.04 x (1 + f)\n"
              "  1 + f    = 1.06010    so  f = 6.01%\n\n"
              "Nobody quoted 6.01%. It is forced: if the forward were 5%, you would borrow "
              "for two years at 5%, lend for one at 4% and lock the second year at 5%, and "
              "the two routes would not balance. A rough check is that the forward is "
              "approximately 2 x 5 - 4 = 6%, which is close enough to catch an error.")
    d.p("Bootstrapping runs the process the other way: starting from the shortest par bond, "
        "solve for each spot rate in turn, using the spot rates already derived to discount "
        "the earlier coupons.")

    d.h2("The shape of the curve")
    d.bullets([
        "Upward sloping, or normal: long rates above short. The usual condition.",
        "Flat: little difference across maturities.",
        "Inverted: short rates above long. Historically associated with an approaching "
        "recession, and a leading indicator in Volume 2.",
        "Humped: rises then falls.",
    ])
    d.p("Three theories explain the shape. Pure expectations says forward rates are the "
        "market's unbiased forecast of future short rates. Liquidity preference adds that "
        "investors demand a premium for lending long, so the curve slopes up even when rates "
        "are expected to be flat. Market segmentation says supply and demand at each maturity "
        "are largely independent, set by the institutions that operate there.")
    d.warn("Under liquidity preference, a forward rate is NOT a pure forecast: it is the "
           "expected future rate plus a term premium. An upward-sloping curve therefore does "
           "not necessarily mean the market expects rates to rise. Questions exploit this "
           "distinction routinely.")


def module10(d):
    d.h1(10, "Interest Rate Risk and Return",
         "Two risks that work in opposite directions, which is what makes fixed income "
         "interesting rather than merely arithmetic.")

    d.h2("The two risks")
    make_table(d,
               ["Risk", "What happens when rates RISE"],
               [["Price risk", "The bond's price falls. Bad if you must sell"],
                ["Reinvestment risk", "Coupons are reinvested at higher rates. Good if you "
                 "are holding"]],
               widths=(24, 76))
    d.key("The two offset. A rate rise hurts the price today and helps every future coupon "
          "reinvestment, and at one particular horizon the two effects cancel exactly. That "
          "horizon is the Macaulay duration, and the insight is the reason duration is "
          "defined the way it is rather than as a simple sensitivity measure.")
    d.formula("If the investment horizon  =  Macaulay duration,\n"
              "   price risk and reinvestment risk offset, and the realised return\n"
              "   is locked in at the original yield to maturity.\n\n"
              "If the horizon is SHORTER than the duration, price risk dominates.\n"
              "If the horizon is LONGER than the duration, reinvestment risk dominates.")
    d.example("An investor holds a bond with a Macaulay duration of 6.5 years.\n\n"
              "  Horizon 4 years  -> shorter than duration -> price risk dominates.\n"
              "     A rate RISE hurts the overall result.\n\n"
              "  Horizon 9 years  -> longer than duration -> reinvestment risk dominates.\n"
              "     A rate rise HELPS the overall result.\n\n"
              "  Horizon 6.5 years -> the two cancel, and the return is immunised.\n\n"
              "This is why a pension fund with liabilities in fifteen years is not "
              "automatically harmed by rising rates.")
    d.warn("A zero coupon bond has no coupons to reinvest, so it has NO reinvestment risk. "
           "Its Macaulay duration equals its maturity exactly, and holding it to maturity "
           "locks in the yield with certainty. This makes it the cleanest instrument for "
           "matching a known future liability.")


def module11(d):
    d.h1(11, "Yield-Based Bond Duration Measures and Properties",
         "How much does the price move when the yield moves? Duration is the answer, and it "
         "is the single most examined concept in the volume.")

    d.h2("The two durations")
    d.formula("Macaulay duration  =  the weighted average time to receive the cash flows,\n"
              "                      weighted by their present values. Measured in YEARS.\n\n"
              "Modified duration  =  Macaulay duration / (1 + yield per period)\n"
              "                      The approximate % price change for a 1% yield move.\n\n"
              "Approximate % price change  =  - modified duration x change in yield")
    d.example("A bond has a Macaulay duration of 7.2 years and a yield to maturity of 6%, "
              "paid annually.\n\n"
              "  Modified duration = 7.2 / 1.06 = 6.79\n\n"
              "If yields rise by 50 basis points:\n"
              "  % price change = -6.79 x 0.005 = -3.40%\n\n"
              "A Rs 1,000,000 holding falls by about Rs 34,000. Note the minus sign: it is "
              "not decoration. Price and yield move in opposite directions, always.")
    d.formula("Money duration  =  modified duration x full price of the position\n\n"
              "Price value of a basis point (PVBP)\n"
              "     =  the price change for a ONE basis point move\n"
              "     =  money duration x 0.0001")
    d.example("A position has a full value of Rs 5,000,000 and a modified duration of 6.79.\n\n"
              "  Money duration = 6.79 x 5,000,000 = Rs 33,950,000\n"
              "  PVBP = 33,950,000 x 0.0001 = Rs 3,395 per basis point\n\n"
              "Money duration and PVBP express the risk in currency rather than percentage "
              "terms, which is what a risk manager actually needs.")

    d.h2("What makes duration longer")
    make_table(d,
               ["Feature", "Effect on duration"],
               [["Longer maturity", "LONGER duration"],
                ["Lower coupon", "LONGER duration"],
                ["Lower yield", "LONGER duration"],
                ["An embedded call or put", "SHORTER duration"]],
               widths=(30, 70))
    d.key("The intuition behind the coupon effect: duration is the average time to get your "
          "money back. A high coupon returns more of the value early, which pulls the average "
          "forward and shortens duration. A zero coupon bond returns nothing until maturity, "
          "so its duration equals its maturity and is the longest possible for that term.")
    d.warn("Duration is NOT a measure of time to maturity, despite being quoted in years. A "
           "thirty-year bond with a high coupon can have a shorter duration than a "
           "ten-year zero coupon bond. Treat it as a sensitivity measure that happens to be "
           "expressed in years.")

    d.h2("Portfolio duration")
    d.formula("Portfolio duration  =  sum of ( weight_i  x  duration_i )",
              "Weighted by MARKET value, not by par value or by number of bonds. The "
              "approximation assumes all yields move together by the same amount.")


def module12(d):
    d.h1(12, "Yield-Based Bond Convexity and Portfolio Properties",
         "Duration assumes the price-yield relationship is a straight line. It is not, and "
         "convexity is the correction.")

    d.h2("Why duration is not enough")
    d.p("The true relationship between price and yield is a curve, convex towards the origin. "
        "Duration is the tangent to that curve at the current yield, so it is accurate for "
        "small moves and increasingly wrong for large ones.")
    d.formula("% price change  =  ( - modified duration x change in yield )\n"
              "                   + ( 0.5 x convexity x (change in yield)^2 )",
              "The first term is the duration estimate; the second is the convexity "
              "correction. Note the yield change is SQUARED, so the correction is always "
              "positive for a conventional bond.")
    d.example("A bond has a modified duration of 8.0 and a convexity of 95. Yields rise by "
              "150 basis points.\n\n"
              "  Duration effect  = -8.0 x 0.015 = -12.00%\n"
              "  Convexity effect = 0.5 x 95 x (0.015)^2 = 0.5 x 95 x 0.000225 = +1.07%\n"
              "  Total estimate   = -10.93%\n\n"
              "Duration alone predicted a 12% loss; the actual loss is nearer 10.93%. Now run "
              "the same bond with yields FALLING 150bp:\n\n"
              "  Duration effect  = +12.00%,  convexity effect = +1.07%,  total +13.07%\n\n"
              "The gain exceeds the loss. That asymmetry is what convexity buys you, and it "
              "is why investors pay for it.")
    d.key("Convexity is always beneficial for a conventional bond: it reduces the loss when "
          "yields rise and increases the gain when they fall. Because it is desirable, a bond "
          "with higher convexity commands a higher price and therefore a lower yield, all "
          "else equal. Convexity is not free.")
    d.warn("A callable bond exhibits NEGATIVE convexity at low yields. As rates fall, the "
           "call becomes likely and the price stops rising, compressing towards the call "
           "price. This price compression is the defining feature of a callable bond and a "
           "guaranteed exam topic.")

    d.h2("What raises convexity")
    d.p("The same features that lengthen duration also raise convexity: longer maturity, "
        "lower coupon, lower yield. In addition, for a given duration, a portfolio whose cash "
        "flows are spread widely across time has more convexity than one whose cash flows are "
        "concentrated at a single date.")


def module13(d):
    d.h1(13, "Curve-Based and Empirical Fixed-Income Risk Measures",
         "Yield-based duration fails when cash flows are not fixed. Effective duration is "
         "what replaces it.")

    d.h2("Effective duration")
    d.p("For a bond with an embedded option, the cash flows themselves change when rates "
        "change, so there is no single yield to differentiate. Effective duration is measured "
        "empirically instead, by shifting the whole benchmark curve and repricing.")
    d.formula("Effective duration  =  (PV_down - PV_up) / (2 x PV_0 x delta curve)\n\n"
              "Effective convexity  =  (PV_down + PV_up - 2 x PV_0)\n"
              "                        / (PV_0 x (delta curve)^2)",
              "PV_up and PV_down are the prices after shifting the entire benchmark yield "
              "curve up and down by the same amount.")
    d.example("A callable bond is priced at 100.00. Shift the curve down 25bp and it prices "
              "at 100.90; shift it up 25bp and it prices at 98.85.\n\n"
              "  Effective duration = (100.90 - 98.85) / (2 x 100.00 x 0.0025)\n"
              "                     = 2.05 / 0.50 = 4.10\n\n"
              "Note the asymmetry: the price rose 0.90 but fell 1.15. The upside is damped "
              "because the call caps it. An identical straight bond would have moved "
              "symmetrically.")
    d.key("Use effective duration whenever the cash flows are uncertain: callable and putable "
          "bonds, mortgage-backed securities, and anything with a prepayment option. Use "
          "modified duration only when the cash flows are genuinely fixed. Applying modified "
          "duration to a callable bond is simply a category error.")

    d.h2("Key rate duration")
    d.p("Effective duration assumes the entire curve shifts in parallel. In practice curves "
        "steepen, flatten and twist. Key rate duration measures sensitivity to a change at "
        "one specific maturity point with the rest of the curve held still, which reveals "
        "exposures a single duration number conceals.")
    d.warn("Two portfolios with identical effective duration can behave completely "
           "differently when the curve twists rather than shifts. A barbell of very short and "
           "very long bonds and a bullet concentrated in the middle can match on duration and "
           "diverge sharply in a steepening. Duration is a one-number summary and it hides "
           "exactly this.")

    d.h2("Empirical duration")
    d.p("Analytical duration is computed from the bond's own mathematics. Empirical duration "
        "is estimated by regressing actual price changes against actual yield changes. The "
        "two differ most for high-yield bonds, because in a crisis government yields fall "
        "while credit spreads widen, and the two effects partly cancel. Empirical duration "
        "for such bonds is therefore lower than the analytical figure, and it is the more "
        "realistic measure of what will actually happen.")
