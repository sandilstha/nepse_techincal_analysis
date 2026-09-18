"""Volume 1 study guide, modules 6-11 plus the formula appendix."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module6(d):
    d.h1(6, "Statistical Distributions for Prices and Returns",
         "Moving from describing data you have to modelling data you have not seen yet. "
         "Which distribution, what its moments mean, and how to update a belief when new "
         "information arrives.")

    d.h2("Expected value and the moments")
    d.p("An expected value is a probability-weighted average of what could happen. It is "
        "not what you expect to see; it is the long-run average if the situation repeated.")
    d.formula("E(X)  =  Σ P(xᵢ) × xᵢ\n\n"
              "Var(X)  =  Σ P(xᵢ) × [xᵢ − E(X)]²",
              "The variance is the probability-weighted average of squared distances from "
              "the mean, exactly as in Module 5 but with probabilities instead of counts.")
    d.p("The four moments describe a distribution completely enough for this curriculum: "
        "the mean locates it, the variance spreads it, skewness tilts it, and kurtosis "
        "thickens its tails.")

    d.h2("The distributions you must know")
    make_table(d,
               ["Distribution", "Shape and use", "Where it appears"],
               [["Uniform", "Every outcome equally likely", "Simulation inputs; simple "
                 "probability questions"],
                ["Binomial", "Count of successes in n independent yes/no trials",
                 "Up-or-down price trees; default counts"],
                ["Normal", "Symmetric bell, fully described by mean and variance",
                 "Returns, sampling distributions, confidence intervals"],
                ["Lognormal", "Right-skewed, cannot go below zero",
                 "Asset prices, because a price cannot be negative"],
                ["Student's t", "Like the normal but fatter tails",
                 "Small samples with unknown population variance"],
                ["Chi-square", "Positive only, right-skewed", "Tests about a variance"],
                ["F", "Ratio of two chi-squares", "Tests comparing two variances; ANOVA"]],
               widths=(20, 44, 36))
    d.key("Why returns are modelled as normal but prices as lognormal: if a continuously "
          "compounded return is normally distributed, then the price, which is the "
          "exponential of that return, is lognormally distributed. The lognormal cannot go "
          "below zero, which matches reality, and it is right-skewed, which matches the "
          "fact that a price can rise without limit but can only fall to zero.")

    d.h2("The normal distribution in practice")
    d.p("The normal distribution's usefulness comes from a single table. Standardise any "
        "value and you can read off the probability.")
    d.formula("z  =  (x − μ) / σ",
              "The z-score is how many standard deviations the observation sits from the "
              "mean. Negative means below.")
    d.p("Three confidence intervals are worth committing to memory, because they appear "
        "constantly and save you a table lookup.")
    make_table(d,
               ["Interval", "Contains", "z"],
               [["μ ± 1.00σ", "About 68% of outcomes", "1.00"],
                ["μ ± 1.65σ", "90%", "1.645"],
                ["μ ± 1.96σ", "95%", "1.96"],
                ["μ ± 2.58σ", "99%", "2.575"]],
               widths=(28, 44, 28))
    d.warn("Be careful whether a question wants one tail or two. A 95% two-tailed interval "
           "uses 1.96, but a 95% one-tailed test uses 1.645. Choosing the wrong one is a "
           "standard distractor, and the two numbers both appear in every answer list.")
    d.p("The safety-first criterion, also called Roy's criterion, applies this directly. "
        "Among portfolios, prefer the one least likely to fall below a threshold return, "
        "which means the one with the highest ratio below.")
    d.formula("SF Ratio  =  [ E(R) − R_threshold ]  /  σ",
              "Identical in form to the Sharpe ratio, with the threshold in place of the "
              "risk-free rate. When the threshold is the risk-free rate they are the same "
              "number.")

    d.h2("Conditional probability and Bayes")
    d.p("A conditional probability is the chance of something given that something else has "
        "already happened. It is the formal way of saying 'now that I know this, what "
        "should I think?'")
    d.formula("P(A | B)  =  P(AB) / P(B)\n\n"
              "Total probability:  P(A)  =  P(A|B)P(B)  +  P(A|Bᶜ)P(Bᶜ)")
    d.p("Bayes' formula reverses the conditioning. You know the probability of the evidence "
        "given the state of the world, and you want the probability of the state given the "
        "evidence.")
    d.formula("P(A | B)  =  P(B | A) × P(A)  /  P(B)",
              "In words: the updated belief equals the prior belief times how well the "
              "evidence fits it, scaled so that all possibilities still sum to one.")
    d.example("5% of companies in a market default. Your model flags 80% of the "
              "companies that go on to default, and it also flags 10% of the healthy ones. "
              "A company has just been flagged. How worried should you be?\n\n"
              "Out of 1,000 companies:\n"
              "  50 will default, and the model flags 40 of them.\n"
              "  950 are healthy, and the model flags 95 of them.\n"
              "  Total flagged = 135\n\n"
              "  P(default | flagged) = 40 / 135 = 29.6%\n\n"
              "The model is good and the flag still means a 70% chance the company is "
              "fine. That is the base rate at work: healthy companies are so much more "
              "numerous that their false positives swamp the true ones.")
    d.warn("Bayes questions almost always hide a low base rate. If only 2% of companies "
           "default and your model flags 90% of defaulters but also 10% of healthy firms, "
           "most flagged companies are healthy. Work through the tree with actual counts "
           "rather than trusting intuition, because intuition gets this wrong every time.")


def module7(d):
    d.h1(7, "Estimation and Hypothesis Testing",
         "You never have the whole population, only a sample. This module is about how much "
         "you can trust a sample, and how to test a claim with it.")

    d.h2("The central limit theorem")
    d.p("The single most useful result in applied statistics. Take repeated samples of size "
        "n from any population, whatever its shape, and the distribution of the sample "
        "means approaches a normal distribution as n grows. In practice n of 30 is treated "
        "as large enough.")
    d.formula("Standard error  =  σ / √n        (or  s / √n  when σ is unknown)",
              "Note the square root. To halve the standard error you need four times the "
              "sample, not twice. This is why precision is expensive.")
    d.key("The central limit theorem is what lets you use normal-distribution tools on data "
          "that is not itself normal. It is a statement about the behaviour of the mean, "
          "not about the behaviour of the underlying data.")

    d.h2("Confidence intervals")
    d.p("A confidence interval is a range built so that, over many repeated samples, the "
        "stated proportion of such ranges would contain the true value.")
    d.formula("Confidence interval  =  point estimate  ±  (reliability factor × standard error)\n\n"
              "                     =  x̄  ±  z × (σ/√n)      when σ is known\n"
              "                     =  x̄  ±  t × (s/√n)      when σ is unknown")
    d.p("Use the t-distribution when the population variance is unknown, which is nearly "
        "always. Its fatter tails produce a wider interval, which is the honest admission "
        "that you had to estimate the variance too. As n rises, t converges on z.")
    d.warn("The common misstatement: a 95% confidence interval does not mean there is a 95% "
           "probability the true value lies inside this particular interval. The true value "
           "is fixed; it is the interval that varies from sample to sample. Examiners test "
           "this wording directly.")

    d.h3("Sampling methods, and how sampling goes wrong")
    d.bullets([
        "Simple random: every member equally likely to be chosen.",
        "Stratified random: split the population into groups, then sample within each. "
        "Produces a sample that mirrors the population's structure.",
        "Cluster: split into clusters, then take whole clusters. Cheaper, usually less "
        "precise.",
        "Convenience and judgmental: non-random, quick, and open to bias.",
    ])
    d.p("Two biases are examined repeatedly. Survivorship bias arises when failed funds or "
        "delisted companies drop out of the data, which flatters every average you compute. "
        "Look-ahead bias arises when a test uses information that was not available at the "
        "time, such as an annual figure published months after the date being tested.")

    d.h2("Hypothesis testing, step by step")
    d.p("A hypothesis test is a disciplined way of deciding whether the data contradicts a "
        "claim. The structure never changes.")
    d.numbered([
        "State the null and the alternative. The null always contains the equality, and it "
        "is the statement you try to knock down.",
        "Choose the test statistic and the significance level, α. Typically 5% or 1%.",
        "Find the critical value or the p-value.",
        "Compare, then decide: reject the null, or fail to reject it.",
        "State the conclusion in the language of the original question, not in symbols.",
    ])
    d.key("You never accept a null hypothesis. You either reject it or fail to reject it. "
          "Failing to reject means the evidence was not strong enough, not that the null is "
          "true. This distinction is worth marks on its own.")

    d.h3("The two errors")
    make_table(d,
               ["", "Null is actually true", "Null is actually false"],
               [["You reject it", "Type I error, probability α", "Correct decision"],
                ["You fail to reject", "Correct decision", "Type II error, probability β"]],
               widths=(28, 36, 36))
    d.p("The power of a test is 1 − β, the chance of correctly rejecting a false null. "
        "Lowering α to reduce false positives raises β and lowers power. The only way to "
        "improve both at once is a larger sample.")
    d.p("The p-value is the probability of seeing a result at least as extreme as the one "
        "observed, if the null were true. Reject when the p-value is below α. It is a "
        "cleaner way to report a result than 'significant at 5%', because it lets the "
        "reader apply their own threshold.")

    d.example("A sample of 36 monthly returns has a mean of 8% and a standard "
              "deviation of 12%. Build a 95% confidence interval, then test the claim "
              "that the true mean is 5%.\n\n"
              "  Standard error = 12 / √36 = 2.0%\n"
              "  t for 35 degrees of freedom at 95%, two-tailed ≈ 2.03\n"
              "  Interval = 8 ± (2.03 × 2.0) = 3.94% to 12.06%\n\n"
              "TESTING μ = 5\n"
              "  t = (8 − 5) / 2.0 = 1.50\n"
              "  1.50 is inside ±2.03, so you fail to reject.\n\n"
              "Notice the shortcut: 5% already sits inside the confidence interval, so the "
              "test was always going to fail to reject. A two-tailed test at α and a "
              "(1 − α) confidence interval are the same statement written two ways.")

    d.h2("Choosing the right test")
    make_table(d,
               ["Question", "Test", "Distribution"],
               [["One mean, variance unknown", "t-test", "Student's t, n − 1 df"],
                ["Difference of two means, independent", "t-test", "Student's t"],
                ["Difference of paired observations", "Paired comparisons t-test",
                 "Student's t, n − 1 df"],
                ["A single variance", "Chi-square test", "Chi-square, n − 1 df"],
                ["Equality of two variances", "F-test", "F"],
                ["Correlation is zero", "t-test on r", "Student's t, n − 2 df"]],
               widths=(38, 30, 32))
    d.p("Parametric tests assume a distribution, usually normality, and are more powerful "
        "when that assumption holds. Non-parametric tests, such as the Spearman rank "
        "correlation, make no such assumption and are the right choice when the data is "
        "ranked, badly non-normal, or the sample is tiny.")
    d.warn("Degrees of freedom trip people up. A test of one mean uses n − 1. A test of a "
           "correlation uses n − 2, because two parameters have been estimated. Getting "
           "this wrong sends you to the wrong row of the table and to a plausible but "
           "wrong answer.")


def module8(d):
    d.h1(8, "The Return and Risk of a Financial Portfolio",
         "Where the volume pays off. Combining assets produces a risk that is less than the "
         "sum of its parts, and that single fact is the foundation of portfolio management.")

    d.h2("Portfolio return and risk")
    d.p("Portfolio return is easy: it is just the weighted average of the components.")
    d.formula("E(R_p)  =  w₁E(R₁)  +  w₂E(R₂)  +  …  +  wₙE(Rₙ)")
    d.p("Portfolio risk is not, and that asymmetry is the entire point of diversification.")
    d.formula("Two assets:\n\n"
              "σ²_p  =  w₁²σ₁²  +  w₂²σ₂²  +  2w₁w₂ρ₁,₂σ₁σ₂\n\n"
              "σ_p   =  √(σ²_p)",
              "The third term is where diversification lives. Because ρ can be less than 1, "
              "the portfolio's standard deviation is less than the weighted average of the "
              "individual standard deviations.")
    d.key("Portfolio standard deviation is a weighted average only when correlation is "
          "exactly +1. At every lower correlation there is a genuine risk reduction, and "
          "the lower the correlation the larger it is. At ρ = −1 risk can be driven to zero "
          "with the right weights.")

    d.example("Asset A returns 10% with a standard deviation of 20%. Asset B returns "
              "6% with a standard deviation of 12%. Their correlation is 0.3. You hold 60% "
              "in A and 40% in B.\n\n"
              "  E(R) = 0.6(10) + 0.4(6) = 8.4%\n\n"
              "  σ² = 0.6²(20²) + 0.4²(12²) + 2(0.6)(0.4)(0.3)(20)(12)\n"
              "     = 144.00 + 23.04 + 34.56\n"
              "     = 201.60\n"
              "  σ  = √201.60 = 14.20%\n\n"
              "The weighted average of the two standard deviations is 0.6(20) + 0.4(12) = "
              "16.8%. The portfolio's actual risk is 14.20%. That 2.6-point gap is "
              "diversification, and you were not charged anything for it.")

    d.h2("Systematic and non-systematic risk")
    d.p("Adding more assets keeps reducing risk, but not without limit. The reduction "
        "flattens out and never reaches zero.")
    d.bullets([
        "Non-systematic risk, also called unsystematic, firm-specific or diversifiable "
        "risk. A factory fire, a lawsuit, a failed product. Diversification removes it.",
        "Systematic risk, also called market or non-diversifiable risk. Interest rates, "
        "recessions, war. Diversification cannot remove it, because it hits everything.",
    ])
    d.key("The market rewards you only for systematic risk. You are not paid for bearing "
          "risk you could have removed for free by diversifying. This one sentence connects "
          "this module to the whole of Volume 9 and to the CAPM.")

    d.h2("The efficient frontier")
    d.p("Plot every possible portfolio on a chart with risk across and return up. The "
        "result is a solid region with a curved upper-left boundary.")
    d.bullets([
        "The minimum-variance frontier is the left-hand edge: the lowest risk achievable "
        "for each level of return.",
        "The global minimum-variance portfolio is the single leftmost point on it.",
        "The efficient frontier is only the part of that edge above the global minimum. "
        "Below it, you could get more return for the same risk, so nobody rational would "
        "choose it.",
    ])

    d.h2("Adding a risk-free asset")
    d.p("Introduce an asset with no risk and the picture changes completely. You can now "
        "combine it with any risky portfolio, and those combinations sit on a straight "
        "line rather than a curve.")
    d.formula("Capital allocation line:\n\n"
              "E(R_p)  =  R_f  +  [ (E(R_m) − R_f) / σ_m ] × σ_p",
              "The bracket is the slope: extra return per unit of risk. It is the Sharpe "
              "ratio of the risky portfolio.")
    d.p("The best line is the steepest one that still touches the frontier, and it touches "
        "at exactly one point. Every investor, whatever their risk tolerance, should hold "
        "that same risky portfolio and adjust their risk by mixing it with the risk-free "
        "asset. This is the two-fund separation theorem.")
    d.p("When every investor does this, the tangency portfolio must be the market portfolio, "
        "and the line is renamed the capital market line.")
    d.warn("The capital allocation line and the capital market line are drawn identically "
           "and are not the same thing. The capital allocation line works for any risky "
           "portfolio; the capital market line is the special case where that portfolio is "
           "the market. Also, both plot total risk on the x-axis. The security market line, "
           "which arrives in Volume 9, plots beta instead. Mixing them up is the most "
           "expensive confusion in portfolio theory.")

    d.h2("Where the investor's own preference enters")
    d.p("The frontier and the capital market line are the same for everybody. What differs "
        "is how much risk each investor will accept, captured by a utility function.")
    d.formula("U  =  E(R)  −  ½ × A × σ²\n\n"
              "  A = the investor's risk-aversion coefficient",
              "Higher A means more risk-averse, so risk is penalised harder and the chosen "
              "portfolio sits further down the line towards the risk-free asset. A can be "
              "negative for a risk-seeking investor, and zero for one who is indifferent.")


def module9(d):
    d.h1(9, "Simulation of Asset Prices and Returns",
         "What to do when the maths has no clean answer. Three techniques, each with a "
         "different assumption about where the future comes from.")

    d.h2("Historical simulation")
    d.p("Take the actual returns that occurred in the past and replay them. It needs no "
        "assumption about the shape of the distribution, because it uses the real one.")
    d.bullets([
        "Strength: the fat tails, skewness and correlations are all genuine, not modelled.",
        "Weakness: you can only replay what happened. If the last twenty years contained "
        "no currency crisis, your simulation contains no currency crisis.",
    ])

    d.h2("Bootstrap resampling")
    d.p("Draw repeatedly from the historical sample, with replacement, to build many "
        "artificial datasets. Each draw is a real observation, but the order and "
        "combination are new.")
    d.p("It answers a question that historical simulation cannot: how much would my answer "
        "have varied if I had drawn a different sample? That makes it a way of putting a "
        "confidence interval around a statistic whose distribution you do not know.")

    d.h2("Monte Carlo simulation")
    d.p("Specify a distribution for each input, then draw random values from it thousands of "
        "times and record the outcome each time. The result is a full distribution of "
        "possible answers rather than a single point estimate.")
    d.numbered([
        "Specify the quantity you want and the variables that drive it.",
        "Choose a distribution for each driver, with its parameters.",
        "Draw one random value for each driver and compute the outcome.",
        "Repeat many thousands of times.",
        "Summarise the distribution of outcomes: mean, spread, and the tails.",
    ])
    d.key("Monte Carlo is the standard tool for problems with no analytical solution: "
          "path-dependent options, retirement planning with uncertain longevity, and "
          "value-at-risk for a complex portfolio.")
    d.warn("Monte Carlo is not forecasting. It tells you what follows from the "
           "distributions you assumed, and nothing more. Assume normal returns and it will "
           "obligingly tell you that extreme losses are rare. The output is only as good as "
           "the input distributions, a point the curriculum makes explicitly.")


def module10(d):
    d.h1(10, "Applications of Simple Linear Regression",
         "Fitting a straight line through data to explain one variable with another, then "
         "checking honestly whether the line is worth anything.")

    d.h2("The model")
    d.formula("Yᵢ  =  b₀  +  b₁Xᵢ  +  εᵢ\n\n"
              "  Y  = dependent variable, the thing being explained\n"
              "  X  = independent variable, the explanation\n"
              "  b₀ = intercept\n"
              "  b₁ = slope\n"
              "  ε  = error, everything the line does not capture")
    d.p("The line is chosen by least squares: the values of b₀ and b₁ that make the sum of "
        "the squared vertical distances from the points to the line as small as possible. "
        "Squaring is what makes large misses count disproportionately, and it is why a "
        "single outlier can pull the whole line.")
    d.formula("b₁  =  Cov(X,Y) / Var(X)            b₀  =  Ȳ  −  b₁X̄",
              "The slope is covariance scaled by the variance of X. The fitted line always "
              "passes through the point of the two means.")

    d.h2("The four assumptions")
    d.p("Every conclusion drawn from a regression depends on these, and most of the "
        "examinable content is about detecting when they fail.")
    make_table(d,
               ["Assumption", "What it means", "How it fails"],
               [["Linearity", "The true relationship is a straight line",
                 "A curved pattern in the residual plot"],
                ["Homoskedasticity", "The error variance is constant",
                 "Residuals fan out; called heteroskedasticity"],
                ["Independence", "Errors are uncorrelated with each other",
                 "Serial correlation, common in time series"],
                ["Normality", "Errors are normally distributed",
                 "Matters mainly for small samples"]],
               widths=(26, 36, 38))
    d.p("Residual plots are the practical tool. Plot the errors against the fitted values "
        "and look for pattern. A random cloud means the assumptions are plausible; any "
        "visible shape means one of them has failed.")

    d.h2("Is the line any good?")
    d.p("Three separate questions, with three separate tests.")
    d.formula("Total variation   SST  =  Σ(Yᵢ − Ȳ)²\n"
              "Explained         SSR  =  Σ(Ŷᵢ − Ȳ)²\n"
              "Unexplained       SSE  =  Σ(Yᵢ − Ŷᵢ)²\n\n"
              "SST  =  SSR  +  SSE\n\n"
              "R²  =  SSR / SST")
    d.p("R² is the share of the variation in Y that the line accounts for. In a simple "
        "regression with one independent variable it equals the square of the correlation "
        "between X and Y.")
    d.formula("Standard error of the estimate  =  √( SSE / (n − 2) )",
              "The typical size of a residual, in the units of Y. Smaller is better, and "
              "unlike R² it is not bounded, so it cannot be compared across different data.")
    d.p("To test whether the slope is genuinely different from zero, use a t-test with "
        "n − 2 degrees of freedom.")
    d.formula("t  =  (b₁ − 0) / standard error of b₁",
              "A significant slope means X explains something about Y. In a simple "
              "regression the F-test of the whole model gives the identical conclusion, "
              "because there is only one explanatory variable.")
    d.warn("A high R² does not make a model correct. It can come from a spurious "
           "relationship, from a single outlier, or from a trend shared by two unrelated "
           "series. And regression never demonstrates causation, however tidy the line "
           "looks. Expect at least one question testing exactly this.")

    d.example("A regression of a fund's return on the market's return, over 20 "
              "observations, gives Cov(X,Y) = 24 and Var(X) = 16. The means are X̄ = 10 "
              "and Ȳ = 25. Total variation SST = 500 and unexplained SSE = 125.\n\n"
              "  b₁ = 24 / 16 = 1.5\n"
              "  b₀ = 25 − 1.5(10) = 10\n"
              "  Fitted line:  Y = 10 + 1.5X\n\n"
              "  SSR = 500 − 125 = 375\n"
              "  R²  = 375 / 500 = 0.75\n"
              "  SEE = √(125 / 18) = 2.64\n\n"
              "Read it in words: when the market rises one point this fund rises one and a "
              "half, three-quarters of its movement is explained by the market, and a "
              "typical miss is about 2.6 percentage points. The slope of 1.5 is what "
              "Volume 9 will call beta.")

    d.h2("Prediction")
    d.p("Put an X value into the fitted line and you get a predicted Y. The interval around "
        "that prediction is wider than the interval around the line itself, because it must "
        "allow both for uncertainty in the estimated coefficients and for the irreducible "
        "error in any single observation.")
    d.warn("Predicting outside the range of the observed X values is extrapolation, and the "
           "relationship you fitted is not evidence about territory you never sampled.")

    d.h2("When the relationship is not a straight line")
    d.p("Some relationships become linear after a transformation, which lets you keep using "
        "the same machinery.")
    d.bullets([
        "Log-lin: take the log of Y. Fits constant growth rates.",
        "Lin-log: take the log of X. Fits diminishing returns.",
        "Log-log: take the log of both. The slope is then an elasticity, the percentage "
        "change in Y for a one percent change in X.",
    ])


def module11(d):
    d.h1(11, "Introduction to Financial Data Science",
         "A descriptive module with no formulas. Learn the vocabulary precisely, because "
         "every mark here is for using the right word for the right thing.")

    d.h2("Two kinds of data")
    d.p("Quantitative data is numeric: prices, returns, rates, accounting figures. "
        "Qualitative data is not: text from filings and news, images, audio, satellite "
        "photographs. Much of the recent progress in the field is about turning the second "
        "kind into the first.")
    d.p("Big data is usually described by the four Vs: volume, how much there is; velocity, "
        "how fast it arrives; variety, how many forms it takes; and veracity, how reliable "
        "it is. Alternative data means anything outside traditional market and accounting "
        "sources, such as card transactions, shipping movements or web traffic.")

    d.h2("Machine learning")
    d.p("The distinction the exam cares about is what the algorithm is given to learn from.")
    make_table(d,
               ["Type", "What it is given", "Typical use"],
               [["Supervised", "Inputs and the correct answers",
                 "Predicting returns, classifying credit quality"],
                ["Unsupervised", "Inputs only, no answers",
                 "Clustering similar companies, finding structure"],
                ["Deep learning", "Layered neural networks",
                 "Image and language tasks, complex patterns"],
                ["Reinforcement", "A reward signal from its own actions",
                 "Trade execution, dynamic allocation"]],
               widths=(22, 40, 38))
    d.key("Overfitting is the central risk and the most examinable idea in the module. A "
          "model that fits its training data perfectly has usually memorised noise, and it "
          "performs badly on data it has not seen. The defence is to hold back part of the "
          "data and test on that, never on the data the model learned from.")

    d.h2("Where it is used, and the cautions")
    d.p("Applications run through the whole investment process: text analysis of filings "
        "and news, sentiment scoring, algorithmic execution, robo-advice, credit scoring "
        "and risk monitoring.")
    d.bullets([
        "Data quality: alternative data is often incomplete, inconsistent, or collected for "
        "some entirely different purpose.",
        "Privacy and regulation: personal data carries legal obligations, and some "
        "alternative data may amount to material non-public information.",
        "Transparency: a complex model may produce a recommendation nobody can explain, "
        "which is difficult to defend to a client or a regulator.",
        "Survivorship and look-ahead bias: both from Module 7, and both easy to reintroduce "
        "accidentally in a large automated dataset.",
    ])


def appendix(d):
    d.h1(None, "Formula sheet")
    d.p("Everything in this volume worth memorising, in one place. If you can reproduce "
        "this page from memory and say what each line means, you are ready.")

    d.h2("Returns")
    d.formula("Total return     =  (P₁ − P₀ + I₁) / P₀\n"
              "Required return  =  real risk-free + inflation + risk premium\n"
              "Real return      =  (1 + nominal)/(1 + inflation) − 1\n"
              "Continuous       =  ln(P₁/P₀)\n"
              "Geometric mean   =  [(1+r₁)…(1+rₙ)]^(1/n) − 1\n"
              "Harmonic mean    =  n / Σ(1/xᵢ)\n"
              "Annualised       =  (1 + r_period)^(periods per year) − 1\n"
              "Leveraged        =  r_p + (debt/equity)(r_p − r_borrow)")

    d.h2("Time value of money")
    d.formula("PV       =  FV / (1 + r)ⁿ\n"
              "EAR      =  (1 + stated/m)^m − 1\n"
              "Gordon   =  D₁ / (r − g)\n"
              "r        =  D₁/P₀ + g\n"
              "Forward  =  (1 + r₂)² = (1 + r₁)(1 + f₁,₁)")

    d.h2("Describing data")
    d.formula("Sample variance  =  Σ(xᵢ − x̄)² / (n − 1)\n"
              "Coefficient of variation  =  s / x̄\n"
              "Cov(X,Y)  =  Σ(xᵢ − x̄)(yᵢ − ȳ) / (n − 1)\n"
              "Corr(X,Y) =  Cov(X,Y) / (s_X s_Y)\n"
              "z         =  (x − μ) / σ")

    d.h2("Inference")
    d.formula("Standard error  =  s / √n\n"
              "Confidence interval  =  x̄ ± (reliability × standard error)\n"
              "Safety-first ratio   =  [E(R) − R_threshold] / σ\n"
              "Bayes:  P(A|B)  =  P(B|A)P(A) / P(B)")

    d.h2("Portfolio")
    d.formula("E(R_p)  =  Σ wᵢE(Rᵢ)\n"
              "σ²_p    =  w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂\n"
              "CAL     =  R_f + [(E(R_m) − R_f)/σ_m] × σ_p\n"
              "Utility =  E(R) − ½Aσ²")

    d.h2("Regression")
    d.formula("Y  =  b₀ + b₁X + ε\n"
              "b₁ =  Cov(X,Y) / Var(X)\n"
              "SST = SSR + SSE\n"
              "R²  =  SSR / SST\n"
              "SEE =  √(SSE / (n − 2))\n"
              "t   =  b₁ / SE(b₁),  with n − 2 degrees of freedom")

    d.h2("The ten things most often got wrong")
    d.numbered([
        "Using the arithmetic mean where the geometric mean belonged.",
        "Dividing by n instead of n − 1 for a sample variance.",
        "Comparing two quoted rates without converting both to effective annual rates.",
        "Using 1.96 for a one-tailed test, or 1.645 for a two-tailed one.",
        "Saying a 95% confidence interval has a 95% chance of containing the true value.",
        "Saying you accept the null hypothesis.",
        "Using n − 1 degrees of freedom for a correlation test instead of n − 2.",
        "Treating the capital market line and the security market line as the same thing.",
        "Reading a high R² as proof the model is right, or as evidence of causation.",
        "Forgetting to clear the calculator's cash flow register between questions.",
    ])


def main(d):
    module6(d)
    module7(d)
    module8(d)
    module9(d)
    module10(d)
    module11(d)
    appendix(d)
