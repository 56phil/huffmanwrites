#!/usr/bin/env python3
"""Watch federal dockets relevant to the site and report anything new.

Philip, 2026-09-19: "I must keep an eye on this story." (Kennedy Center.)
Philip, 2026-09-24: "I want to start following the docket for Katie Fang's
suite against AG Tod Blanch regarding the Epstein files." — the names as given
were wrong; the case is *Phang v. Blanche*, No. 1:26-cv-01417 (EGS).

Philip, 2026-10-24: "Alison Gill has a suite against the FBI seeking information
about their handling of the Epstein files. I want you add it to your docket
watch." — as with Phang, the name as given is not the caption. The plaintiff is
*MSW Media, Inc.*, Gill's company, not Gill; the defendant is the Department of
Justice, and the FBI is the component that holds the records. *MSW Media, Inc. v.
Department of Justice*, No. 1:25-cv-02518 (BAH), D.D.C., Judge Beryl A. Howell.

Philip, 2026-10-24: "What about the golf course case?" — *D.C. Preservation
League v. Department of the Interior*, No. 1:26-cv-00477 (ACR), D.D.C., Judge
Ana C. Reyes: the challenge to the East Potomac Golf Links redevelopment. It is
the same beat as Beatty (the administration remaking a Washington landmark, and
the court deciding on what record), which is why the registry carries it.

Five dockets are watched, from the same primitive and the same report:

  beatty  — Beatty v. Trump, No. 1:25-cv-04480 (CRC), D.D.C. (Kennedy Center)
  phang   — Phang v. Blanche, No. 1:26-cv-01417 (EGS), D.D.C. (Epstein Files
            Transparency Act)
  msw     — MSW Media, Inc. v. Department of Justice, No. 1:25-cv-02518 (BAH),
            D.D.C. (Epstein review training videos, FOIA)
  golf    — D.C. Preservation League v. Department of the Interior, No.
            1:26-cv-00477 (ACR), D.D.C. (East Potomac Golf Links)
  cadc    — Phang v. Blanche, D.C. Cir. No. 26-5299 (Epstein files appeal)

Each case moves in day-scale bursts, and the coverage of all of them is unreliable —
outlets conflate the Kennedy Center's two-year renovation closure with the
seven-day safety closure, and the Epstein-files coverage reports deadlines
Sullivan set by minute order that never appear in a news story. What can be
trusted is the docket. So watch the docket.

This reads the CourtListener Atom feed for each case and compares the newest
entries against stored watermarks. Two kinds of entry matter and both are
tracked:

  * ECF-numbered entries ("Entry #50"), watermarked by entry number; and
  * minute entries ("Minute entry from 2026-09-19"), which carry only an opaque
    id and no ECF number, watermarked by that id.

The split is not academic. In *Phang*, Judge Sullivan rules and sets deadlines
by minute order — the September 19 schedule for the stay motion and the order
setting the September 24 answer deadline are both minute entries — and in the
30-entry window currently served, 18 of 30 entries are minute entries. A
watcher that keyed only on "Entry #N" would silently drop every one of them,
which is the failure mode that matters most here: not a wrong report but a
missing one.

Exit codes:
  0 — nothing new (the common case; a no-op)
  0 — new material found AND the report was delivered
  2 — could not read a feed (network, or CourtListener changed shape)
  3 — new material found but delivery failed

A non-zero exit routes to scripts/alert-failure.sh via the runner, so a silent
failure to reach a docket does not look like "nothing happened" — which is the
failure mode that matters for a watch job.

Usage:
  check-docket.py                 # watch every case, update watermarks, report
  check-docket.py --case phang    # restrict to one case (repeatable)
  check-docket.py --dry-run       # report what WOULD change; touch nothing
  check-docket.py --no-update     # report but do not move the watermarks
  check-docket.py --quiet         # only report on change
  check-docket.py --status        # print watermarks and newest entries
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "scripts" / "docket-watch-state.json"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) huffmanwrites-docket-watch"


# --------------------------------------------------------------------------
# Registry. One entry per case. KNOWN is a map of ECF number -> one-line
# summary, so a report says what changed rather than just "entry 90 appeared".
# Kept short on purpose: this is a pointer to go read the document, not a
# substitute for reading it.
#
# CALENDAR is dates that force a fresh look regardless of whether anything is
# filed. The docket and the case calendar are different instruments and both
# matter. Past entries are kept as a record of what a date meant once it
# passed, and are marked DISCHARGED (or the like) in place.
# --------------------------------------------------------------------------
CASES: "dict[str, dict]" = {
    "beatty": {
        "case": "BEATTY v. TRUMP, 1:25-cv-04480",
        "docket_id": "72069932",
        "slug": "beatty-v-trump",
        "label": "Kennedy Center",
        "known": {
            48: "Preliminary injunction — bars effectuating the Mar 16 closure decision until the Board approves a conforming closure AND the court dissolves/modifies. STILL IN FORCE.",
            49: "Permanent injunction — the renaming is void; no signage on the building or grounds naming anyone but JFK. STILL IN FORCE.",
            50: "Memorandum opinion, Beatty v. Trump, 834 F. Supp. 3d 41 (D.D.C. 2026).",
            77: "Memo opinion & order — enjoins the renovation inscription and the Trump Plaza renaming; denies the $100M endowment plaque as unripe (60-day notice instead).",
            78: "Notice of board closure vote + Trump Truth Social statement.",
            79: "Notice of appeal -> D.C. Cir. No. 26-5322.",
            82: "Scheduling order (the Oct 16 / 23 / 27 briefing dates).",
            84: "Beatty emergency motion (staffer barred at 10:12 a.m.).",
            85: "Notice of supplemental authority (Trump 'ripped down' quote; Air Force One placard photo).",
            86: "DOJ response ('seven days, unless extended').",
            87: "Beatty reply (pretext).",
            88: "Motion to dissolve the PI (Rule 60(b)(5)) + 50-page memo.",
            89: "Renewed motion for partial summary judgment (+ Sep 18 Floca declaration, Delta Consulting report, Sep 15 board exhibits).",
            90: "Beatty reply in support of the motion to unseal the JLL Plan and Delta deck.",
            91: "DEFENDANTS' STATUS REPORT + Sep 23 Floca declaration (ECF 91-1). Closure extended to Sep 30. Says the temporary closure is a management safety measure 'separate from implementation of the Board's longer-term closure plan.'",
            92: "Notice of appearance — Mary Lyle Dohrmann for Representative Beatty. No RECAP copy in the feed, so this registry has not read it; the docket line is all that is known.",
            93: "Notice of appearance — Rosa L. Baum of the Washington Litigation Group for the plaintiff. Read: a one-page entry of appearance, filed the day the extended closure ran out. The last thing on the docket this week.",
            94: "Defendants' status report + Oct. 2 Floca declaration (94-1). The temporary closure 'remains in effect as of today' and 'continues to be reviewed on a weekly basis'; the Sept. 25 Walter P Moore report affirms the soffit-panel findings; access 'under and adjacent to the soffits' stays restricted while the emergency egress routes are reassessed; remediation of the overhead soffit panels has begun; NO reopening date.",
            95: "Plaintiff's position statement from the Oct. 1 discovery hearing. The Sept. 30 production held approximately 100 documents, 35 emails and no texts, and withheld the core financial records; Defendants refused admissions about Trump's two closure/demolition threats and asserted blanket executive privilege. Seeks a 1-2 week extension of the lift-motion schedule and bifurcation from summary judgment; gives notice of a motion to compel and a possible Rule 56(d) motion. Footnote 1: Beatty's deposition postponed by agreement.",
            96: "MOTION TO COMPEL — Beatty moves to compel documents, admissions and interrogatory answers withheld on presidential communications privilege. Five grounds: the President or a designee never invoked it; a blanket invocation is invalid; the records are held by the Kennedy Center, which is not an Article II entity; need outweighs any confidentiality interest; and Defendants waived privilege by relying on Trump-Floca communications in their own summary judgment papers. Says she has asked for nothing from the Executive Office of the President and nothing from Secretary Lutnick. Asserted privilege covers RFPs 1, 4, 6, 12, 13, 15, 38, 39, 45; ROGs 6, 13, 19; RFAs 42-44, 46, 48-51, 53-55.",
            97: "DEFENDANTS' RESPONSE TO PLAINTIFF'S DISCOVERY POSITION STATEMENT — asks the Court to close discovery 'immediately' ('Enough is enough'), or at least not to reopen it, and to grant the motion to dissolve the preliminary injunction (ECF 88) now. Says Defendants produced 'almost seven thousand pages' in a week and a half; that the FY25 ledger was produced in full but the FY26 data sits on a financial system updated at the start of FY26 and is 'neither reasonably accessible from that system nor necessarily verified'; and that executive privilege was raised after a burden objection rather than as a first move.",
            98: "PLAINTIFF'S REPLY TO DEFENDANTS' POSITION STATEMENT RESPONSE — filed the same day, reporting that Floca testified that morning that JLL sent Center management a letter on the feasibility of phased construction and that no such letter was produced. Opposes closing discovery, and reiterates the 1-2 week extension and bifurcation.",
            99: "OPINION AND ORDER on the sealing motions (ECF 65, 74). The JLL Plan is a judicial record and the Hubbard factors favour unsealing; Defendants did not meet their burden, and the sixth factor 'strongly militates toward unsealing' because Defendants introduced the plan and rely on it. Orders the Delta PowerPoint unsealed in full, and the JLL Plan unsealed subject to narrowly tailored redactions proposed by Oct. 14 with Plaintiff's response by Oct. 19. Any redactions 'must be narrowly tailored and specifically supported'.",
            100: "SEALED DOCUMENT — exhibits filed by the defendants. No RECAP copy in the feed, so this registry has not read it and cannot say what it contains.",
            101: "MOTION FOR EXTENSION OF TIME to respond to the motion to compel — two more business days, to Oct. 14. Cites Cheney on the burden the privilege itself imposes on the Executive and the depositions that occupied counsel Oct. 5-7. Quotes Plaintiff's LCvR 7(m) position: any extension 'should be accompanied by a modest 1-2-week extension of the deadline to complete discovery'.",
            102: "SUPPLEMENTAL MEMORANDUM REGARDING MOTION TO COMPEL — from Floca's Oct. 6 personal deposition and his Oct. 7 Rule 30(b)(6) deposition, where Defendants asserted privilege and instructed him not to answer on the two-year timeline, Lutnick's role, the cash position, the revenue effect of the renaming, whether Trump would withhold renovations absent his name, demolition, and the Sept. 16 closure. Reports Floca's testimony that the two-year duration was decided by Chairman Trump in his Feb. 1 Truth Social announcement and never revisited, and that JLL and Delta were both told to assume a two-year closure rather than evaluate a duration.",
            103: "ORDER on Plaintiff's discovery position statement — extends discovery two weeks, through October 23, 2026, and bifurcates briefing on the lift motion from summary judgment, with the parties to propose a revised schedule by Oct. 13. Orders FY26 financial statements sufficient to show FY26 performance, but not the full general ledger, payroll reports or all internal management reports; holds that non-privileged text messages must be produced because nothing in the scheduling order exempts a medium of communication; orders responses to the RFAs on the timing of appropriated funds; finds the withdrawn Sept. 15 renaming resolution irrelevant; and holds that documents showing the Feb. 1 announcement affected the August or September votes must be produced. Footnote 3 extends discovery to the Sept. 15 meeting as well as Aug. 13. Declines to reach executive privilege until briefing is complete. Footnote 1 calls the emergency closure a decision of the Executive Director taken over 'purported safety concerns' and says the preliminary injunction does not implicate it.",
            104: "PARTIES' PROPOSED BRIEFING SCHEDULE — two proposals, not one. Defendants would keep Oct. 16 for Beatty's opposition to the lift motion and Oct. 23 for their reply, and say 'any extension of the briefing schedule for the dissolution motion would significantly prejudice Defendants'. Plaintiff proposes Oct. 30 and Nov. 6, one week after discovery closes, and warns she would have 'no option but to move for an extension' if the Court took the government's dates. Both sides agree to defer summary judgment briefing until the lift motion is resolved; Defendants want her SJ response set two weeks after the Court rules, Plaintiff wants no SJ schedule set at all until then.",
            105: "TRANSCRIPT of the Oct. 1 scheduling conference before Judge Cooper, 48 pp., reporter Lisa A. Moreira. No RECAP copy in the feed, so this registry has not read it.",
            106: "DEFENDANTS' RESPONSE TO THE MOTION TO COMPEL — answers Beatty's five grounds in order, and the first is now moot. Attached at 106-1 is the Declaration of Joshua T. Hoyt, Deputy Assistant to the President and Deputy Counsel to the President, who at the President's direction formally invokes the presidential communications privilege over the Kennedy Center discovery. The declaration reaches 'his advisors (government and non-government)', expressly covers 'communications that do not include the President', names Secretary Howard Lutnick, and enumerates RFPs 1, 4, 6, 12, 13, 15, 23, 38, 39, 45; ROGs 5, 6, 13, 19, 21, 23; RFAs 42-44, 46, 48-51, 53-55; and passages of three deposition transcripts. The brief argues the only question left is whether the Board complied with its duties, that Plaintiff has 'far more than needed' (5 depositions, 25 interrogatories, ~6,800 pages now over 7,500, 44 RFA responses), and that the withheld material is not directly relevant. Waiver, per In re Sealed Case, reaches only 'the information specifically released'.",
            107: "SEALED DOCUMENT filed by the defendants, with a single exhibit titled 'Proposed Redactions to ECF No. 65-1' (the JLL Plan), filed on the Oct. 14 deadline ECF 99 set. No RECAP copy in the feed, so this registry has not read it and cannot say what is proposed for redaction.",
            108: "SEALED OPPOSITION filed by Plaintiff on the Oct. 19 deadline ECF 99 set for her response to the proposed JLL Plan redactions; the docket describes it as an opposition to the sealed motion for leave to file at ECF 65. No RECAP copy in the feed, so this registry has not read it and cannot say what it argues.",
            109: "NOTICE OF ERRATA — Defendants WITHDRAW the comparison of a two-year closure with a four-year phased project and the $41 million construction-cost figure resting on it from the consolidated memorandum at ECF 88-1 & 89-1, conceding both came from 'an alternate version of the report provided to the Center on August 20, 2026, which was not provided to the Board' rather than the June 8 version presented before the August 13 vote, and correct '180-page' to '160-page'. 'Defendants regret these errors.' This removes a load-bearing factual premise from the motion to dissolve the injunction.",
            110: "PLAINTIFF'S REPLY IN SUPPORT OF THE MOTION TO COMPEL — argues the Hoyt declaration does not say the President directed the privilege's INVOCATION as opposed to the declaration's submission, and that it asserts privilege 'on behalf of the Office of the President'; that the assertion remains a blanket one with no privilege-log particulars; that the privilege cannot reach Trump's acts as Chairman given the dual-hat burden of In re Sealed Case; that need overcomes it; and that Defendants waived it. Discloses that Defendants produced a JLL report dated August 20, 2026 only on October 19 — never given to the Board, confirming a phased renovation was feasible and appearing to contradict what the Board was told — and quotes a produced document: 'Q3 2028 reopening is absolute; driven by Presidential mandate.' Exhibit A accompanies it; no copy of the exhibit is in the feed.",
            111: "PLAINTIFF'S NOTICE REGARDING PRIVILEGE LOG — the log Defendants served at 5 p.m. on the last day of discovery lists nine categories of withheld Kennedy Center emails and text threads, April 23 to September 15, 2026, under presidential communications privilege. Log No. 9 is roughly 180 texts between Floca and Secretary Lutnick, May 30 to September 15; Log No. 8 is nineteen texts between Floca and Natalie Harp, eleven of them on September 15, the day of the third closure vote and the day before the building closed. Also withheld: a July 30 summary sent after an in-person meeting with the President (Log Nos. 1-2, 7), a May 29 memorandum sent the day the injunction issued (Log Nos. 5-6), and a seventeen-email thread on Honors planning (Log No. 4). Argues the log is underinclusive (it covers only communications in which Floca was involved, and nothing withheld in response to deposition questions) and that the descriptions themselves concede Trump was acting as Chairman. Asks the Court to compel production immediately.",
            112: "PLAINTIFF'S OPPOSITION TO THE MOTION TO DISSOLVE THE PRELIMINARY INJUNCTION — 51 pages. Argues the Board's process grew worse after the injunction: Delta got 60 days and was given days; the written Delta report reached trustees only on August 31, after the August 13 vote; Delta told trustees closure was needed because appropriated funds had to be spent by September 2029 when they can be spent through September 2034; Delta put phased renovation at $560 million while JLL's August 20 plan put the additional cost at $41 million and called phasing 'technically feasible', and management withheld that plan. Internal messages: 'we need to get shut' because 'we are burning money'. Asks the Court to deny the motion, to hear Floca live, and to require 30 days' notice before modifying project plans including any demolition. Footnote 20 says public reporting indicates Floca ordered the façade obscured because he feared the spectacle of removing Trump's name would 'enrage' Trump.",
            113: "SEALED MOTION FOR LEAVE TO FILE DOCUMENT UNDER SEAL filed by Plaintiff, with a single attachment described on the docket as 'Exhibit H: JLL Aug. 2026 Comprehensive P[lan]'. No copy is in the feed, so this registry has not read it; the brief at ECF 112 cites Exhibit H for the $41 million phased-renovation premium and the 'technically feasible' finding.",
            114: "PLAINTIFF'S REQUEST FOR LEAVE TO PRESENT LIVE TESTIMONY — asks to call Floca for up to 90 minutes at the hearing on the motion to dissolve, under Rule 43(c) and LCvR 65.1(d), on the Center's finances, the origin of the two-year closure, the information withheld from the Board, and management's role in shaping Delta's work. Notes Defendants produced the August 20 JLL plan and the shaping text messages only after Floca's depositions, and that the Court heard Floca live and assessed his credibility in the East Potomac case. Quotes Defendants' opposition: live testimony would be 'duplicative of extensive record evidence'.",
        },
        "calendar": [
            ("2026-09-23", "DISCHARGED — status report + sworn declaration filed as ECF 91 / 91-1. Discovery requests and deposition notices due. The 'seven-day' closure window expired and was extended."),
            ("2026-09-26", "NSO's first concert of its exile season (six DMV venues)."),
            ("2026-09-30", "PASSED and SUPERSEDED — the Sept. 23 closure extension ran out on this date, and ECF 94 (Oct. 2) records that the closure 'remains in effect as of today' and 'continues to be reviewed on a weekly basis', with no reopening date set. Discovery responses were also due on this date (ECF 82)."),
            ("2026-10-06", "DISCHARGED — Defendants' response to Plaintiff's discovery position statement filed as ECF 97, with Plaintiff's reply at ECF 98 the same day."),
            ("2026-10-08", "The Board's own extended deadline to carry out two parts of its August 13 resolution: the inscribed recognition of President Trump, and the 'President Donald J. Trump Plaza' naming of the site and grounds. The Board vowed September 8 and extended to this date (ECF 77, citing the notice at ECF 71). ECF 77 holds that at least two of the three August 13 actions violate the court's order. PASSED — nothing in the week's filings records whether the Board acted."),
            ("2026-10-09", "SUPERSEDED — discovery did not close. ECF 103 extended the period two weeks, through October 23, 2026, and bifurcated briefing on the lift motion from summary judgment."),
            ("2026-10-13", "DISCHARGED — the parties filed their competing proposals as ECF 104."),
            ("2026-10-14", "DISCHARGED, and the day the case moved. Defendants' response to the motion to compel was filed as ECF 106, with the Declaration of Joshua T. Hoyt at 106-1; the proposed narrowly tailored redactions to the JLL Plan were filed under seal as ECF 107. The Court also issued its Revised Scheduling Order this day (see below)."),
            ("2026-10-14", "REVISED SCHEDULING ORDER (minute order, modifying ECF 82) — Plaintiff's opposition to the motion to dissolve or vacate the preliminary injunction due October 30, 2026; Defendants' reply due November 6, 2026; and briefing on the summary judgment motion STAYED until the Court resolves the lift motion, with that schedule to be set later."),
            ("2026-10-16", "SUPERSEDED — by the Oct. 14 Revised Scheduling Order, which replaced this date with October 30. Was: Plaintiff opposition + cross-motion for summary judgment."),
            ("2026-10-19", "DISCHARGED — Plaintiff's sealed opposition to the sealing motion at ECF 65 was filed as ECF 108 on this deadline. No public copy. The same day, per ECF 110, Defendants produced the August 20, 2026 JLL report in discovery."),
            ("2026-10-21", "DISCHARGED — Plaintiff's reply in support of the motion to compel filed as ECF 110, with Exhibit A, the same day Defendants filed their Notice of Errata at ECF 109 withdrawing the phased-renovation comparison and the $41 million figure from ECF 88-1 & 89-1."),
            ("2026-10-23", "PASSED — discovery closed, as extended by ECF 103. Productions are not docketed, so the docket cannot show what was produced on the final day."),
            # 2026-10-27 (plaintiff's summary judgment reply) was superseded by
            # the Oct. 14 Revised Scheduling Order and is deleted rather than
            # kept as a record: this list is what raises the deadline alert, and
            # a superseded date still in it fires a banner on a day the docket
            # has nothing due. The Oct. 14 entry above records the replacement.
            ("2026-10-30", "DISCHARGED — Plaintiff's opposition to the motion to dissolve or vacate the preliminary injunction was filed as ECF 112, with the live-testimony request at ECF 114 and the sealed JLL Plan at ECF 113. The same day's minute order set a status conference on the motion to compel for November 3."),
            ("2026-11-03", "Status conference on Plaintiff's motion to compel (ECF 96), 11:00 a.m. in Courtroom 27A, in person, before Judge Cooper (Oct. 30 minute order). This is the motion to compel, not the motion to dissolve; no hearing is set on the lift motion."),
            ("2026-11-06", "Defendants' reply in support of the motion to dissolve or vacate the preliminary injunction due (Oct. 14 Revised Scheduling Order). After this the Court can rule on whether the injunction stands."),
        ],
    },
    "phang": {
        "case": "PHANG v. BLANCHE, 1:26-cv-01417",
        "docket_id": "73246595",
        "slug": "phang-v-blanche",
        "label": "Epstein files (Phang v. Blanche)",
        "known": {
            1: "Complaint — APA challenge to the Justice Department's withholding, redacting, and non-disclosure of Epstein records under the Epstein Files Transparency Act (EFTA), Pub. L. 119-38. Judge Emmet G. Sullivan.",
            9: "Plaintiff's application for a preliminary injunction, on a limited list of apparent EFTA violations.",
            15: "PRELIMINARY INJUNCTION ORDER (June 25) — largely adopting Plaintiff's proposed order, which Defendant never addressed: by July 2, produce or show cause on the listed Bates-numbered emails (sender/recipient names unredacted) and DOJ documents (co-conspirator names unredacted); produce or show cause on the underlying FBI interview notes behind four FD-302 reports; initiate foreign-language review and notice; publish or show cause on the EFTA § 2(c)(2) redaction log.",
            16: "Memorandum opinion granting the preliminary injunction. Phang v. Blanche, 2026 WL 1831251 (D.D.C. 2026).",
            19: "Defendant's response to the order to show cause — says redactions are victims' names and law-enforcement email addresses, and that it did not review foreign-language documents because first-level reviewers could not assess responsiveness.",
            20: "Plaintiff's response + motion to enforce.",
            22: "Defendant's reply.",
            23: "Order requiring Defendant to submit unredacted copies to the Court for in camera review, with documentation supporting its 'victim' representation.",
            25: "Notice of compliance — Defendant timely submitted the in camera materials (July 30).",
            27: "Plaintiff's motion to compel an Answer and to produce the Administrative Record.",
            28: "Defendant's motion to stay all filing deadlines nunc pro tunc pending the PI motion, and to set a briefing schedule.",
            29: "Order scheduling the August 13 status hearing.",
            32: "Plaintiff's proposed order (the 'interim step': a declaration explaining what is being submitted and when).",
            34: "Hearing transcript (Aug 13). Defendant: the handwritten notes were withheld because 'the determination had been made that the handwritten notes were duplicative'. On the § 2(c)(2) Federal Register log, counsel could say only that publication was 'forthcoming'.",
            35: "Notice of appeal of the PI order -> D.C. Cir. No. 26-5299 (docketed Aug 25).",
            37: "Defendant's response to the proposed order — claims it published the EFTA § 2(c)(2) written justification in the Federal Register that day (Aug 27).",
            39: "Notice of withdrawal of appearance.",
            40: "Plaintiff's response to ECF 37.",
            42: "MEMORANDUM OPINION AND ORDER — grants the motion to compel; DENIES the motion to stay deadlines. Defendant's Answer was due June 26 and he never moved for an extension; the Court allows a late Answer but refuses a late motion to dismiss, which Defendant has conceded. Answer due 9/24; certified list of the Administrative Record due 10/1; Administrative Record produced to Plaintiff by 10/15.",
            43: "MEMORANDUM OPINION AND ORDER on the parties' responses to the June 25 PI Order. Discharges the show-cause orders as to five documents (including the draft SDNY indictment, marked 'OLD Draft', and the two Privacy Act email-address redactions); finds Defendant provided NO documentation that the redactions in EFTA01187999, EFTA02504630 and EFTA01022356 are victims' names, and orders in camera documentation by 9/24 at 11:00 am; orders the underlying FBI interview notes in redacted AND unredacted form by 9/24 at 11:00 am; orders Defendant to initiate foreign-language review and give notice by 9/24; DISCHARGES the § 2(c)(2) show-cause order, leaving the adequacy of the Section 3 Report for later proceedings.",
            44: "Notice of appeal of the September 16 Order -> D.C. Cir. No. 26-5334 (docketed Sept 21).",
            45: "Transmission of the Notice of Appeal to the D.C. Circuit (no fee — filed by the government).",
            46: "DEFENDANT'S MOTION FOR A PARTIAL STAY PENDING APPEAL — asks the Court to stay the portion of the September 16 Order requiring him to initiate review and production of foreign-language EFTA materials and certify by 9/24. Filed Friday Sept 18 at 8:45 pm, requesting a ruling by Monday 5:00 pm; signed by the Associate Attorney General's office.",
            47: "Plaintiff's memorandum in opposition to the partial stay.",
            48: "Defendant's reply — asks the Court to rule by 8:00 pm Sept 21.",
            49: "ORDER DENYING the partial stay — on the merits, and independently under Local Civil Rule 7(m): Defendant did not confer with Plaintiff before filing (motion filed 8:45 pm Friday, ruling demanded over Yom Kippur) and the rule's violation 'is, on its own, reason to deny'. The Court notes Defendant never responded to the merits of the PI motion and did not address the proposed order. BUT it TEMPORARILY STAYS the foreign-language-review portion so Defendant may move for a stay in the D.C. Circuit, and orders a joint Notice within three days of the circuit's ruling.",
            50: "DEFENDANT'S ANSWER TO THE COMPLAINT — filed on the court-ordered deadline. Denies most allegations as legal conclusions; admits the EFTA is a public-disclosure law requiring the Attorney General to make certain records public; says no files were withheld or redacted on 'national defense or foreign policy' grounds; and asserts the Department 'has complied with the law and produced millions of pages of records'.",
            51: "Motion for leave to postpone the certified list of the Administrative Record (due Oct. 1) until the Rule 12(c) motion is resolved. Says Phang 'has attempted to circumvent the Freedom of Information Act' by suing under a statute that 'does not otherwise provide a private cause of action'; that 'there are no material facts in dispute'; and that the record is already public on the DOJ Epstein Library and the FBI Vault.",
            52: "Motion for judgment on the pleadings under Rule 12(c), with a memorandum in support at 52-1. Asks the court to decide the case on the pleadings alone: no discovery, no Administrative Record, no factual development.",
            54: "DEFENDANT'S NOTICE OF COMPLIANCE with ECF 43, filed on the Oct. 5 noon deadline. Hard copy was hand-delivered to Chambers at 10:43 am on Sept. 24. Says the three disputed name and email redactions rest on counsel's representation for victims, and that the handwritten notes are duplicative of the typed FD-302s already on the Epstein Library, with 2021 SDNY emails describing collection efforts.",
            55: "PLAINTIFF'S RESPONSE IN OPPOSITION to the motion to postpone the Administrative Record (ECF 51). Argues the record is necessary, that the Rule 12(c) motion poses factbound questions and relies on documents outside the Complaint while denying her the full record, that the postponement motion violates the Court's standing order (filed the day of the deadline, after close of court, with no agreed alternative dates), and that it relitigates what ECF 42 already decided. Asks the Court to order the certified list immediately and the record by October 15.",
            56: "PLAINTIFF'S UNOPPOSED MOTION TO EXTEND her deadline to respond to the Rule 12(c) motion (ECF 52), currently Oct. 15. Asks for 30 days after the record is produced if the postponement motion is denied, or 14 days after the ruling if it is granted.",
            57: "ORDER on the in camera review. DISCHARGES the show-cause orders as to the three disputed name and email redactions and as to EFTA02858495: Defendant's documentation was adequate. Orders Defendant to submit the underlying handwritten FBI interview notes behind EFTA01245620, EFTA02858481 and EFTA02858491 in REDACTED versions, 'as required by the Epstein Files Transparency Act', by 12:00 pm on October 16, 2026. A second request: the Sept. 16 order asked for redacted and unredacted versions and Defendant supplied only the unredacted ones.",
            58: "DEFENDANT'S REPLY in support of postponing the certified list of the Administrative Record. Reads the Court's standing order as covering briefs and hearing dates rather than a motion filed concurrently with a Rule 12(c) motion ('different in nature'), and on filing at 9:18 p.m. on the deadline says 'the deadline is the end of the day unless the Court orders otherwise'. Argues an Administrative Record is the wrong vehicle for testing redactions (a Vaughn index is, and in camera review can stand in for one), that four decisions in this District allowed waiver of LCvR 7(n), and that the Government 'has already disclosed all disclosable information that could conceivably go in an Administrative Record'. Reserves the jurisdictional point: it 'in no way waives the argument that the Court lacks jurisdiction to engage in such a review'.",
            59: "DEFENDANT'S NOTICE OF COMPLIANCE with ECF 57 — a binder hand-delivered to chambers at 10:55 a.m. on Oct. 16 holding the redacted handwritten notes behind EFTA01245620, EFTA02858481 and EFTA02858491. Explains why the redacted copies did not exist on Sept. 24: the notes were deemed duplicative of the typed FD-302s already on the library, and the EFTA 'does not require the production of duplicative records'. Warns the redaction work 'should not be taken as a representative sample of what could be done' at scale, and asks the Court to STAY any order requiring production so the Government may seek appellate review.",
            60: "REQUEST FOR LEAVE TO FILE — a non-party, Eugene Gibbs-Squires, seeks leave to file a motion to clarify. The clerk's reason line reads 'Filer is not a party to the case.' No RECAP copy in the feed. A filing by a non-party that touches none of the questions before the Court.",
            61: "REQUEST FOR LEAVE TO FILE — the same non-party seeks leave to file a motion for an order, with one exhibit. The clerk's reason line again reads 'Filer is not a party to the case.' No RECAP copy in the feed.",
        },
        "calendar": [
            ("2026-09-24", "Answer to the Complaint due (ECF 42) — FILED as ECF 50. Also due at 11:00 am: in camera documentation that the EFTA01187999 / EFTA02504630 / EFTA01022356 redactions are victims' names, and the underlying FBI interview notes (redacted and unredacted) for four FD-302 reports (ECF 43). The notice that foreign-language review is underway is TEMPORARILY STAYED (ECF 49)."),
            ("2026-10-01", "Defendant's certified list of the contents of the Administrative Record due (ECF 42, LCivR 7(n)(1)). NOT FILED — Defendant moved to postpone it (ECF 51)."),
            ("2026-10-05", "DISCHARGED — Defendant's Notice of Compliance with the Court's Memorandum Opinion and Order, ECF 43, filed as ECF 54 at the 12:00 pm deadline (Oct. 2 minute order)."),
            ("2026-10-08", "DISCHARGED — Plaintiff's response to the motion to postpone the Administrative Record (ECF 51) filed as ECF 55, with her unopposed extension motion at ECF 56."),
            ("2026-10-13", "DISCHARGED — Defendant's reply in support of ECF 51 filed as ECF 58."),
            ("2026-10-15", "PASSED with the record unproduced — no entry records production of the Administrative Record, and the motion that would excuse it (ECF 51) is still undecided. Also the default date for Plaintiff's response to the Rule 12(c) motion under LCvR 7(b), which ECF 56 asks the Court to move; no ruling appears on that either."),
            ("2026-10-16", "DISCHARGED — Defendant's Notice of Compliance filed as ECF 59; the redacted notes were hand-delivered to chambers at 10:55 a.m., ahead of the noon deadline."),
        ],
    },
    "msw": {
        # Philip asked on 2026-10-24 to follow "Alison Gill's suite against the
        # FBI". The caption is her company against the Department of Justice;
        # the FBI is the component the request and the search belong to. Read
        # against the RECAP copies at ECF 15, 18, 19 and 21, not against press
        # coverage, which describes a different procedural posture.
        #
        # Two dates in this case cannot be read off the feed. CourtListener
        # truncates a docket entry's short description at 500 characters, and
        # the August 24 and September 4 scheduling orders were both served as
        # minute entries whose text is cut off mid-order. The dates below are
        # the ones ECF 19 quotes from the August 24 order, with the one-week
        # extension ECF 19 asked for noted where it applies. Do not present an
        # inferred date as an order of the court.
        "case": "MSW MEDIA, INC. v. DEPARTMENT OF JUSTICE, 1:25-cv-02518",
        "docket_id": "70999320",
        "slug": "msw-media-inc-v-department-of-justice",
        "label": "Epstein files (MSW Media v. DOJ)",
        "known": {
            1: "Complaint (Aug 2, 2025) — FOIA suit on two requests: a July 17, 2025 request to DOJ's Office of Information Policy for all grand jury testimony in the Epstein and Maxwell criminal cases, and a July 22, 2025 request to the FBI for every video created or used to train personnel how to review Epstein records, on unclassified SharePoint or on classified SharePoint or BuTube (ECF 19 ¶ 1).",
            7: "Amended complaint (Sept 4, 2025) — withdraws the OIP grand jury request and maintains and expands the claims against the FBI, as the Second through Fifth Causes of Action (ECF 19 ¶ 2).",
            8: "Plaintiff's unopposed motion for expedited consideration and a joint proposed briefing schedule, granted by the Sept 16, 2025 minute order, which set plaintiff's summary judgment motion for Sept 17, 2025 and extended the answer to 14 days after that motion is decided.",
            9: "Plaintiff's motion for partial summary judgment — the expedited-processing motion. Denied at ECF 15.",
            10: "Notice of appearance — Jason Altabet for the Department of Justice.",
            11: "Memorandum in opposition to ECF 9, with an exhibit, a statement of facts and a proposed order (Dec 9, 2025).",
            12: "Plaintiff's reply in support of ECF 9 (filed Dec 30, 2025, entered Dec 31).",
            13: "Notice of appearance — James D. Todd, Jr. for all defendants.",
            14: "Notice of withdrawal of appearance — Jason Altabet terminated.",
            15: "MEMORANDUM AND ORDER (Judge Howell, July 1, 2026) DENYING plaintiff's motion for partial summary judgment on expedited processing, and directing defendant to answer the amended complaint and the parties to file a joint status report. The expedited-processing ruling, not a merits ruling: whether the nine videos are properly withheld is still open.",
            16: "Unopposed motion to extend the answer and joint status report nunc pro tunc (Aug 6, 2026). The answer had been due July 15 and the status report July 29, and an Aug 4 order had directed plaintiff to show cause why the case should not be dismissed; the Aug 6 minute order vacated that show-cause order and granted this motion.",
            17: "ANSWER to the amended complaint (Aug 7, 2026), filed on the deadline the Aug 6 minute order set.",
            18: "JOINT STATUS REPORT (Aug 21, 2026) — each side's position on the scope of the request and on a briefing schedule for cross motions for summary judgment. This is the filing the Aug 24 scheduling order was issued upon.",
            19: "DEFENDANT'S CONSENT MOTION TO EXTEND BRIEFING DEADLINES by one week (Sept 3, 2026), so counsel could prepare the summary judgment motion around previously scheduled annual leave. Quotes the Aug 24 schedule: defendant's motion due Sept 25, plaintiff's combined opposition and cross-motion Oct 26, defendant's combined reply and opposition Nov 9, plaintiff's reply Nov 16. Granted by the Sept 4 minute order.",
            20: "Notice of appearance — Isaac C. Belfer for the Department of Justice.",
            21: "DEFENDANT'S MOTION FOR SUMMARY JUDGMENT (Oct 2, 2026) — with a memorandum, a statement of material facts, a proposed order, the Declaration of Shannon R. Hammer and Hammer declaration exhibits A through G, and four further exhibits. Asks the court to uphold the search and the categorical withholding of the responsive training videos.",
            22: "Notice of appearance — Steven Chasin for the Department of Justice.",
            23: "PLAINTIFF'S CONSENT MOTION FOR A FOUR-DAY EXTENSION of its opposition to the summary judgment motion, to 6 November 2026, on the ground that counsel has three deadlines and an in-person status conference the Monday the brief is due. Proposes a modified schedule: Plaintiff's opposition and cross-motion Nov 6; Defendant's reply and opposition to the cross-motion Nov 24; Plaintiff's reply Dec 10. First extension request, consented to, with a proposed order. No ruling appears in the feed.",
        },
        "calendar": [
            ("2026-06-30", "The FBI completed its search and gave a categorical denial, withholding the responsive records in full under FOIA Exemptions 5, 6, 7(C) and 7(E) (ECF 19 ¶ 3). The merits now turn on whether those exemptions hold, which is what ECF 21 argues."),
            ("2026-07-01", "DISCHARGED — ECF 15: Howell denied the partial summary judgment motion on expedited processing, and ordered the answer and a joint status report."),
            ("2026-08-21", "DISCHARGED — the parties filed their joint status report as ECF 18."),
            ("2026-09-25", "PASSED with nothing filed — defendant's summary judgment motion was due this date under the Aug 24 scheduling order. ECF 19 moved it a week, and the motion was filed Oct 2 as ECF 21."),
            ("2026-10-26", "PASSED with nothing filed — no opposition or cross motion appears in the window. ECF 23, filed October 30, now asks for a four-day extension to November 6 with a proposed schedule running to December 10, which supersedes this date whether or not the Court grants it."),
            ("2026-11-02", "SUPERSEDED — ECF 23 proposes November 6 for the plaintiff's opposition and cross motion, so this date no longer describes anything on the docket. No order on ECF 23 appears in the feed."),
            ("2026-11-09", "SUPERSEDED — ECF 23 proposes November 24 for the defendant's reply and opposition, which would replace this date. No order on ECF 23 appears in the feed."),
            ("2026-11-16", "SUPERSEDED — ECF 23 proposes December 10 for the plaintiff's reply. After that the case would be fully briefed for a ruling on the cross motions."),
        ],
    },
    "golf": {
        # Philip, 2026-10-24: "What about the golf course case?" He means the
        # East Potomac one, which is the only case here whose caption nobody
        # says out loud: the press calls it the golf course case and the
        # Lawfare liveblog filed it under that name.
        #
        # Read against the RECAP copies at ECF 8, 75, 76, 94 and 98 and the
        # minute orders, not against coverage. ECF 79 (the TRO opinion) and
        # ECF 95 (the recusal denial) have NO RECAP copy, so this registry has
        # not read either one; where the record below rests on what the court
        # said in them, it says so.
        "case": "DC PRESERVATION LEAGUE v. DEPARTMENT OF INTERIOR, 1:26-cv-00477",
        "docket_id": "72278895",
        "slug": "dc-preservation-league-v-department-of-interior",
        "label": "East Potomac golf course",
        "known": {
            1: "COMPLAINT (Feb 13, 2026) — D.C. Preservation League and two rec golfers, Dave Roberts and Alex Dickson, against Interior, Secretary Burgum, the National Park Service and Jessica Bowron (styled 'Comptroller Exercising the Delegated Authority of the Director' of NPS). Challenges the East Potomac redevelopment under NEPA, the National Historic Preservation Act and the NPS Organic Act, through the APA. Judge Ana C. Reyes.",
            8: "PLAINTIFFS' MOTION FOR A STAY UNDER 5 U.S.C. § 705 OR, IN THE ALTERNATIVE, A PRELIMINARY INJUNCTION (Feb 23, 2026) — alleges 30,000 cubic yards of fill and debris had been dumped on the course, containing solid waste and 'presumably contaminated with asbestos', some of it from the White House East Wing demolition. Seeks to halt work and to have the material removed.",
            34: "MOTION TO DISMISS for lack of jurisdiction and for failure to state a claim (Apr 10, 2026). The jurisdictional theory is the one the case turns on: no final agency action, so nothing for the court to review.",
            51: "Plaintiffs' motion for expedited discovery (May 14, 2026) — the vehicle by which the plaintiffs tried to get behind the government's assurances before relief was decided.",
            72: "MOTION FOR LEAVE TO FILE AN AMENDED COMPLAINT (Sept 18, 2026, Rule 15). Briefed at ECF 78 (defendants' opposition) and ECF 81 (plaintiffs' reply), and still undecided as of Oct 23.",
            74: "NOTICE OF ACTIVITY (Oct 9, 2026) — the Friday-evening notice that NPS would begin removing up to 529 trees the next morning, attached to the declaration of Kevin Griess, Superintendent of National Mall and Memorial Parks. The three days' notice the Court had been promised, compressed into twelve hours before a holiday weekend.",
            75: "DEFENDANTS' MOTION FOR SUMMARY JUDGMENT and response in opposition to plaintiffs' Rule 15 motion (Oct 9, 2026). Its proposed order (75-2) shows the shape of the case: counts 1-6 challenge the course rehabilitation, counts 7-11 challenge the decision to temporarily stockpile soil at the park, and it asks for judgment on standing, final agency action, ripeness or the merits.",
            76: "PLAINTIFFS' EMERGENCY MOTION FOR A TEMPORARY RESTRAINING ORDER or, alternatively, a 14-day stay under 5 U.S.C. § 705 (Oct 11, 2026) — filed after 529 trees came down in one day. Argues NEPA segmentation: the government breaking one project into pieces and calling each piece independent, citing Delaware Riverkeeper Network v. FERC, 753 F.3d 1304 (D.C. Cir. 2014). Also asks for three business days' written notice before any irreparable modification to the park.",
            78: "Defendants' memorandum in opposition to the Rule 15 motion, filed Oct 9, 2026.",
            79: "MEMORANDUM OPINION (Oct 13, 2026) granting the emergency TRO. No RECAP copy in the feed, so this registry has not read it; the docket says only that it granted ECF 76. The TRO barred further tree removal and required notice, and it ran to Oct 26 — that end date comes from the October reporting, not from a document this registry has read.",
            80: "MOTION FOR PRELIMINARY INJUNCTION (Oct 14, 2026), which is the motion that survived the TRO. Briefed at ECF 84 (opposition, Oct 16) and ECF 88 (reply, Oct 17); heard and TAKEN UNDER ADVISEMENT at the Oct 19 evidentiary hearing.",
            81: "Plaintiffs' reply in support of the Rule 15 motion, filed Oct 14, 2026.",
            83: "MOTION for leave to file an amicus brief by Hains Point Runners and Cherry Blossom, Inc. (Oct 15, 2026), granted at ECF 97.",
            84: "Defendants' memorandum in opposition to the preliminary injunction motion (Oct 16, 2026).",
            86: "DEFENDANTS' MOTION TO DISQUALIFY JUDGE AND RELEASE AUDIO (Oct 16, 2026) — the Associate Attorney General's office, having added four lawyers in two days, asked Reyes to recuse on grounds of bias. Denied at ECF 95.",
            88: "Plaintiffs' reply in support of the preliminary injunction motion (Oct 17, 2026).",
            90: "Plaintiffs' response to the motion to disqualify (Oct 18, 2026).",
            91: "NOTICE OF FACTUAL DEVELOPMENT REGARDING RELEASE OF GOLF COURSE DESIGN (Oct 18, 2026) — the President's two Truth Social posts announcing a Tom Fazio championship design and a Nov 15 closure for about 15 months. Filed by the plaintiffs and taken judicial notice of by the Court the same day.",
            94: "DEFENDANTS' RESPONSE TO THE COURT'S ORDER ON FINAL AGENCY ACTION (Oct 18, 2026), signed by Associate Attorney General Woodward. Maintains there is no final agency action: the plan is not final, and redesigning a golf course is not 'rule, order, license, sanction, [or] relief' under 5 U.S.C. § 551(13). Says a decision to redesign the art exhibits in a Smithsonian museum would not be agency action either, and that the Court's order mischaracterized the government's position.",
            95: "MEMORANDUM OPINION AND ORDER (Oct 18, 2026) DENYING the motion to disqualify. No RECAP copy in the feed, so this registry has not read it; the docket records that the main document was replaced on Oct 19.",
            96: "NOTICE OF FACTUAL DEVELOPMENT REGARDING ANOTHER SOCIAL MEDIA POST BY THE PRESIDENT (Oct 19, 2026) — filed the morning of the hearing, after the President posted that work would begin 'IMMEDIATELY'.",
            97: "AMICUS BRIEF of Hains Point Runners and Cherry Blossom, Inc. (entered Oct 15, 2026).",
            98: "AMENDED AND SUPPLEMENTAL COMPLAINT (filed Oct 15, entered Oct 21, 2026) — eleven counts, the first six on the rehabilitation and counts 7-11 on the soil stockpiling. Filed without leave having been granted and while ECF 72 was still pending, so the docket holds both the motion and the pleading.",
            99: "PLAINTIFFS' MOTION TO EXTEND THE TRO AND RESUME THE TESTIMONY OF GREGORY WISCHER, or alternatively to order production of text messages (Oct 22, 2026). DENIED the same day by minute order, without prejudice to renewing the testimony request before a permanent injunction hearing — but the Court ordered the Government to ensure Wischer preserved his personal phone and expanded the preservation order to any material on the East Potomac course and this litigation. That preservation order is the part that outlived the motion.",
            100: "MOTION for leave to file an amicus brief by the Washington Area Bicyclist Association (Oct 23, 2026). The most recent entry.",
            101: "ORDER GRANTING the preliminary injunction (Oct 26, 2026) — bars cutting, felling, removing, girdling, topping or substantially pruning any tree in East Potomac Park absent Court order, with an imminent-safety exception requiring notice within 24 hours and a sworn declaration from a senior NPS employee; requires ten business days' written notice before any course closure or irreversible modification, listing seven particulars including who authorized the action and whether it relates to the Washington National Plan or a Fazio design; orders DOI to notify its employees by Oct 28 and Fazio Designs, Tom Fazio and Gavin Fazio by Oct 30; orders a show-cause response on preservation by Oct 28 at 10:00 a.m.; and sets a $1.00 bond by Nov 2.",
            103: "MEMORANDUM OPINION (Oct 26, 2026), 70 pages, accompanying the injunction. Finds as fact that 'the Washington National Plan exists' — a plan to replace the course with a Fazio-designed championship course — resting on the President's repeated statements, the Secretary's silence, the soil dumping, the lease termination, the June tour and the tree removal. Finds the Tree Management Plan was 'part of the Washington National Plan' and that the CLR-compliance justification is 'pretextual'. Finds the individual plaintiffs have standing, DCPL lacks organizational standing but has associational standing through a member. Finds plaintiffs likely to succeed on the NEPA segmentation claim, rejecting the government's reliance on Seven County. Assesses Griess and Lands credible, Wischer not credible, and calls part of Bowron's declaration misleading. Notes the government's statement that it intends to remove 300 more trees if the TMP proceeds as planned. Opens by observing that DOJ urged the Court not to believe the sitting President.",
            108: "DEFENDANTS' POSITION STATEMENT ON PLAINTIFF'S MOTION FOR EXTENSION — does not oppose ECF 104's request to extend the time to oppose the summary judgment motion (Dkt. 75), pursuant to the Court's Oct 28 minute order requiring a position by 5:00 p.m.",
            111: "DEFENDANTS' NOTICE under the preliminary injunction — discloses that on Friday, October 30, NPS will submit to the NCPC a Tom Fazio rendering for a 'World Class, championship-level golf course' capable of hosting the U.S. Open, the PGA Championship, the Ryder Cup and the Presidents Cup, for consideration at the NCPC's December 3, 2026 meeting; that NPS will close East Potomac Park south of Buckeye Drive, including the Golf Course, on November 15, 2026 'consistent with the President's directive'; and that NPS entered a new lease with National Links Trust on October 28 ending its operation of East Potomac by November 15. Gives the sea wall's disrepair as an independent reason for the closure. The first document in which the government states a plan and a closure date.",
            112: "DEFENDANTS' MOTION TO STAY THE PRELIMINARY INJUNCTION PENDING APPEAL — asks the Court to stay its order by November 4, 2026. Argues plaintiffs lack standing (invoking the Supreme Court's NTHP decision on aesthetic and historic interests), that redesigning a golf course is not agency action and no final plan exists, and that the NEPA segmentation holding misreads Seven County. Says the injunction is overbroad under Monsanto because it reaches all of East Potomac Park and every tree, substitutes the Court for NPS as manager, and imposes notice requirements contrary to Vermont Yankee.",
            113: "PLAINTIFFS' NOTICE OF FACTUAL DEVELOPMENT — quotes the President's 6:08 a.m. post of October 19, 2026, announcing that work 'is scheduled to begin IMMEDIATELY!', with the post as Exhibit A. The header reads Filed 10/29/26 and the signature block reads October 19, which is the date of the post rather than of the filing. SUPERSEDED the same day by ECF 114.",
            114: "AMENDED NOTICE OF FACTUAL DEVELOPMENT — 'This Amended Notice supersedes the Notice filed earlier today as ECF 113.' Reports the President's post of 10:43 p.m. Eastern on October 28, 2026, calling the course 'highly dangerous, dilapidated, and absolutely disgusting', describing the sea wall and driving range, and saying 'We will hold the judge, Ana C. Reyes, fully responsible for anybody who is hurt, or killed' on it. Attaches the posts as Exhibit A and the October 26 post as Exhibit B. This is the filing that carries the week's newest statement; ECF 113 does not.",
            116: "PLAINTIFFS' MOTION TO COMPEL PRODUCTION OF THE OCTOBER 30 NCPC FILINGS — says Defendants declined to provide the submission Plaintiffs must respond to by November 5 under the Court's minute order, that counsel represented the material is usually public within 10 to 14 days and might be available November 3, and that counsel had no authority either to produce it sooner or to join a call with the Court. Asks for an order compelling production, or an explanation, by 10:00 a.m. October 31.",
        },
        "calendar": [
            ("2026-10-26", "DISCHARGED — the temporary restraining order ran out and the Court granted the preliminary injunction the same day, as ECF 101, with the memorandum opinion at ECF 103 (see the known map)."),
            ("2026-11-02", "Four things due under the Oct 26 order and the Oct 30 minute order: Plaintiffs' $1.00 bond (ECF 101); the parties' proposed preservation order (Oct 30 minute order); the Government's list of everyone who worked on the NCPC submission and its brief on whether deliberative process privilege protects the date tree removal or a links-style design entered that submission (which it may file under seal); and its disclosure of whether any contract exists with Fazio Design, Tom Fazio or Gavin Fazio."),
            ("2026-11-03", "The parties must file a joint proposal revising the Court's notice requirement by 10:00 a.m., or, failing agreement, the Government files its own at 10:00 a.m. and Plaintiffs file theirs November 4. Also due: Plaintiffs' response on the deliberative-process question."),
            ("2026-11-04", "Defendants ask the Court to rule on their motion to stay the preliminary injunction pending appeal by this date (ECF 112). A request, not an order."),
            ("2026-11-05", "Plaintiffs must file any motion in connection with the NCPC submission (Oct 30 minute order), which is also the date ECF 116 says they must respond to it. The Government's reply is due November 6."),
            ("2026-11-15", "The date the President's Oct 18 Truth Social post gives for closing the course to play, for a renovation it says will last about 15 months. Recorded in the docket at ECF 91 and 96 and judicially noticed by the Court; it is a statement by the defendant's principal, not an order, and the government told the Court there was no plan to close the course. ECF 111, filed October 28, confirms the closure and adds that NPS closes the park south of Buckeye Drive that day."),
            ("2026-12-03", "The National Capital Planning Commission's meeting at which the Fazio rendering submitted October 30 will be considered (ECF 111)."),
        ],
    },
    "cadc": {
        "case": "PHANG v. BLANCHE, D.C. Cir. No. 26-5299 (consolidated with 26-5334)",
        "docket_id": "74696600",
        "slug": "katie-phang-v-todd-blanche",
        "label": "Epstein files appeal (D.C. Circuit)",
        # The circuit does not use ECF numbers on its feed. Its entries carry
        # a CourtListener id instead, which is opaque and NOT an ECF number, so
        # labelling them "ECF 1208891769" would invent a docket number that
        # cannot be looked up. Say what the number actually is.
        "number_label": "Entry",
        "known": {
            1208881795: "NOTICE OF APPEAL (protective) -> appeal docketed as No. 26-5299.",
            1208881798: "CLERK'S ORDER [2189799] — initial submissions due 9/24/2026 (certificate as to parties, docketing statement, entry of appearance, procedural motions, appendix-deferral statement, statement of issues, transcript report, underlying decision); DISPOSITIVE motions due 10/9/2026; transcript status report every 30 days; and BRIEFING DEFERRED pending further order of the court.",
            1208890202: "CLERK'S ORDER [2194153] — 26-5334 CONSOLIDATED with 26-5299; the Aug 25 deadlines now govern both. This is why watching 26-5299 sees both appeals.",
            1208890756: "Entry of appearance — Michael Weisbuch for Appellant Blanche.",
            1208890787: "Entry of appearance — Samuel T. Ward-Packard for Appellee Phang.",
            1208890917: "MOTION [2194494] — Appellant's motion to STAY the underlying order pending appeal, and to expedite. The motion this watch exists to follow.",
            1208891196: "PER CURIAM ORDER [2194635] — Srinivasan (C.J.), Pillard and Pan. Appellee's response to the stay motion due Fri 9/25/2026 at 11:59 p.m.; any reply due Tue 9/29/2026 at 4:00 p.m. The ruling itself will be a new entry on this docket.",
            1208891675: "Docketing statement (Appellant).",
            1208891687: "Certificate as to parties, rulings and related cases (Appellant).",
            1208891716: "Transcript status report — all transcripts needed for the appeal complete; next report due 30 days out.",
            1208891719: "Statement of issues (Appellant).",
            1208891733: "Underlying decision from which the appeal arises (Appellant).",
            1208891742: "Statement of intent re appendix deferral — deferred.",
            1208891760: "Entry of appearance — Brendan Ballou for Appellee Phang.",
            1208891769: "Certificate as to parties, rulings and related cases (Appellee Phang).",
            1208892248: "PLAINTIFF-APPELLEE'S COMBINED MOTION TO DISMISS APPEAL NO. 26-5334 AND OPPOSITION TO THE STAY MOTION (Doc #2195149, 98 pp). Moves to dismiss the enforcement-order appeal as not appealable under § 1292(a)(1): the September 16 order did not 'actually change[] the legal relationship of the parties' and he was 'already bound' by the June 25 order, whose foreign-language direction is 'identical to the PI order's, save for the change in dates'. In the alternative the appeal is an attempt to 'embellish the PI record' with forfeited arguments. Opposes the stay on three grounds: the merits were conceded below, no record evidence of irreparable harm, and his conduct has been inequitable — a 'nine-month reprieve' from the statute and 'a three-month stay-by-defiance' of the order.",
            1208892754: "APPELLANT'S REPLY IN SUPPORT OF THE STAY MOTION AND RESPONSE TO THE MOTION TO DISMISS (Doc #2195401, 28 pp). Reframes the appeal as a question about whether Congress meant EFTA disputes to run through congressional oversight and the political process 'or through piecemeal litigation and judicial supervision', not about what the EFTA requires. Merits: the EFTA/FOIA scheme 'precludes judicial review' under 5 U.S.C. § 701(a)(1); cites proposed 'EFTA II' (which would add a private right of action) as evidence Congress did not intend private enforcement. Irreparable harm: 'Documents cannot be unreviewed or unproduced.' On the motion to dismiss: 'even if granted, it should not meaningfully impact the parties or the issues presented.' Asks to stay the June 25 and September 16 orders.",
            1208902811: "PER CURIAM ORDER [2200619] (Oct 28, 2026) — DENIES the motion for a stay pending appeal and REFERS Phang's motion to dismiss to the merits panel, directing the parties to address in their briefs the issues the motion raises rather than incorporate them by reference. On the stay: 'The government has not satisfied the stringent requirements for a stay pending appeal', citing Nken and the Circuit's handbook. 'In particular, the government has failed to show that it is irreparably harmed by merely initiating review of foreign-language documents under the Epstein Files Transparency Act', and production 'does not appear to be imminent'. Where the government does not dispute its obligation it would 'only produce documents that' it concludes 'must be disclosed by law', and disputes over redactions 'will need to be resolved through further litigation', which is not present harm. Before Chief Judge Srinivasan and Judges Pillard and Pan.",
        },
        "calendar": [
            ("2026-09-25", "Appellee Phang's response to the motion for stay pending appeal due at 11:59 p.m. (per curiam order 9/23). A STAY GRANTED would pause the district court's foreign-language obligation; a denial leaves it live."),
            ("2026-09-29", "Any reply in support of the stay motion due at 4:00 p.m."),
            ("2026-10-09", "PASSED with nothing filed — no dispositive motion appears in the window (clerk order 8/25). Briefing is otherwise DEFERRED pending further order. The stay motion has been fully briefed since Sept. 29 and remains undecided."),
            ("2026-10-28", "DISCHARGED — the stay motion was DENIED by per curiam order (entry 1208902811) after 29 days, and Phang's motion to dismiss was referred to the merits panel. Briefing on the merits is what comes next; the docket sets no date for it."),
        ],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def feed_url(case: dict) -> str:
    return f"https://www.courtlistener.com/docket/{case['docket_id']}/feed/"


def docket_url(case: dict) -> str:
    return f"https://www.courtlistener.com/docket/{case['docket_id']}/{case['slug']}/"


def fetch_feed(url: str) -> str:
    # --compressed: see scripts/check-quotes.py. A gzip-forcing host would make
    # this read mojibake, the "<entry" test below would fail, and a live docket
    # would be reported as unreadable — the false-negative that makes a watch
    # job useless.
    r = subprocess.run(
        ["curl", "-sL", "--compressed", "--max-time", "30", "-A", USER_AGENT, url],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"curl exit {r.returncode}")
    body = r.stdout.decode("utf-8", "replace")
    if "<entry" not in body:
        raise RuntimeError("feed contained no <entry> elements — shape changed?")
    return body


def parse_entries(xml: str) -> "list[dict]":
    """Return one record per feed entry, newest-last.

    Two kinds of entry are recognized and both are returned:

      * ECF-numbered entries — "Entry #50 in PHANG v. BLANCHE" — carry a
        numeric ECF number in the title and are keyed by it; and
      * minute entries — "Minute entry from 2026-09-19" — which carry no ECF
        number and are keyed by the opaque `minute-entry-<id>` id.

    Dropping the second kind used to be this script's quiet defect: in *Phang*,
    Judge Sullivan sets deadlines and schedules briefing by minute order, so a
    watcher blind to them would report a quiet docket on the days the case
    actually moved. The feed interleaves the two and sorts each newest-first.
    """
    out = []
    for block in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        date_m = re.search(r"<published>([^<]+)</published>", block)
        date = (date_m.group(1) if date_m else "")[:10]
        summ_m = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
        summary = re.sub(r"\s+", " ", summ_m.group(1) if summ_m else "").strip()
        # The document URL as the feed reports it. Captured rather than built:
        # this is a link the feed itself supplied, so it is an observed URL and
        # safe to cite, which a URL assembled from an ECF number would not be.
        # Entries with no RECAP copy (sealed, or not yet scraped) have none.
        doc_m = re.search(
            r'<link[^>]*href="(https://storage\.courtlistener\.com/[^"]+)"', block
        )
        doc = doc_m.group(1) if doc_m else None

        m = re.search(r"Entry #(\d+)", block)
        if m:
            num = int(m.group(1))
            summary = re.sub(
                r"^(?:MOTION|ORDER|NOTICE|RESPONSE|REPLY|MEMORANDUM|DECLARATION)[^.]{0,80}?\bby\s+"
                r"(?:[A-Z][A-Z.\s,'-]+,\s*){4,}",
                lambda mm: mm.group(0).split(" by ")[0] + " by [45 defendants] ",
                summary,
            )
            out.append({"kind": "entry", "num": num, "mid": None,
                        "date": date, "summary": summary[:400], "doc": doc})
            continue

        mid_m = re.search(r"minute-entry-(\d+)", block)
        if mid_m:
            out.append({"kind": "minute", "num": None, "mid": int(mid_m.group(1)),
                        "date": date, "summary": summary[:400], "doc": doc})
    return out


def _max_entry(entries: "list[dict]") -> int:
    return max((e["num"] for e in entries if e["kind"] == "entry"), default=0)


def _max_minute(entries: "list[dict]") -> int:
    return max((e["mid"] for e in entries if e["kind"] == "minute"), default=0)


def load_state() -> dict:
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")


def migrate_state(state: dict) -> dict:
    """Return the state in its per-case shape, converting the legacy flat file.

    The file used to hold one case at a single watermark:
    `{"last_entry": 91, "updated": "...", "case": "BEATTY v. TRUMP, ..."}`.
    That flat watermark is Beatty's — it is the only case the watcher had — so
    it migrates there rather than being discarded. Without this, adding a second
    case would either re-alert on Beatty's whole filing history (if the key
    were simply renamed) or force a manual first run, and the point of a
    watermark is that it survives a change to the file's shape.
    """
    if "dockets" in state:
        return state
    if "last_entry" in state:
        # `last_minute: None` rather than 0: the old watcher tracked no minute
        # entries at all, so 0 is not a watermark, it is the absence of one.
        # Recording 0 would make the next run report every minute entry in the
        # feed — Beatty's window currently holds 13 — as if it were a filing
        # burst that just happened.
        return {
            "dockets": {
                "beatty": {
                    "last_entry": int(state.get("last_entry", 0)),
                    "last_minute": None,
                    "updated": state.get("updated", ""),
                    "case": CASES["beatty"]["case"],
                }
            }
        }
    return {"dockets": {}}


def due_calendar(case: dict, today: str, horizon_days: int = 3) -> "list[tuple[str, str]]":
    """Calendar items due within the horizon, or already past but unreported."""
    out = []
    t0 = datetime.strptime(today, "%Y-%m-%d")
    for date, what in case["calendar"]:
        d = datetime.strptime(date, "%Y-%m-%d")
        delta = (d - t0).days
        if 0 <= delta <= horizon_days:
            tag = "TODAY" if delta == 0 else f"in {delta}d"
            out.append((f"{date} ({tag})", what))
    return out


def new_entries(entries: "list[dict]", last_entry: int, last_minute) -> "list[dict]":
    """Entries past either watermark — ECF-numbered by number, minute by id.

    A `last_minute` of None means the case has never tracked minute entries.
    The first time it does, those already in the feed are recorded silently
    instead of reported: they are history the watcher was not asked to follow
    yet, and reporting them would be a one-time false burst. From then on the
    watermark is an int and new minute entries report normally.
    """
    track_minutes = last_minute is not None
    lm = last_minute or 0
    out = []
    for e in entries:
        if e["kind"] == "entry":
            if e["num"] > last_entry:
                out.append(e)
        elif track_minutes and e["mid"] > lm:
            out.append(e)
    out.sort(key=lambda e: (e["date"], e["num"] or 10**9, e["mid"] or 0))
    return out


def describe(e: dict, known: "dict[int, str]", number_label: str = "ECF") -> str:
    if e["kind"] == "entry":
        note = known.get(e["num"]) or e["summary"][:200]
        return f"{number_label} {e['num']} ({e['date']}): {note}"
    return f"Minute entry ({e['date']}): {e['summary'][:200] or '(no summary)'}"


def deliver(title: str, body: str, quiet: bool) -> bool:
    """Two channels, matching alert-failure.sh: durable log + notification."""
    log = Path.home() / "Library" / "Logs" / "huffmanwrites-docket.log"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"\n=== {_now()} ===\n{title}\n{body}\n")
    except Exception:
        pass
    if quiet:
        return True
    r = subprocess.run(
        ["/usr/bin/osascript",
         "-e", "on run argv",
         "-e", 'display notification (item 1 of argv) with title "Docket watch" '
               'subtitle (item 2 of argv) sound name "Glass"',
         "-e", "end run",
         body[:300], title],
        capture_output=True,
    )
    return r.returncode == 0


def watch(key: str, case: dict, state: dict, args) -> "tuple[int, bool, dict]":
    """Watch one case. Returns (exit_code, changed, updated_state)."""
    dockets = state.setdefault("dockets", {})
    cur = dockets.get(key, {})
    # First run for this case: record the watermark, do not alert on the whole
    # filing history. A missing key is the signal, so this keeps working when a
    # new case is registered without editing the state file by hand.
    first_run = "last_entry" not in cur
    last_entry = int(cur.get("last_entry", 0))
    # None (not 0) means this case has never tracked minute entries — see
    # migrate_state. 0 would be a real watermark and would flood the first run.
    last_minute = cur.get("last_minute")

    try:
        entries = parse_entries(fetch_feed(feed_url(case)))
    except Exception as exc:
        print(f"docket-watch [{key}]: ERROR: could not read feed: {exc}", file=sys.stderr)
        return 2, False, state

    if not entries:
        print(f"docket-watch [{key}]: ERROR: feed parsed to zero entries", file=sys.stderr)
        return 2, False, state

    newest = _max_entry(entries)
    newest_minute = _max_minute(entries)

    if args.status:
        wm_min = "untracked" if last_minute is None else last_minute
        print(f"docket-watch [{key}]: {case['case']}")
        print(f"  watermark : ECF {last_entry or '(unset)'} / minute {wm_min}")
        print(f"  newest    : ECF {newest or '(none)'} / minute {newest_minute or '(none)'}")
        print(f"  feed      : {feed_url(case)}")
        print(f"  docket    : {docket_url(case)}")
        return 0, False, state

    today = datetime.now().strftime("%Y-%m-%d")
    cal = due_calendar(case, today)

    if first_run:
        if not args.dry_run:
            cur["last_entry"] = newest
            cur["last_minute"] = newest_minute
            cur["updated"] = _now()
            cur["case"] = case["case"]
            dockets[key] = cur
        print(f"docket-watch [{key}]: first run — watermark set to "
              f"ECF {newest} / minute {newest_minute}; {len(cal)} calendar item(s) within 3 days")
        for when, what in cal:
            print(f"  {when}: {what}")
        return 0, False, state

    new = new_entries(entries, last_entry, last_minute)

    if not new and not cal:
        if not args.quiet:
            wm_min = "untracked" if last_minute is None else last_minute
            print(f"docket-watch [{key}]: no new filings "
                  f"(watermark ECF {last_entry} / minute {wm_min}; "
                  f"newest ECF {newest} / minute {newest_minute})")
        return 0, False, state

    lines = []
    if new:
        n_ecf = sum(1 for e in new if e["kind"] == "entry")
        n_min = len(new) - n_ecf
        bits = []
        if n_ecf:
            bits.append(f"{n_ecf} ECF filing(s)")
        if n_min:
            bits.append(f"{n_min} minute entr{'y' if n_min == 1 else 'ies'}")
        lines.append(f"{' and '.join(bits)} new in {case['case']}:")
        for e in new:
            lines.append("  " + describe(e, case["known"], case.get("number_label", "ECF")))
    if cal:
        lines.append("Calendar due:")
        for when, what in cal:
            lines.append(f"  {when}: {what}")
    body = "\n".join(lines)

    head = new[-1] if new else None
    if head:
        title = f"{case['label']}: " + (
            f"ECF {head['num']}" if head["kind"] == "entry" else "minute order"
        )
    else:
        title = f"{case['label']}: deadline approaching"

    print(f"docket-watch [{key}]: {'CHANGE' if new else 'DEADLINE'}\n{body}")

    if args.dry_run:
        print(f"\ndocket-watch [{key}]: --dry-run, watermark unchanged")
        return 0, bool(new), state

    ok = deliver(title, body, args.quiet)
    if not ok:
        print(f"docket-watch [{key}]: ERROR: delivery failed", file=sys.stderr)
        return 3, bool(new), state

    if not args.no_update:
        cur["last_entry"] = max(last_entry, newest)
        # (last_minute or 0): when None, the case is being brought under minute
        # tracking for the first time, so the newest minute in the feed becomes
        # the watermark and the history behind it is never reported.
        cur["last_minute"] = max(last_minute or 0, newest_minute)
        cur["updated"] = _now()
        cur["case"] = case["case"]
        dockets[key] = cur

    return 0, bool(new), state


def report_window(key: str, case: dict, args, feed_xml: "str | None" = None) -> "dict":
    """Return everything filed in a date window, for the weekly report.

    Read-only: this mode never touches state. It answers a different question
    from the watch loop — not "what is new since I last looked" (a watermark)
    but "what is in the last N days" (a window). The distinction matters because
    a watermark is a single point and cannot be re-derived after the fact, while
    a window can be recomputed from the feed at any time. The weekly report must
    survive a missed run, so it is built on the recomputable one.

    `feed_xml` is the test seam: pass a feed to exercise the window logic
    without a network call.

    `truncated` is the honest-reporting guard: the feed serves a fixed number of
    entries (about 30), so a case that files heavily can fill the window with
    less than N days of history. When the oldest entry in the feed is NEWER than
    the window start, the feed cannot prove the window is complete, and the
    report says so rather than presenting a partial week as a full one.
    """
    entries = parse_entries(feed_xml if feed_xml is not None else fetch_feed(feed_url(case)))
    today = args.today or datetime.now().strftime("%Y-%m-%d")

    if args.since:
        start = args.since
    else:
        start = (
            datetime.strptime(today, "%Y-%m-%d") - timedelta(days=args.days - 1)
        ).strftime("%Y-%m-%d")

    in_window = [e for e in entries if start <= e["date"] <= today]
    # Chronological, oldest first: a report is read forward, and the feed's own
    # newest-first order would bury the first filing of the week at the bottom.
    in_window.sort(key=lambda e: (e["date"], e["num"] or 0, e["mid"] or 0))
    oldest = min((e["date"] for e in entries), default=None)
    truncated = bool(oldest and oldest > start)

    # Calendar items split by direction: what the window covered, and what the
    # week ahead holds. A weekly report has to do both — the past week is the
    # news, the next week is why the reader cares.
    upcoming_to = (
        datetime.strptime(today, "%Y-%m-%d") + timedelta(days=args.ahead)
    ).strftime("%Y-%m-%d")
    covered = [(d, w) for d, w in case["calendar"] if start <= d <= today]
    ahead = [(d, w) for d, w in case["calendar"] if today < d <= upcoming_to]

    return {
        "key": key,
        "case": case["case"],
        "label": case["label"],
        "docket": docket_url(case),
        "feed": feed_url(case),
        "window": [start, today],
        "feed_oldest": oldest,
        "truncated": truncated,
        "entries": [
            {"ecf": e["num"], "minute_id": e["mid"], "date": e["date"],
             "kind": e["kind"],
             "number": None if e["num"] is None else f"{case.get('number_label', 'ECF')} {e['num']}",
             "doc": e.get("doc"),
             "note": describe(e, case["known"], case.get("number_label", "ECF"))}
            for e in in_window
        ],
        "calendar_covered": [{"date": d, "what": w} for d, w in covered],
        "calendar_ahead": [{"date": d, "what": w} for d, w in ahead],
    }


def render_report(reports: "list[dict]", days: int) -> str:
    """Render the window reports as markdown, for the weekly-report agent."""
    out = []
    for r in reports:
        start, end = r["window"]
        out.append(f"## {r['label']}")
        out.append("")
        out.append(f"*{r['case']}* — {r['docket']}")
        out.append("")
        n = len(r["entries"])
        if r["truncated"]:
            out.append(
                f"**Coverage warning:** the feed's oldest entry is "
                f"{r['feed_oldest']}, NEWER than this window's start "
                f"({start}). The feed serves a fixed number of entries, so it "
                f"cannot prove the window is complete. Say so in the report "
                f"rather than presenting a partial week as a full one."
            )
            out.append("")
        out.append(f"**Filed in the window ({start} to {end}): {n}**")
        out.append("")
        if n:
            for e in r["entries"]:
                doc = f" ([PDF]({e['doc']}))" if e.get("doc") else ""
                out.append(f"- {e['date']} — {e['note']}{doc}")
        else:
            out.append("- Nothing filed in this window. That is a finding, not a gap: say so plainly.")
        out.append("")
        if r["calendar_covered"]:
            out.append("**Calendar dates inside the window:**")
            out.append("")
            for c in r["calendar_covered"]:
                out.append(f"- {c['date']}: {c['what']}")
            out.append("")
        if r["calendar_ahead"]:
            out.append("**Calendar ahead:**")
            out.append("")
            for c in r["calendar_ahead"]:
                out.append(f"- {c['date']}: {c['what']}")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Watch the site's federal dockets.")
    ap.add_argument("--case", action="append", choices=sorted(CASES),
                    help="restrict to one case (repeatable; default: all)")
    ap.add_argument("--dry-run", action="store_true", help="report but change nothing")
    ap.add_argument("--no-update", action="store_true", help="report, keep watermarks")
    ap.add_argument("--quiet", action="store_true", help="only report on change")
    ap.add_argument("--status", action="store_true", help="show watermarks and newest entries")
    ap.add_argument("--report", action="store_true",
                    help="print a window report (markdown) instead of watching; read-only")
    ap.add_argument("--days", type=int, default=7,
                    help="window length in days for --report (default 7)")
    ap.add_argument("--since", metavar="YYYY-MM-DD",
                    help="window start for --report; overrides --days")
    ap.add_argument("--ahead", type=int, default=7,
                    help="how many days of calendar to look ahead for --report (default 7)")
    ap.add_argument("--today", metavar="YYYY-MM-DD",
                    help="treat this as today for --report (testing; default: the real date)")
    ap.add_argument("--json", action="store_true", help="machine-readable output for --report")
    args = ap.parse_args()

    keys = args.case or sorted(CASES)

    if args.report:
        reports = []
        for key in keys:
            try:
                reports.append(report_window(key, CASES[key], args))
            except Exception as exc:
                print(f"docket-watch [{key}]: ERROR: could not read feed: {exc}", file=sys.stderr)
                return 2
        if args.json:
            print(json.dumps({"days": args.days, "reports": reports}, indent=2))
        else:
            print(render_report(reports, args.days))
        return 0

    state = migrate_state(load_state())

    worst = 0
    for key in keys:
        rc, _changed, state = watch(key, CASES[key], state, args)
        worst = max(worst, rc)

    # Persist once, after every case has been checked: a single run that reads
    # both dockets should leave one consistent state file, not two writes racing
    # the next scheduled run.
    if not args.dry_run and not args.status:
        save_state(state)

    return worst


if __name__ == "__main__":
    sys.exit(main())
