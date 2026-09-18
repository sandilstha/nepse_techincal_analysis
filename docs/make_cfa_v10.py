"""
Plain-language study guide for
    CFA Program Curriculum 2027, Level I, Volume 10 - Ethical and Professional Standards

Run:  venv/Scripts/python.exe docs/make_cfa_v10.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import Guide, cover, make_table   # noqa: E402
from _cfa_v10_part2 import (module6, module7, module8, module9, module10,
                            appendix)   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CFA-L1-V10-Ethics-Summary.pdf")

MODULES = [
    (1, "Ethics and Trust in the Investment Profession", "Why any of this matters"),
    (2, "Code of Ethics and Standards of Professional Conduct", "The text itself"),
    (3, "Standard I: Professionalism", "Law, competence, independence, misrepresentation"),
    (4, "Standard II: Integrity of Capital Markets", "Material non-public information"),
    (5, "Standard III: Duties to Clients", "Loyalty, suitability, fair dealing"),
    (6, "Standard IV: Duties to Employers", "Loyalty, compensation, supervision"),
    (7, "Standard V: Investment Analysis and Recommendations", "Reasonable basis, records"),
    (8, "Standard VI: Conflicts of Interest", "Disclose, prioritise, referrals"),
    (9, "Standard VII: Responsibilities as a Member or Candidate", "The programme itself"),
    (10, "Application of the Code and Standards", "Working through cases"),
]

STANDFIRST = ("All ten learning modules in everyday English, with every Standard explained, "
              "worked cases, and the traps that catch candidates in the exam.")


def how_to_use(d):
    d.h1(None, "How to use this guide")
    d.p("Ethics carries between 15% and 20% of the Level I exam, more than any other topic "
        "except Financial Statement Analysis, and it is the one candidates most often "
        "underprepare because it appears to require no study. It does.")
    d.numbered([
        "Modules 1 and 2 set up the framework and give you the text of the Code and the seven "
        "Standards. Learn the Standards by NUMBER, because answer choices are phrased as "
        "'Standard III(B)' rather than in words.",
        "Modules 3 to 9 work through the seven Standards one at a time, with the guidance and "
        "recommended procedures for each.",
        "Module 10 applies them to cases, which is exactly what the exam does.",
    ])
    d.key("Ethics questions are not tests of whether you are a good person. They are tests of "
          "whether you know which specific Standard a fact pattern violates. Two answers may "
          "both describe behaviour that feels wrong; only one names the Standard that was "
          "actually breached. Study it as vocabulary with rules attached, not as morality.")
    d.warn("The single most important rule in the entire volume: where law and the Code "
           "differ, follow the STRICTER. If local law is less strict than the Code, follow "
           "the Code. If local law is stricter than the Code, follow the law. Members must "
           "comply with the Code everywhere they operate, regardless of local practice, and "
           "'everyone here does it' is never a defence.")


def module1(d):
    d.h1(1, "Ethics and Trust in the Investment Profession",
         "The conceptual introduction. Short, and the source of a handful of definitional "
         "questions.")

    d.h2("Why ethics matters here specifically")
    d.p("Investment management runs on trust to an unusual degree. Clients hand over money to "
        "people whose work they cannot evaluate, whose decisions they cannot observe, and "
        "whose results are largely indistinguishable from luck over any short period. That "
        "information asymmetry is why the profession needs enforced standards rather than "
        "general good intentions.")
    d.key("Ethical failures damage the whole profession, not only the firm involved. When "
          "trust falls, clients withdraw, regulation tightens, and the cost of capital rises "
          "for everyone. This is why the Code treats conduct as a collective obligation "
          "rather than a private matter.")

    d.h2("Ethics, law and the framework")
    d.p("Legal standards set a floor: what you must not do. Ethical standards sit above them, "
        "covering conduct that is legal but wrong. Much damaging behaviour in finance has "
        "been entirely lawful.")
    d.p("The curriculum describes an ethical decision-making framework in four steps: "
        "identify the relevant facts, duties and conflicts; consider the alternatives and "
        "seek guidance; act; and reflect afterwards on the outcome.")
    d.warn("Behavioural pressures cause more misconduct than bad character does. Overconfidence "
           "in one's own judgement, situational pressure from a deadline or a target, and "
           "loyalty to colleagues all push ordinarily decent people towards poor decisions. "
           "The curriculum's position is that a framework applied in advance protects better "
           "than good intentions applied under pressure.")


def module2(d):
    d.h1(2, "Code of Ethics and Standards of Professional Conduct",
         "The text you are being examined on. Learn the structure, then the detail.")

    d.h2("The Code of Ethics")
    d.p("Six principles, stated at a high level. Members and candidates must:")
    d.numbered([
        "Act with integrity, competence, diligence and respect, in an ethical manner with the "
        "public, clients, prospective clients, employers, employees, colleagues and other "
        "participants in the global markets.",
        "Place the integrity of the profession and the interests of clients above their own "
        "personal interests.",
        "Use reasonable care and exercise independent professional judgement when conducting "
        "analysis, making recommendations, taking action and engaging in other professional "
        "activities.",
        "Practise and encourage others to practise in a professional and ethical manner that "
        "reflects credit on themselves and the profession.",
        "Promote the integrity and viability of the global capital markets for the ultimate "
        "benefit of society.",
        "Maintain and improve their professional competence and strive to maintain and "
        "improve the competence of other investment professionals.",
    ])

    d.h2("The seven Standards")
    make_table(d,
               ["", "Standard", "Covers"],
               [["I", "Professionalism", "Knowledge of the law, independence and objectivity, "
                 "misrepresentation, misconduct"],
                ["II", "Integrity of Capital Markets", "Material non-public information, "
                 "market manipulation"],
                ["III", "Duties to Clients", "Loyalty and care, fair dealing, suitability, "
                 "performance presentation, confidentiality"],
                ["IV", "Duties to Employers", "Loyalty, additional compensation, "
                 "responsibilities of supervisors"],
                ["V", "Investment Analysis, Recommendations and Actions",
                 "Diligence and reasonable basis, communication, record retention"],
                ["VI", "Conflicts of Interest", "Disclosure, priority of transactions, "
                 "referral fees"],
                ["VII", "Responsibilities as a Member or Candidate",
                 "Conduct in the programme, reference to the designation"]],
               widths=(8, 30, 62))
    d.key("Memorise the number-to-topic mapping above. In the exam, answer choices name "
          "Standards by number and letter, and a candidate who knows the behaviour was wrong "
          "but cannot identify which Standard covers it will still choose incorrectly "
          "between two plausible options.")
    d.p("The Code and Standards apply to all CFA Institute members and to all candidates in "
        "the programme, worldwide, in every professional activity. Violations are handled "
        "through CFA Institute's Professional Conduct Program, with sanctions ranging from a "
        "private censure to suspension or revocation of membership and the designation.")


def module3(d):
    d.h1(3, "Guidance for Standard I: Professionalism",
         "Four sub-standards covering the foundations: obeying the law, staying objective, "
         "telling the truth, and general conduct.")

    d.h2("I(A) Knowledge of the Law")
    d.p("Members must understand and comply with all applicable laws, rules and regulations, "
        "including the Code and Standards, and must not knowingly participate in any "
        "violation.")
    d.formula("WHERE THEY CONFLICT, FOLLOW THE STRICTER:\n\n"
              "  Local law less strict than the Code   ->  follow the CODE\n"
              "  Local law stricter than the Code      ->  follow the LAW\n"
              "  No applicable local law               ->  follow the CODE",
              "This rule generates more exam questions than any other single provision in "
              "the volume. Commit it to memory in exactly this form.")
    d.p("On discovering a violation, a member must dissociate: stop participating, and "
        "document the concern in writing to a supervisor or compliance. Reporting to "
        "regulators is recommended where appropriate but not generally required by the Code "
        "itself.")
    d.warn("Inaction is participation. A member who knows of ongoing misconduct and merely "
           "keeps out of it has still violated I(A). The required response is active "
           "dissociation, and if the conduct continues, resignation may be necessary. "
           "'I wasn't involved' is not a defence available under this Standard.")

    d.h2("I(B) Independence and Objectivity")
    d.p("Members must use reasonable care and judgement to achieve and maintain independence "
        "and objectivity, and must not offer, solicit or accept any gift or consideration "
        "that could reasonably be expected to compromise their own or another's independence.")
    d.example("An analyst covering a company is invited by that company to tour a remote "
              "facility. Which arrangement is acceptable?\n\n"
              "  Company-chartered flight, luxury hotel, all paid by the company:\n"
              "    NOT acceptable. Accepting lavish hospitality from a covered company "
              "compromises the appearance of independence.\n\n"
              "  Analyst's firm pays for commercial flights and accommodation:\n"
              "    Acceptable. Paying your own way removes the conflict entirely.\n\n"
              "  Modest transport from the airport where no commercial option exists:\n"
              "    Acceptable, because it is necessary and not lavish.\n\n"
              "The test is not whether you would in fact be influenced. It is whether a "
              "reasonable observer would think your objectivity could be affected.")
    d.p("A gift from a CLIENT for past performance is treated differently from one from a "
        "company under coverage, but it must still be disclosed to the employer, because it "
        "could bias the member towards that client over others.")

    d.h2("I(C) Misrepresentation")
    d.p("Members must not knowingly make any misrepresentation relating to investment "
        "analysis, recommendations, actions, or other professional activities. This covers "
        "guaranteeing returns, overstating credentials or the firm's capabilities, and "
        "plagiarism.")
    d.warn("Plagiarism sits under I(C) and catches people repeatedly. Using another's work "
           "without attribution violates it, INCLUDING in these situations: copying a "
           "competitor's report; using a phrase from a research piece without quoting; "
           "presenting a model built by a departed colleague as your own. The one recognised "
           "exception is factual information from recognised statistical services, which need "
           "not be individually attributed.")

    d.h2("I(D) Misconduct")
    d.p("Members must not commit any act involving dishonesty, fraud or deceit, or do "
        "anything that reflects adversely on their professional reputation, integrity or "
        "competence. This reaches personal conduct where it bears on professional "
        "trustworthiness.")
    d.key("I(D) is about trustworthiness, not respectability. Personal behaviour that is "
          "merely embarrassing or unpopular does not violate it. Behaviour indicating "
          "dishonesty, such as a conviction for fraud or misappropriating funds, does, even "
          "if entirely outside work.")


def module4(d):
    d.h1(4, "Guidance for Standard II: Integrity of Capital Markets",
         "Two sub-standards protecting the market itself rather than any individual client.")

    d.h2("II(A) Material Non-public Information")
    d.p("Members in possession of material non-public information that could affect the value "
        "of an investment must not act or cause others to act on it.")
    make_table(d,
               ["Test", "Meaning"],
               [["Material", "A reasonable investor would want to know it, or it would "
                 "affect the price if disclosed"],
                ["Non-public", "Not yet disseminated to the marketplace generally. "
                 "Selective disclosure to a few analysts does NOT make it public"]],
               widths=(20, 80))
    d.key("The mosaic theory is the essential exception and the exam tests it constantly. An "
          "analyst may combine PUBLIC information with NON-MATERIAL non-public information to "
          "reach a conclusion that is itself material, and may trade on that conclusion. The "
          "skill of assembling the picture is precisely what analysts are paid for. What is "
          "forbidden is acting on a single piece of information that is both material AND "
          "non-public.")
    d.example("Which of these may an analyst act upon?\n\n"
              "  A director says earnings will miss badly next week:\n"
              "    NO. Material and non-public. Do not trade, and do not tell anyone.\n\n"
              "  Counting lorries leaving a factory, noting hiring patterns, and speaking "
              "to suppliers, then concluding output has fallen sharply:\n"
              "    YES. This is the mosaic theory. Each item is non-material or public; "
              "the conclusion is the analyst's own work.\n\n"
              "  The company's results were released this morning and you read them first:\n"
              "    YES. Public information. Being quick is not a violation.\n\n"
              "  A friend at the printer mentions an unannounced takeover:\n"
              "    NO. Material and non-public, and the source makes it worse.")
    d.p("Where a firm has both an investment banking arm and a research arm, information "
        "barriers, historically called Chinese walls, restrict the flow of information "
        "between them. Firms should also maintain restricted lists and watch lists, and "
        "supervise personal trading.")
    d.warn("If a company discloses material information to you selectively, you must not "
           "trade on it, but you should encourage the company to disclose it publicly. "
           "Receiving it accidentally does not make trading permissible. The obligation "
           "attaches to the information, not to how you came by it.")

    d.h2("II(B) Market Manipulation")
    d.p("Members must not engage in practices that distort prices or artificially inflate "
        "trading volume with the intent to mislead. Two forms are identified.")
    d.bullets([
        "Information-based: spreading false or misleading information, or 'pump and dump' "
        "schemes.",
        "Transaction-based: trades that create a false impression of activity or price, such "
        "as wash trading, or securing a closing price to flatter a valuation.",
    ])
    d.key("INTENT is the distinguishing element of II(B). Legitimate trading strategies, "
          "including large orders that move the market and arbitrage between related "
          "securities, do not violate it. What matters is whether the purpose was to deceive "
          "other participants.")


def module5(d):
    d.h1(5, "Guidance for Standard III: Duties to Clients",
         "The largest Standard, with five sub-standards, and the source of a large share of "
         "exam questions.")

    d.h2("III(A) Loyalty, Prudence and Care")
    d.p("Members have a duty of loyalty to clients and must act with reasonable care and "
        "exercise prudent judgement. Client interests come before the employer's and before "
        "the member's own.")
    d.warn("Identifying the CLIENT is the examinable difficulty. For a pension fund, the "
           "client is the plan BENEFICIARIES, not the company that sponsors the plan or the "
           "trustees who hired you. If the sponsor asks you to invest in a way that suits the "
           "company but harms the beneficiaries, the beneficiaries win. This fact pattern "
           "recurs constantly.")
    d.p("Soft dollars, or client brokerage, belong to the client and must be used for "
        "research that benefits the client, not for the firm's general overheads.")

    d.h2("III(B) Fair Dealing")
    d.p("Members must deal fairly and objectively with all clients when providing analysis, "
        "making recommendations, taking action or engaging in other professional activities.")
    d.key("Fair does not mean equal. Clients may legitimately receive different services "
          "according to what they pay for, and a firm may offer a premium tier. What is "
          "forbidden is DISADVANTAGING any client, particularly by giving favoured clients "
          "advance notice of a recommendation or allocating good trades preferentially.")
    d.p("Recommended procedures: distribute recommendations to all eligible clients "
        "simultaneously, shorten the time between decision and dissemination, maintain a "
        "written allocation policy for block trades and new issues, and allocate pro rata.")

    d.h2("III(C) Suitability")
    d.p("Where a member is in an advisory relationship, they must make reasonable inquiry "
        "into the client's experience, risk and return objectives and financial constraints, "
        "must reassess and update that information regularly, and must judge suitability in "
        "the context of the client's TOTAL portfolio.")
    d.warn("Suitability is judged at the portfolio level, not the individual security level. "
           "A single volatile holding can be entirely suitable within a diversified portfolio "
           "for a client with that risk tolerance. Where the member manages to a stated "
           "mandate or index rather than for an individual, the obligation is to the stated "
           "strategy, not to any one investor's circumstances.")

    d.h2("III(D) Performance Presentation")
    d.p("Communications about performance must be fair, accurate and complete. Do not "
        "misstate performance, do not present the results of a selected subset of accounts as "
        "representative, and disclose whether figures are gross or net of fees.")

    d.h2("III(E) Preservation of Confidentiality")
    d.p("Information about current, former and prospective clients must be kept confidential "
        "unless it concerns illegal activities, disclosure is required by law, or the client "
        "permits it.")
    d.key("Note that the duty survives the relationship: it applies to FORMER clients "
          "indefinitely. The one situation in which a member must always cooperate is a CFA "
          "Institute Professional Conduct Program investigation, where confidentiality does "
          "not shield the member.")


def build():
    d = Guide(volume=10, subject="Ethical and Professional Standards")
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
