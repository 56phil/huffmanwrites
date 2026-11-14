# Source notes — the nationwide ground stop of 13NOV26

**Status:** collection complete for the first pass, 13–14NOV26. Not a draft. Nothing here is prose for publication.
**Purpose:** every load-bearing claim in the eventual piece resolves to a page that was fetched, on a date recorded here.
**Piece window:** Thanksgiving (26NOV26) to Christmas (25DEC26).

## How to read this file

| Label | Meaning |
|---|---|
| **FETCHED** | This collection read the page. Quotations are character-for-character, with whitespace normalised only where a source printed a line break. |
| **FETCHED-MIRROR** | The origin refused a direct fetch; the wire copy was read in full from a syndication that carries it identically. |
| **SEARCH-EXTRACTED** | Text surfaced by a search index, not read off the page. Usable for orientation, not for quotation. |
| **UNAVAILABLE** | Attempted and failed. The failure is stated. |

Three rules the piece inherits, all from `CLAUDE.md`:

- **Nothing is asserted that was not read.** A claim that cannot be verified is dropped, replaced, or stated as a gap.
- **No constructed URLs.** Every link here was retrieved at least once.
- **Contradictions are reported, not resolved.** Where two sources disagree the piece says so, and never averages.

**A correction to an earlier working assumption.** I had this file say United cancelled the rest of Friday. **That is wrong.** United *resumed* operations that night; **JetBlue** is the airline that scrapped its remaining Friday flying. Sources in §10.

---

## 1. The primary documents. Start here.

These are the only documents that state the order in its own words. Everything else is commentary on them.

### 1.1 Advisory 111 — the national ground stop

**FETCHED.** `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111`
Wayback: `http://web.archive.org/web/20261113210113/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111`

Header: `ATCSCC ADVZY 111 DCC 11/13/2026 NATIONAL GROUND STOP`

> EVENT TIME: 13/2053 - 14/0400 DUE TO EXTRAORDINARY CIRCUMSTANCES AND FOR REASONS OF SAFETY. ATTENTION ALL AIRCRAFT OPERATORS, BY ORDER OF THE FEDERAL AVIATION COMMAND CENTER ALL AIRPORTS ARE GROUND STOPPED. ALL DEPARTING TRAFFIC SHOULD REMAIN GROUND STOPPED UNTIL FURTHER NOTICE. INBOUND INTERNATIONAL FLIGHTS WILL BE MANAGED ON A CASE BY CASE BASIS.

> EFFECTIVE TIME: 132054-140430
> SIGNATURE: 26/11/13 20:54

**The most important negative finding in this file: advisory 111 has no REASON field and no REMARKS field.** The order that stopped every departure in the country carries no stated cause. Its only causal language is the boilerplate "DUE TO EXTRAORDINARY CIRCUMSTANCES AND FOR REASONS OF SAFETY."

Two internal details:
- The event window opens at `13/2053`, one minute before the signature at 20:54.
- The window is capped at `14/0400`. "UNTIL FURTHER NOTICE" is bounded by a four-hour expected-update horizon, not an open-ended order.

### 1.2 Advisory 120 — the re-issue, with the first and only REASON field

**FETCHED.** `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120`
Wayback: `http://web.archive.org/web/20261113235506/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120`

> EVENT TIME: 13/2245 - 14/0400 DESTINATION AIRPORT:ALL FACILITIES INCLUDED: ALL EXPECT UPDATE:0400Z REASON: COMMUNICATIONS FAILURE            REMARKS: THE FAA COMMAND CENTER GROUND STOP REMAINS IN EFFECT. AS ENROUTE FACILITIES RECOVER, FLIGHTS WILL BE ALLOWED TO DEPART THROUGH COORDINATION WITH THE AIR TRAFFIC CONTROL SYSTEM COMMAND CENTER.

**The FAA's own internal classification of the same advisory is different.** The OIS rendering adds a categorical column:

**FETCHED.** `https://www.fly.faa.gov/ois/oisedit/adv_oisedit_dis?day=11132026&gdp=-1&gstop=196093&number=120`

> `ALL | 0400 | MED | ALL | EQUIPMENT / OUTAGE | 120`

So the free-text reason reads **COMMUNICATIONS FAILURE** and the label reads **EQUIPMENT / OUTAGE**. Both official, not the same thing. Any sentence about what the FAA called this must pick one and say which field it came from.

### 1.3 Advisory 119 — the tiered-release plan

**FETCHED.**

> TRAFFIC WILL BE RELEASED FROM THE NATIONWIDE GROUND STOP AS CONDITIONS ALLOW. THE CURRENT STRATEGY WILL BE A TIERED APPROACH FOR RELEASING MORE TRAFFIC AS LIMITATIONS ARE REDUCED AND VOLUME CAN BE INCREASED.

Terminal line: `UNTIL 0400	-NATIONWIDE GROUND STOP`

### 1.4 Advisory 005 — the cancellation

**FETCHED.** `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5`
Wayback: `http://web.archive.org/web/20261114013716/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5`

Header: `ATCSCC ADVZY 005 DCC 11/14/2026 CNX NATIONWIDE GROUND STOP`

> EVENT TIME: 14/0116 - 14/0130 DESTINATION AIRPORT:ALL FACILITIES INCLUDED: ALL EXPECT UPDATE:0400Z REASON:            REMARKS: THE FAA COMMAND CENTER NATIONWIDE GROUND STOP HAS BEEN CANCELLED.

> EFFECTIVE TIME: 140119-140200
> SIGNATURE: 26/11/14 01:19

**The REASON field is present and blank.** The cancellation states no cause, no confirmation that the fault is cleared, and no qualifier. That blank field is a fact the piece can stand on.

### 1.5 Advisory 001 — the last plan to describe the stop as in force

**FETCHED.** `...&adv_date=11142026&advn=1`

> THE NATIONAL GROUND STOP REMAINS IN EFFECT FOR A LARGE PORTION OF THE COUNTRY, HOWEVER, SOME OF THE COASTAL FACILITIES HAVE BEEN ABLE TO RELEASE SOME INTERNATIONAL DEPARTURES.

Terminal line: `UNTIL 0400	-NATIONWIDE GROUND STOP W/SELECTIVE RELEASES`

Sent 00:37Z. **The cancellation came 42 minutes later.** The plan and the cancellation contradict each other at 42 minutes' remove.

### 1.6 Advisory 018 — the first plan with no national stop

**FETCHED.** `...&adv_date=11142026&advn=18`, sent 02:24Z.

> SEVERAL GROUND STOPS ARE IN PLACE AT AIRLINE'S REQUESTS.

Its terminal list names no national stop, only carrier-specific holds: `-SEA GROUND STOP - ASA ONLY`, `-SAN GROUND STOP - ASA ONLY`, `-EWR GROUND STOP - UAL & UAL SUBS ONLY`, `-MSP GROUND STOP - DAL & DAL SUBS ONLY`.

### 1.7 The FAA's public statement

**FETCHED.** `https://www.faa.gov/newsroom/faa-statement-nationwide-ground-stop`, dated **Friday, November 13, 2026**.

> *This information is preliminary and subject to change.*
> The FAA issued a nationwide ground stop for all U.S. airports following communication issues impacting multiple Air Route Traffic Control Centers. FAA technicians are investigating the issue. We will provide updates.

**"Multiple," not "all."** Duffy's X post the same hour says "all Air Route Traffic Control Centers." The agency's own page is the more conservative, and the two were issued within an hour of each other.

**The FAA's statement does not contain the word "telecommunications."** That word comes from the agency's X post and from the DHS Secretary.

### 1.8 Three texts, one agency, one hour

| Text | Says | Time |
|---|---|---|
| ATCSCC advisory 111 | "ALL AIRPORTS ARE GROUND STOPPED" | 20:54Z |
| FAA press statement | "a nationwide ground stop for all U.S. airports following communication issues impacting multiple Air Route Traffic Control Centers" | 13NOV26, undated on the page |
| FAA post on X | "There has been a temporary telecommunications outage — out of an abundance of caution all flights have been halted"; "Every flight has been accounted for" | `UNAVAILABLE` at source (X blocks automated access); verbatim via NBC and AP |

Only the advisory carries times. A piece that cites "the FAA said" without naming which of the three is citing a moving target.

---

## 2. Chronology

All times Z on 13–14NOV26. Eastern is Z minus five. Advisory numbers and times are from the FAA index, which was **FETCHED complete for both days**: `https://www.fly.faa.gov/adv/adv_list` with the form parameters `whichAdvisories=ATCSCC&advisoryCategory=All&date=YYYY-MM-DD&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`.

| Time | Advisory | Event | Stated reason |
|---|---|---|---|
| 19:55 | 102 | EWR CDM ground stop cancelled | — |
| 20:07 / 20:13 | 104 / 105 | Las Vegas ground delay program proposed, then issued | WEATHER / WIND |
| **20:10** | — | O'Hare ground stop event time begins (adv 107, sent 20:28) | EQUIPMENT / OUTAGE, `COMMENTS: COMMS ISSUES` |
| **20:17** | — | Midway ground stop event time begins (adv 109, sent 20:31) | EQUIPMENT / OUTAGE |
| 20:21 | 106 | O'Hare arrival delays, expect holding up to 30 min | "DUE TO EQUIPMENT ISSUES" |
| 20:30 | 108 | All airports diversion recovery activated, to 14/0500 | none |
| 20:43 | 110 | Oceanic route closure L451–L454 | THUNDERSTORMS |
| **20:54** | **111** | **National ground stop** | **none** |
| 21:02 | 112 | Operations plan repeats the stop | none |
| 21:11 | 114 | Chicago Center flight-plan drop times to 180 min | "DUE TO EQUIPMENT OUTAGE" |
| 21:13 | 115 | Los Angeles Center, same | "DUE TO EQUIPMENT ISSUES" |
| 21:20 | 116 | Nationwide airborne holding 2100–0300 | "DUE EQUIPTMENT OUTAGES" [sic] |
| 21:21 | 117 | Flight-plan drop times 240 min at all en-route centers | "DUE TO NATIONWIDE COMMS FAILURE" |
| 22:46 | 119 / 120 | Operations plan + stop re-issued to 0400Z | 120: COMMUNICATIONS FAILURE |
| 23:58 | — | Boston international departures spaced 15 MIT (per IFR Meter) | frequency |
| 00:37 | 001 | Plan: stop remains in force for "a large portion of the country" | none |
| 01:15 | — | Airspace reopened per Duffy | — |
| **01:19** | **005** | **CNX NATIONWIDE GROUND STOP** | **blank** |
| 01:20–01:23 | 006–010 | Ground delay programs for LGA, BOS, LAS, SAN, SFO cancelled, "PROGRAM GOALS MET" / "disregard EDCTs" | — |
| 01:41 | 011 | O'Hare ground stop, **United and subsidiaries only** | OTHER / OTHER, `CARRIER UAL ONLY` |
| 02:01 | 012 | Seattle ground stop, ASA only | OTHER / OTHER, `COMMENTS: AIRLINE REQUEST` |
| 02:04 | 014 | San Diego ground stop, ASA only | `AIRLINE REQUEST MAIN AND SUBS` |
| 02:09 | 016 | Newark ground stop, UAL only | `UAL AND UAL SUBS ONLY` |
| 02:19 | 017 | Minneapolis ground stop, DAL only | `CARRIER DAL ONLY` |
| 02:24 | 018 | Plan with no national stop | — |
| 02:42 | 021 | LAX, `CARRIER ASA ONLY` | OTHER / OTHER |
| 03:08 | 025 | O'Hare, UAL only, `COMMENTS: 2ND TIER RELEASED. CZY ADDED.` | OTHER / OTHER |

**The 14NOV26 sequence is the recovery, and it is worth reading closely:** after the national stop is cancelled, every remaining ground stop is requested by an airline for its own flights. `AIRLINE REQUEST` is written in the advisory. That is carriers managing their own aircraft and gates, not the FAA managing airspace. It is the clearest documentary evidence of the displacement problem in §11.

**A warning about one secondary timeline.** IFR Meter records facility stops at Boston (2024Z), Potomac (2031Z–2041Z) and Washington Center (2033Z, 2041Z) citing "frequency." **Those do not appear in the FAA's numbered index**, which runs contiguously 001–123 with no gap in that window; the surrounding advisories are unrelated. They were evidently carried as traffic-management restrictions rather than as numbered advisories. Do not attribute them to advisory text. `[INFERENCE]`

---

## 3. Duration — choose a clock and name it

The two government timestamps give **4 h 21 m** (20:54Z → 01:15Z per Duffy's "8:15 p.m."). By advisory stamps: 20:54Z → 01:19Z = **4 h 25 m**. By event windows: 20:53Z → 01:16Z = **4 h 23 m**. IFR Meter's figure is 4 h 22 m.

Press accounts: "five-hour" (AP, WIRED), "more than five hours" (NBC, whose own two stated times yield 4 h 21 m), "more than four hours" (BBC, ABC), "nearly 4½ hours" (Washington Post), "roughly four hours" (NY Post), "about five hours" (CBS).

**Any sentence stating a duration must say by which clock.** The defensible form: "four hours and 25 minutes, by the Command Center's own two signatures."

---

## 4. Scale — the figures do not converge, and the divergence is the point

FlightAware, timestamped, all US-related, **FETCHED** (WPXI carried two timestamped snapshots; NBC one; Mediaite one):

| Time (ET) | Delays | Cancellations | Source |
|---|---|---|---|
| 5:56 p.m. | 9,086 | 663 | Mediaite quoting CNN's Pete Muntean |
| 6:20 p.m. | "more than 10,000" | "more than 2,000" | ABC/GMA |
| 7:30 p.m. | 10,079 | 4,238 | NBC |
| 8:05 p.m. | 9,535 | 5,144 | WPXI |
| ~8:20 p.m. | — | "upwards of 5,300" | NBC |
| 9:00 p.m. | — | "more than 6,000" | Axios |
| 9:52 p.m. | 8,553 | 6,828 | WPXI |

**Delays fall while cancellations rise.** That is the whole analysis: the queue was converted into a schedule. Muntean said it out loud at 5:56 p.m.: "Seems that that small cancellation number will turn into a larger cancellation number as the day goes on, as airplanes and crews, pilots, flight attendants, will be left out of position. This is not going to be a short haul story."

**Do not mix trackers.** Reuters used **FlightRadar24**: "More than 6,600 flights were canceled and 8,600 delayed, with another 1,500 already canceled for Sunday." FlightAware's 8,553 at 9:52 p.m. is a coincidence of magnitude, not the same number.

**Unreconciled and therefore unusable:** CBS "more than 10,000 delays and over 4,000 cancellations"; BBC "more than 8,500 delayed and nearly 8,000 cancelled"; NBC "more than 7,000 flights were canceled"; ABC "Nearly 5,000 flights were canceled"; Gothamist "over 25,000 delays" (search-index only, off by a factor of ~2.5 from every other figure, do not use). Different clock hours and different counting rules. Name the counter and the time, or omit.

Other scale figures:
- Airborne at the order: **"over 3,500 airplanes in the air"** (Duffy, FETCHED via NBC) — against "about 3,100 airborne aircraft bound for U.S. airports" (FlightRadar24, via CBS) and "4,042 flights headed for U.S. destinations were airborne" (FlightRadar24, via NBC). Three different quantities. Pick one and label it.
- Diverted: **"At least 827 flights had been diverted. As of 7:05 p.m. EST, 670 flights were sent back to the airport from where they originally took off, while 157 were redirected to a different airport."** (AP citing Cirium, FETCHED)
- Previous day for comparison, from the same tracker: "Yesterday, there were around 6,800 U.S.-related delays and 1,024 U.S.-related cancellations … Wednesday only had 3,424 delays and 99 cancellations in the U.S." (NBC, FETCHED)

---

## 5. Cause — five accounts, none official, all quotable

There is **no official root-cause document.** As of collection the FAA has published one paragraph, marked "preliminary and subject to change."

| # | Account | Source | Wording |
|---|---|---|---|
| 1 | Overloaded legacy switches and routers returning inconsistent data | Duffy, White House briefing | See the transcript problem below |
| 2 | A network update caused a reboot and crash | CBS, "multiple sources" | "An update to the private communications network that connects America's air traffic control system caused the system to reboot, leading to a crash and a communications outage, multiple sources told CBS News earlier Friday. The system is operated by L3Harris, which did not immediately respond to CBS News' request for comment." |
| 3 | New technology added to the system overloaded antiquated systems | AP, unattributed officials | "Trump administration officials said Friday that new technology being added to the nation's air traffic control system overloaded antiquated systems and caused 'intermittent' communications and radar gaps, leading to the longest nationwide ground stop in 25 years." |
| 4 | Legacy copper network failed; new equipment did not | Duffy, same briefing, later entry | "We use 1980s little copper lines. It's an old system that went down and went down everywhere. It got overloaded." … "I think our fix gives us a pretty good indication that it was a legacy network problem that went down" … "By the way, all of the new equipment that we put in, none of that went down." |
| 5 | Not established | FAA statement; Mullin | "FAA technicians are investigating the issue." Mullin: "It appears that this was mechanically driven. However, we're still looking, so we're not going to rule that out." |

**Accounts 2 and 3/4 are in tension, and the tension is the argument.** CBS's sources say an update — new software — caused the outage. Duffy says no new equipment went down and blames legacy copper. AP's officials say new technology overloaded the old systems. A piece that picks one without saying the others exist is picking a side in an unresolved dispute.

### The transcript problem — the single most-quoted sentence does not exist in one form

Five fetched outlets render the key sentence five ways. **Any quotation must name its outlet.**

| Outlet | Text |
|---|---|
| ABC | "Our switches, our routers, actually got overloaded with data ... and started to give us inconsistency in the data from those routers. And because of that, we shut the system down." |
| CBS | "... Our routers actually got overloaded with data and … they started to give us inconsistency in the data from those routers. And because of that, we shut the system down." *(no "switches")* |
| Reuters | "Our switches, our routers actually got overloaded with data and they started to give us inconsistencies in the data from those routers and because of that we shut the system down" *(plural "inconsistencies")* |
| NBC | split: "Our switches, our routers, actually got overloaded with data." / routers "started to give us inconsistency in the data." |
| BBC | "So this is analogue telecom. Our switches, our routers actually got overloaded with data **and they went down**" |

**Recommendation:** quote Reuters or ABC, name the outlet, and note in a footnote that transcripts differ. "Because of that, we shut the system down" is stable across four of the five and is the sentence the piece should be built on — it is a decision, not a diagnosis.

### What is *not* claimed by anyone
- That DOGE caused this. No fetched source ties them. Structural link only (§12).
- That the cause is known. Duffy: "We're still working on the details of what went wrong today."
- Whether every facility recovered at 01:16Z. Advisory 005 says only that the stop is cancelled.

### The AI tool, on the record
The FAA's own statements page carries a **10NOV26** entry: "After a successful initial rollout to the National Capital Region in September, the FAA will now use SMART in the airspace of all 22 centers across the country." `FETCHED`. Three days before the outage. Duffy, asked, said they were looking into it; the vendor, Air Space Intelligence, denied involvement: "The current ground stop is not based on or a result of the SMART system" (via NBC). NATCA had said in September it was "not involved in the design, testing or implementation of the system" (via NBC). **A line of inquiry, not a finding.**

---

## 6. The OIG record

**None of these documents mentions 13NOV26.** The most recent predates it by eleven days. They are the pre-existing findings the piece can hold the agency to. Every item is the auditor's own title.

### 6.1 The one to lead with

| Field | Value |
|---|---|
| Title | "FAA Does Not Effectively Secure Its High-Impact Systems Supporting the National Airspace System" |
| Report No. | **FI2026023** — `FI`, not `AV`; it originates in Financial, IT and Procurement Audits |
| Date | **1 April 2026** |
| Status | Self-initiated. Four recommendations |

**FETCHED.** Page `https://www.oig.dot.gov/library-item/47238`; PDF `https://www.oig.dot.gov/sites/default/files/library-items/FAA%20High-Impact%20Systems%20Final%20report_Redacted_4.1.2026.pdf`

> "FAA has begun selecting and implementing required security controls for its high-impact systems supporting the NAS, but gaps remain."

> "We found 15 of the 45 high-impact systems we reviewed had security controls selected under the outdated NIST SP 800-53 Revision 4 (Rev 4) standards, rather than the current Revision 5 (Rev 5) standards."

> "According to system documentation we reviewed, FAA had not fully implemented 1,836 (11.3 percent) of the 16,245 required controls for the 45 systems."

> "FAA is not tracking and mitigating all vulnerabilities within DOT's system of record, as required. As a result, FAA is not being fully transparent with the Department in identifying its vulnerabilities."

> "Until these gaps are filled, these systems may be vulnerable to cyberattacks that could cause severe or catastrophic effects on the NAS."

**Disclosure caveat, mandatory if quoted:** "The Department has determined that this report contains sensitive security information (SSI) that is controlled under 49 C.F.R. parts 15 and 1520… Relevant portions of this public version of the report have been redacted."

Note the office that wrote it: signed by Dormayne "Dory" Dillard-Christian, Assistant Inspector General for Financial, IT, and Procurement Audits — an office whose head, per the OIG's own leadership page, is still serving under an acting Inspector General.

**Verified independently on 14NOV26** by re-reading the library page: title, date (April 1, 2026), project ID FI2026023, the 1,836-of-16,245 figure, the 15-of-45 Rev 4 finding, and the four recommendations all match. The library page's own wording of the consequence line is: "According to FAA, these gaps exist in part because of technical and other challenges with FAA's systems. Until these gaps are filled, these systems may be vulnerable to cyberattacks that could cause severe or catastrophic effects on the NAS."

> **⚠️ NAME COLLISION — do not confuse two FAA systems both called SMART.** The air-traffic-management AI tool rolled out to all 22 centers is **SMART** (Strategic Management of Airspace, Routes and Trajectories, vendor Air Space Intelligence). The system named in this OIG report is a different thing: **FAA's Security Management & Assessment Reporting Tool (SMART)**, an internal vulnerability tracker. Recommendation 3 reads: "Develop and implement a process to ensure that system vulnerabilities currently being tracked only in FAA's Security Management & Assessment Reporting Tool (SMART) system are fully tracked within Cyber Security Assessment & Management (CSAM), the Departmental system of record." A piece that says "SMART" without disambiguating will be read as an accusation about the AI tool.

### 6.2 The rest of the shelf

| Report | No. | Date | Finding |
|---|---|---|---|
| FAA's Use of Flight Delay Data and Analyses To Monitor NAS Performance | AV2026030 | 24JUN26 | "The 2018 OPSNET Shortfall Report identified a number of weaknesses in FAA's data entry processes as well as concerns with FAA's reliance on legacy systems, which do not allow for seamless data sharing." Wilbur: 2029 if fully funded, 2032 without; $22.7M in FY2026 after partial funding in FY2024–25. No new recommendations |
| Despite Implementing the National Training Initiative and Increasing Supplemental Pay, FAA Still Faces Challenges Meeting Air Traffic Controller On-the-Job Training Goals | AV2026031 | 24JUN26 | "while FAA increased the amount of supplemental pay offered to OJT instructors, which raised OJT instruction costs by 160 percent, the number of training hours conducted has increased less than 20 percent"; "From 2022 to 2024, only 2 of the 313 air traffic facilities met or exceeded their target training hours"; the agency "fell short of its target training hours by more than 1 million hours" |
| Audit Initiated of FAA Air Traffic Organization's Safety Management System and Organizational Culture | 26A3005A000 | 1JUL26 | Announced, not issued. Origin: "Recommended by NTSB AIR-26-02 and Requested by the Secretary of Transportation." The NTSB found the ATO "had gaps in its Safety Management System (SMS) and deficiencies in their organizational safety culture that contributed to the accident" — the 29JAN25 DCA midair |
| FAA's Processes and Procedures for Design Assurance Level Assignment for Ground-Based Navigation Aids Are Insufficient | AV2026039 | 29SEP26 | "the Agency will rely on aging NavAids to guide an ever-evolving airspace" |
| DOT's Fiscal Year 2027 Top Management Challenges | 26P9001P000 | 2NOV26 | "the $12.5 billion investment in the Brand New Air Traffic Control System (BNATCS)"; priorities "include updating telecommunication wires, aging radars, and displays for controllers." **Signed by Mitch Behm, Deputy Inspector General** |
| Opportunities Exist for FAA To Strengthen Its Workforce Planning and Training Processes for Maintenance Technicians | AV2023027 | 2MAY23 | Those technicians "install, maintain, repair, and certify roughly 74,000 pieces of equipment in the NAS (e.g., radar systems…)" |
| FAA's Information Technology and Telecommunications Contracting Practices Limit Best Value Outcomes | ZA2024019 | 26FEB24 | See §10 on FENS |
| Letter regarding the 2009 FTI outage | — | 17JUN10 | See §7 |

### 6.3 OIG's own words on its capacity

**FETCHED.** Agency RIF and Reorganization Plan, Phase 1, CC2025006, 13MAR25, signed by Behm:

> "we anticipate our FTEs will be reduced by at least 10 percent from our February 2025 level, at least 10 percent from the level requested in 2020 in the FY 2021 President's Budget, and at least 15 percent from the level requested in the FY 2025 President's Budget."

> "any cost and staffing reductions must be balanced against their negative impact to our mission of reducing fraud, waste, and abuse and enhancing public safety. Staffing reductions limit our ability to accomplish planned work and thus could result in us returning less of an ROI to taxpayers."

> "DOT-OIG makes up less than 1 percent of the Department's total staff."

**Important limit on that quote.** The OIG's 06FEB25 letter to Congress does **not** claim the vacancy degraded oversight; it reports that work continued, and encloses a 32-page inventory of ongoing and planned work. Do not attribute a capacity claim to it. The Semiannual Report for Oct 2025–Mar 2026 contains no self-assessment either.

---

## 7. The pattern — four failures in the same equipment family

### 7.1 11JAN23 — NOTAM

**Cause, quote the later wording.** FAA, 19JAN23 (FETCHED, `https://www.faa.gov/newsroom/faa-notam-statement`):

> "A preliminary FAA review of last week's outage of the Notice to Air Missions (NOTAM) system determined that contract personnel unintentionally deleted files while working to correct synchronization between the live primary database and a backup database. The agency has so far found no evidence of a cyber-attack or malicious intent."

An earlier 11JAN23 statement on the same page — "Our preliminary work has traced the outage to a damaged database file" — was superseded. Do not use it.

**Duration, official.** Acting Administrator Billy Nolen, Senate Commerce testimony, 15FEB23: ground stop ordered "at approximately 7:15 a.m. EST," lifted "at 9:07 a.m. EST" — **1 h 52 m**.

**Impact, the stable figures.** GAO, twice: "over 1,300 flight cancellations and almost 10,000 flight delays throughout the day. Some airlines took several days to fully recover." Reuters' "over 4,000 delayed / 600 canceled" is an early-morning snapshot; never reconcile the two, time-stamp both or use GAO.

**Only GAO records this, and it matters:** "The system again failed in February 2025 followed by an additional outage in March 2025. A backup system, which was implemented in mid-2024, was activated and mitigated these disruptions, but the outages still resulted in flight delays and cancellations."

**And this, from the FAA's own ICAO paper:** "Military, medical and law enforcement flights were exempt from the nationwide ground stop." On 13NOV26 no advisory mentions exemptions.

### 7.2 April–May 2025 — Newark / Philadelphia TRACON

**FAA's own dated statement log, FETCHED** (`https://www.faa.gov/newsroom/faa-statements-newark-liberty-international-airport`):

- 28APR25: "telecommunications and equipment issues at Philadelphia TRACON… Both have been resolved but now there are staffing issues."
- 5MAY25: "Our antiquated air traffic control system is affecting our workforce… Some controllers at the Philadelphia TRACON who work Newark arrivals and departures have taken time off to recover from the stress of multiple recent outages."
- 7MAY25: "The FAA system – called STARS - that processes radar data for Newark is based in New York. Telecommunications lines feed this data from New York to the Philadelphia TRACON."
- 9MAY25: "There was a telecommunications outage that impacted communications and radar display at Philadelphia TRACON Area C… The outage occurred around 3:55 a.m. on Friday, May 9, and lasted approximately 90 seconds."
- 19MAY25: "lost radio frequencies for approximately two seconds around 11:35 a.m."

**OIG's cause finding, audit announcement 28JUL25** (`https://www.oig.dot.gov/library-item/46879`):

> "On April 28, 2025, air traffic controllers overseeing Newark's airspace experienced an approximately 90-second blackout of radar and radio contact with air traffic **due to a burnt copper wire**. An additional 90-second outage occurred on May 9, 2025, due to failures of both primary and redundant communication infrastructure."

**GAO's independent finding, 2026:** "FAA attributed the incidents to aging infrastructure, specifically old copper wiring, and the decision to relocate Newark's airspace control to the Philadelphia facility without adequately testing the reliability of the commercial telecommunications lines used for critical data."

**The audit was never published.** Project `25A3005A000` still reads "Audit Initiated," dated 07/28/2025. Do not assert findings that do not exist.

### 7.3 21SEP26 — Philadelphia TRACON, both paths down

**Cause.** A circuit failed; the fallback fiber was cut. NBC quoting Bedford:

> "A major circuit blew at the Philadelphia facility that controls air traffic to Newark Liberty International, Teterboro and Philadelphia airports Monday" … "when it went to flip into the backup, we discovered that the backup fiber had a break" … "That fiber break is probably 13 hours to repair."

**Four parties blame four parties.** Duffy named Amtrak. NJ Transit named its own crew but questioned Verizon's markings. Verizon named NJ Transit: "Construction contractors working in the area dug up and cut our cable. Verizon's facilities were fully functional up to that point." Any single-cause sentence is a choice among accounts.

**Impact.** 619 cancellations at Newark and 197 at Philadelphia by 6 p.m. (FlightAware via NBC); about 90 diversions (BBC); "About 9,500 US flights were delayed or canceled that day" (Reuters, whole system).

### 7.4 The thread the piece can lean on hardest

**The FAA declared this fixed eleven weeks before it failed.** FAA statement, **3JUL25**, FETCHED:

> "This morning, the FAA successfully transitioned to a brand-new fiber optic communications network between New York and the Philadelphia Terminal Radar Approach Control (TRACON)… This upgrade significantly enhances resiliency with new fiber optic connections on two separate communications paths, ensuring equipment will continue to operate if one path is disrupted."

On 21SEP26 both paths were unavailable at once — one because it failed, one because a contractor cut it. **A documented promise and a documented failure of the promise, in the agency's own words, with no reporter in between.** That is the strongest single paragraph in the file.

### 7.5 6AUG26 — Minneapolis Center

FAA statement, quoted identically by two outlets:

> "The FAA briefly paused flights into and out of Minneapolis Air Route Traffic Control Center's airspace due to telecommunication issues. Services have been fully restored and flights are returning to normal. The FAA is investigating the cause."

Duration in dispute: "about an hour and a half" (airport spokesperson), "around two hours" (The Verge, Simple Flying), lifted "by 4:15 p.m." (AeroCorner citing CBS Minnesota). **No FAA root-cause document exists.** The "1,100+ flights" figure is The Verge's alone; everything else says "hundreds."

### 7.6 4AUG26 — Marine One at DCA, which is *not* a system failure

The popular version of this is wrong, and the piece should not repeat it. **NTSB preliminary report, incident OPS26LA063, FETCHED:**

> "The frequency had been working normally and there were no known outages or reports of degradation of this frequency on the day of the event, nor was there a history of problems with this frequency according to FAA."

> "the first attempt to contact DCA ATCT was not received at all, and the second attempt was broken and completely unreadable"

> FAA's coverage analysis found "there was not adequate line-of-sight" from The Ellipse, where Marine One was operating during White House construction; technicians relocated the radios to the top of the DCA tower.

> "This would meet the required minimum radar separation as set forth in FAA Order JO 7110.65BB… paragraph 7-9-4, which required 1.5 nm lateral or 500 feet vertical separation"

The Verge's rendering — "the air traffic controllers never heard the transmission and cleared a different airplane for takeoff — which came closer than the minimum safe distance allowed" — is not supported on two counts: the second attempt was heard (unreadably), and the FAA's own estimate met the standard. **Cite the NTSB, not the paraphrase.** There *was* a prior warning: DCA tower and HMX-1 met on 30JUL26 about missed 3-minute calls, and HMX-1 said comms "had been spotty."

### 7.7 The 2009 FTI outage — the closest ancestor

**FETCHED.** OIG letter, 17JUN10:

> "On November 19, 2009, 129 of the Nation's air traffic facilities experienced an outage of the Federal Aviation Administration's (FAA) telecommunications that delayed thousands of travelers and grounded hundreds of flights nationwide."

> "We found that network configuration and procedural errors by the contractor caused the FTI outage, which blocked approximately 75 percent of the FTI network traffic and delayed service restoration for 5 hours."

> "FAA's oversight of FTI and Harris was not as effective as it should have been."

**A national-scale telecom failure, in the same network, seventeen years ago, with a contractor named and an oversight failure found.** If the piece needs one sentence to establish that 13NOV26 was foreseeable, this is it.

---

## 8. The sustainment numbers — cite GAO, not OIG and not The Verge

The "unsustainable" classification comes from an **FAA operational risk assessment conducted after the 11JAN23 outage**, which the FAA has not published. GAO reviewed it and reproduced the results. **No OIG report establishes these percentages.** The Verge's aggregate is right and its attribution to the FAA is right, but the citable document is GAO's.

**GAO-24-107001, 23SEP24, FETCHED:**
> "The assessment determined that of its 138 systems, 51 (37 percent) were unsustainable and 54 (39 percent) were potentially unsustainable"
> "Of the 105 unsustainable and potentially unsustainable systems, 58 (29 unsustainable and 29 potentially unsustainable systems) have critical operational impacts on the safety and efficiency of the national airspace"
> "as of May 2024, FAA had 17 systems that were especially concerning. The investments intended to modernize these systems are not planned to be completed for at least 6 years, and in some cases, they will not be completed for 10 to 13 years. In addition, FAA does not have ongoing investments associated with four of these critical systems"
> "This table omits the official names of the 17 systems due to sensitivity concerns."

**GAO-25-108162, 4MAR25, FETCHED:**
> "Of the 105 unsustainable or potentially unsustainable systems, 73 were deployed over 20 years ago, with 40 being deployed over 30 years ago, and six of those deployed over 60 years ago."
> "74 systems (70 percent) face one or more challenges that are historically problematic of aging systems. These challenges include no longer meeting mission needs, difficulty finding spare parts for the systems, and limited technical staff with expertise in repairing the aging system."

**GAO-26-107992, 14SEP26, FETCHED (AOPA's hosted PDF — cite the report number and note the hosting):**
> "In September 2024, GAO reported that over 75 percent of FAA's 138 ATC systems were unsustainable or potentially unsustainable."
> "as of May 2026, FAA reported replacing 2,560 of 5,170 old and frail copper wires with high-speed fiber optic communications cables"
> "FAA has not developed a comprehensive and well-documented lifecycle cost estimate for BNATCS… officials were unable to provide the analysis that supported these figures."
> "FAA has 11,389 individual project schedules that are not integrated. As a result, individual projects are scheduled for installations at the same sites, generally without optimizing the schedules to reduce impacts to controller operations."
> "Phase 1 is to be fully completed by December 2028." … "FAA stated that they will need approximately $10.2 billion for this phase (not including facilities)."
> "If these risks are realized, FAA would need to continue to rely on severely outdated systems that are prone to failure leading to more flight delays and safety incidents."

**2,560 of 5,170.** Half the copper is still in the ground, by the agency's own count, six months before the outage. That number belongs in the piece.

**Bedford, to Reuters in September 2026:** "When it fails, we just don't have the redundancy that we would get if we had a modern architecture." And: the agency's "more than 300 air traffic facilities operated as technological silos, relying in some cases on decades-old computers and telecommunications systems that cannot communicate seamlessly with one another." / "Some obsolete equipment requires replacement parts obtained through online auction websites or made using 3D printing." `FETCHED-MIRROR` (Reuters via investing.com).

---

## 9. Money — four numbers, four different things

### 9.1 The statute, and the personnel question settled

**P.L. 119-21, §40003, signed 4JUL25. FETCHED** from the govinfo Public Law XML (`https://www.govinfo.gov/content/pkg/PLAW-119publ21/uslm/PLAW-119publ21.xml`).

Chapeau: the appropriation is "for the purpose of the acquisition, construction, sustainment, and improvement of **facilities and equipment** necessary to improve or maintain aviation safety." **There is no salary, personnel, or hiring authority in the section.**

Fourteen line items totalling **$12,520,000,000**, available until 30SEP29. The ones that matter here:

| ¶ | Amount | Purpose (verbatim) |
|---|---|---|
| (1) | $4,750,000,000 | "for telecommunications infrastructure modernization and systems upgrades" |
| (2) | $3,000,000,000 | "for radar systems replacement" |
| (7) | $1,900,000,000 | "for necessary actions to construct a new air route traffic control center" |
| (9) | $1,000,000,000 | "to support recapitalization and consolidation of terminal radar approach control facilities" |
| (10) | $350,000,000 | "for unstaffed infrastructure sustainment and replacement" |
| (14) | $100,000,000 | "for air traffic controller advanced training technologies" |

**¶(1) is the direct hit: $4.75 billion was appropriated for the exact category of equipment that failed on 13NOV26, in July 2025.**

¶(14) funds training *technologies*, not trainees. That distinction is the hinge of the personnel argument.

**The recruitment money was stripped.** AAAE, 3JUL25: "The bill also includes $100 million for tower simulators, but does not contain $1 billion for controller recruitment, retention, and training that the House approved." Vote: 218–214.

**And the White House said otherwise.** Its July 2025 fact sheet claims the act "Addresses the more than 3,000-controller shortage by investing in recruitment, retention, and advanced training technologies." **The statute does not appropriate a dollar for recruitment or retention.** A live, quotable contradiction between a signed public law and the sheet describing it.

### 9.2 The $30.1B request

A **letter** from OMB Director Russell Vought and Duffy, to Collins, Murray, Cole and DeLauro. Sent Thursday 12NOV26, reported Friday 13NOV26 — Bloomberg Government and Roll Call say "Thursday"; Reuters says "on Friday." Say "a letter sent Thursday and reported Friday," or attribute the date.

Reuters `FETCHED-MIRROR`:
> "The request from White House Office of Management and Budget Director Russell Vought and Transportation Secretary Sean Duffy seeks $10.1 billion for air traffic control modernization, including $7.2 billion for a common automation platform and controller workstations and $2 billion for cloud computing."

> "This investment is critical to complete the modernization of our national airspace - delivering a resilient telecommunications backbone for air traffic controllers, modern hardware and software, state-of-the-art control towers, and world-class airport infrastructure," Duffy and Vought wrote.

**"A resilient telecommunications backbone" — the request was signed the day before the backbone failed.**

Also: "Vought and Duffy in their letter said the FAA has replaced 68% of legacy copper telecommunications network with high-speed fiber infrastructure." Note GAO's May 2026 figure: 2,560 of 5,170 = 49.5%. The 68% and the 49.5% are measuring different things or one of them is wrong; report both, reconcile neither.

**Status: not law.** The Modern Skies Act (H.R. 10683, introduced 28SEP26) carries the same $10.1B structure — §4: $300M facility consolidation, $7.2B common automation platform and controller workstation, $2B cloud, $600M flow management — and **no personnel line.** Reuters: "The administration has called for the Republican-led Congress to approve funding in the final weeks of the year. Democrats are set to take control of Congress in January."

### 9.3 The $50B

**Confirmed, and confirmed as a spoken demand with nothing filed behind it.** Mediaite and ABC carry the same words, differing only in punctuation:

> "This is an emergency. I want Congress to give us emergency funding. This is bipartisan. This is American. I want $50 billion."

Roll Call: "The increased allotment, which the administration officials didn't fully flesh out"; "The latest figure is $19.1 billion higher than the figure Duffy and Office of Management and Budget Director Russ Vought called on congressional appropriators to approve in a Thursday letter." And Mullin: "We need someone to come in and build the whole system. Nickel and diming it together does not work."

**The cleanest line in the pack**, Duffy on Newsmax via Yahoo:
> "the president has asked for $30 billion. I want $50 billion."

**Say "he said it, and nothing was filed."** Not "unconfirmed" — the words are confirmed by four outlets. What is unconfirmed is whether it is a formal position.

### 9.4 Duffy on whether it recurs

From the AP live page, FETCHED:
> "Is this exact thing going to happen again?" the transportation secretary told reporters. "I don't — I don't know that this exact scenario will happen."

From CBS:
> "But you will have more of these," Duffy said. "You will have more of them unless the American people and the Congress tell us to build."

**Two answers, hours apart, from the same official. Both quotable. The second is the piece's closing problem.**

---

## 10. The 2025 record, and why it is not the cause

### 10.1 The firings

**AP, 19–20FEB25, FETCHED-MIRROR:**
> "About 400 personnel were let go starting Friday. There is still not a complete picture of who was fired, but the union representing about 130 of them said the staffers included aviation safety assistants, maintenance mechanics and nautical information specialists."

> "Meanwhile, in the firings, 18 air traffic control facilities lost maintenance mechanics, employees who work on electronic issues and other building repairs at those facilities, said David Spero, president of the Professional Aviation Specialists Association, a union representing about 130 of the roughly 400 FAA staffers who were fired."

**This corrects a widely repeated compression.** The "18 centers" figure means eighteen ATC facilities lost *maintenance mechanics*. It does not mean 400 employees at 18 centers, which is how The Verge's sentence reads if skimmed. Say what AP said, and attribute it to Spero.

**The count itself is disputed inside the administration:** Duffy "Less than 400" (17FEB25); Duffy to CBS "So 352 cuts is 0.8% of the workforce" (20FEB25); Reuters "The FAA fired 350 employees last week" (27FEB25); PASS's own list "132 of our probationary employees" (18FEB25); The Air Current "133 of its members." **Report the range.**

**And on the radar/nav-aid claim:** AP reported, on one anonymous controller's word, that the impacted workers included "personnel hired for FAA radar, landing and navigational aid maintenance." The Air Current reported the opposite from the PASS-supplied FAA list — no ATSS personnel were laid off — and ATSS is a different job class from maintenance mechanics. The two can be reconciled only if the piece says which class it means.

**The union's own sentence, The Verge 17FEB25 (FETCHED):**
> "This draconian action will increase the workload and place new responsibilities on a workforce that is already stretched thin," David Spero, National President of the Professional Aviation Specialists, AFL-CIO, said in a statement. "This decision did not consider the staffing needs of the FAA, which is already challenged by understaffing."

**The administration's response, same day:** Karoline Leavitt: "No air traffic controllers nor any professionals who perform safety critical functions were terminated."

### 10.2 The contract fight

**WaPo, 26FEB25, FETCHED via the Seattle Times reprint:**
> "The Federal Aviation Administration is close to canceling a $2.4 billion contract to overhaul a communications system that serves as the backbone of the nation's air traffic control system and awarding the work to Elon Musk's Starlink, according to two people briefed on the plans."

> "Several senior FAA officials have refused to sign paperwork authorizing the switch… so Musk's team is now seeking help from the acting administrator of the agency, Trump appointee Chris Rocheleau, and Duffy."

> "The FAA said in a statement Wednesday that 'no decisions have been made' about the Verizon project."

**⚠️ FIGURE CONFLICT, unresolved.** WaPo calls it a **$2.4 billion** contract. The OIG (ZA2024019, FETCHED) says: "FAA awarded a 15-year, $4 billion FAA Enterprise Network Services contract in March 2023 to serve as the Agency's primary means of acquiring telecom services as it phases out its legacy 21-year, $5 billion FAA Telecommunications Infrastructure contract." **Do not mix $2.4B and $4B without saying which source each comes from.** The OIG's is a government document; use it for the contract's structure and WaPo for the fight over it.

**Musk was wrong, and said so.** Reuters, 27FEB25:
> "Billionaire presidential adviser Elon Musk on Thursday falsely accused Verizon, a rival contractor of his SpaceX Starlink system, of putting U.S. air safety at risk through a communications system that is actually operated by L3Harris."

> "Musk admitted that he made a mistake… 'Correction: the ancient system that is rapidly declining in capability was made (by) L3Harris. The new system that is not yet operational is from Verizon,' Musk posted."

**This is the hinge for §12 and it needs care.** In February 2025 Musk identified L3Harris as the operator of the "ancient system that is rapidly declining in capability," and Verizon as the not-yet-operational replacement. On 13NOV26 CBS's sources named **L3Harris** as the operator of the network whose update caused the reboot. That is a coincidence of parties across eighteen months, not a causal chain, and the piece must not present it as one — but the reader will notice, and the honest move is to lay both facts down and say the link is unestablished.

**The contract was never cancelled.** Reuters, 16JUL25, quoting Bedford's letter to lawmakers:
> "The FAA is not aware of any effort by SpaceX to assume the (telecommunications) contracts. Nor has FAA considered replacing the awardees of those contracts with SpaceX." … "FAA would not use Starlink (or any satellite service) as the sole communications technology for safety-critical air traffic services."

Duffy, same story: "more than 90% of the telecom funds would be used to replace copper with fiber. 'That was the mission - not some competitive advantage to Starlink.'"

### 10.3 Project Lift

Rolling Stone, 25APR25, **FETCHED**:
> "Elon Musk's so-called Department of Government Efficiency (DOGE) has been spearheading a multi-million dollar communications project at the Federal Aviation Administration… and employees roped into it have been forced to sign non-disclosure agreements, sources with knowledge of the situation say."

> "DOGE staffers who now work at the FAA have been directing FAA funds to a new initiative called 'Project Lift,' and employees involved have been made to sign NDAs"

**The FAA's three denials, in the same piece:**
> "DOGE is not spearheading anything at the FAA, nor are there any DOGE employees at FAA… Project Lift was conceived and is managed by federal employees."
> "The federal employees running Project Lift are exploring a variety of solutions to modernize the FAA's telecommunications network. Current contractors are part of the discussion."
> "Employees routinely sign non-disclosure agreements to avoid conflicts of interest."

**Sourcing standard the piece inherits:** three anonymous sources and an agency spokesperson who confirms the project exists while denying the premise. Nothing in it names a document. No 2026 reporting on Project Lift's outcome surfaced. **Do not assert what became of it.**

### 10.4 The Verge's verdict

18AUG26, **FETCHED**:
> "But Musk ended up as more wrecking ball than problem solver. His agency did not help the FAA buy or implement any major system upgrades. He wrongly accused Verizon of running the FAA's communications system, while also failing to turn Starlink into the agency's telecom provider of choice. Its signature achievement was the termination of 400 FAA employees, including maintenance technicians at 18 different air traffic control centers."

The piece misnames the Secretary as "Ryan Duffy" in one paragraph and compresses the 18-centers figure. Quote its verdict, verify everything else.

### 10.5 The framing this supports, and the one it forbids

**Supported:** the modernization that existed to retire the failing equipment spent 2025 as a contract fight, an NDA-covered pilot, and a terminated maintenance workforce — and then the equipment failed.

**Forbidden:** that DOGE caused the outage. No fetched source establishes it. The causal claim is unresolved between five official and semi-official accounts (§5), and none of them is DOGE.

---

## 11. What the recovery looked like, in the FAA's own advisories

The most under-covered part of the story. After 01:19Z every remaining ground stop in the advisory index is **carrier-specific and requested by the carrier**: UAL at O'Hare and Newark, DAL at Minneapolis, ASA at Los Angeles, San Diego and Seattle. `AIRLINE REQUEST` is printed in the comments field.

**That is aircraft and crews out of position, in the government's own filing system.** The airlines rebuilt their own schedules by holding their own flights. Any account of the recovery that ignores this is describing an abstraction.

Airlines:
- **United resumed.** "United is resuming operations, including some Friday night flights… Safety is our highest priority as we take care of our customers and employees." (via NBC, FETCHED)
- **JetBlue cancelled.** "Due to the nationwide FAA mandated ground stop, JetBlue is canceling all remaining flights this evening with the exception of Europe-bound departures from JFK and Boston… We expect disruptions to continue into tomorrow, including additional cancellations." (via NY Post and AP, FETCHED). CNBC adds, from a memo: it also cancelled **Saturday** flights "so that crews and planes are in place to resume operations."
- Air Canada cancelled its remaining Canada–US Friday flights. Delta and United issued waivers.

The metering data — **IFR Meter's own measurements, not official FAA counts.** The count fell from 2,983 at 2040Z to a trough of about 136 between 0120Z and 0130Z, against roughly 2,900–3,250 at the same hours on 12NOV26, then climbed. Use it as an operator-side indicator, labelled.

---

## 12. The accountability record

| Fact | Detail | Source |
|---|---|---|
| IGs fired, 24JAN25 | **17**, per the court record: "Late in the day on Friday, January 24, 2025, the Trump administration fired 17 IGs *en masse*." | FETCHED — *Storch v. Hegseth*, No. 25-cv-415 (ACR), D.D.C., Memorandum Opinion at 9 (filed 24SEP25) |
| Contemporaneous range | "at least 12" (NYT headline, Reuters slug) to 18. **Safest sentence: "seventeen, according to the court record; contemporaneous accounts ranged from 'at least 12' to 18."** | — |
| The statute | 5 U.S.C. § 403(b): the president "shall communicate in writing the substantive rationale, including detailed and case-specific reasons for any such removal or transfer to both Houses of Congress (including the appropriate congressional committees), not later than 30 days before the removal or transfer" | FETCHED — CRS IF11546, updated 27JAN25, quoting the section as amended by P.L. 117-263 |
| DOT IG tenure | "Eric J. Soskin Inspector General 01/11/2021 - 01/24/2025" | FETCHED — oig.dot.gov |
| Acting | "On January 24, 2025, per the IG Act, as amended, as the first assistant to the Inspector General, Mr. Behm became the Acting Inspector General when that position became vacant." | FETCHED — oig.dot.gov |
| Vacancy today | **Department of Transportation: 655–656 days** on Oversight.gov's vacancy table, no nominee listed | FETCHED — `https://www.oversight.gov/about/inspectors-general-vacancies` — **re-read on publication day** |
| Trump's explanation | "Because it's a very common thing to do." | FETCHED — quoted by Safety+Health from the Air Force One pool |
| Soskin's own position | He declined to join the eight fired IGs' suit and filed an amicus brief **supporting the president's removal authority** | FETCHED — Fox News, 07MAR25 |
| OIG headcount | DOT OIG 405 → 326 (Dec 2024 → May 2026), −19.5% | REPORTED — FederalHiringData, an independent analysis of OPM files. **Not a government publication. Label it.** |
| System-wide | 27 of 72 IG posts vacant per CIGIE, Aug 2026 | REPORTED — same source |
| What the DOT IG covers | Recent audits critiqued FAA oversight of Boeing production, "criticized FAA actions related to air traffic control modernization," and covered airline consumer protection and safety oversight | FETCHED — Travel Weekly, 27JAN25 |

**The piece must include Soskin's amicus brief.** Omitting it makes the accountability section an argument rather than a record.

---

## 13. Leadership as of November 2026

| Post | Holder | Status |
|---|---|---|
| FAA Administrator | **Bryan Bedford** | **Confirmed**, Senate 53–43 on 9JUL25, five-year term; listed as "Administrator" on the FAA key-officials page last updated 22OCT26 — **not acting** |
| Deputy Administrator | **Liam McKenna** | **Acting** — the FAA's own "(A)" marker. Chris Rocheleau left 30JUL26; Bedford called it "a big loss" leaving "big shoes to fill" |
| ATO Chief Operating Officer | **Franklin McIntosh** | Permanent since 26JAN26; acting from 23MAY25 |
| Also vacant on the key-officials page | Assistant Administrator, Airspace Modernization Office; Chief Administrative Officer; Associate Administrator, Commercial Space Transportation | Vacant |

**McIntosh, on the funding sequence** (conference report, treat as secondary): the $12.5B "covers NextGen Phase 1, what McIntosh called foundational infrastructure: new radars, voice switches, and communications," and "93 percent of our budget years past was spent purely on sustainment, while 7 percent was only on advancing the National Airspace System."

**Controller workforce, primary.**
- FAA, 15MAY26: full staffing target **12,563** CPCs, "down from a prior target of 14,633" — a cut of **2,070**.
- "As of April 2026, approximately 11,000 CPCs are deployed across more than 300 FAA air traffic facilities, with an additional 4,000 controllers in the training pipeline."
- **NATCA was not in the room.** "NATCA was not involved in the development of the 2026-2028 Air Traffic Controller Workforce Plan," the union told FLYING (via AVweb). The prior target had been developed with NATCA.
- FY2025: 2,028 trainees hired, 1,460 losses, net +568; ended with 14,832 total; estimated FY2026 losses 1,711.
- FY2026: 2,235 trainees hired, "the most in its history" (Fortune, 9NOV26).
- GAO, January analysis via Fortune: "The U.S. has about 6% fewer air traffic controllers than it did a decade ago, even as the number of flights relying on the air traffic control system has grown 10%."

**Unresolved:** a Reuters figure of "about 3,500 fully certified controllers short" against 13,164 employed cannot be reconciled with the 12,563 target or the 14,832 total. **Do not use 3,500.** The defensible statement: about 11,000 certified against a 12,563 target as of April 2026.

---

## 14. Contradiction register

Consolidated. The piece must not silently pick.

| Quantity | Account A | Account B | Account C |
|---|---|---|---|
| Duration, 13NOV26 | 4 h 21–25 m (FAA timestamps) | "five-hour" (AP, WIRED, CBS) | "more than four hours" (BBC, ABC); "nearly 4½" (WaPo) |
| Time of the order | 20:54Z (FAA signature) | "3:44PM ET" (The Verge) | "3:54 p.m." (NBC, IFR Meter) |
| Lift time | 8:15 p.m. ET (Duffy, AP, Reuters, CBS) | "Shortly after 8:30 p.m." (NY Post) | advisory 005 event 01:16Z / effective 01:19Z |
| Airborne | "over 3,500" (Duffy) | "about 3,100 bound for U.S." (FlightRadar24) | "4,042 headed for U.S. destinations" (FlightRadar24) |
| Cancellations | 6,828 at 9:52 p.m. (FlightAware via WPXI) | "more than 7,000" (NBC) | "nearly 8,000" (BBC); "over 4,000" (CBS) |
| Tracker | FlightAware | FlightRadar24 (Reuters) | — do not mix |
| Cause | legacy copper overloaded (Duffy) | an update caused a reboot (CBS sources) | new technology overloaded antiquated systems (AP) |
| Centers affected | "multiple" (FAA statement) | "all" (Duffy's X post) | — |
| Onset | 3:36 p.m. ET (Duffy) | 20:10Z = 3:10 p.m. (adv 107 event time) | 26-minute gap, unexplained |
| IGs fired | 17 (court record) | "at least 12" (NYT, Reuters slug) | 18 (NBC, Reason) |
| FENs contract value | $2.4B (WaPo) | $4B, 15-year (OIG ZA2024019) | legacy FTI: $5B, 21-year (same) |
| Copper replaced | 68% (Vought–Duffy letter) | 2,560 of 5,170 = 49.5% as of May 2026 (GAO) | — |
| FAA staff fired, 2025 | "Less than 400" (Duffy) | 352 (Duffy to CBS) | 350 (Reuters); 132–133 PASS members |
| 6AUG26 duration | ~1.5 h (airport) | ~2 h (Verge) | — |
| 4AUG26 severity | "would meet the required minimum" (NTSB) | "closer than the minimum safe distance" (Verge) | — |

---

## 15. Source registry

### Primary
- `https://www.fly.faa.gov/adv/adv_list` — the advisory index, needs the full query string (§2). **Retains only 15 days.**
- `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=<N>` — 13NOV26 advisories
- `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=<N>` — 14NOV26 advisories
- `https://www.fly.faa.gov/ois/oisedit/adv_oisedit_dis?day=11132026&number=111` and `&number=120` — the OIS rendering with the FAA's reason column
- `https://www.faa.gov/newsroom/faa-statement-nationwide-ground-stop`
- `https://www.faa.gov/newsroom/statements/general-statements` — carries the 13NOV26 statement and the 10NOV26 SMART statement
- `https://www.faa.gov/newsroom/faa-notam-statement` — 19JAN23
- `https://www.faa.gov/testimony/statement-billy-nolen-acting-administrator-federal-aviation-administration-hearing-united` — 15FEB23
- `https://www.faa.gov/newsroom/faa-statements-newark-liberty-international-airport` — the 2025 dated log
- `https://www.faa.gov/newsroom/faa-releases-bold-new-air-traffic-controller-hiring-plan` — 15MAY26
- `https://www.faa.gov/about/key_officials` — leadership, 22OCT26
- `https://www.govinfo.gov/content/pkg/PLAW-119publ21/uslm/PLAW-119publ21.xml` — P.L. 119-21
- `https://www.law.cornell.edu/uscode/text/5/403` — 5 U.S.C. § 403
- GAO-24-107001, GAO-25-108162 (`https://files.gao.gov/reports/GAO-25-108162/index.html`), GAO-26-107992 (AOPA-hosted PDF)
- NTSB, incident OPS26LA063, `https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/203529/pdf`
- FAA ICAO paper AAITF/18 IP/06 on the 2023 outage

### OIG
- `https://www.oig.dot.gov/agency/federal-aviation-administration`
- `https://www.oig.dot.gov/library-item/47238` — FI2026023
- `https://www.oig.dot.gov/library-item/47303` — AV2026030
- `https://www.oig.dot.gov/library-item/47304` — AV2026031
- `https://www.oig.dot.gov/library-item/47306` — ATO culture audit initiation
- `https://www.oig.dot.gov/library-item/47372` — AV2026039
- `https://www.oig.dot.gov/library-item/47332` — FY2027 Top Management Challenges
- `https://www.oig.dot.gov/library-item/46879` — Newark relocation audit initiation
- `https://www.oig.dot.gov/library-item/29670` — the 2009 FTI outage letter
- `https://www.oig.dot.gov/library-item/30085` — AV-2008-089
- `https://www.oig.dot.gov/sites/default/files/av2006047.pdf` — AV-2006-047
- `https://www.oig.dot.gov/sites/default/files/library-items/FAA%20IT%20and%20Telecom%20Contracts%20Final%20Report%202.26.2024.pdf` — ZA2024019
- `https://www.oig.dot.gov/about-oig/oig-history`, `/leadership`, `/deputy-inspector-general`
- `https://www.oig.dot.gov/sites/default/files/library-items/DOT%20OIG%20ARRP%20Phase%201_3-13-25.pdf` — capacity statement
- `https://www.oversight.gov/about/inspectors-general-vacancies`

### Event coverage (perishable — archive before use)
- AP: `https://apnews.com/article/flights-halted-airports-faa-f81b0904331dafad6133f291e5f531a8`; `https://apnews.com/live/ground-stop-aviation-flights-news-updates-11-13-2026` (Wayback `20261114024340`); `https://apnews.com/article/faa-us-flights-grounded-extraordinary-circumstances-6aaa6bd4991ef22eb0c3baa6961a91d1`
- BBC live `https://www.bbc.com/news/live/c6z9dwn12037t` (Wayback `20261113224703`); `https://www.bbc.com/news/articles/cqx2wyvyr3zzo`
- CBS `https://www.cbsnews.com/news/faa-issues-nationwide-ground-stop/`; CBS Chicago `https://www.cbsnews.com/chicago/news/ground-stop-chicago-ohare-midway-airports-equipment-outage/`
- NBC live `https://www.nbcnews.com/news/us-news/live-blog/live-updates-flights-grounded-faa-communications-outage-rcna609268`; NBC main `https://www.nbcnews.com/news/us-news/faa-orders-nationwide-ground-stop-departing-flights-reasons-safety-rcna609247`
- ABC live `https://abcnews.com/US/live-updates/faa-ground-stop-live-updates-hundreds-flights-canceled/?id=138125140` (entries `?entryId=138129305`, `138130405`); GMA `https://www.goodmorningamerica.com/news/story/nationwide-ground-stop-ordered-airports-faa-138121848`
- Reuters `https://www.reuters.com/3fec1b0a85a0/world/us/faa-issues-national-ground-stop-due-extraordinary-circumstance-reasons-safety-2026-11-13/`; Reuters via syndication `https://www.investing.com/news/stock-market-news/us-flight-shutdown-exposes-deepening-air-traffic-network-crisis-5026935`
- Axios `https://www.axios.com/2026/11/13/faa-nationwide-ground-stop`; CNBC `https://www.cnbc.com/2026/11/13/faa-ground-stop.html`; The Verge `https://www.theverge.com/news/1033489/faa-ground-stop`; IFR Meter `https://ifrmeter.com/blog/national-ground-stop-2026-11-13`; Mediaite (two pieces, both cited above); WPXI `https://www.wpxi.com/news/local/faa-orders-nationwide-ground-stop-all-departing-flights-reports-say/YPU5Y7NHBVDJTB4MGOZQHKDJX4/`; NY Post `https://nypost.com/2026/11/13/us-news/jetblue-cancels-most-remaining-flights-due-to-faa-ground-stop-predicts-chaos-wont-end-soon/`; Roll Call `https://rollcall.com/2026/11/13/air-travel-halt-prompts-calls-for-faa-communications-upgrades/`; WIRED `https://www.wired.com/story/the-faa-nationwide-ground-stop-is-over/`

### 2025 and the IG record
AP firings (both), The Hill, POLITICO (Feb 2025, partial), The Independent, Reuters (Verizon, Starlink, 16JUL25, 27FEB25), WaPo via Seattle Times, Rolling Stone (two pieces), The Verge (Feb 2025 and Aug 2026), Safety+Health, American Oversight, Travel Weekly, Fox News, NYT, CRS IF11546, FederalHiringData.

---

## 16. Open items before drafting

1. **Re-archive the advisories.** The FAA retains 15 days, so the URLs die around **29NOV26** — before the publication window. Wayback captures secured this session:
   - 111: `http://web.archive.org/web/20261113210113/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111`
   - 120: `http://web.archive.org/web/20261113235506/…adv_date=11132026&advn=120`
   - 117: `http://web.archive.org/web/20261114032411/…adv_date=11132026&advn=117`
   - 005: `http://web.archive.org/web/20261114013716/…adv_date=11142026&advn=5`
   - 001 (14NOV): `http://web.archive.org/web/20261114032430/…adv_date=11142026&advn=1`
   - 119: `http://web.archive.org/web/20261114032358/…adv_date=11132026&advn=119`
   - 018 (14NOV): `http://web.archive.org/web/20261114032528/…adv_date=11142026&advn=18`
   **All seven are captured.** The remaining 13NOV26 advisories in §2 and the carrier-specific holds of 14NOV26 are transcribed but not archived; capture any the piece quotes before 29NOV26. **The transcriptions in §1 and §2 are the durable record regardless.**
2. **Verify the 68% copper figure** against the letter itself, which is not published anywhere reachable. Currently second-hand from Reuters.
3. **Ask L3Harris.** No statement located. If the answer is "no comment," that is a sentence.
4. **FENS $2.4B vs $4B** — decide which to print and why.
5. **Whether an OIG report on 13NOV26 or a root-cause publication has appeared.** None as of collection. Check on publication day; if one exists, the piece changes shape.
6. **The OIG's Semiannual Report for the period covering 13NOV26** would be due in April 2027 — after the window.
7. **NATCA and ALPA.** No written statement for the event exists. NATCA's only output was a CNN interview with no transcript. That absence is itself reportable, but do not imply silence means dissent.
8. **Re-read the Oversight.gov vacancy figure on publication day.**
9. **Gothamist and DW totals** — search-index only, and inconsistent with every other figure. Do not use.

## 17. Hazards specific to this piece

- **The status page is a trap.** `nasstatus.faa.gov` never carried the national stop as an entry, swung between nine airports and none in half an hour, and listed cancelled delay programs for another half hour. IFR Meter: "The public status page was not a reliable guide." Any sentence resting on it is wrong.
- **Advisory 111 states no reason.** The reason has to be sourced to 120's REASON field, or to a human being's mouth, or stated as absent.
- **"Five hours" is wrong by the FAA's own clocks** unless you say which clock.
- **Three airborne counts measure three different things.**
- **The 18-centers figure is maintenance mechanics at 18 facilities, per PASS, per AP.**
- **Soskin filed an amicus brief supporting the removal power.** Include it.
- **DOGE causation is unestablished.** Structural link only, and say so.
- **United resumed; JetBlue cancelled.**
- **The 3:36 p.m. onset is Duffy's, and the FAA's first restriction is stamped 20:10Z — twenty-six minutes earlier.** Note it.
- **Two different FAA systems are called SMART.** The airspace AI tool and the internal vulnerability tracker (§6.1). Disambiguate every use.
- **The FAA's own statement says "multiple" centers, not "all."**
- **Two names for one statute:** P.L. 119-21 is the One Big Beautiful Bill Act, the "Big Beautiful Bill," and the **Working Families Tax Cut Act of 2025** — the last is what the FAA and DOT print in official documents.
