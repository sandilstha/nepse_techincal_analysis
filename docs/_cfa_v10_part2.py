"""Volume 10, modules 6 to 10 and the summary sheet. Imported by make_cfa_v10.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfa_guide import make_table   # noqa: E402


def module6(d):
    d.h1(6, "Guidance for Standard IV: Duties to Employers",
         "What you owe the firm that employs you, and the boundaries of that obligation.")

    d.h2("IV(A) Loyalty")
    d.p("Members must act for the benefit of their employer, must not deprive it of the "
        "advantage of their skills and abilities, must not divulge confidential information, "
        "and must not otherwise cause harm.")
    d.key("The rule on leaving is precise. BEFORE resigning, you may not solicit clients, "
          "take records, or begin competing. AFTER leaving, you may compete and may contact "
          "former clients from PUBLICLY available sources, but you may never take or use the "
          "employer's records, client lists or models. Nothing may be taken, even material "
          "you personally created, without written permission.")
    d.example("An analyst has accepted a job at a competitor, starting next month. Which acts "
              "are permitted?\n\n"
              "  Emailing her own research models home for later use:\n"
              "    NOT permitted. The models are the employer's property.\n\n"
              "  Telling her best clients privately that she is leaving and inviting them:\n"
              "    NOT permitted while still employed. This is soliciting.\n\n"
              "  Memorising nothing and, after joining, contacting former clients found in "
              "a public directory:\n"
              "    Permitted, provided no employer records were used and no agreement "
              "forbids it.\n\n"
              "  Working weekends on an unrelated consulting job without telling anyone:\n"
              "    NOT permitted. Independent practice requires consent, because it may "
              "compete with the employer.")
    d.p("Whistleblowing is the recognised exception. Where the employer's conduct is illegal "
        "or unethical and would harm clients or the market, the duty to protect them "
        "overrides the duty of loyalty.")

    d.h2("IV(B) Additional Compensation Arrangements")
    d.p("Members must not accept gifts, benefits, compensation or consideration that competes "
        "with, or might create a conflict with, their employer's interest, unless they obtain "
        "WRITTEN consent from all parties involved.")
    d.warn("Written consent from all parties is the requirement, and the word 'written' is "
           "what makes the difference in exam answers. Verbal permission from a supervisor is "
           "not sufficient. A performance bonus offered by a grateful client is the standard "
           "fact pattern, and the correct response is always to disclose it in writing and "
           "obtain written consent before accepting.")

    d.h2("IV(C) Responsibilities of Supervisors")
    d.p("Members with supervisory responsibility must make reasonable efforts to ensure that "
        "anyone subject to their supervision complies with applicable laws, rules, regulations "
        "and the Code and Standards.")
    d.key("A supervisor can violate IV(C) without any personal wrongdoing at all, simply by "
          "failing to establish or enforce adequate compliance procedures. The obligation is "
          "to make reasonable EFFORTS, so a supervisor who has good systems and is deceived "
          "by a determined subordinate has not necessarily violated it.")
    d.p("Where a firm has no adequate compliance system, a supervisor should decline "
        "supervisory responsibility in writing until one is established. On detecting a "
        "violation, the supervisor must investigate promptly, place limits on the individual's "
        "activities while doing so, and not rely on the person's assurances.")


def module7(d):
    d.h1(7, "Guidance for Standard V: Investment Analysis, Recommendations, and Actions",
         "The Standard governing the actual analytical work, and the one that connects "
         "directly to every other volume in the curriculum.")

    d.h2("V(A) Diligence and Reasonable Basis")
    d.p("Members must exercise diligence, independence and thoroughness in analysing "
        "investments and making recommendations, and must have a reasonable and adequate "
        "basis, supported by appropriate research and investigation, for any analysis, "
        "recommendation or action.")
    d.warn("Relying on a third party does not transfer the obligation. If you use an outside "
           "research provider, a quantitative model, or another firm's analysis, you must "
           "make reasonable efforts to establish that it is sound. Using a model you do not "
           "understand, or forwarding a report you have not evaluated, violates V(A) even if "
           "the underlying work happened to be correct.")
    d.example("Which of these constitutes a reasonable basis?\n\n"
              "  Recommending a share after reading a single newspaper article:\n"
              "    NO. Insufficient investigation.\n\n"
              "  Recommending a fund after reviewing its strategy, holdings, risk controls, "
              "manager record and fee structure:\n"
              "    YES.\n\n"
              "  Using a third-party model after reviewing its assumptions, testing it, and "
              "understanding its limitations:\n"
              "    YES. Reliance is permitted once you have verified soundness.\n\n"
              "  Repeating a respected analyst's conclusion because she is usually right:\n"
              "    NO. Her reputation is not your reasonable basis.")

    d.h2("V(B) Communication with Clients and Prospective Clients")
    d.p("Members must disclose to clients the basic format and general principles of the "
        "investment processes used, must promptly disclose any material change to those "
        "processes, must use reasonable judgement in identifying which factors are important "
        "to an analysis, and must DISTINGUISH FACT FROM OPINION.")
    d.key("Separating fact from opinion is the sub-standard tested most often. A "
          "recommendation may state opinions freely, but they must be identifiable as "
          "opinions. Writing 'earnings will grow 20%' as though it were established fact "
          "violates V(B); writing 'we expect earnings to grow 20%, based on the following "
          "assumptions' does not.")
    d.p("Members must also disclose the significant limitations and risks inherent in the "
        "process, and may not omit factors merely because they are unfavourable.")

    d.h2("V(C) Record Retention")
    d.p("Members must develop and maintain appropriate records supporting their analysis, "
        "recommendations, actions and other communications with clients.")
    d.warn("Records belong to the FIRM, not to the member, and this connects directly to "
           "IV(A). A member leaving an employer cannot take the supporting records with them, "
           "and must therefore recreate the analysis from public sources at the new firm "
           "before relying on it again. CFA Institute recommends a seven-year retention "
           "period where no regulatory requirement applies.")


def module8(d):
    d.h1(8, "Guidance for Standard VI: Conflicts of Interest",
         "Conflicts are not forbidden. Concealing them is.")

    d.h2("VI(A) Disclosure of Conflicts")
    d.p("Members must make full and fair disclosure of all matters that could reasonably be "
        "expected to impair their independence or objectivity, or to interfere with their "
        "duties to clients, prospective clients and employers. Disclosures must be prominent, "
        "in plain language, and communicated effectively.")
    d.key("The remedy under VI(A) is DISCLOSURE, not abstention. A member who owns shares in "
          "a company may still recommend it, provided the holding is disclosed prominently. "
          "Compare this with I(B), where the remedy for a compromised gift is to refuse it. "
          "Knowing which Standard governs tells you which remedy the answer requires.")
    d.p("Matters requiring disclosure include personal ownership of securities under "
        "coverage, board memberships, the firm's investment banking relationships with a "
        "covered company, market-making activity, and any compensation arrangement that could "
        "create a bias.")
    d.example("An analyst is about to publish a favourable report on a company. Which facts "
              "must be disclosed?\n\n"
              "  She personally owns shares in the company:  YES, prominently.\n"
              "  Her firm underwrote the company's recent bond issue:  YES.\n"
              "  Her brother works there as an engineer:  YES, if it could reasonably be "
              "seen as affecting objectivity.\n"
              "  She once toured the factory at her own firm's expense:  Not required; no "
              "conflict arises.\n\n"
              "Having disclosed, she may publish the favourable recommendation. The conflict "
              "does not disqualify her; concealing it would.")

    d.h2("VI(B) Priority of Transactions")
    d.p("Investment transactions for clients and employers must have priority over "
        "transactions in which a member is the beneficial owner.")
    d.formula("THE ORDER OF PRIORITY\n\n"
              "  1.  Clients\n"
              "  2.  The employer\n"
              "  3.  The member personally",
              "Members may trade for their own accounts, provided clients are not "
              "disadvantaged and the firm's policies are followed.")
    d.warn("Front running, meaning trading ahead of a client order to benefit from the price "
           "impact, violates VI(B). Personal trading is not prohibited; doing it FIRST is. "
           "Recommended procedures include blackout periods around client trades, "
           "pre-clearance requirements, and duplicate confirmations to compliance.")

    d.h2("VI(C) Referral Fees")
    d.p("Members must disclose to their employer, clients and prospective clients, as "
        "appropriate, any compensation, consideration or benefit received from or paid to "
        "others for the recommendation of products or services.")
    d.key("Disclosure under VI(C) must be made BEFORE the client engages, so that the client "
          "can evaluate the referral and any partiality in it, and the arrangement must be "
          "disclosed whether the member pays the fee or receives it. Disclosing afterwards "
          "defeats the purpose and does not satisfy the Standard.")


def module9(d):
    d.h1(9, "Guidance for Standard VII: Responsibilities as a CFA Institute Member or "
            "CFA Candidate",
         "Conduct within the programme itself, and how the designation may be described.")

    d.h2("VII(A) Conduct as Participants in CFA Institute Programs")
    d.p("Members and candidates must not engage in any conduct that compromises the "
        "reputation or integrity of CFA Institute or the CFA designation, or the integrity, "
        "validity or security of CFA Institute programs.")
    d.bullets([
        "Do not disclose or discuss exam questions or content after sitting the exam.",
        "Do not cheat, or assist anyone else to.",
        "Do not disregard exam rules or the testing centre's instructions.",
        "Do not misrepresent your candidacy or your results.",
    ])
    d.warn("Discussing specific exam questions with anyone, including future candidates and "
           "on social media, violates VII(A). Expressing an opinion ABOUT the programme, such "
           "as criticising the curriculum or the exam's difficulty, is entirely permitted. "
           "The line is between the exam's confidential CONTENT and your views about the "
           "programme, and questions are written precisely on that line.")

    d.h2("VII(B) Reference to CFA Institute, the CFA Designation, and the CFA Program")
    d.p("When referring to membership, candidacy or the designation, members and candidates "
        "must not misrepresent or exaggerate the meaning or implications of any of them.")
    make_table(d,
               ["Correct", "Incorrect"],
               [["'John Smith, CFA'", "'John Smith, C.F.A.' with full stops"],
                ["'Chartered Financial Analyst'", "'Chartered Financial Analyst' used as a "
                 "noun, as in 'he is a CFA'"],
                ["'I am a Level II candidate in the CFA Program'",
                 "'CFA Level II' or 'CFA (Level II)' after your name"],
                ["'Passed all three levels on the first attempt', if true",
                 "Any claim that the designation implies superior performance"]],
               widths=(48, 52))
    d.key("Three rules that cover most VII(B) questions. The designation is an ADJECTIVE, "
          "never a noun: 'a CFA charterholder', not 'a CFA'. There is no partial designation, "
          "so you are a candidate in the programme until you hold the charter. And you may "
          "never suggest that holding the charter predicts better investment results.")
    d.p("You may only describe yourself as a candidate if you are registered for the next "
        "scheduled exam. Someone who has passed Level II but is not currently enrolled is not "
        "a candidate and must not claim to be one.")


def module10(d):
    d.h1(10, "Application of the Code and Standards: Level I",
         "How to answer the questions, which is a distinct skill from knowing the Standards.")

    d.h2("A method for case questions")
    d.numbered([
        "Identify who the parties are, and specifically WHO THE CLIENT IS. Many questions "
        "turn entirely on this.",
        "Identify what the member actually did, separating the act from the surrounding "
        "narrative detail, most of which is there to distract you.",
        "Ask which duty that act touches: to the market, the client, the employer, or the "
        "profession. That points you to the Standard.",
        "Check whether disclosure, consent or abstention was the required remedy. Different "
        "Standards require different responses to superficially similar facts.",
        "Choose the answer that names the Standard actually breached, not the one that "
        "describes the most objectionable behaviour.",
    ])
    d.key("When two answers both look defensible, the question is almost always testing a "
          "specific distinction rather than your judgement. Common ones: disclosure against "
          "abstention; written against verbal consent; before leaving against after leaving; "
          "material and non-public together against either one alone; the plan sponsor "
          "against the plan beneficiaries.")

    d.h2("The distinctions most often tested")
    make_table(d,
               ["Question", "Answer"],
               [["Law and Code conflict", "Follow the STRICTER of the two"],
                ["Conflict of interest exists", "DISCLOSE it; you need not abstain"],
                ["Gift from a covered company", "Refuse anything beyond token value"],
                ["Extra compensation from a client", "WRITTEN consent from all parties"],
                ["Material non-public information", "Do not trade, do not tell; urge public "
                 "disclosure"],
                ["Public plus non-material non-public", "Mosaic theory; you may act"],
                ["Leaving an employer", "Take nothing; do not solicit before you go"],
                ["Pension fund client", "The duty runs to the BENEFICIARIES"],
                ["Suitability", "Judge it at the TOTAL PORTFOLIO level"],
                ["Using the designation", "It is an adjective; there is no partial charter"]],
               widths=(38, 62))
    d.warn("Two habits cost marks even when the Standards are known. First, answering from "
           "instinct rather than from the text: something that feels unfair may violate no "
           "Standard at all, and 'no violation' is frequently the correct answer. Second, "
           "missing that a single fact pattern can breach SEVERAL Standards at once, so read "
           "whether the question asks which one is 'most likely' violated or asks you to "
           "identify all of them.")

    d.h2("Recommended procedures worth remembering")
    d.p("Many questions ask what a firm SHOULD do rather than what was violated. The "
        "recurring answers are: adopt a written compliance manual and a code of ethics; "
        "require pre-clearance and duplicate confirmations for personal trading; maintain "
        "restricted and watch lists; establish information barriers between departments; "
        "document allocation policies for block trades; and provide regular ethics training "
        "with a designated compliance officer.")


def appendix(d):
    d.h1(None, "Summary sheet")
    d.p("The seven Standards, their sub-standards, and the rules that decide most questions. "
        "If you can reproduce this page from memory, you are ready.")

    d.h2("The seven Standards by number")
    d.formula("I    PROFESSIONALISM\n"
              "     A Knowledge of the Law     B Independence and Objectivity\n"
              "     C Misrepresentation        D Misconduct\n\n"
              "II   INTEGRITY OF CAPITAL MARKETS\n"
              "     A Material Non-public Information   B Market Manipulation\n\n"
              "III  DUTIES TO CLIENTS\n"
              "     A Loyalty, Prudence and Care   B Fair Dealing   C Suitability\n"
              "     D Performance Presentation     E Preservation of Confidentiality\n\n"
              "IV   DUTIES TO EMPLOYERS\n"
              "     A Loyalty   B Additional Compensation\n"
              "     C Responsibilities of Supervisors\n\n"
              "V    INVESTMENT ANALYSIS, RECOMMENDATIONS AND ACTIONS\n"
              "     A Diligence and Reasonable Basis   B Communication\n"
              "     C Record Retention\n\n"
              "VI   CONFLICTS OF INTEREST\n"
              "     A Disclosure of Conflicts   B Priority of Transactions\n"
              "     C Referral Fees\n\n"
              "VII  RESPONSIBILITIES AS A MEMBER OR CANDIDATE\n"
              "     A Conduct in CFA Institute Programs\n"
              "     B Reference to CFA Institute and the Designation")

    d.h2("The decisive rules")
    d.formula("LAW v CODE        follow the STRICTER\n"
              "CONFLICT          disclose it; abstention is not required\n"
              "EXTRA PAY         written consent from ALL parties, in advance\n"
              "MNPI              do not trade, do not tell, urge public disclosure\n"
              "MOSAIC            public + NON-material non-public = you may act\n"
              "PRIORITY          clients, then employer, then yourself\n"
              "LEAVING           take nothing; no soliciting before departure\n"
              "PENSION CLIENT    the beneficiaries, not the sponsor\n"
              "SUITABILITY       judged on the TOTAL portfolio\n"
              "DESIGNATION       an adjective; no partial charter exists")

    d.h2("The things most often got wrong")
    d.bullets([
        "Where law is less strict than the Code, the Code governs.",
        "A conflict requires DISCLOSURE; a compromising gift requires REFUSAL.",
        "Consent for additional compensation must be WRITTEN, not verbal.",
        "Selective disclosure to a few analysts does not make information public.",
        "The mosaic theory permits acting on a material conclusion you assembled yourself.",
        "For a pension fund, the client is the beneficiaries.",
        "Suitability is assessed at portfolio level, not security level.",
        "Confidentiality survives the end of the relationship, but never applies against a "
        "Professional Conduct Program investigation.",
        "A supervisor can violate IV(C) through inadequate procedures alone.",
        "Discussing exam content violates VII(A); criticising the programme does not.",
        "'CFA' is an adjective. There is no such thing as 'a CFA' or 'CFA Level II'.",
        "'No violation' is often the correct answer. Do not manufacture one.",
    ])
