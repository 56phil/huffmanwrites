# Source notes — the nationwide ground stop of 13NOV26

**Status:** first pass complete 13–14NOV26; **daily passes begin 15NOV26** (§18 is the first manual delta, §19 is the automated daily log). Not a draft. Nothing here is prose for publication. Philip, 15NOV26: keep this pack current daily until further notice.
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
Wayback: `http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1` (saved by hand 15NOV26, body text checked: it holds the "large portion of the country" sentence).

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

1. **Cite §21, not this list — two of these seven snapshots do not carry the advisory.** Measured 17NOV26 with `scripts/faa-ground-stop-pack.py --audit`, which is the check to repeat: `111` (`20261113210113`) and `120` (`20261113235506`) return **200 with no advisory text in them**; `117` (`20261114032411`) could not be read at all, a verdict about the checker rather than about the capture; `5`, `1`, `119` and `18` still serve their advisories. **An earlier version of this item said four of the seven were dead, and that was wrong** — repeated fetches through a throttled archive turned "could not be read" into "not there". A retrieval failure and a wrong document are different findings, and only the second is a defect in the citation.
   The authoritative list is **§21**, generated from §19's verified captures and rewritten twice a day, and every row in it is fetched and checked for `ADVZY` before it is written down. As of 17NOV26 it holds verified snapshots for `111`, `119`, `120`, `001`, `005` and `018`, plus the day index pages for 13–17NOV26 and the FAA Q&A page. The remaining 13NOV26 advisories in §2 and the carrier-specific holds of 14NOV26 are transcribed but not archived; capture any the piece quotes before 29NOV26. **The transcriptions in §1 and §2 are the durable record regardless.**
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

---

## 18. Delta, 14–16NOV26 — the government states a cause

The pack closed at 14NOV26 ≈03:30Z, before Saturday's DOT/FAA briefing. Everything in this section postdates it and was fetched on 15NOV26 unless the entry says otherwise. **Nothing above has been edited**; where a line here contradicts a line earlier, §18.7 names which one governs.

### 18.1 The account, as the government now tells it

Told at the DOT briefing on 14NOV26 by Secretary Duffy and Administrator Bedford. The transcript is on `transportation.gov/briefing-room/icymi-us-transportation-secretary-sean-p-duffy-provides-update-restoration-airspace` — that page answers **403** to this client (measured 15NOV26); the text below is the page as rendered by the search backend, and each sentence is also carried by Reuters and CNBC, fetched directly. **Label any quotation with the outlet, per §5.**

The mechanism, in Duffy's words as DOT renders them:

> "In at least one of our remote FAA locations, a contractor was doing routine maintenance to switch telecommunication lines from old copper wire and they were bringing it over to fiber. That contractor that does the work for us is L3Harris."

> "…that router that was being replaced as we switched from copper to fiber, it started flooding other routers in our air traffic control system."

> "So, specifically, we had over 1,000 connection attempts every four to five seconds. And what that did was give us issues with our communication with airplanes and it also caused some disruption with our radar feeds."

Two renderings of the same line already diverge, and this is §5's transcript problem recurring inside the new account:

| Outlet | Rendering of the causal question |
|---|---|
| DOT transcript | "whether we had incompetence, meaning was it user error or install error from L3Harris or did they install a faulty router?" |
| CNBC, 14NOV26 | "whether we had incompetence, meaning was it user error, installator error from L3 Harris, or did they install a faulty router" |

**Scope of the fault.** ABC (AU), 15NOV26: the overload hit "17 of the FAA's 22 en route centres across the country." Bedford, per CNBC: "no FAA facilities went dark," and the stop was ordered on "instability" in information feeds to the centers. The pack's §5 count of affected centers — "multiple" (FAA statement) vs "all" (Duffy's X post) — now has a third figure, from a briefing rather than an advisory. Print the figure with its outlet.

**Two negatives, stated by Bedford, attributed:** "We see zero evidence of anything nefarious, and zero evidence of anything AI-related" (CNBC and ABC, identical wording). §5's AI note therefore keeps its shape: the tool was rolled out to all 22 centers on 10NOV26 and the vendor denied involvement; the government's denial is now on the record as well.

**Not established, and said so at the briefing:** whether the cause was contractor error, install error, or a faulty router. L3Harris's statement (via CNBC, 14NOV26): "We are supporting the FAA in its investigation to understand the conditions that led to the Nov. 13 ground stop of our nation's air travel." It adds that it has "completed more than 70% of the planned airspace communications conversion from legacy copper wires to a fiber optic system."

### 18.2 A labour fact the briefing did not mention

PASS, the union representing ~11,000 FAA employees, issued a statement on 14NOV26 (via ABC):

> "Historically, contractors have followed a protocol where FAA employees conduct a risk assessment and coordinate the maintenance of the system or equipment. PASS-represented technicians were not involved in the upgrades that led to the ground stop yesterday."

This is the first source in the record that describes a *process* control, not a component, and it is the union's account of its own exclusion. It is not corroborated by the FAA in any fetched page. `[INFERENCE]` It also supplies the piece's strongest non-technical sentence: the maintenance that stopped the airspace was done without the agency's own technicians.

### 18.3 The counts, settled

FlightAware, fetched directly on 15NOV26 at 05:31 CT, US-related flights:

| Day | Cancellations | Delays |
|---|---|---|
| Fri 13NOV26 (final) | 9,201 | 7,468 |
| Sat 14NOV26 (final) | 6,692 | 8,689 |
| Sun 15NOV26 (in progress at fetch) | 1,390 | 1,390* |

\*The page printed the **same value for US cancellations and US delays** on Sunday, which is almost certainly a render artifact; the cancellation line agrees with the morning wire copy (AFP: "more than 1,200"; AP: "more than 800"), the delay line does not. **Re-read before printing; do not print the Sunday delay figure from this pass.** Saturday's worldwide totals were 7,345 cancellations and 22,168 delays.

This supersedes §4's intraday Friday snapshots, which stop at 9:52 p.m. ET and will read low. Friday's settled figure is 9,201, not "6,828 at 9:52 p.m."

### 18.4 The only forward commitment on record

Bedford, 14NOV26, carried identically by ABC, CNBC and AFP: airlines "believe that they'll be able to have full schedule integrity by the close of business on Sunday." Duffy the same day, via AFP: operations were "slowly returning to normal," and "It is going to take us some time to unwind what has happened."

**The deadline that matters is not Sunday.** Airlines for America (A4A), the trade association for the major US passenger and cargo carriers, **fetched at source 15NOV26** (`airlines.org/news-update/u-s-airlines-prepare-for-busy-thanksgiving-travel-period-amid-record-high-jet-fuel-costs/`, 10NOV26):

> "Airlines for America (A4A) projects U.S. airlines will carry nearly 29 million passengers over the Thanksgiving holiday travel period (November 20 – 30)."

The same release adds the capacity and the cost, both usable: carriers are offering "38,000 more seats daily, on average, than they did in 2025," the busiest days are expected to be **Sunday 29NOV26 and Monday 30NOV26**, and October's jet-fuel spot price averaged **$4.64 a gallon**, past September's record, with "fuel and labor combined … about 55% of an airline's operating expenses." Its membership is the piece's cast — American, Delta, United, Southwest, Alaska, JetBlue, plus Atlas Air, FedEx and UPS — which is worth knowing before quoting it as a neutral authority: it is an industry lobby, and ABC News calls it exactly that ("a trade association and lobbying group").

### 18.5 What passengers actually hold

- **Waivers, not compensation.** American extended its travel alert through **18NOV26** and capped fares on domestic and short international routes (ABC, 15NOV26). Delta is encouraging flexible passengers to move to Monday. US carriers owe a refund only where a flight was cancelled and the passenger chooses not to fly; a government-caused failure triggers no duty of care. This is the fact that makes "the airline will look after you" false, and it belongs in the piece.
- **Crew cost.** American offered flight attendants extra pay to pick up trips; Delta offered double pay and confirmed seats to reposition crews; United offered premium pay through Sunday (CNBC, 14NOV26, from internal messages). The recovery was bought.

### 18.6 Politics, 14–15NOV26

AFP, 15NOV26: Governor Hochul called on Duffy to resign or be fired — "We're fortunate no lives were lost." Governor Pritzker, on X: "Cut the crap. Trump and Republicans have controlled Congress and could have funded the system." Senator Schmitt: "If today proves anything, it's that we need to update our air traffic control system & rebuild our airport infrastructure." Lawmakers called for investigations into the cause and into cyber exposure. **The President had made no public statement on the outage as of Sunday morning**, per AFP — a fact with a timestamp, so date it if used.

Duffy's ask is already in §9.3 ($50B, spoken, nothing filed). AFP renders it as an appeal for "$50 billion"; §9.3's "confirmed as a spoken demand with nothing filed behind it" still holds.

### 18.7 What this changes in the sections above

| Section | Was | Now |
|---|---|---|
| §5, "There is **no** official root-cause document" | true of documents | still true of documents; **no longer true of statements.** The government has an account on the record as of 14NOV26, and it offers two candidate faults in one breath. Say "no published root-cause report; the administration's account as briefed on 14NOV26 is…" |
| §5, Duffy "still working on the details" | 13NOV26 | now dated; do not present as current |
| §4 | Friday snapshots to 9:52 p.m. | settled totals in §18.3 |
| §5, centers affected | "multiple" vs "all" | add "17 of 22 en route centers" (ABC AU) |
| §11 | carrier-requested stops after the national one lifted | unchanged, and the 15NOV26 advisory index carries no national stop — only operations plans, FCA notices and volcanic-activity bulletins |

### 18.8 Perishability, measured

The FAA advisory index retains **15 days** (§16, item 1), so the 13–14NOV26 advisory URLs die around **29NOV26**. Wayback's availability API answered on 15NOV26 and returned a capture of advisory 111 taken **15NOV26 09:22:20Z** — after the pack was closed, which means the URLs are being re-captured by others and the capture to cite is the latest, not the one this pack recorded. A daily pass (§19) records the capture URL for each advisory it sees, so the piece cites a snapshot that exists. **Advisory 119**, which no archive held when §19's first block was written, was saved by hand on 15NOV26 at **11:40:06Z** (`http://web.archive.org/web/20261115114006/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119`); the Wayback save endpoint answered in about seven seconds this time, where the same request had timed out at 45 s earlier in the day.

### 18.9 Open items this pass closes or moves

- §16 item 5 (root-cause publication): no report exists; the briefing is the substitute, and it is not a report.
- §16 item 1 (re-archive): now mechanical, see §19.
- New: **whether the FAA resumed the copper-to-fiber cutover work after 14NOV26**, and under what risk assessment. No fetched page answers it. Duffy, via DOT: "there'll be a reevaluation of when we do this work." That is the question the next pass should put to the FAA statements index.

### 18.10 The contractor, in its own filings — added 15NOV26

The piece names L3Harris, so the pack should hold what the company says about itself and what the government's own records say about the contract. All fetched 15NOV26.

**Scale.** L3Harris Technologies, NYSE LHX, Melbourne, Florida, ~**45,000** employees. FY2025 revenue **$21.87B**; FY2026 guidance **$23.5–23.7B** (Q3 release, 29OCT26, which also reports quarterly revenue of $6.1B and a **record backlog of $53.2B**, book-to-bill 3.2x). Market capitalisation at the 13NOV26 close: **$50.7B** (stockanalysis.com). The company reorganised into three segments effective FY2026 — Space & Mission Systems, Communications & Spectrum Dominance, Missile Solutions — and divested its Space Technology Group to AE Industrial Partners on **3AUG26**. President and CEO: **Sam Mehta**.

**The contract.** L3Harris operates the **FAA Telecommunications Infrastructure (FTI)** network as a managed service and, in its own words, "own[s] the equipment and lease[s] the telecommunications services." The scope, from its own programme page and sell sheet: **4,400+ facilities**, **29,000+ telecommunications services**, "45,000 daily flights," "over 100,000 communications devices" monitored 24/7, and a claimed availability of **99.99971%**. Its copper-to-fiber tracker read **70% of sites upgraded, 5,170 fiber connections, last updated 2NOV26** — the number Duffy and the company both cite.

**Age of the arrangement.** The contract PIID is **DTFA01-02-D-03006**; the award went to **Harris Corp** in **July 2002** as FTI, "potentially worth $3.5 billion across 15 years" (Nextgov/FCW, 22JUL02). USAspending lists the recipient as **HARRIS CORPORATION** with **L3HARRIS TECHNOLOGIES, INC** as parent, potential end date **30SEP27** — the paperwork itself shows the lineage, which is why the piece can say "the same contractor since 2002" without asserting a merger date it has not fetched. A **single-source extension** was announced in September 2022 (`sam.gov`, justification notice).

**The successor already exists.** In **March 2023** the FAA awarded **Verizon** the **FENS** recompete — $2.4B, a 15-year period of performance if all options are exercised — explicitly to move off the copper/TDM environment FTI runs on (Washington Technology, 28MAR23). FTI is therefore an incumbent network being replaced, extended in the meantime, which is the institutional fact behind "we're doing the switchover now."

**The company has been blamed for this before, and its answer is on the record.** After a contractor cut Frontier fiber in Denton County and grounded flights at DFW in **September 2025**, the FAA and American Airlines faulted **L3Harris** for "failing to ensure redundancies in the system functioned properly." L3Harris's statement to NBC 5:

> "L3Harris has successfully operated the FAA telecom network for over 20 years with a reliability of 99.999% uptime. The unfortunate outages at DFW were preventable and are a direct result of lack of U.S. government investment to replace legacy, end-of-life analog telecom circuits."

The same statement says the company is "on contract to replace these legacy analog circuits (which total over 5,000) with new modern circuits," and a spokesperson gave the timeline: "modernize the legacy TDM telecom nationwide by the end of 2027." **That is the shape of this event too** — old equipment, a contractor mid-replacement, an outage — and it is the closest thing in the record to a pattern with a named party.

**Two things this section does not establish, and the piece must not imply.** That the 13NOV26 router was L3Harris's own equipment rather than a vendor's — Duffy's briefing offers "contractor error" or "a faulty router" without choosing. And that the company's 99.99971% figure has been independently audited; it is the contractor's own claim, printed here as such.

### 18.11 Was it avoidable? Three layers, and only two of them are evidenced — added 15NOV26

The claim a reader will bring is "this could have been prevented with better mitigation." It is **partly true, and the part that is unproven is the part a network engineer would attack first**, so the piece must not make the claim in one piece. Split it.

**First, fix what "avoided" modifies.** The ground stop was not the failure. Three thousand five hundred aircraft aloft, landed without loss, is the safety system working (§1.1–§1.6, §3). What may have been avoidable is the **event** — a maintenance action that destabilised the network the airspace depends on — and the **duration**, 4 h 22 m to find and isolate one device (§3).

| Layer | The claim | Verdict | Evidence |
|---|---|---|---|
| **Process** | The cutover proceeded without the FAA's own technicians performing their normal risk assessment and coordination | **Supported.** The strongest fact in the case | PASS, 14NOV26: "Historically, contractors have followed a protocol where FAA employees conduct a risk assessment and coordinate the maintenance of the system or equipment. PASS-represented technicians were not involved in the upgrades that led to the ground stop yesterday." Uncorroborated by the FAA in any fetched page |
| **Method** | A remote-site copper-to-fiber cutover could have been staged, isolated and reversed | **Supported** — see §18.12, which raises this from "probably" | Duffy's account is that remote locations were treated as low-impact and worked "during the day" (§18.1). This was not one-off surgery: the company had completed ~70% of a 5,170-connection programme (§18.10), so it was a repeated procedure with no canary described and, as it turned out, no isolation that held. **GAO had already said so in writing on 14SEP26:** 11,389 unintegrated project schedules, installations sequenced "without optimizing the schedules to reduce impacts to controller operations," with ground stops named among the predicted consequences |
| **Architecture** | Better redundancy design would have stopped the propagation | **Not established — do not assert it** | FTI's redundancy is built for carrier and path failure: "dual private Metro Ring solution … optical carrier protection switching across diverse telecommunications ingress and egress" at 20 ARTCCs, a multi-carrier last mile, 99.99971% claimed availability (§18.10). It **worked**: no facility went dark (§18.1). A faulty router advertising itself into routing adjacencies is a failure *inside* the redundancy, where every alternate path learns from the same broken speaker. More rings do not reach it |

**Why the architecture half fails as an argument.** Redundancy is a statement about *paths*. This failure was a statement about *participants*: one device generating "over 1,000 connection attempts every four to five seconds" (Duffy, §18.1) into peers that believed it. The controls that bear on that are different in kind — control-plane rate limiting, route dampening, prefix limits, and out-of-band management so a flooding device can be reached and shut down without traversing the path it is flooding. `[INFERENCE]` Whether the legacy TDM-to-IP equipment at a remote FAA site supports any of those is **unknown from every fetched page**, and a piece that assumes it is making an engineering claim about gear it has never seen.

**The detection gap is design, and it is evidenced.** Bedford, per CNBC: officials could not identify the cause "for about 45 minutes," and no facility went dark — the symptom was instability in information feeds, not a link failure (§18.1). A monitoring regime built on circuit availability is blind to that class: the circuit was up, the device was up, and the device was the fault. **Availability is the metric that hid this**, which is why the contractor's "99.999% uptime" (NBC 5, September 2025, §18.10) is a true sentence about the wrong quantity. Print the two side by side.

**What would settle the architecture question**, and where to look:

1. The FTI contract's technical requirements for router configuration management and out-of-band access — not public in any page this pack holds.
2. The FAA's post-event investigation, if one is published. None exists as of 15NOV26 (§18.9).
3. L3Harris's own account of the maintenance procedure — it has issued a statement of support, not a description of method (§18.1).
4. Whether the same cutover method ran at the other completed sites without incident. If it did, the method is not the cause and the individual device or install is; if an incident occurred and was absorbed, that is the piece's central finding. **No fetched page answers this.**

**How to phrase it in the piece, once.** "The stop was the safety action; what was avoidable was doing a live cutover on the network that carries the airspace without the agency's own technicians assessing the risk, and then needing three-quarters of an hour to find the cause. Whether more redundancy would have contained it is a question the FAA has not answered, and the system that failed was the system designed to be redundant."

### 18.12 The warning existed in writing, and it was not about DOGE — added 15NOV26

**The document.** GAO-26-107992, *Air Traffic Control Systems: Ambitious New Modernization Effort Needs Cost and Schedule Planning*, report dated **14SEP26**, to the House Oversight Subcommittee on Government Operations. **Fetched whole 15NOV26** (`download.aopa.org/advocacy/2026/2026-09_GAO-26-107992-Air-Traffic-Control-Systems.pdf`, 10 MB, text extracted with `pdftotext`).

**Why it matters to §18.11.** It is why the **method** layer there reads *supported* rather than *probably supported*, and it does so in the government's own words, two months before the outage:

> "FAA has not developed an integrated master schedule for phase 1. Instead, FAA has 11,389 individual project schedules that are not integrated. As a result, individual projects are scheduled for installations at the same sites, generally without optimizing the schedules to reduce impacts to controller operations."

And its own prediction of the consequence:

> "…could lead to more system outages, ground stops, flight delays, and safety incidents."

That is the September warning the Washington Post reported on 14NOV26 as "FAA was warned for years about repair risks leading to nationwide ground stop" — the article answered a timeout to this client, so **the GAO PDF is the citation, not the newspaper**. GAO also records the sequencing problem in the concrete: the integrator delivered a preliminary integrated master schedule in **April 2026**, and as of **May 2026** the 11,389 schedules were still unintegrated, because FAA officials said integrating them "would not be useful or helpful." An AI tool to optimise them was in testing, with no business rules and no implementation date.

**Also from the report, for §4's numbers.** As of **May 2026**, FAA had replaced **2,560 of 5,170** copper connections — 49.5%. The Vought–Duffy letter put it at 68% and the contractor's own tracker at 70% by 2NOV26 (§14, §18.10). Three figures, three dates, one trend; never printed as agreement.

**And the pattern, in GAO's own list:** the January 2023 NOTAM stop (≈2 hours, 1,300 cancellations, 10,000 delays); Newark's April and May 2025 failures at Philadelphia TRACON ("controllers were unable to see aircraft positions or communicate with pilots"); and **September 2025 at Dallas TRACON**, where "a telecommunications issue led to a loss of radar, frequencies, and automation equipment … ground stops and over 1,800 flight delays and cancellations as controllers reverted to manual methods." The §7 list now has a fourth citation, from an auditor rather than a newspaper.

### 18.13 Can any of it be traced to DOGE? No, and the honest answer is more useful than yes

Asked directly on 15NOV26. The verdict the pack already carried (§10.5: "DOGE causation is unestablished. Structural link only, and say so") survives this week's disclosures, and now has a better rival explanation.

**What breaks a DOGE chain on the evidence.**

1. **The work was contract work on a contract older than DOGE.** FTI is `DTFA01-02-D-03006`, awarded to Harris in **July 2002** and held ever since (§18.10). The cutover was performed under it. No fetched source places a DOGE decision anywhere in the chain from contract to router.
2. **The money came from Congress, not from DOGE, and it went to modernisation.** $12.5B under P.L. 119-21, July 2025 (§9.1). The Verge's finding is the opposite of causation: DOGE "did not help the FAA buy or implement any major system upgrades," and "none of the $12.5 billion … goes toward personnel" (§10.4, §10.5).
3. **The specific failure is an install or equipment fault.** Duffy: "user error or install error from L3Harris or … a faulty router," undetermined (§18.1). PASS says its technicians were not involved — the risk-assessment step — which is a **process** statement about a *protocol*, not automatically a statement about headcount.
4. **The strongest causal document points at programme design.** GAO, September 2026: 11,389 unintegrated schedules, installations sequenced "without optimizing the schedules to reduce impacts to controller operations" (§18.12). That is a finding about how the modernisation is managed, and it implicates an administration that was in a hurry — but not the DOGE episode in particular.

**The one channel that stays open, and how to state it.** Staffing may bear on the *duration* rather than the cause. The FAA's own **ATSS Workforce Plan 2026–2030** (fetched 15NOV26) says the agency is "currently unable to staff all shifts at 67 facilities"; that ATSSs averaged **115 hours of overtime each in FY 2025** "fixing aging equipment"; and that "staffing shortfalls have resulted in longer restoration times and increased reliance on second level support." **Longer restoration times** is precisely the 4 h 22 m in §3 and the ~45-minute detection window in §18.1. The plan does not mention the February 2025 terminations, and the shortfall it documents long predates them — GAO reported in September 2024 that 51 of 138 ATC systems were unsustainable and 54 more potentially so, and the understaffing was chronic before 2025.

**So the defensible sentence is:** the modernisation that broke the airspace was already running behind a schedule nobody had integrated, on equipment an auditor had called unsustainable for two years, with a technician corps the agency says cannot cover every shift — and the DOGE episode neither caused that nor repaired it; it terminated roughly 350–400 people, delivered no upgrades, and left the rest to contractors. Structural link, named and bounded; causation, not established, and the paperwork now points elsewhere.

**What would change this verdict:** a fetched source showing that the risk assessment was skipped *because* of the 2025 reductions, or that the cutover was accelerated to a political deadline. Neither exists in the record as of 15NOV26. Look for both in any OIG report on 13NOV26 (§18.9).

### 18.14 The agency answers in writing — added 16NOV26

**The document.** FAA, ["Nationwide Ground Stop: Questions and Answers"](https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers), dated **Sunday, November 15, 2026**, fourteen questions answered. Fetched 16NOV26 05:2x CT. It 403s to a client sending the pack's own User-Agent and answers a plain one; the newsroom index at `faa.gov/newsroom` loads only with `-L` after a 301.

**What it establishes that no earlier page did.** Two candidate locations by name: "a radar site in Amarillo, Texas and a radio communications site in El Dorado, Arkansas." L3Harris "had been doing work at the El Dorado site, including deployment of a new router." Blocking the two sites stabilised the network, and "the broadcasting function was also disabled on all the new routers as a precaution."

**The remedy's size, stated once.** "As a precaution, we disabled the same functionality on approximately 60 similar routers in the system." Duffy on ABC's *This Week* the same day puts the fleet at 69: "we have 69 of these routers in the national airspace. We've stopped their ability to broadcast" (§18.14's ABC citation below). The two counts may differ by whether the originating machines are included; no page says.

**The facility count is now the agency's own.** "We began experiencing instability at 17 of our 22 Air Route Traffic Control Centers, and it spread into several Terminal Radar Approach Controls," and "Approximately 3,500 aircraft safely landed" (§1–§2 record 17 only via ABC AU).

**The denial, verbatim.** "No, this is due to the legacy TDM system causing instabilities. None of the upgraded towers that received modifications from the down payment in the Working Families Tax Cuts went down." Read with the answer above it, the sentence is true of the equipment that failed and silent about the router that spoke; the piece must not present the denial as a finding.

**The timing, conceded.** Asked why the replacement ran mid-day: "This disruption was a result of a routine replacement at a remote facility, which has regularly been done for decades … However, based on what happened Friday, we will reevaluate when we do replacement/maintenance work." That is the first process commitment in the record and it bears on §18.2's PASS claim, which the Q&A does not address.

**Counts that do not agree.** "operators canceled approximately 12,462 flights, including 9,082 cancellations by major airlines," against FlightAware's settled 9,201 US and 9,938 worldwide (§19, 15NOV block). The agency adds: "While not all cancellations were directly caused by the nationwide ground stop."

**Duffy, 15NOV26, ABC News** (`abcnews.com/Politics/transportation-secretary-duffy-atc-routers-ability-broadcast-data/story?id=138155545`, fetched 16NOV26): the router is "in the L3Harris lab down in Florida" with FAA staff on site; the FBI has offered assistance; "no indication that this was a hack"; "We don't think that someone tried to sabotage the network on the install at all. But we don't actually have the root cause." On the sequence: "When the router in that area was turned on, we saw that in Amarillo, Texas, a system we had replaced about three weeks earlier, that started to flood our system as well." On money: none of the $12.5B is "for a new architecture for telecom"; AT&T, Verizon and Lumen are "ready to start working tomorrow"; completion "by the end of 2028 or possibly the first quarter of 2029."

**The appropriators' counter, same weekend** (Larsen and Carson, via ABC): "$4.3 billion but only spent $1 billion, leaving $8 billion unobligated and $11 billion unspent."

**The Amarillo facility, from the ground.** ABC 7 News (KVII), 15NOV26: a "Remote Center Air/Ground Communication (RCAG)" next to Highland Park High School, unmanned, part of the Albuquerque Center, replaced about three weeks before the outage. The agency's word is "radar site"; the local report describes an RCAG. Print both, reconcile neither.

**Open items this pass closes or moves.** §16 item 5 unchanged: no OIG report (the OIG's FAA page carried none at 16NOV26 05:2x CT) and no root cause (Duffy: "we don't actually have the root cause"). §16 item 1 unaffected: the advisories still die around 29NOV26. New and unanswered: what the broadcast function did, what disabling it costs the operation, whether the same cutover method ran at the other converted sites without incident, and whether the Amarillo replacement was itself a latent fault.

**Index state at 16NOV26 05:30 CT:** 21 rows, no national restriction; a CDM ground stop at Las Vegas (Advisory 010) cancelled fourteen minutes later (011). The published piece is [`the-sixty-routers.md`](https://www.huffmanwrites.org/posts/essays/the-sixty-routers/).

### 18.15 The week after — Juniper named, installs paused, a reproduction, and a $50.1 billion ask (added 19NOV26)

Everything here was fetched on 19NOV26 unless the entry says otherwise. Nothing above is edited; this section is the delta from 17NOV26 to 19NOV26, and the record it changes is named in the last two paragraphs.

**The vendor is named and its rollout is stopped.** ABC News, 17NOV26: "The Federal Aviation Administration is halting the installation of Juniper routers following last week's rare nationwide ground stop, an agency spokesperson confirmed to ABC News on Tuesday." The pause holds "while the FAA investigates the cause." The agency's 15NOV26 Q&A already names the brand in its last answer ("the originating Juniper routers", "more than 60 other Juniper routers", "we have paused installing them"), so ABC's confirmation is the agency saying it to a reporter rather than only on a page. Per Roll Call (17NOV26), the pause came a day after Senate Commerce Committee Democrats wrote asking for one: "With thousands of conversions remaining, FAA must address outstanding safety and reliability concerns before expanding installation."

**The 69th installation, from the secretary's own mouth.** Duffy, 17NOV26, in the DOT's "ICYMI" transcript: "this was the 69th installation of that router. Sixty-eight times it worked well. This one, the router started to broadcast into our network and it started to overload the network." ABC carries the same count in his words to reporters: "This was the 69th, and 68 had gone really well … So we thought it's only prudent to pause the use of these routers." Print the count from the transcript, not from a paraphrase, because it is the fact that turns the event from a bad design into a bad unit or a bad installation.

**A reproduction, not a cause.** CNBC, 18NOV26, two named reporters, three anonymous people "familiar with the investigation": "Engineers and analysts searching for the root cause of the technical issues behind Friday's nationwide ground stop … have been able to replicate the situation that was overwhelming parts of the air traffic system." The same piece: "those investigating the matter have yet to determine exactly why two routers in question failed"; the routers are "being examined at an L3Harris lab in Florida" (ABC, 17NOV26); and the flood began "within eight minutes of its installation." **The eight-minute figure is CNBC's, attributed to investigators, and it is not on any FAA page fetched to date.**

**Duffy states the same thing in the government's own words.** DOT "ICYMI", 17NOV26: "We've been able to recreate what happened in El Dorado, but the root cause of what happened, we don't have clarity yet." That sentence is the piece's current status line, and it is safer than any outlet's summary, because it concedes replication and denies cause in one breath. He also names the lab's occupants: "at that facility is L3Harris, HP is there, Cisco is there, the FAA is there," and says he asked FBI Director Kash Patel for a team.

**The vendor's sentence, and what it leaves open.** Hewlett Packard Enterprise, via ABC, 17NOV26: "Based on what we know and have been told by others, our equipment was working as configured." Read beside Duffy's "user error or install error … or a faulty router" (§18.1), the vendor's claim is about configuration and the secretary's list is about cause, so the two are not yet in contradiction. Do not print one as an answer to the other.

**The money: $30.1B became $50.1B, and the Hill pushed back.** DOT release, 17NOV26: Duffy, Bedford and OMB Director Russ Vought sent appropriators a letter requesting **$50.1 billion**, split five ways:

| Amount | Purpose, as the release states it |
|---|---|
| $10.1B | "a reliable digital architecture," including "building more resilient telecommunication systems" |
| $10B | "overhaul outdated airport infrastructure" |
| $10B | "fully modernize aging airport terminals" |
| $10B | "five new consolidated Air Route Traffic Control Centers (ARTCC), replacing the current 22 … the last was built in 1969" |
| $10B | "build and improve up to 140 air traffic control towers" |

The release's own framing: "Last week, we urged Congress to act swiftly … Less than 24 hours later, the urgent news for this investment became undeniable when outdated, legacy equipment disrupted aircraft communications and radar feeds." **The increase is where the sourcing must be careful.** Roll Call, 17NOV26: "Transportation Secretary Sean Duffy and Office of Management and Budget Director Russ Vought last week asked for $30.1 billion before Duffy voiced support for the rest of the funds at a Friday night press conference," and the added $20B is "half for construction of five new air route traffic control centers, and half for construction, replacement and improvement of up to 140 air traffic control towers." CNBC and WIRED round the whole ask to $50B and describe a $30B to $50B step. **Cite the letter for $50.1B, Roll Call for the $30.1B baseline, and never present the two asks as one number.**

**Only $10.1B of it is the network that failed.** That is the sentence the piece needs: the ask that follows a telecommunications failure devotes one fifth of its money to telecommunications. The other $40B is buildings, terminals and towers, which is why the appropriators objected. Cruz, via Roll Call: "I don't think the full $50 billion will be funded … the request needs to be focused on safety modernization." Tillis expects "more in the $10 billion to $30 billion range." The standing objection: about $8B of the $12.5B down payment is still unspent (Roll Call; §18.14's Larsen and Carson figure is $8B unobligated and $11B unspent). Duffy's answer, same page: "I only pay when they deliver," and on the current course "it would take 300 years to replace every U.S. tower."

**The controllers' account, the first one in the record.** WIRED, 19NOV26, Aarian Marshall, two anonymous people familiar plus a controller: "That was the hairiest 90 minutes of my career." The sequence, which no FAA page has published: "intermittent dropouts on radio frequencies at Centers in the region, from Kansas City to Chicago," then a cascade "to other regions, including the areas around Washington, DC, and New York." El Dorado is "part of the larger Center based in Memphis, Tennessee," and the conversion is "about 70 percent complete." Bedford the same week, via Politico as WIRED quotes it, called the outage "a knee scrape, and I'm sorry." An airline pilot and lecturer, Scott Miller: "It was not dangerous, but it was highly inconveniencing, and it was not normal." **Attribute the dropouts and the cascade to WIRED's sources; they are the only account of what controllers saw, and no official document confirms the order of failure.**

**The duration is stated four ways and the piece must pick one and name it.** The FAA Q&A: 3:30 p.m. to 8:15 p.m. ET, which is 4 h 45 m. WIRED: "a 4.5-hour nationwide ground stop." CNBC: "more than four hours." §3's own computation from the advisories: 4 h 22 m. These measure different things (the first advisory to the cancellation, the stop as the agency describes it, the stop as a reporter rounds it), and one clock named in the sentence is honest where "about four and a half hours" is not.

**What this section moves in §16.**

- Item 5 (root cause and OIG): unchanged on both halves. No root cause as of 19NOV26, in the secretary's words; no OIG report fetched.
- New, closed: the vendor is named (Juniper, via HPE), the installs are paused, and a lab reproduction exists. None of the three is a cause.
- New, open: **why this unit and not the other 68**, which is the question the piece should ask and no fetched page answers. Also open: whether the pause stops the remaining 30% of the conversion, and what the disabled broadcast function did in normal operation (§18.14's unanswered item, still unanswered).
- The advice to the writer: the strongest new sentence in the record is Duffy's "we don't have clarity yet," printed beside the $50.1B ask, because the money request arrived four days before any cause did.

**Operationally the airspace is normal, and the pack's own blocks are the proof.** The 18NOV26 index carries 78 rows and no ground-stop row; 19NOV26 carried 8 rows at 23:30 CT and 34 at 08:00 CT, and neither pass found a ground-stop row (§19). Settled US cancellations, FlightAware, last read 18NOV26 23:30: 13NOV 9,201; 14NOV 6,695; 15NOV 2,336; 16NOV 375; 17NOV 105; 18NOV 133. 19NOV26 is not settled and must not be printed as one: 33 US cancellations at 23:30 CT on the 18th, 55 at 08:00 CT on the 19th. The 08:00 pass also lost FlightAware's three-day page to a **504**, so the block records `SOURCE UNAVAILABLE`, which is a gap in the record and not a quiet day. The FAA's "approximately 12,462 flights" (9,082 by major airlines) is not a cancellation count for the stop and cannot be reconciled with the tracker's 9,201 US (§18.14).

**Sources, fetched 19NOV26.** ABC News, ["FAA halts router installation following nationwide ground stop, root cause of issue unknown"](https://abcnews.com/US/faa-halts-router-installation-nationwide-ground-stop/story?id=138221009), 17NOV26. CNBC, ["FAA ground stop investigation: Engineers replicate network overload"](https://www.cnbc.com/2026/11/18/faa-ground-stop-router-investigation.html), 18NOV26. WIRED, ["'The Hairiest 90 Minutes of My Career': How the FAA Ground Stop Went Down"](https://www.wired.com/story/how-the-november-13-faa-ground-stop-went-down/), 19NOV26. DOT, ["Trump Administration Calls on Congress to Fully Fund Air Traffic Control Modernization with $50.1 Billion Investment"](https://www.transportation.gov/briefing-room/trump-administration-calls-congress-fully-fund-air-traffic-control-modernization-501) and ["ICYMI: … Duffy Shares Update on Nationwide Ground Stop Investigation"](https://www.transportation.gov/briefing-room/icymi-trumps-transportation-secretary-sean-p-duffy-shares-update-nationwide-ground), both 17NOV26 and **both 403 to this client** (§18.1's limit); their text is quoted as the search backend rendered it. Roll Call, ["Hill GOP looking to trim White House's $50 billion aviation ask"](https://rollcall.com/2026/11/17/hill-gop-looking-to-trim-white-houses-50-billion-aviation-ask/), 17NOV26.

---

## 19. Daily collection log

### 15NOV26

**Collected** 15NOV26 08:00 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-15** — 25 rows, fetched 08:00 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 025 | SFO/ZOA | 11/15/26 13:54 | SFO AIRPORT SCHEDULING DELAYS |
| 024 | DCC | 11/15/26 13:17 | ATCSCC ADVZY 024 DCC 11/15/26 ROUTE RQD /FL / NAME: FLORIDA_TO_OHIO_VALLEY_1 / CONSTRAINED AREA: ZJX / VALID: ETD 151600 TO 151900 |
| 023 | DCC | 11/15/26 12:57 | OPERATIONS PLAN |
| 022 | DCC | 11/15/26 12:41 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 021 | DCC/ZHU | 11/15/26 12:26 | ZHU SWAP_FYI |
| 020 | DCC | 11/15/26 12:10 | ATCSCC ADVZY 020 DCC 11/15/26 ROUTE RQD /FL / NAME: IAH_DOOBI_NORTH_PARTIAL / CONSTRAINED AREA: ZHU / VALID: ETD 151300 TO 151700 |
| 019 | DCC/ZJX | 11/15/26 11:48 | ZJX CAPPING/TUNNELING_RQD |
| 018 | DCC | 11/15/26 11:47 | ATCSCC ADVZY 018 DCC 11/15/26 FCA RQD / NAME: FCA001:NO_AR_ATLANTIC_Y-RTES_TO_MCO_TPA_RSW_AREAS / CONSTRAINED AREA: ZJX ZMA / VALID: FCA ENTRY TIME FROM 151626 TO 151850 |
| 017 | DCC | 11/15/26 10:28 | OPERATIONS PLAN |
| 016 | DCC | 11/15/26 10:05 | ATCSCC ADVZY 016 DCC 11/15/26 FCA RQD / NAME: FCA006:ZMA_CARIBBEAN_NORTHBOUND_NO_ARS / CONSTRAINED AREA: ZMA ZJX ZDC ZNY / VALID: FCA ENTRY TIME FROM 151711 TO 151850 |
| 015 | DCC | 11/15/26 09:41 | ATCSCC ADVZY 015 DCC 11/15/26 FCA RQD / NAME: FCA004:CAPE_LAUNCH_WEST_COAST_1_PARTIAL / CONSTRAINED AREA: ZMA ZJX ZDC ZNY / VALID: FCA ENTRY TIME FROM 151711 TO 151850 |
| 014 | DCC | 11/15/26 09:33 | ATCSCC ADVZY 014 DCC 11/15/26 FCA RQD / NAME: FCA003:CAPE_LAUNCH_1B / CONSTRAINED AREA: ZMA ZJX ZDC ZNY / VALID: FCA ENTRY TIME FROM 151711 TO 151850 |
| 013 | DCC | 11/15/26 09:27 | ATCSCC ADVZY 013 DCC 11/15/26 FCA RQD / NAME: FCA002:CAPE_LAUNCH_1A_PARTIAL / CONSTRAINED AREA: ZMA ZJX ZDC ZNY / VALID: FCA ENTRY TIME FROM 151711 TO 151850 |
| 012 | DCC | 11/15/26 09:26 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 011 | DCC | 11/15/26 09:21 | ATCSCC ADVZY 011 DCC 11/15/26 FCA RQD / NAME: FCA001:NO_AR_ATLANTIC_Y-RTES_TO_MCO_TPA_RSW_AREAS / CONSTRAINED AREA: ZJX ZMA / VALID: FCA ENTRY TIME FROM 151626 TO 161850 |
| 010 | DCC | 11/15/26 08:56 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 009 | DCC | 11/15/26 08:26 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 008 | DCC | 11/15/26 07:02 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 007 | DCC | 11/15/26 03:38 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 006 | DCC | 11/15/26 02:57 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 005 | DCC | 11/15/26 02:30 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 004 | DCC | 11/15/26 00:19 | OPERATIONS PLAN |
| 003 | DCC/ZDC | 11/15/26 00:04 | ZDC NRP SUSPENSION_RQD |
| 002 | DCC | 11/15/26 00:03 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 001 | DCC | 11/15/26 00:03 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |

No row on this day's index is a ground-stop advisory.

**Advisories, 2026-11-16** — the index returned no rows, fetched 08:00 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

**FlightAware totals** — fetched 08:00 CT. The date column is this pass's CT date for that page; the tracker words its own pages by weekday.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Fri 13NOV26 | 9,201 | 7,468 | 9,938 | 25,041 |
| Sat 14NOV26 | 6,695 | 8,969 | 7,349 | 22,498 |
| Sun 15NOV26 | 1,446 | 2,043 | 1,752 | 11,016 |

**Wayback captures** — nearest snapshot the availability API returned for each advisory, fetched 08:00 CT. The advisory index keeps 15 days; a row reading `no capture` is a document no archive holds yet.

| Advisory | Captured (UTC) | Snapshot |
|---|---|---|
| 11132026/111 | 20261115092220 | http://web.archive.org/web/20261115092220/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |
| 11132026/119 | 20261115114006 | http://web.archive.org/web/20261115114006/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |
| 11132026/120 | 20261114173544 | http://web.archive.org/web/20261114173544/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |
| 11142026/1 | no capture |  |
| 11142026/5 | 20261115112924 | http://web.archive.org/web/20261115112924/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |
| 11142026/18 | 20261114032528 | http://web.archive.org/web/20261114032528/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |
| 11152026/23 | no capture |  |
| 11152026/17 | no capture |  |
| 11152026/4 | no capture |  |

**Reading — 15NOV26** (written by hand from the block above; prose lives here, the block stays machine-written).

- **The airspace carried no restriction on 15NOV26, and the index says so in its own words.** All 17 rows are operations plans, FCA notices for a Cape Canaveral launch window, five volcanic-activity bulletins, and a ZDC national-route-program suspension. There is no ground stop, no ground delay program, no national entry. For a piece that has to answer "is it over," this is the primary document, not a press line.
- **The two stop advisories are titled differently, and the difference is in the FAA's own index.** Advisory 111 reads **"NATIONAL GROUND STOP"**; advisory 120, sent 112 minutes later, reads **"NATIONWIDE GROUND STOP."** Verified 15NOV26 by running the collector's parser over the 13NOV26 index (123 rows). Cite by number, never as "the FAA's ground stop advisory," because there were two and they are named differently.
- **Advisory 119 — the tiered-release plan — was the one primary document no archive held, and it is captured now** (§1.3). This bullet read *has no capture* when it was written on 15NOV26; the save request was retried later the same day and answered, so the snapshot is **`http://web.archive.org/web/20261115114006/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119`** (captured 15NOV26 11:40:06Z, checked for the body text: it holds the tiered-approach paragraph verbatim). The earlier statement is left standing above so the correction is visible rather than silent. Advisory 119 is no longer on the capture-gap list; the remaining gaps are the rows the daily pass reports itself.
- **The 111 capture was refreshed on 15NOV26 at 09:22Z**, after this pack closed on 14NOV26 at ~03:30Z. Somebody else archived it. The snapshot to cite is the newest one, which is what §18.8 said would happen and what the daily pass now records automatically.
- **The empty 16NOV26 index at 05:40 CT is not a finding.** The day had not begun; the collector fetches tomorrow so that a later re-run in the same day can see it. A reading that treats an empty tomorrow as a quiet day would be reading noise.
- **The FlightAware Sunday line reproduces the page's duplicate figure** (US cancellations and US delays both 1,390). The block did its job — it printed what the page said. §18.3's instruction stands: re-read before printing that one number.

### 16NOV26

**Collected** 17NOV26 03:19 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-16** — 82 rows, fetched 03:19 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 082 | DCC | 11/16/26 23:54 | OCEANIC ROUTE CLOSURES_RQD |
| 081 | SFO/ZOA | 11/16/26 23:46 | SFO AIRPORT ARRIVAL DELAYS - EXTENSION |
| 080 | DCC | 11/16/26 23:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 079 | LGA/ZNY | 11/16/26 23:29 | CDM GROUND STOP |
| 078 | SFO/ZOA | 11/16/26 23:24 | CDM GROUND DELAY PROGRAM |
| 077 | DCC | 11/16/26 22:51 | GULF ROUTE CLOSURES_RQD |
| 076 | AUS/ZHU | 11/16/26 22:50 | CDM GS CNX |
| 075 | DCC | 11/16/26 22:22 | OPERATIONS PLAN |
| 074 | SFO/ZOA | 11/16/26 22:15 | SFO AIRPORT ARRIVAL DELAYS |
| 073 | AUS/ZHU | 11/16/26 22:14 | AUS AIRPORT ARRIVAL DELAYS |
| 072 | SFO/ZOA | 11/16/26 22:12 | CDM GROUND STOP |
| 071 | AUS/ZHU | 11/16/26 22:04 | CDM GROUND STOP |
| 070 | TEB/ZNY | 11/16/26 21:44 | CDM GS CNX |
| 069 | DCC/ZMA | 11/16/26 21:39 | OCEANIC ROUTE CLOSURES_RQD |
| 068 | DCC/ZMA | 11/16/26 21:34 | OCEANIC ROUTE CLOSURES_RQD |
| 067 | DCC | 11/16/26 20:59 | ATCSCC ADVZY 067 DCC 11/16/26 FCA RQD /FL / NAME: FCA005:DFW_DOGS_HEAD_MODIFIED / CONSTRAINED AREA: ZAB / VALID: FCA ENTRY TIME FROM 170000 TO 170500 |
| 066 | DCC | 11/16/26 20:54 | GULF ROUTE CLOSURES_RQD |
| 065 | SAN/ZLA | 11/16/26 20:52 | CDM GROUND DELAY PROGRAM CNX |
| 064 | DCC | 11/16/26 20:46 | ATCSCC ADVZY 064 DCC 11/16/26 FCA RQD / NAME: FCA004:PHX_NO_EAGUL_PARTIAL / CONSTRAINED AREA: ZAB / VALID: FCA ENTRY TIME FROM 170000 TO 170500 |
| 063 | TEB/ZNY | 11/16/26 20:30 | CDM GROUND STOP |
| 062 | DCC | 11/16/26 20:27 | REROUTE CANCELLATION |
| 061 | DCC | 11/16/26 20:24 | OPERATIONS PLAN |
| 060 | DCC | 11/16/26 20:11 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 059 | AUS/ZHU | 11/16/26 19:44 | CDM GS CNX |
| 058 | DCC | 11/16/26 19:40 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 057 | LGA/ZNY | 11/16/26 19:36 | CDM GS CNX |
| 056 | TEB/ZNY | 11/16/26 19:36 | CDM GROUND STOP |
| 055 | DCC | 11/16/26 19:28 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 054 | AUS/ZHU | 11/16/26 19:07 | CDM GROUND STOP |
| 053 | LGA/ZNY | 11/16/26 18:51 | CDM GROUND STOP |
| 052 | DCC | 11/16/26 18:44 | OPERATIONS PLAN |
| 051 | DCC | 11/16/26 18:19 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 050 | LGA/ZNY | 11/16/26 18:12 | CDM GROUND STOP |
| 049 | AUS/ZHU | 11/16/26 18:10 | CDM GROUND STOP |
| 048 | DCC | 11/16/26 18:03 | ATCSCC ADVZY 048 DCC 11/16/26 FCA RQD / NAME: FCA003:NO_Q34_2_PARTIAL / CONSTRAINED AREA: ZDC / VALID: FCA ENTRY TIME FROM 161900 TO 162200 |
| 047 | DCC/ZHU | 11/16/26 17:52 | GULF ROUTE CLOSURES_RQD |
| 046 | DCC | 11/16/26 17:40 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 045 | AUS/ZHU | 11/16/26 17:27 | CDM GS CNX |
| 044 | AUS/ZHU | 11/16/26 16:44 | CDM GROUND STOP |
| 043 | DCC | 11/16/26 16:37 | OPERATIONS PLAN |
| 042 | TEB/ZNY | 11/16/26 16:35 | TEB AIRPORT ARRIVAL DELAYS |
| 041 | DCC/ZMA | 11/16/26 16:28 | OCEANIC ROUTE CLOSURES_RQD |
| 040 | DCC | 11/16/26 16:20 | ATCSCC ADVZY 040 DCC 11/16/26 FCA RQD / NAME: FCA002:LAKE_ERIE_WEST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 161130 TO 170400 |
| 039 | DCC | 11/16/26 15:59 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 038 | DCC | 11/16/26 15:58 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 037 | DCC/ZBW | 11/16/26 14:59 | NATOTS_RQD |
| 036 | DCC | 11/16/26 14:55 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 035 | SAN/ZLA | 11/16/26 14:39 | CDM GROUND DELAY PROGRAM |
| 034 | DCC | 11/16/26 14:38 | US/MEXICO OUTLOOK_FYI |
| 033 | SAN/ZLA | 11/16/26 14:33 | CDM PROPOSED GROUND DELAY PROGRAM |
| 032 | DCC | 11/16/26 14:30 | OPERATIONS PLAN |
| 031 | SFO/ZOA | 11/16/26 14:27 | CDM GROUND DELAY PROGRAM |
| 030 | DCC/ZHU | 11/16/26 14:25 | GULF ROUTE CLOSURES_RQD |
| 029 | DCC | 11/16/26 14:23 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 028 | SFO/ZOA | 11/16/26 14:22 | CDM PROPOSED GROUND DELAY PROGRAM |
| 027 | DCC | 11/16/26 13:46 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 026 | DCC | 11/16/26 12:48 | OPERATIONS PLAN |
| 025 | DCC/ZHU | 11/16/26 12:15 | GULF ROUTE CLOSURES_RQD |
| 024 | DCC | 11/16/26 12:06 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 023 | DCC/ZMA | 11/16/26 11:56 | OCEANIC ROUTE CLOSURES_RQD |
| 022 | DCC | 11/16/26 11:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 021 | DCC | 11/16/26 11:00 | ATCSCC ADVZY 021 DCC 11/16/26 FCA RQD / NAME: FCA002:LAKE_ERIE_WEST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 161130 TO 161700 |
| 020 | DCC | 11/16/26 10:20 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 019 | DCC | 11/16/26 09:56 | OPERATIONS PLAN |
| 018 | DCC | 11/16/26 09:09 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 017 | DCC | 11/16/26 08:38 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 016 | DCC | 11/16/26 08:02 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 015 | SFO/ZOA | 11/16/26 07:36 | CDM GROUND DELAY PROGRAM CNX |
| 014 | DCC | 11/16/26 05:44 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 013 | SFO/ZOA | 11/16/26 04:12 | CDM GROUND DELAY PROGRAM |
| 012 | DCC | 11/16/26 03:16 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 011 | LAS/ZLA | 11/16/26 03:04 | CDM GS CNX |
| 010 | LAS/ZLA | 11/16/26 02:50 | CDM GROUND STOP |
| 009 | DCC | 11/16/26 02:48 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 008 | DCC | 11/16/26 02:24 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 007 | FCAP93 | 11/16/26 01:40 | CDM AIRSPACE FLOW PROGRAM CNX |
| 006 | AUS/ZHU | 11/16/26 01:17 | CDM GROUND DELAY PROGRAM CNX |
| 005 | DCC | 11/16/26 00:51 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | DCC/ZDC | 11/16/26 00:32 | ZDC NRP SUSPENSION_RQD |
| 003 | SFO/ZOA | 11/16/26 00:24 | CDM GROUND DELAY PROGRAM |
| 002 | DCC | 11/16/26 00:22 | OPERATIONS PLAN |
| 001 | SFO/ZOA | 11/16/26 00:13 | CDM PROPOSED GROUND DELAY PROGRAM |

Ground-stop rows above, by number: 079, 072, 071, 063, 056, 054, 053, 050, 049, 044, 010.

**Advisories on the index, 2026-11-17** — 20 rows, fetched 03:19 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 020 | DCC | 11/17/26 08:23 | OPERATIONS PLAN |
| 019 | DCC | 11/17/26 08:08 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 018 | DCC | 11/17/26 07:53 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 017 | SFO/ZOA | 11/17/26 06:58 | CDM GROUND DELAY PROGRAM CNX |
| 016 | DCC | 11/17/26 06:53 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 015 | DCC | 11/17/26 06:45 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 014 | DCC | 11/17/26 06:15 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 013 | SAN/ZLA | 11/17/26 05:59 | CDM GROUND DELAY PROGRAM CNX |
| 012 | DCC | 11/17/26 05:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 011 | SFO/ZOA | 11/17/26 04:54 | SFO GROUND STOP CANCELLATION |
| 010 | SFO/ZOA | 11/17/26 04:51 | CDM GROUND DELAY PROGRAM |
| 009 | SFO/ZOA | 11/17/26 04:07 | CDM GROUND STOP |
| 008 | DCC | 11/17/26 02:07 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 007 | LGA/ZNY | 11/17/26 01:42 | CDM GS CNX |
| 006 | DCC | 11/17/26 01:14 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 005 | DCC | 11/17/26 00:57 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | LGA/ZNY | 11/17/26 00:35 | CDM GROUND STOP |
| 003 | SAN/ZLA | 11/17/26 00:32 | CDM GROUND DELAY PROGRAM |
| 002 | DCC | 11/17/26 00:22 | OPERATIONS PLAN |
| 001 | DCC | 11/17/26 00:12 | VOLCANIC ACTIVITY BULLETIN - SANGAY |

Ground-stop rows above, by number: 011, 009, 004.

**FlightAware totals** — fetched 03:19 CT. The tracker's own day is **2026-11-17**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Sun 15NOV26 | 2,336 (was 369 at 23:30) | 11,131 (was 6,666 at 23:30) | 2,860 (was 879 at 23:30) | 26,886 (was 21,064 at 23:30) |
| Mon 16NOV26 | 371 (was 16 at 23:30) | 6,847 (was 177 at 23:30) | 889 (was 242 at 23:30) | 21,660 (was 2,532 at 23:30) |
| Tue 17NOV26 | 32 | 283 | 299 | 4,844 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 03:19 CT. The advisory index keeps 15 days. 5 watch item(s) fell outside this pass's cap of 30. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053042 | http://web.archive.org/web/20261117053042/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261115231106 | http://web.archive.org/web/20261115231106/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261117053121 | http://web.archive.org/web/20261117053121/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261116220823 | http://web.archive.org/web/20261116220823/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261116220847 | http://web.archive.org/web/20261116220847/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261116050959 | http://web.archive.org/web/20261116050959/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11162026/79 | 20261117053128 | http://web.archive.org/web/20261117053128/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=79 |  |
| 11162026/75 | 20261116222847 | http://web.archive.org/web/20261116222847/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=75 |  |
| 11162026/72 | 20261116221929 | http://web.archive.org/web/20261116221929/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=72 |  |
| 11162026/71 | 20261116221001 | http://web.archive.org/web/20261116221001/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=71 |  |
| 11162026/63 | 20261116215904 | http://web.archive.org/web/20261116215904/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=63 |  |
| 11162026/61 | 20261116220020 | http://web.archive.org/web/20261116220020/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=61 |  |
| 11162026/56 | 20261116220117 | http://web.archive.org/web/20261116220117/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=56 |  |
| 11162026/54 | 20261116220140 | https://web.archive.org/web/20261116220140/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=54 | saved this pass |
| 11162026/53 | 20261116220243 | http://web.archive.org/web/20261116220243/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=53 |  |
| 11162026/52 | 20261116220454 | http://web.archive.org/web/20261116220454/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=52 |  |
| 11162026/50 | 20261116221017 | https://web.archive.org/web/20261116221017/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=50 | saved this pass |
| 11162026/49 | unverified |  | snapshot did not serve (URLError); save budget spent |
| 11162026/44 | unverified |  | snapshot did not serve (URLError); save budget spent |
| 11162026/43 | unverified |  | snapshot did not serve (URLError); save budget spent |
| 11162026/32 | unverified |  | snapshot did not serve (URLError); save budget spent |
| 11162026/26 | 20261116222117 | http://web.archive.org/web/20261116222117/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=26 |  |
| 11162026/19 | 20261116222218 | http://web.archive.org/web/20261116222218/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11162026&advn=19 |  |
| 11162026/10 | no capture |  | no capture; save budget spent |
| 11162026/2 | no capture |  | no capture; save budget spent |

coverage: 102 advisory rows, 3 totals tables, 35 watch items (24 verified, 2 saved this pass)

**Reading — 16NOV26** (written by hand, 17NOV26 03:20 CT; the block above was corrected in place at 03:19 CT).

- **The 23:30 pass collected the right numbers and dated them a day early.** FlightAware rolls its pages at **00:00Z**, so at 23:30 CT on the 16th the tracker was already on the 17th: its `minus2days` page was Sunday the 15th and its `yesterday` page Monday the 16th. The pass labelled both from the CT date, recording **Sunday's 2,336 US cancellations against Saturday** and Monday's 371 against Sunday, and printing the result under a heading that read as a correction of the earlier figures. The collector now converts to UTC (`tracker_day`) and dates each page from the weekday it prints (`resolve_page_day`); a page whose word disagrees with the offset is a problem, not a silent relabel.
- **What the corrected rows say.** Sunday 15NOV26 settled at **2,336** US cancellations and **11,131** US delays; Monday 16NOV26 at **371** and **6,847**; Tuesday 17NOV26 was **32** and **283** by 03:19 CT, with the day still open.
- **Saturday 14NOV26 is no longer in this block, and its settled figures are recorded here so the record keeps them.** Last read at **16:31 CT on 16NOV26**, before the block was replaced: **6,700** US cancellations, **9,188** US delays, **7,355** worldwide cancellations, **22,740** worldwide delays. The tracker's three-day window means no later pass can print that day again. **§20's ledger row for 2026-11-14 carries 6,695**, the 15NOV26 08:00 reading, because that is the last one still inside the log; the later reading of the same date is the 6,700 above.
- **The lesson is the one this file keeps teaching.** An offset from "now" is an inference; the page's own word is a measurement. The same shape of error as a reconstructed URL: correct-looking, plausible by an hour or a day, and invisible to every check that is not a fetch of the thing itself.

### 17NOV26

**Collected** 17NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-17** — 82 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 082 | SAN/ZLA | 11/17/26 23:56 | SAN AIRPORT SCHEDULING DELAYS |
| 081 | SFO/ZOA | 11/17/26 23:49 | CDM GS CNX |
| 080 | DEN/ZDV | 11/17/26 23:41 | DEN AIRPORT ARRIVAL DELAYS |
| 079 | DCC | 11/17/26 23:41 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 078 | DCC/ZMA | 11/17/26 23:26 | OCEANIC ROUTE CLOSURE_RQD |
| 077 | EWR/ZNY | 11/17/26 23:04 | EWR AIRPORT ARRIVAL DELAYS |
| 076 | TEB/ZNY | 11/17/26 23:01 | CDM GS CNX |
| 075 | EWR/ZNY | 11/17/26 22:59 | EWR AIRPORT ARRIVAL DELAYS |
| 074 | ZMA/DCC | 11/17/26 22:55 | SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| 073 | TEB/ZNY | 11/17/26 22:44 | CDM GROUND STOP |
| 072 | SFO/ZOA | 11/17/26 22:40 | CDM GROUND STOP |
| 071 | SFO/ZOA | 11/17/26 22:00 | SFO AIRPORT SCHEDULING DELAYS |
| 070 | ZMA/DCC | 11/17/26 21:26 | SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| 069 | FCAP93 | 11/17/26 21:12 | CDM AIRSPACE FLOW PROGRAM CNX |
| 068 | DCC | 11/17/26 20:45 | OCEANIC ROUTE CLOSURE_RQD |
| 067 | DCC | 11/17/26 20:37 | OPERATIONS PLAN |
| 066 | DCC | 11/17/26 20:13 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 065 | DCC/ZHU | 11/17/26 20:01 | GULF ROUTE CLOSURES_RQD |
| 064 | FCAP93 | 11/17/26 19:45 | CDM AIRSPACE FLOW PROGRAM |
| 063 | DCC | 11/17/26 19:44 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 062 | DCC | 11/17/26 19:11 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 061 | TEB/ZNY | 11/17/26 18:59 | CDM GROUND STOP |
| 060 | PHX/ZAB | 11/17/26 18:54 | CDM GS CNX |
| 059 | DCC/ZMA | 11/17/26 18:48 | OCEANIC ROUTE CLOSURE_RQD |
| 058 | DCC | 11/17/26 18:40 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 057 | DCC | 11/17/26 18:29 | OPERATIONS PLAN |
| 056 | PHX/ZAB | 11/17/26 18:23 | CDM GROUND STOP |
| 055 | DCC | 11/17/26 18:10 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 054 | DCC | 11/17/26 17:43 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 053 | TEB/ZNY | 11/17/26 17:28 | TEB AIRPORT ARRIVAL DELAYS |
| 052 | PHX/ZAB | 11/17/26 17:07 | CDM GROUND DELAY PROGRAM CNX |
| 051 | DCC | 11/17/26 16:47 | GULF ROUTE CLOSURES_RQD |
| 050 | DCC | 11/17/26 16:32 | OPERATIONS PLAN |
| 049 | DCC/ZHU | 11/17/26 15:21 | GULF ROUTE CLOSURES_RQD |
| 048 | DCC | 11/17/26 15:09 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 047 | DCC | 11/17/26 14:54 | REROUTE CANCELLATION |
| 046 | DCC | 11/17/26 14:54 | REROUTE CANCELLATION |
| 045 | DCC/ZMA | 11/17/26 14:44 | OCEANIC ROUTE CLOSURE_RQD |
| 044 | DCA/ZDC | 11/17/26 14:44 | DCA AIRPORT ARRIVAL DELAYS |
| 043 | DCC | 11/17/26 14:39 | US/MEXICO OUTLOOK_FYI |
| 042 | DCC/ZBW | 11/17/26 14:37 | NATOTS_RQD |
| 041 | DCC | 11/17/26 14:35 | OPERATIONS PLAN |
| 040 | PHX/ZAB | 11/17/26 14:22 | CDM GROUND DELAY PROGRAM |
| 039 | SAN/ZLA | 11/17/26 14:20 | SAN AIRPORT ARRIVAL & DEPARTURE DELAYS |
| 038 | PHX/ZAB | 11/17/26 14:15 | CDM PROPOSED GROUND DELAY PROGRAM |
| 037 | DCC | 11/17/26 14:12 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 036 | DCC | 11/17/26 13:48 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 035 | DCC | 11/17/26 13:32 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 034 | DCC/ZHU | 11/17/26 13:26 | GULF ROUTE CLOSURES_RQD |
| 033 | DCC | 11/17/26 13:07 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 032 | PHX/ZAB | 11/17/26 13:01 | PHX AIRPORT SCHEDULING DELAYS |
| 031 | DCC | 11/17/26 12:49 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 030 | DCC | 11/17/26 12:35 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 029 | DCC | 11/17/26 12:29 | OPERATIONS PLAN |
| 028 | DCC | 11/17/26 12:23 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 027 | DCC/ZHU | 11/17/26 12:22 | GULF ROUTE CLOSURES_RQD |
| 026 | DCC | 11/17/26 11:54 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 025 | DCC | 11/17/26 10:59 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 024 | DCC | 11/17/26 10:59 | ATCSCC ADVZY 024 DCC 11/17/26 FCA RQD / NAME: FCA003:LAKE_ERIE_WEST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 171100 TO 171900 |
| 023 | DCC | 11/17/26 10:55 | ATCSCC ADVZY 023 DCC 11/17/26 FCA RQD / NAME: FCA002:LAKE_ERIE_EAST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 171100 TO 171900 |
| 022 | DCC/ZMA | 11/17/26 10:49 | OCEANIC ROUTE CLOSURE_RQD |
| 021 | DCC | 11/17/26 09:57 | ZDC NRP SUSPENSION_RQD |
| 020 | DCC | 11/17/26 08:23 | OPERATIONS PLAN |
| 019 | DCC | 11/17/26 08:08 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 018 | DCC | 11/17/26 07:53 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 017 | SFO/ZOA | 11/17/26 06:58 | CDM GROUND DELAY PROGRAM CNX |
| 016 | DCC | 11/17/26 06:53 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 015 | DCC | 11/17/26 06:45 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 014 | DCC | 11/17/26 06:15 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 013 | SAN/ZLA | 11/17/26 05:59 | CDM GROUND DELAY PROGRAM CNX |
| 012 | DCC | 11/17/26 05:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 011 | SFO/ZOA | 11/17/26 04:54 | SFO GROUND STOP CANCELLATION |
| 010 | SFO/ZOA | 11/17/26 04:51 | CDM GROUND DELAY PROGRAM |
| 009 | SFO/ZOA | 11/17/26 04:07 | CDM GROUND STOP |
| 008 | DCC | 11/17/26 02:07 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 007 | LGA/ZNY | 11/17/26 01:42 | CDM GS CNX |
| 006 | DCC | 11/17/26 01:14 | VOLCANIC ACTIVITY BULLETIN - KATMAI |
| 005 | DCC | 11/17/26 00:57 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | LGA/ZNY | 11/17/26 00:35 | CDM GROUND STOP |
| 003 | SAN/ZLA | 11/17/26 00:32 | CDM GROUND DELAY PROGRAM |
| 002 | DCC | 11/17/26 00:22 | OPERATIONS PLAN |
| 001 | DCC | 11/17/26 00:12 | VOLCANIC ACTIVITY BULLETIN - SANGAY |

Ground-stop rows above, by number: 073, 072, 061, 056, 011, 009, 004.

**Advisories on the index, 2026-11-18** — 8 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 008 | DCC | 11/18/26 02:03 | VOLCANIC ACTIVITY BULLETIN - TEST |
| 007 | DCC | 11/18/26 01:58 | VOLCANIC ACTIVITY BULLETIN - TEST |
| 006 | DCC | 11/18/26 01:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 005 | DCC | 11/18/26 01:11 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 004 | DCC | 11/18/26 00:41 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 003 | DCC | 11/18/26 00:25 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 002 | DCC | 11/18/26 00:25 | OPERATIONS PLAN |
| 001 | DCC | 11/18/26 00:11 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |

No row on this day's index is a ground-stop advisory.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-18**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Mon 16NOV26 | 375 (was 373 at 08:00) | 7,218 (was 7,057 at 08:00) | 896 (was 894 at 08:00) | 22,198 (was 22,039 at 08:00) |
| Tue 17NOV26 | 102 (was 46 at 08:00) | 3,136 (was 618 at 08:00) | 647 (was 428 at 08:00) | 15,330 (was 8,208 at 08:00) |
| Wed 18NOV26 | 23 | 122 | 281 | 3,041 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261117053121 | http://web.archive.org/web/20261117053121/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261117093830 | http://web.archive.org/web/20261117093830/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261116220847 | http://web.archive.org/web/20261116220847/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261118015518 | http://web.archive.org/web/20261118015518/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11172026/73 | no capture |  | no capture; save failed (HTTPError) |
| 11172026/72 | no capture |  | no capture; save failed (TimeoutError) |
| 11172026/67 | no capture |  | no capture; save budget spent |
| 11172026/61 | no capture |  | no capture; save budget spent |
| 11172026/57 | no capture |  | no capture; save budget spent |
| 11172026/56 | no capture |  | no capture; save budget spent |
| 11172026/50 | no capture |  | no capture; save budget spent |
| 11172026/41 | no capture |  | no capture; save budget spent |
| 11172026/29 | 20261117140226 | http://web.archive.org/web/20261117140226/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11172026&advn=29 |  |
| 11172026/20 | 20261117140355 | http://web.archive.org/web/20261117140355/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11172026&advn=20 |  |
| 11172026/11 | no capture |  | snapshot does not carry the wording; save budget spent |
| 11172026/9 | no capture |  | no capture; save budget spent |
| 11172026/4 | no capture |  | no capture; save budget spent |
| 11172026/2 | no capture |  | no capture; save budget spent |
| 11182026/2 | no capture |  | no capture; save budget spent |

coverage: 90 advisory rows, 3 totals tables, 27 watch items (14 verified, 0 saved this pass)

### 18NOV26

**Collected** 18NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-18** — 78 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 078 | DCC | 11/18/26 23:59 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 077 | DCC | 11/18/26 23:30 | SOUTH FLORIDA HOTLINE DEACTIVATED |
| 076 | SFO/ZOA | 11/18/26 23:06 | SFO AIRPORT ARRIVAL DELAYS |
| 075 | DCC | 11/18/26 22:57 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 074 | SAN/ZLA | 11/18/26 22:28 | SAN AIRPORT SCHEDULING DELAYS |
| 073 | DCC | 11/18/26 22:26 | OPERATIONS PLAN |
| 072 | DCC | 11/18/26 22:11 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 071 | TEB/ZNY | 11/18/26 21:51 | CDM GS CNX |
| 070 | TEB/ZNY | 11/18/26 21:12 | CDM GROUND STOP |
| 069 | DCC | 11/18/26 20:26 | OPERATIONS PLAN |
| 068 | DJT/ZMA | 11/18/26 20:12 | CDM GS CNX |
| 067 | TEB/ZNY | 11/18/26 20:02 | CDM GROUND STOP |
| 066 | SFO/ZOA | 11/18/26 19:46 | CDM GROUND DELAY PROGRAM |
| 065 | SFO/ZOA | 11/18/26 19:29 | CDM PROPOSED GROUND DELAY PROGRAM |
| 064 | DJT/ZMA | 11/18/26 19:04 | CDM GROUND STOP |
| 063 | DCC | 11/18/26 18:57 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 062 | DCC | 11/18/26 18:33 | OPERATIONS PLAN |
| 061 | DCC | 11/18/26 18:28 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 060 | SFO/ZOA | 11/18/26 18:27 | CDM GROUND STOP |
| 059 | SFO/ZOA | 11/18/26 18:19 | SFO AIRPORT DIVERSION RECOVERY ACTIVATED |
| 058 | TEB/ZNY | 11/18/26 18:18 | TEB AIRPORT ARRIVAL DELAYS |
| 057 | SFO/ZOA | 11/18/26 18:18 | SFO AIRPORT ARRIVAL DELAYS |
| 056 | DCC/ZHU | 11/18/26 18:07 | GULF ROUTE CLOSURE_RQD |
| 055 | DCC | 11/18/26 17:55 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 054 | DCC | 11/18/26 17:52 | SOUTH FLORIDA HOTLINE_FYI |
| 053 | DCC | 11/18/26 17:48 | OCEANIC ROUTE CLOSURE_RQD |
| 052 | ZMA/DCC | 11/18/26 17:47 | SOUTH FLORIDA AIRPORTS DIVERSION RECOVERY ACTIVATED |
| 051 | SFO/ZOA | 11/18/26 17:34 | CDM GROUND STOP |
| 050 | DCC | 11/18/26 17:05 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 049 | DCC | 11/18/26 16:35 | OPERATIONS PLAN |
| 048 | DCC | 11/18/26 16:15 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 047 | SFO/ZOA | 11/18/26 16:10 | CDM GROUND DELAY PROGRAM |
| 046 | SFO/ZOA | 11/18/26 16:01 | CDM PROPOSED GROUND DELAY PROGRAM |
| 045 | SEA/ZSE | 11/18/26 15:46 | SEA AIRPORT SCHEDULING DELAYS |
| 044 | DCC/ZMA | 11/18/26 15:24 | GULF ROUTE CLOSURE_RQD |
| 043 | DCC | 11/18/26 15:14 | OCEANIC ROUTE CLOSURE_RQD |
| 042 | DCC | 11/18/26 15:08 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 041 | MIA/ZMA | 11/18/26 15:08 | CDM GS CNX |
| 040 | DCC | 11/18/26 15:02 | OCEANIC ROUTE CLOSURE_RQD |
| 039 | DCC/ZBW | 11/18/26 14:52 | NATOTS_RQD |
| 038 | DCC | 11/18/26 14:37 | US/MEXICO OUTLOOK_FYI |
| 037 | DCC | 11/18/26 14:36 | OPERATIONS PLAN |
| 036 | FLL/ZMA | 11/18/26 14:32 | CDM GS CNX |
| 035 | SAN/ZLA | 11/18/26 14:21 | SAN AIRPORT SCHEDULING DELAYS |
| 034 | DCC/ZBW | 11/18/26 14:20 | NATOTS_RQD |
| 033 | DCC | 11/18/26 14:17 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 032 | MIA/ZMA | 11/18/26 14:13 | CDM GROUND STOP |
| 031 | FLL/ZMA | 11/18/26 13:30 | CDM GROUND STOP |
| 030 | SFO/ZOA | 11/18/26 13:27 | CDM GROUND DELAY PROGRAM |
| 029 | DCC | 11/18/26 13:26 | REROUTE CANCELLATION |
| 028 | SFO/ZOA | 11/18/26 13:19 | CDM PROPOSED GROUND DELAY PROGRAM |
| 027 | PHX/ZAB | 11/18/26 12:56 | PHX AIRPORT SCHEDULING DELAYS |
| 026 | DCC | 11/18/26 12:56 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 025 | PHX/ZAB | 11/18/26 12:55 | PHX AIRPORT ARRIVAL DELAYS |
| 024 | SFO/ZOA | 11/18/26 12:54 | SFO AIRPORT ARRIVAL DELAYS |
| 023 | DCC | 11/18/26 12:48 | OPERATIONS PLAN |
| 022 | DCC | 11/18/26 12:27 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 021 | DCC/ZMA | 11/18/26 12:05 | ZMA CDRS_FYI |
| 020 | DCC | 11/18/26 12:03 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 019 | DCC | 11/18/26 12:03 | ZMA SWAP_FYI |
| 018 | DCC | 11/18/26 11:50 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 017 | DCC | 11/18/26 11:49 | OCEANIC ROUTE CLOSURE_RQD |
| 016 | DCC | 11/18/26 11:13 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 015 | ZMA/DCC | 11/18/26 11:10 | SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| 014 | DCC | 11/18/26 09:55 | OPERATIONS PLAN |
| 013 | DCC | 11/18/26 07:33 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 012 | DCC | 11/18/26 07:05 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 011 | DCC | 11/18/26 06:42 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 010 | DCC | 11/18/26 06:00 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 009 | DCC | 11/18/26 05:39 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 008 | DCC | 11/18/26 02:03 | VOLCANIC ACTIVITY BULLETIN - TEST |
| 007 | DCC | 11/18/26 01:58 | VOLCANIC ACTIVITY BULLETIN - TEST |
| 006 | DCC | 11/18/26 01:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 005 | DCC | 11/18/26 01:11 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 004 | DCC | 11/18/26 00:41 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 003 | DCC | 11/18/26 00:25 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 002 | DCC | 11/18/26 00:25 | OPERATIONS PLAN |
| 001 | DCC | 11/18/26 00:11 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |

Ground-stop rows above, by number: 070, 067, 064, 060, 051, 032, 031.

**Advisories on the index, 2026-11-19** — 8 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 008 | DCC | 11/19/26 04:15 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 007 | DCC/ZDC | 11/19/26 02:09 | ZDC NRP SUSPENSION_RQD |
| 006 | DCC | 11/19/26 01:34 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 005 | DCC | 11/19/26 01:03 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | DCC | 11/19/26 00:55 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 003 | DCC | 11/19/26 00:26 | OPERATIONS PLAN |
| 002 | DCC | 11/19/26 00:26 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 001 | DCC | 11/19/26 00:12 | VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |

No row on this day's index is a ground-stop advisory.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-19**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Tue 17NOV26 | 105 (was 106 at 08:00) | 3,728 (was 3,464 at 08:00) | 659 (was 660 at 08:00) | 16,419 (was 16,160 at 08:00) |
| Wed 18NOV26 | 133 (was 41 at 08:00) | 4,162 (was 579 at 08:00) | 711 (was 431 at 08:00) | 19,171 (was 9,813 at 08:00) |
| Thu 19NOV26 | 33 | 191 | 285 | 3,711 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | https://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | saved this pass |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261117093830 | http://web.archive.org/web/20261117093830/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261116220847 | http://web.archive.org/web/20261116220847/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261119053038 | https://web.archive.org/web/20261119053038/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | saved this pass |
| faa-qa | 20261119023710 | http://web.archive.org/web/20261119023710/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11182026/73 | no capture |  | no capture; save failed (TimeoutError) |
| 11182026/70 | 20261119053124 | https://web.archive.org/web/20261119053124/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11182026&advn=70 | saved this pass |
| 11182026/69 | no capture |  | no capture; save budget spent |
| 11182026/67 | no capture |  | no capture; save budget spent |
| 11182026/64 | no capture |  | no capture; save budget spent |
| 11182026/62 | no capture |  | no capture; save budget spent |
| 11182026/60 | no capture |  | no capture; save budget spent |
| 11182026/51 | no capture |  | no capture; save budget spent |
| 11182026/49 | no capture |  | no capture; save budget spent |
| 11182026/37 | no capture |  | no capture; save budget spent |
| 11182026/32 | no capture |  | no capture; save budget spent |
| 11182026/31 | 20261118140217 | http://web.archive.org/web/20261118140217/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11182026&advn=31 |  |
| 11182026/23 | 20261118140337 | http://web.archive.org/web/20261118140337/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11182026&advn=23 |  |
| 11182026/14 | no capture |  | no capture; save budget spent |
| 11182026/2 | no capture |  | no capture; save budget spent |
| 11192026/3 | no capture |  | no capture; save budget spent |

coverage: 86 advisory rows, 3 totals tables, 29 watch items (16 verified, 3 saved this pass)

### 19NOV26

**Collected** 19NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-19** — 74 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 074 | SAN/ZLA | 11/19/26 23:56 | CDM GROUND STOP |
| 073 | SAN/ZLA | 11/19/26 23:53 | SAN AIRPORT DIVERSION RECOVERY ACTIVATED |
| 072 | DCC | 11/19/26 23:38 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 071 | DCC/ZMA | 11/19/26 23:30 | OCEANIC ROUTE CLOSURE_RQD |
| 070 | DCC | 11/19/26 23:21 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 069 | DCC | 11/19/26 22:22 | OPERATIONS PLAN |
| 068 | SFO/ZOA | 11/19/26 21:44 | CDM GROUND DELAY PROGRAM |
| 067 | DCC | 11/19/26 21:14 | REROUTE CANCELLATION |
| 066 | AUS/ZHU | 11/19/26 20:50 | CDM GS CNX |
| 065 | AUS/ZHU | 11/19/26 20:31 | CDM GROUND STOP |
| 064 | DCC | 11/19/26 20:25 | OPERATIONS PLAN |
| 063 | SAT/ZHU | 11/19/26 20:10 | SAT AIRPORT ARRIVAL DELAYS |
| 062 | DCC | 11/19/26 19:29 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 061 | DCC | 11/19/26 19:06 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 060 | LAS/ZLA | 11/19/26 18:50 | LAS AIRPORT ARRIVAL DELAYS |
| 059 | DCC | 11/19/26 18:38 | OPERATIONS PLAN |
| 058 | AUS/ZHU | 11/19/26 18:37 | CDM GROUND DELAY PROGRAM CNX |
| 057 | DCC | 11/19/26 18:37 | ATCSCC ADVZY 057 DCC 11/19/26 FCA RQD / NAME: FCA005:MIDWEST_TO_FLORIDA_PARTIAL / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 191900 TO 200000 |
| 056 | DCC | 11/19/26 18:36 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 055 | PHLC/ZNY | 11/19/26 18:34 | EWR AND SATELLITE AIRPORTS ARRIVAL DELAYS |
| 054 | LAS/ZLA | 11/19/26 18:13 | CDM GROUND DELAY PROGRAM |
| 053 | DCC | 11/19/26 17:50 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 052 | AUS/ZHU | 11/19/26 17:18 | AUS AIRPORT ARRIVAL DELAYS |
| 051 | DCC | 11/19/26 17:04 | OCEANIC ROUTE CLOSURE_RQD |
| 050 | AUS/ZHU | 11/19/26 16:48 | CDM GROUND DELAY PROGRAM |
| 049 | DCC | 11/19/26 16:41 | OPERATIONS PLAN |
| 048 | DCC | 11/19/26 16:28 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 047 | AUS/ZHU | 11/19/26 16:27 | CDM PROPOSED GROUND DELAY PROGRAM |
| 046 | AUS/ZHU | 11/19/26 16:04 | CDM GROUND STOP |
| 045 | DCC | 11/19/26 15:49 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 044 | DCC | 11/19/26 15:46 | ATCSCC ADVZY 044 DCC 11/19/26 ROUTE RQD /FL / NAME: MIDWEST_TO_FLORIDA_PARTIAL / CONSTRAINED AREA: ZJX ZMA / VALID: ETD 191200 TO 191800 |
| 043 | DEN/ZDV | 11/19/26 15:42 | DEN AIRPORT ARRIVAL DELAYS |
| 042 | AUS/ZHU | 11/19/26 15:17 | CDM GS CNX |
| 041 | DCC/ZMA | 11/19/26 15:03 | OCEANIC ROUTE CLOSURE_RQD |
| 040 | DCC | 11/19/26 14:45 | US/MEXICO OUTLOOK_FYI |
| 039 | AUS/ZHU | 11/19/26 14:39 | AUS AIRPORT DIVERSION RECOVERY ACTIVATED |
| 038 | AUS/ZHU | 11/19/26 14:34 | CDM GROUND STOP |
| 037 | DCC | 11/19/26 14:29 | OPERATIONS PLAN |
| 036 | DCC/ZBW | 11/19/26 14:25 | NATOTS_RQD |
| 035 | AUS/ZHU | 11/19/26 14:09 | CDM GROUND STOP |
| 034 | SAN/ZLA | 11/19/26 13:54 | SAN AIRPORT ARRIVAL DELAYS |
| 033 | SAN/ZLA | 11/19/26 13:54 | SAN AIRPORT SCHEDULING DELAYS |
| 032 | LAX/ZLA | 11/19/26 13:53 | LAX AIRPORT SCHEDULING DELAYS |
| 031 | LAX/ZLA | 11/19/26 13:52 | LAX AIRPORT ARRIVAL DELAYS |
| 030 | SFO/ZOA | 11/19/26 13:42 | CDM GROUND DELAY PROGRAM |
| 029 | SFO/ZOA | 11/19/26 13:35 | CDM PROPOSED GROUND DELAY PROGRAM |
| 028 | DCC | 11/19/26 13:24 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 027 | FLL/ZMA | 11/19/26 12:59 | FLL AIRPORT ARRIVAL DELAYS |
| 026 | MIA/ZMA | 11/19/26 12:58 | MIA AIRPORT ARRIVAL DELAYS |
| 025 | AUS/ZHU | 11/19/26 12:58 | AUS AIRPORT BELOW USER MINS |
| 024 | DCC | 11/19/26 12:53 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 023 | DCC | 11/19/26 12:38 | OPERATIONS PLAN |
| 022 | DCC | 11/19/26 12:18 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 021 | DCC | 11/19/26 12:14 | ATCSCC ADVZY 021 DCC 11/19/26 ROUTE RQD /FL / NAME: MIDWEST_TO_FLORIDA_PARTIAL / CONSTRAINED AREA: ZJX ZMA / VALID: ETD 191200 TO 191600 |
| 020 | DCC | 11/19/26 12:09 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 019 | DCC | 11/19/26 11:45 | ATCSCC ADVZY 019 DCC 11/19/26 ROUTE RQD /FL / NAME: TEXAS_ZME_TO_ZNY / CONSTRAINED AREA: EAST COAST / VALID: ETD 191230 TO 191630 |
| 018 | DCC | 11/19/26 11:32 | ATCSCC ADVZY 018 DCC 11/19/26 ROUTE RQD /FL / NAME: MIDWEST_TO_FLORIDA_PARTIAL / CONSTRAINED AREA: ZJX ZMA / VALID: ETD 191200 TO 191600 |
| 017 | DCC | 11/19/26 11:23 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 016 | DCC | 11/19/26 10:35 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 015 | DCC | 11/19/26 10:11 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 014 | DCC | 11/19/26 09:55 | OPERATIONS PLAN |
| 013 | DCC | 11/19/26 09:21 | VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| 012 | DCC | 11/19/26 07:36 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 011 | DCC | 11/19/26 07:00 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 010 | DCC | 11/19/26 06:44 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 009 | SFO/ZOA | 11/19/26 05:59 | CDM GROUND DELAY PROGRAM CNX |
| 008 | DCC | 11/19/26 04:15 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 007 | DCC/ZDC | 11/19/26 02:09 | ZDC NRP SUSPENSION_RQD |
| 006 | DCC | 11/19/26 01:34 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 005 | DCC | 11/19/26 01:03 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | DCC | 11/19/26 00:55 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 003 | DCC | 11/19/26 00:26 | OPERATIONS PLAN |
| 002 | DCC | 11/19/26 00:26 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 001 | DCC | 11/19/26 00:12 | VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |

Ground-stop rows above, by number: 074, 065, 046, 038, 035.

**Advisories on the index, 2026-11-20** — 21 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 021 | DCC | 11/20/26 05:14 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 020 | SAN/ZLA | 11/20/26 04:48 | CDM GROUND DELAY PROGRAM CNX |
| 019 | LAS/ZLA | 11/20/26 04:19 | CDM GROUND DELAY PROGRAM CNX |
| 018 | LAS/ZLA | 11/20/26 03:39 | CDM GROUND STOP |
| 017 | DCC | 11/20/26 03:00 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 016 | SFO/ZOA | 11/20/26 02:49 | CDM GROUND DELAY PROGRAM |
| 015 | SFO/ZOA | 11/20/26 02:31 | CDM PROPOSED GROUND DELAY PROGRAM |
| 014 | SFO/ZOA | 11/20/26 02:26 | SFO AIRPORT ARRIVAL DELAYS |
| 013 | DCC | 11/20/26 01:11 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 012 | LAS/ZLA | 11/20/26 00:50 | LAS AIRPORT SCHEDULING DELAYS |
| 011 | SAN/ZLA | 11/20/26 00:46 | CDM GROUND DELAY PROGRAM |
| 010 | DCC | 11/20/26 00:45 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 009 | DCC | 11/20/26 00:41 | ATCSCC ADVZY 009 DCC 11/20/26 FCA RQD / NAME: FCA008:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 008 | DCC | 11/20/26 00:40 | ATCSCC ADVZY 008 DCC 11/20/26 FCA RQD / NAME: FCA007:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 007 | DCC | 11/20/26 00:40 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 006 | DCC | 11/20/26 00:40 | ATCSCC ADVZY 006 DCC 11/20/26 FCA RQD / NAME: FCA009:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 005 | DCC | 11/20/26 00:32 | OPERATIONS PLAN |
| 004 | SAN/ZLA | 11/20/26 00:29 | CDM PROPOSED GROUND DELAY PROGRAM |
| 003 | DCC | 11/20/26 00:22 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 002 | SAN/ZLA | 11/20/26 00:02 | SAN AIRPORT ARRIVAL DELAYS |
| 001 | DCC/ZDC | 11/20/26 00:01 | ZDC NRP SUSPENSION_RQD |

Ground-stop rows above, by number: 018.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-20**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Wed 18NOV26 | 142 (was 140 at 08:00) | 4,754 (was 4,487 at 08:00) | 737 (was 734 at 08:00) | 20,430 (was 20,160 at 08:00) |
| Thu 19NOV26 | 124 (was 55 at 08:00) | 5,286 (was 707 at 08:00) | 707 (was 422 at 08:00) | 21,926 (was 10,927 at 08:00) |
| Fri 20NOV26 | 32 | 158 | 260 | 5,091 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | no capture |  | no capture; save failed (TimeoutError) |
| index 2026-11-16 | 20261116220847 | http://web.archive.org/web/20261116220847/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261119053038 | http://web.archive.org/web/20261119053038/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-19 | 20261119140035 | http://web.archive.org/web/20261119140035/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261119184515 | http://web.archive.org/web/20261119184515/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11192026/74 | 20261120053102 | https://web.archive.org/web/20261120053102/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11192026&advn=74 | saved this pass |
| 11192026/69 | 20261120053122 | https://web.archive.org/web/20261120053122/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11192026&advn=69 | saved this pass |
| 11192026/65 | no capture |  | no capture; save budget spent |
| 11192026/64 | no capture |  | no capture; save budget spent |
| 11192026/59 | no capture |  | no capture; save budget spent |
| 11192026/49 | no capture |  | no capture; save budget spent |
| 11192026/46 | no capture |  | no capture; save budget spent |
| 11192026/38 | no capture |  | no capture; save budget spent |
| 11192026/37 | no capture |  | no capture; save budget spent |
| 11192026/35 | no capture |  | no capture; save budget spent |
| 11192026/23 | 20261119140055 | http://web.archive.org/web/20261119140055/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11192026&advn=23 |  |
| 11192026/14 | 20261119140114 | http://web.archive.org/web/20261119140114/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11192026&advn=14 |  |
| 11192026/3 | no capture |  | no capture; save budget spent |
| 11202026/18 | no capture |  | no capture; save budget spent |
| 11202026/5 | no capture |  | no capture; save budget spent |

coverage: 95 advisory rows, 3 totals tables, 29 watch items (17 verified, 2 saved this pass)

### 20NOV26

**Collected** 20NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-20** — 105 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 105 | ORD/ZAU | 11/20/26 23:52 | CDM PROPOSED GROUND DELAY PROGRAM |
| 104 | DCC/ZNY | 11/20/26 23:50 | OCEANIC ROUTE CLOSURE_RQD |
| 103 | DCC | 11/20/26 23:42 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 102 | DCC | 11/20/26 23:18 | GULF ROUTES OPEN_FYI |
| 101 | DCC | 11/20/26 22:56 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 100 | DCC | 11/20/26 22:43 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 099 | DCC | 11/20/26 22:29 | OPERATIONS PLAN |
| 098 | TEB/ZNY | 11/20/26 21:59 | CDM GS CNX |
| 097 | TEB/ZNY | 11/20/26 21:39 | CDM GROUND STOP |
| 096 | TEB/ZNY | 11/20/26 21:31 | CDM GROUND STOP |
| 095 | DCC | 11/20/26 20:58 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 094 | BFI/ZSE | 11/20/26 20:58 | CDM GS CNX |
| 093 | SFO/ZOA | 11/20/26 20:43 | SFO AIRPORT ARRIVAL DELAYS |
| 092 | DCC/ZNY/ZMA | 11/20/26 20:42 | OCEANIC ROUTE CLOSURE_RQD |
| 091 | DCC | 11/20/26 20:37 | OPERATIONS PLAN |
| 090 | TEB/ZNY | 11/20/26 20:31 | CDM GROUND STOP |
| 089 | AUS/ZHU | 11/20/26 20:26 | CDM GS CNX |
| 088 | DCC/ZNY/ZMA | 11/20/26 20:17 | OCEANIC ROUTE CLOSURE_RQD |
| 087 | BFI/ZSE | 11/20/26 19:51 | CDM GROUND STOP |
| 086 | AUS/ZHU | 11/20/26 19:35 | CDM GROUND STOP |
| 085 | DCC | 11/20/26 19:28 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 084 | BFI/ZSE | 11/20/26 19:17 | CDM GROUND STOP |
| 083 | DCC | 11/20/26 19:09 | OPERATIONS PLAN |
| 082 | DCC | 11/20/26 18:31 | ATCSCC ADVZY 082 DCC 11/20/26 ROUTE RMD / NAME: FLORIDA_TO_OHIO_VALLEY_2_PARTIAL / CONSTRAINED AREA: ZMA ZJX / VALID: ETD 201600 TO 202100 |
| 081 | DCC | 11/20/26 18:15 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 080 | FCAPV1 | 11/20/26 18:11 | CDM AIRSPACE FLOW PROGRAM CNX |
| 079 | DCC/ZMA | 11/20/26 18:01 | OCEANIC ROUTE CLOSURE_RQD |
| 078 | DCC | 11/20/26 17:49 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 077 | EWR/ZNY | 11/20/26 17:47 | EWR AND SATS AIRPORT ARRIVAL DELAYS |
| 076 | DCC/ZHU | 11/20/26 17:26 | GULF ROUTE CLOSURE_RQD |
| 075 | DCC | 11/20/26 17:00 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 074 | DCC | 11/20/26 16:55 | REROUTE CANCELLATION |
| 073 | TEB/ZNY | 11/20/26 16:46 | CDM GS CNX |
| 072 | DCC | 11/20/26 16:46 | OPERATIONS PLAN |
| 071 | DCC | 11/20/26 16:44 | ATCSCC ADVZY 071 DCC 11/20/26 FCA RQD / NAME: FCALEW:LAKE_ERIE_WEST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 201900 TO 210400 |
| 070 | DCC | 11/20/26 16:43 | ATCSCC ADVZY 070 DCC 11/20/26 FCA RQD / NAME: FCALEE:LAKE_ERIE_EAST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 201900 TO 210400 |
| 069 | DCC | 11/20/26 16:38 | ATCSCC ADVZY 069 DCC 11/20/26 ROUTE RQD /FL / NAME: TPA_AREA_ESCAPE_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 201630 TO 201900 |
| 068 | DCC | 11/20/26 16:35 | ATCSCC ADVZY 068 DCC 11/20/26 FCA RQD / NAME: FCA001:MIDWEST_TO_FLORIDA_MODIFIED / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 201400 TO 202000 |
| 067 | AUS/ZHU | 11/20/26 16:25 | AUS AIRPORT ARRIVAL DELAYS |
| 066 | MCO/ZJX | 11/20/26 16:21 | MCO AIRPORT ARRIVAL DELAYS |
| 065 | TEB/ZNY | 11/20/26 16:21 | CDM GROUND STOP |
| 064 | DCC | 11/20/26 16:16 | ATCSCC ADVZY 064 DCC 11/20/26 ROUTE RMD /FL / NAME: TPA_AREA_ESCAPE_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 201630 TO 201900 |
| 063 | DCC | 11/20/26 15:55 | ATCSCC ADVZY 063 DCC 11/20/26 FCA RQD / NAME: FCA001:MIDWEST_TO_FLORIDA_MODIFIED / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 201400 TO 202000 |
| 062 | DCC | 11/20/26 15:51 | ATCSCC ADVZY 062 DCC 11/20/26 ROUTE RMD / NAME: FLORIDA_TO_OHIO_VALLEY_2_PARTIAL / CONSTRAINED AREA: ZMA ZJX / VALID: ETD 201600 TO 201900 |
| 061 | DCC | 11/20/26 15:38 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 060 | DCC/ZJX | 11/20/26 15:32 | ZJX CAPPING/TUNNELING |
| 059 | SAN/ZLA | 11/20/26 15:01 | CDM GROUND DELAY PROGRAM |
| 058 | DCC | 11/20/26 14:59 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 057 | SAN/ZLA | 11/20/26 14:50 | CDM PROPOSED GROUND DELAY PROGRAM |
| 056 | DCC | 11/20/26 14:44 | OPERATIONS PLAN |
| 055 | DCC | 11/20/26 14:36 | US/MEXICO OUTLOOK_FYI |
| 054 | FCAPV1 | 11/20/26 14:30 | CDM AIRSPACE FLOW PROGRAM |
| 053 | SAN/ZLA | 11/20/26 14:29 | SAN AIRPORT ARRIVAL DELAYS |
| 052 | SAN/ZLA | 11/20/26 14:27 | SAN AIRPORT SCHEDULING DELAYS |
| 051 | FCAPV1 | 11/20/26 14:19 | CDM PROPOSED AIRSPACE FLOW PROGRAM |
| 050 | SFO/ZOA | 11/20/26 14:16 | SFO AIRPORT SCHEDULING DELAYS |
| 049 | SFO/ZOA | 11/20/26 14:16 | SFO AIRPORT ARRIVAL DELAYS |
| 048 | DCC/ZBW | 11/20/26 14:12 | NATOTS _RQD |
| 047 | DCC/ZMA | 11/20/26 14:10 | OCEANIC ROUTE CLOSURE_RQD |
| 046 | DCC/ZHU | 11/20/26 13:56 | GULF ROUTE CLOSURE_RQD |
| 045 | DCC | 11/20/26 13:38 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 044 | DCC | 11/20/26 13:28 | ATCSCC ADVZY 044 DCC 11/20/26 ROUTE RQD /FL / NAME: MCO_NO_GTOUT_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 201345 TO 201800 |
| 043 | DCC | 11/20/26 13:25 | CARIBBEAN OUTLOOK_FYI |
| 042 | DCC | 11/20/26 12:59 | OPERATIONS PLAN |
| 041 | DCC | 11/20/26 12:52 | ATCSCC ADVZY 041 DCC 11/20/26 FCA RQD / NAME: FCA005:HITMN_PARTIAL / CONSTRAINED AREA: ZDC/ZTL / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 040 | DCC/ZHU | 11/20/26 12:42 | GULF ROUTE CLOSURE_RQD |
| 039 | DCC | 11/20/26 12:35 | ATCSCC ADVZY 039 DCC 11/20/26 FCA RQD / NAME: FCA001:MIDWEST_TO_FLORIDA_MODIFIED / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 201400 TO 202000 |
| 038 | DCC | 11/20/26 12:34 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 037 | DCC/ZMA | 11/20/26 12:25 | SOUTH FLORIDA CDRS_FYI |
| 036 | DCC/ZMA | 11/20/26 12:24 | ZMA SWAP_FYI |
| 035 | DCC | 11/20/26 12:15 | ATCSCC ADVZY 035 DCC 11/20/26 FCA RMD / NAME: FCA005:HITMN_PARTIAL / CONSTRAINED AREA: ZDC / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 034 | DCC | 11/20/26 12:14 | ATCSCC ADVZY 034 DCC 11/20/26 FCA RQD / NAME: FCA003:CREEP_PARTIAL / CONSTRAINED AREA: ZDC/ZTL / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 033 | DCC | 11/20/26 12:13 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 032 | DCC | 11/20/26 11:55 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 031 | DCC/ZMA | 11/20/26 11:38 | OCEANIC ROUTE CLOSURE_RQD |
| 030 | DCC | 11/20/26 11:00 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 029 | DCC | 11/20/26 10:33 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 028 | DCC | 11/20/26 09:25 | OPERATIONS PLAN |
| 027 | DCC | 11/20/26 08:58 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 026 | SFO/ZOA | 11/20/26 06:43 | CDM GROUND DELAY PROGRAM CNX |
| 025 | DCC | 11/20/26 06:16 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 024 | DCC | 11/20/26 05:56 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 023 | MIA/ZMA | 11/20/26 05:47 | MIA AIRPORT DIVERSION RECOVERY ACTIVATED |
| 022 | DCC | 11/20/26 05:30 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 021 | DCC | 11/20/26 05:14 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 020 | SAN/ZLA | 11/20/26 04:48 | CDM GROUND DELAY PROGRAM CNX |
| 019 | LAS/ZLA | 11/20/26 04:19 | CDM GROUND DELAY PROGRAM CNX |
| 018 | LAS/ZLA | 11/20/26 03:39 | CDM GROUND STOP |
| 017 | DCC | 11/20/26 03:00 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 016 | SFO/ZOA | 11/20/26 02:49 | CDM GROUND DELAY PROGRAM |
| 015 | SFO/ZOA | 11/20/26 02:31 | CDM PROPOSED GROUND DELAY PROGRAM |
| 014 | SFO/ZOA | 11/20/26 02:26 | SFO AIRPORT ARRIVAL DELAYS |
| 013 | DCC | 11/20/26 01:11 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 012 | LAS/ZLA | 11/20/26 00:50 | LAS AIRPORT SCHEDULING DELAYS |
| 011 | SAN/ZLA | 11/20/26 00:46 | CDM GROUND DELAY PROGRAM |
| 010 | DCC | 11/20/26 00:45 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 009 | DCC | 11/20/26 00:41 | ATCSCC ADVZY 009 DCC 11/20/26 FCA RQD / NAME: FCA008:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 008 | DCC | 11/20/26 00:40 | ATCSCC ADVZY 008 DCC 11/20/26 FCA RQD / NAME: FCA007:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 007 | DCC | 11/20/26 00:40 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 006 | DCC | 11/20/26 00:40 | ATCSCC ADVZY 006 DCC 11/20/26 FCA RQD / NAME: FCA009:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 201400 TO 202200 |
| 005 | DCC | 11/20/26 00:32 | OPERATIONS PLAN |
| 004 | SAN/ZLA | 11/20/26 00:29 | CDM PROPOSED GROUND DELAY PROGRAM |
| 003 | DCC | 11/20/26 00:22 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 002 | SAN/ZLA | 11/20/26 00:02 | SAN AIRPORT ARRIVAL DELAYS |
| 001 | DCC/ZDC | 11/20/26 00:01 | ZDC NRP SUSPENSION_RQD |

Ground-stop rows above, by number: 097, 096, 090, 087, 086, 084, 065, 018.

**Advisories on the index, 2026-11-21** — 19 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 019 | DCC | 11/21/26 05:01 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 018 | SEA/ZSE | 11/21/26 04:59 | CDM GROUND DELAY PROGRAM CNX |
| 017 | DCC | 11/21/26 04:38 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 016 | ORD/ZAU | 11/21/26 04:12 | CDM GROUND DELAY PROGRAM CNX |
| 015 | DCC | 11/21/26 02:53 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 014 | SAN/ZLA | 11/21/26 02:28 | CDM GROUND DELAY PROGRAM CNX |
| 013 | SEA/ZSE | 11/21/26 01:56 | CDM GROUND DELAY PROGRAM |
| 012 | SFO/ZOA | 11/21/26 01:55 | SFO AIRPORT SCHEDULING DELAYS |
| 011 | SEA/ZSE | 11/21/26 01:36 | CDM PROPOSED GROUND DELAY PROGRAM |
| 010 | DCC | 11/21/26 00:53 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 009 | DCC | 11/21/26 00:30 | OPERATIONS PLAN |
| 008 | DCC | 11/21/26 00:17 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 007 | DCC | 11/21/26 00:12 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 006 | ORD/ZAU | 11/21/26 00:10 | CDM GROUND DELAY PROGRAM |
| 005 | DCC | 11/21/26 00:06 | ATCSCC ADVZY 005 DCC 11/21/26 FCA RQD / NAME: FCA020:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 211400 TO 212200 |
| 004 | DCC | 11/21/26 00:05 | ATCSCC ADVZY 004 DCC 11/21/26 FCA RQD / NAME: FCA019:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 211400 TO 212200 |
| 003 | DCC | 11/21/26 00:05 | ATCSCC ADVZY 003 DCC 11/21/26 FCA RQD / NAME: FCA018:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 211400 TO 212200 |
| 002 | DCC | 11/21/26 00:04 | ATCSCC ADVZY 002 DCC 11/21/26 FCA RQD / NAME: FCA021:HOLIDAY_GULF_ROUTES / CONSTRAINED AREA: ZHU/ZJX/ZMA / VALID: FCA ENTRY TIME FROM 211100 TO 220300 |
| 001 | DCC/ZDC | 11/21/26 00:02 | ZDC NRP SUSPENSION_RQD |

No row on this day's index is a ground-stop advisory.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-21**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Thu 19NOV26 | 127 | 5,969 (was 5,738 at 08:00) | 728 | 23,377 (was 23,120 at 08:00) |
| Fri 20NOV26 | 148 (was 70 at 08:00) | 5,960 (was 785 at 08:00) | 802 (was 475 at 08:00) | 25,965 (was 14,012 at 08:00) |
| Sat 21NOV26 | 40 | 148 | 257 | 3,388 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 2 watch item(s) fell outside this pass's cap of 30. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261120053059 | http://web.archive.org/web/20261120053059/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261116220847 | http://web.archive.org/web/20261116220847/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261119053038 | http://web.archive.org/web/20261119053038/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-19 | 20261119140035 | http://web.archive.org/web/20261119140035/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-20 | 20261120140120 | http://web.archive.org/web/20261120140120/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261120141232 | http://web.archive.org/web/20261120141232/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11202026/99 | no capture |  | no capture; save failed (TimeoutError) |
| 11202026/97 | 20261121053044 | https://web.archive.org/web/20261121053044/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11202026&advn=97 | saved this pass |
| 11202026/96 | no capture |  | no capture; save budget spent |
| 11202026/91 | no capture |  | no capture; save budget spent |
| 11202026/90 | no capture |  | no capture; save budget spent |
| 11202026/87 | no capture |  | no capture; save budget spent |
| 11202026/86 | no capture |  | no capture; save budget spent |
| 11202026/84 | no capture |  | no capture; save budget spent |
| 11202026/83 | no capture |  | no capture; save budget spent |
| 11202026/72 | no capture |  | no capture; save budget spent |
| 11202026/65 | no capture |  | no capture; save budget spent |
| 11202026/56 | no capture |  | no capture; save budget spent |
| 11202026/42 | 20261120140211 | http://web.archive.org/web/20261120140211/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11202026&advn=42 |  |
| 11202026/28 | 20261120140314 | http://web.archive.org/web/20261120140314/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11202026&advn=28 |  |
| 11202026/18 | no capture |  | no capture; save budget spent |

coverage: 124 advisory rows, 3 totals tables, 32 watch items (18 verified, 1 saved this pass)

### 21NOV26

**Collected** 21NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-21** — 102 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 102 | DCC | 11/21/26 23:44 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 101 | DCC | 11/21/26 23:28 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 100 | CYYZ/CZY | 11/21/26 23:02 | CDM GS CNX |
| 099 | CYYZ/CZY | 11/21/26 22:39 | CDM GROUND STOP |
| 098 | DCC | 11/21/26 22:27 | OPERATIONS PLAN |
| 097 | DCC | 11/21/26 22:14 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 096 | DCC | 11/21/26 22:07 | REROUTE CANCELLATION |
| 095 | DCC | 11/21/26 21:23 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 094 | DCC | 11/21/26 20:57 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 093 | DCC/ZMA | 11/21/26 20:38 | SOUTH FLORIDA CDRS_FYI |
| 092 | DCC | 11/21/26 20:31 | OPERATIONS PLAN |
| 091 | FCASD1 | 11/21/26 20:26 | CDM AIRSPACE FLOW PROGRAM CNX |
| 090 | MCO/ZJX | 11/21/26 20:23 | MCO AIRPORT ARRIVAL DELAYS |
| 089 | MIA/ZMA | 11/21/26 19:54 | CDM GS CNX |
| 088 | CYVR/CZV | 11/21/26 19:32 | CDM GROUND DELAY PROGRAM CNX |
| 087 | DCC | 11/21/26 19:23 | REROUTE CANCELLATION |
| 086 | DCC | 11/21/26 19:22 | REROUTE CANCELLATION |
| 085 | DCC/ZNY | 11/21/26 19:14 | OCEANIC ROUTE CLOSURE_RQD |
| 084 | SFO/ZOA | 11/21/26 18:54 | CDM GROUND DELAY PROGRAM CNX |
| 083 | MIA/ZMA | 11/21/26 18:52 | CDM GROUND STOP |
| 082 | AUS/ZHU | 11/21/26 18:40 | AUS AIRPORT SCHEDULING DELAYS |
| 081 | FCAMA1 | 11/21/26 18:35 | CDM AIRSPACE FLOW PROGRAM CNX |
| 080 | DCC | 11/21/26 18:28 | OPERATIONS PLAN |
| 079 | DCC | 11/21/26 18:11 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 078 | LGA/ZNY | 11/21/26 17:44 | CDM GROUND DELAY PROGRAM CNX |
| 077 | DCC | 11/21/26 17:43 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 076 | CYVR/CZV | 11/21/26 17:39 | CYVR GROUND DELAY PROGRAM |
| 075 | AUS/ZHU | 11/21/26 17:13 | CDM GS CNX |
| 074 | AUS/ZHU | 11/21/26 16:48 | CDM GROUND STOP |
| 073 | DCC | 11/21/26 16:36 | REROUTE CANCELLATION |
| 072 | DCC | 11/21/26 16:27 | OPERATIONS PLAN |
| 071 | CYYZ/CZY | 11/21/26 16:16 | CDM GS CNX |
| 070 | CYOW/CZU | 11/21/26 16:15 | CDM GS CNX |
| 069 | DCC | 11/21/26 16:12 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 068 | ZMA | 11/21/26 16:09 | SOUTH FLORIDA AIRPORTS DIVERSION RECOVERY ACTIVATED |
| 067 | DCC | 11/21/26 16:00 | ATCSCC ADVZY 067 DCC 11/21/26 ROUTE RMD / NAME: TPA_AREA_TO_OHIO_VALLEY / CONSTRAINED AREA: ZJX / VALID: ETD 211600 TO 212200 |
| 066 | DCC | 11/21/26 15:59 | ATCSCC ADVZY 066 DCC 11/21/26 ROUTE RMD / NAME: TPA_AREA_TO_NE / CONSTRAINED AREA: ZJX / VALID: ETD 211600 TO 212200 |
| 065 | DCC | 11/21/26 15:57 | ATCSCC ADVZY 065 DCC 11/21/26 ROUTE RMD / NAME: TPA_AREA_TO_MIDWEST / CONSTRAINED AREA: ZJX / VALID: ETD 211600 TO 212200 |
| 064 | CYYZ/CZY | 11/21/26 15:37 | CDM GROUND STOP |
| 063 | DCC | 11/21/26 15:34 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 062 | CYOW | 11/21/26 15:24 | CDM GROUND STOP |
| 061 | CYYZ/CZY | 11/21/26 15:05 | CYYZ GROUND STOP |
| 060 | DCC | 11/21/26 15:04 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 059 | DCC/ZNY | 11/21/26 14:55 | OCEANIC ROUTE CLOSURE_RQD |
| 058 | ZMA/DCC | 11/21/26 14:50 | SOUTH FLORIDA AIRPORTS ARRIVAL DELAYS |
| 057 | DCC | 11/21/26 14:42 | US/MEXICO OUTLOOK_FYI |
| 056 | DCC | 11/21/26 14:39 | OPERATIONS PLAN |
| 055 | CYOW/CZY | 11/21/26 14:29 | CYOW GROUND STOP |
| 054 | DCC/ZBW | 11/21/26 14:11 | NATOTS_RQD |
| 053 | SFO/ZOA | 11/21/26 13:58 | CDM GROUND DELAY PROGRAM |
| 052 | SFO/ZOA | 11/21/26 13:49 | SFO AIRPORT ARRIVAL DELAYS |
| 051 | SFO/ZOA | 11/21/26 13:46 | CDM PROPOSED GROUND DELAY PROGRAM |
| 050 | DCC | 11/21/26 13:18 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 049 | FCASD1 | 11/21/26 13:16 | CDM AIRSPACE FLOW PROGRAM |
| 048 | DCC | 11/21/26 13:16 | CARIBBEAN OUTLOOK_FYI |
| 047 | AUS/ZHU | 11/21/26 13:15 | CDM GROUND DELAY PROGRAM CNX |
| 046 | DCC | 11/21/26 12:59 | OPERATIONS PLAN |
| 045 | DCC | 11/21/26 12:56 | ATCSCC ADVZY 045 DCC 11/21/26 FCA RQD / NAME: FCA016:LAKE_ERIE_WEST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 211500 TO 220400 |
| 044 | DCC | 11/21/26 12:55 | ATCSCC ADVZY 044 DCC 11/21/26 FCA RQD / NAME: FCA015:LAKE_ERIE_EAST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 211500 TO 220400 |
| 043 | DCC/ZNY | 11/21/26 12:53 | OCEANIC ROUTE CLOSURE_RQD |
| 042 | AUS/ZHU | 11/21/26 12:52 | AUS AIRPORT ARRIVAL DELAYS |
| 041 | DCC | 11/21/26 12:51 | REROUTE CANCELLATION |
| 040 | AUS/ZHU | 11/21/26 12:47 | AUS AIRPORT BELOW USER MINS |
| 039 | AUS/ZHU | 11/21/26 12:44 | CDM GROUND DELAY PROGRAM |
| 038 | FCAMA1 | 11/21/26 12:36 | CDM AIRSPACE FLOW PROGRAM |
| 037 | DCC | 11/21/26 12:10 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 036 | FCAMA1 | 11/21/26 12:02 | CDM PROPOSED AIRSPACE FLOW PROGRAM |
| 035 | DCC | 11/21/26 12:00 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 034 | LGA/ZNY | 11/21/26 11:49 | CDM GROUND DELAY PROGRAM |
| 033 | FCASD1 | 11/21/26 11:48 | CDM PROPOSED AIRSPACE FLOW PROGRAM |
| 032 | DCC | 11/21/26 11:45 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 031 | DCC | 11/21/26 11:40 | ATCSCC ADVZY 031 DCC 11/21/26 ROUTE RQD /FL / NAME: NE_TO_FLORIDA_VIA_J48_3_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 211200 TO 211600 |
| 030 | LGA/ZNY | 11/21/26 11:37 | CDM PROPOSED GROUND DELAY PROGRAM |
| 029 | DCC | 11/21/26 11:34 | ATCSCC ADVZY 029 DCC 11/21/26 FCA RQD / NAME: FCA011:ZMA_CARIBBEAN_VOLUME / CONSTRAINED AREA: ZMA / VALID: FCA ENTRY TIME FROM 211500 TO 212200 |
| 028 | DCC | 11/21/26 11:33 | ATCSCC ADVZY 028 DCC 11/21/26 ROUTE RQD /FL / NAME: TX_AND_ZME_TO_NORTHEAST / CONSTRAINED AREA: ZTL/ZDC / VALID: ETD 211300 TO 211900 |
| 027 | DCC | 11/21/26 11:30 | ATCSCC ADVZY 027 DCC 11/21/26 FCA RQD / NAME: FCA009:MIDWEST_TO_TPA_MCO / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 211300 TO 211900 |
| 026 | DCC | 11/21/26 11:26 | ATCSCC ADVZY 026 DCC 11/21/26 ROUTE RQD /FL / NAME: OHIO_VALLEY_TO_FLORIDA_2_PARTIAL / CONSTRAINED AREA: ZJX ZMA / VALID: ETD 211130 TO 211330 |
| 025 | DCC | 11/21/26 11:08 | ATCSCC ADVZY 025 DCC 11/21/26 FCA RQD / NAME: FCA013:LAKE_ERIE_EAST / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 211100 TO 211500 |
| 024 | DCC | 11/21/26 11:06 | ATCSCC ADVZY 024 DCC 11/21/26 FCA RQD / NAME: FCA014:LAKE_ERIE_WEST / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 211100 TO 211500 |
| 023 | DCC | 11/21/26 10:53 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 022 | DCC | 11/21/26 10:04 | OPERATIONS PLAN |
| 021 | DCC | 11/21/26 09:42 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 020 | DCC | 11/21/26 09:13 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 019 | DCC | 11/21/26 05:01 | VOLCANIC ACTIVITY BULLETIN - SANTA |
| 018 | SEA/ZSE | 11/21/26 04:59 | CDM GROUND DELAY PROGRAM CNX |
| 017 | DCC | 11/21/26 04:38 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 016 | ORD/ZAU | 11/21/26 04:12 | CDM GROUND DELAY PROGRAM CNX |
| 015 | DCC | 11/21/26 02:53 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 014 | SAN/ZLA | 11/21/26 02:28 | CDM GROUND DELAY PROGRAM CNX |
| 013 | SEA/ZSE | 11/21/26 01:56 | CDM GROUND DELAY PROGRAM |
| 012 | SFO/ZOA | 11/21/26 01:55 | SFO AIRPORT SCHEDULING DELAYS |
| 011 | SEA/ZSE | 11/21/26 01:36 | CDM PROPOSED GROUND DELAY PROGRAM |
| 010 | DCC | 11/21/26 00:53 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 009 | DCC | 11/21/26 00:30 | OPERATIONS PLAN |
| 008 | DCC | 11/21/26 00:17 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 007 | DCC | 11/21/26 00:12 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 006 | ORD/ZAU | 11/21/26 00:10 | CDM GROUND DELAY PROGRAM |
| 005 | DCC | 11/21/26 00:06 | ATCSCC ADVZY 005 DCC 11/21/26 FCA RQD / NAME: FCA020:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 211400 TO 212200 |
| 004 | DCC | 11/21/26 00:05 | ATCSCC ADVZY 004 DCC 11/21/26 FCA RQD / NAME: FCA019:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 211400 TO 212200 |
| 003 | DCC | 11/21/26 00:05 | ATCSCC ADVZY 003 DCC 11/21/26 FCA RQD / NAME: FCA018:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 211400 TO 212200 |
| 002 | DCC | 11/21/26 00:04 | ATCSCC ADVZY 002 DCC 11/21/26 FCA RQD / NAME: FCA021:HOLIDAY_GULF_ROUTES / CONSTRAINED AREA: ZHU/ZJX/ZMA / VALID: FCA ENTRY TIME FROM 211100 TO 220300 |
| 001 | DCC/ZDC | 11/21/26 00:02 | ZDC NRP SUSPENSION_RQD |

Ground-stop rows above, by number: 099, 083, 074, 064, 062, 061, 055.

**Advisories on the index, 2026-11-22** — 9 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-22&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 009 | DCC | 11/22/26 02:41 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 008 | DCC | 11/22/26 01:11 | OPERATIONS PLAN |
| 007 | CYYZ/CZY | 11/22/26 00:33 | CDM GS CNX |
| 006 | DCC | 11/22/26 00:26 | OPERATIONS PLAN |
| 005 | DCC | 11/22/26 00:24 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | DCC/ZNY | 11/22/26 00:17 | OCEANIC ROUTE CLOSURE_RQD |
| 003 | DCC | 11/22/26 00:15 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 002 | CYYZ/CZY | 11/22/26 00:12 | CDM GROUND STOP |
| 001 | DCC | 11/22/26 00:04 | ZDC NRP SUSPENSION_RQD |

Ground-stop rows above, by number: 002.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-22**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Fri 20NOV26 | 149 (was 148 at 08:00) | 6,706 (was 6,465 at 08:00) | 819 | 27,259 (was 26,984 at 08:00) |
| Sat 21NOV26 | 133 (was 53 at 08:00) | 5,415 (was 772 at 08:00) | 697 (was 416 at 08:00) | 19,020 (was 9,390 at 08:00) |
| Sun 22NOV26 | 42 | 158 | 260 | 2,797 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 4 watch item(s) fell outside this pass's cap of 30. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261120053059 | http://web.archive.org/web/20261120053059/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | no capture |  | no capture; save failed (HTTPError) |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261119053038 | http://web.archive.org/web/20261119053038/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-19 | 20261119140035 | http://web.archive.org/web/20261119140035/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-20 | no capture |  | no capture; save failed (HTTPError) |
| index 2026-11-21 | 20261121140115 | http://web.archive.org/web/20261121140115/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261120141232 | http://web.archive.org/web/20261120141232/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11212026/99 | no capture |  | no capture; save failed (HTTPError) |
| 11212026/98 | no capture |  | no capture; save failed (HTTPError) |
| 11212026/92 | no capture |  | no capture; save budget spent |
| 11212026/83 | no capture |  | no capture; save budget spent |
| 11212026/80 | no capture |  | no capture; save budget spent |
| 11212026/74 | no capture |  | no capture; save budget spent |
| 11212026/72 | no capture |  | no capture; save budget spent |
| 11212026/64 | no capture |  | no capture; save budget spent |
| 11212026/62 | no capture |  | no capture; save budget spent |
| 11212026/61 | no capture |  | no capture; save budget spent |
| 11212026/56 | no capture |  | no capture; save budget spent |
| 11212026/55 | no capture |  | no capture; save budget spent |
| 11212026/46 | 20261121140134 | http://web.archive.org/web/20261121140134/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11212026&advn=46 |  |
| 11212026/22 | 20261121140153 | http://web.archive.org/web/20261121140153/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11212026&advn=22 |  |

coverage: 111 advisory rows, 3 totals tables, 34 watch items (16 verified, 0 saved this pass)

### 22NOV26

**Collected** 22NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-22** — 135 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-22&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 135 | DCC/ZNY/ZMA | 11/22/26 23:35 | OCEANIC ROUTE CLOSURE_RQD |
| 134 | TEB/ZNY | 11/22/26 23:31 | CDM GS CNX |
| 133 | DCC/ZNY/ZMA | 11/22/26 23:24 | OCEANIC ROUTE CLOSURE_RQD |
| 132 | EWR/ZNY | 11/22/26 23:19 | CDM GROUND DELAY PROGRAM CNX |
| 131 | LGA/ZNY | 11/22/26 22:53 | CDM GROUND DELAY PROGRAM |
| 130 | HPN/ZNY | 11/22/26 22:44 | CDM GS CNX |
| 129 | LGA/ZNY | 11/22/26 22:31 | CDM PROPOSED GROUND DELAY PROGRAM |
| 128 | DCC | 11/22/26 22:28 | OPERATIONS PLAN |
| 127 | DCC | 11/22/26 22:25 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 126 | TEB/ZNY | 11/22/26 22:16 | CDM GROUND STOP |
| 125 | SAN/ZLA | 11/22/26 22:02 | SAN AIRPORT SCHEDULING DELAYS |
| 124 | SAN/ZLA | 11/22/26 21:58 | CDM GROUND DELAY PROGRAM CNX |
| 123 | DCC | 11/22/26 21:57 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 122 | SFO/ZOA | 11/22/26 21:49 | CDM GROUND DELAY PROGRAM CNX |
| 121 | DCC | 11/22/26 21:41 | REROUTE CANCELLATION |
| 120 | DCC | 11/22/26 21:41 | REROUTE CANCELLATION |
| 119 | DCC | 11/22/26 21:41 | REROUTE CANCELLATION |
| 118 | DCC | 11/22/26 21:40 | REROUTE CANCELLATION |
| 117 | HPN/ZNY | 11/22/26 21:30 | CDM GROUND STOP |
| 116 | TEB/ZNY | 11/22/26 21:13 | CDM GROUND STOP |
| 115 | DCC | 11/22/26 21:00 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 114 | DCC | 11/22/26 20:58 | ATCSCC ADVZY 114 DCC 11/22/26 ROUTE RQD /FL / NAME: TX_AND_ZME_TO_NORTHEAST / CONSTRAINED AREA: ZTL/ZDC / VALID: ETD 221330 TO 222300 |
| 113 | LGA/ZNY | 11/22/26 20:34 | CDM GROUND DELAY PROGRAM |
| 112 | SAN/ZLA | 11/22/26 20:32 | SAN AIRPORT ARRIVAL DELAYS |
| 111 | DCC | 11/22/26 20:31 | OPERATIONS PLAN |
| 110 | TEB/ZNY | 11/22/26 20:13 | CDM GROUND STOP |
| 109 | LGA/ZNY | 11/22/26 20:11 | CDM PROPOSED GROUND DELAY PROGRAM |
| 108 | DCC | 11/22/26 20:01 | VOLCANIC ACTIVITY BULLETIN - TELICA |
| 107 | DCC/ZNY/ZMA | 11/22/26 19:50 | OCEANIC ROUTE CLOSURE_RQD |
| 106 | LGA/ZNY | 11/22/26 19:48 | CDM GROUND STOP |
| 105 | DCC/ZNY | 11/22/26 19:43 | NORTH EAST AIRPORTS DIVERSION RECOVERY ACTIVATED |
| 104 | PSP/UDD/TRM/ZLA | 11/22/26 19:43 | PSP, TRM AND UDD AIRPORT ARRIVAL DELAYS |
| 103 | PCT/ZDC | 11/22/26 19:43 | DC METRO AIRPORTS ARRIVAL DELAYS |
| 102 | DCC/ZNY | 11/22/26 19:34 | NORTH EAST AIRPORTS ARRIVAL DELAYS |
| 101 | TEB/ZNY | 11/22/26 19:13 | CDM GROUND STOP |
| 100 | LGA/ZNY | 11/22/26 19:02 | CDM GROUND STOP |
| 099 | DCC | 11/22/26 18:50 | OPERATIONS PLAN |
| 098 | IAD/ZDC | 11/22/26 18:39 | IAD AIRPORT ARRIVAL DELAYS |
| 097 | DCA/ZDC | 11/22/26 18:38 | DCA AIRPORT ARRIVAL DELAYS |
| 096 | DCC | 11/22/26 18:15 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 095 | DCC | 11/22/26 18:06 | ATCSCC ADVZY 095 DCC 11/22/26 FCA RQD / NAME: FCA017:LAKE_ERIE_WEST_PARTIAL / CONSTRAINED AREA: CZY / VALID: FCA ENTRY TIME FROM 221900 TO 230400 |
| 094 | EWR/ZNY | 11/22/26 17:55 | CDM GROUND DELAY PROGRAM |
| 093 | DCC | 11/22/26 17:53 | ATCSCC ADVZY 093 DCC 11/22/26 FCA RQD / NAME: FCA015:MIDWEST_TO_FLORIDA_PARTIAL / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 221430 TO 222000 |
| 092 | DCC | 11/22/26 17:51 | ATCSCC ADVZY 092 DCC 11/22/26 ROUTE RQD /FL / NAME: MCO_ESCAPE_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 221230 TO 222000 |
| 091 | SFO/ZOA | 11/22/26 17:45 | CDM GROUND DELAY PROGRAM |
| 090 | EWR/ZNY | 11/22/26 17:42 | CDM PROPOSED GROUND DELAY PROGRAM |
| 089 | SFO/ZOA | 11/22/26 17:25 | CDM PROPOSED GROUND DELAY PROGRAM |
| 088 | SFO/ZOA | 11/22/26 17:19 | CDM GROUND STOP |
| 087 | LGA/ZNY | 11/22/26 17:09 | CDM GROUND DELAY PROGRAM |
| 086 | EWR/ZNY | 11/22/26 16:59 | CDM GROUND DELAY PROGRAM |
| 085 | DCC | 11/22/26 16:54 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 084 | LGA/ZNY | 11/22/26 16:46 | CDM PROPOSED GROUND DELAY PROGRAM |
| 083 | EWR/ZNY | 11/22/26 16:42 | CDM PROPOSED GROUND DELAY PROGRAM |
| 082 | DCC | 11/22/26 16:41 | OPERATIONS PLAN |
| 081 | DCC | 11/22/26 16:39 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 080 | ATL/ZTL | 11/22/26 16:28 | CDM GROUND DELAY PROGRAM CNX |
| 079 | ZNY | 11/22/26 16:20 | NORTH EAST AIRPORTS ARRIVAL DELAYS |
| 078 | PHLC/ZNY | 11/22/26 16:10 | EWR & EWR SATELLITE AIRPORTS DELAYS |
| 077 | DCC/ZNY/ZMA | 11/22/26 16:06 | OCEANIC ROUTE CLOSURES_RQD |
| 076 | LGA/ZNY | 11/22/26 15:59 | CDM GROUND STOP |
| 075 | DCC | 11/22/26 15:56 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 074 | DCC/ZMA | 11/22/26 15:53 | ZMA CDR_FYI |
| 073 | LGA/ZNY | 11/22/26 15:39 | CDM GROUND DELAY PROGRAM |
| 072 | DCC | 11/22/26 15:34 | ATCSCC ADVZY 072 DCC 11/22/26 ROUTE RQD /FL / NAME: MCO_ESCAPE_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 221230 TO 221800 |
| 071 | DCC/ZNY/ZMA | 11/22/26 15:27 | OCEANIC ROUTE CLOSURES_RQD |
| 070 | LGA/ZNY | 11/22/26 15:24 | CDM PROPOSED GROUND DELAY PROGRAM |
| 069 | LGA/ZNY | 11/22/26 15:07 | CDM GROUND STOP |
| 068 | DCC | 11/22/26 15:06 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 067 | LGA/ZNY | 11/22/26 15:05 | CDM GROUND STOP |
| 066 | SAN/ZLA | 11/22/26 14:51 | CDM GROUND DELAY PROGRAM |
| 065 | DCC | 11/22/26 14:42 | OPERATIONS PLAN |
| 064 | DCC | 11/22/26 14:41 | US/MEXICO OUTLOOK_FYI |
| 063 | ZLA | 11/22/26 14:38 | EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| 062 | SAN/ZLA | 11/22/26 14:37 | CDM PROPOSED GROUND DELAY PROGRAM |
| 061 | DCC/ZBW | 11/22/26 14:12 | NATOTS_RQD |
| 060 | ZTL | 11/22/26 14:07 | EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| 059 | ZNY | 11/22/26 14:01 | EXTENDED FLIGHT PLAN DROP TIMES IMPLEMENTED |
| 058 | LGA/ZNY | 11/22/26 14:01 | CDM GS CNX |
| 057 | DCC | 11/22/26 13:58 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 056 | DCC | 11/22/26 13:55 | VOLCANIC ACTIVITY BULLETIN - TELICA |
| 055 | DCC/ZNY | 11/22/26 13:47 | OCEANIC ROUTE CLOSURES_RQD |
| 054 | EWR/ZNY | 11/22/26 13:46 | CDM GS CNX |
| 053 | HOU/ZHU | 11/22/26 13:40 | CDM GS CNX |
| 052 | DCC/ZNY | 11/22/26 13:33 | OCEANIC ROUTE CLOSURES_RQD |
| 051 | ATL/ZTL | 11/22/26 13:32 | CDM GROUND DELAY PROGRAM |
| 050 | DCC/ZNY | 11/22/26 13:30 | OCEANIC ROUTE CLOSURES_RQD |
| 049 | HOU/ZHU | 11/22/26 13:23 | CDM GROUND STOP |
| 048 | LGA/ZNY | 11/22/26 13:21 | CDM GROUND STOP |
| 047 | EWR/ZNY | 11/22/26 13:18 | CDM GROUND STOP |
| 046 | DCC | 11/22/26 13:18 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 045 | LGA/ZNY | 11/22/26 13:15 | CDM GS CNX |
| 044 | DCC | 11/22/26 13:15 | ATCSCC ADVZY 044 DCC 11/22/26 ROUTE RQD /FL / NAME: TX_AND_ZME_TO_NORTHEAST / CONSTRAINED AREA: ZTL/ZDC / VALID: ETD 221330 TO 222200 |
| 043 | ZNY | 11/22/26 13:02 | NORTH EAST AIRPORTS DIVERSION RECOVERY ACTIVATED |
| 042 | ATL/ZTL | 11/22/26 12:59 | CDM GROUND STOP |
| 041 | DCC | 11/22/26 12:58 | OPERATIONS PLAN |
| 040 | ZNY | 11/22/26 12:51 | NORTH EAST AIRPORTS ARRIVAL DELAYS |
| 039 | LGA/ZNY | 11/22/26 12:43 | CDM GROUND STOP |
| 038 | DCC | 11/22/26 12:38 | ATCSCC ADVZY 038 DCC 11/22/26 FCA RQD /FL / NAME: FCA015:MIDWEST_TO_FLORIDA_PARTIAL / CONSTRAINED AREA: ZJX / VALID: FCA ENTRY TIME FROM 221430 TO 221800 |
| 037 | HOU/ZHU | 11/22/26 12:37 | HOU AIRPORT DIVERSION RECOVERY ACTIVATED |
| 036 | DCC/ZAU | 11/22/26 12:35 | ORD MDW CDRS_FYI |
| 035 | HOU/ZHU | 11/22/26 12:35 | CDM GROUND STOP |
| 034 | DCC | 11/22/26 12:16 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 033 | LGA/ZNY | 11/22/26 12:14 | LGA GROUND STOP - DAL SUBS |
| 032 | DCC | 11/22/26 12:07 | ATCSCC ADVZY 032 DCC 11/22/26 ROUTE RQD /FL / NAME: MCO_ESCAPE_PARTIAL / CONSTRAINED AREA: ZJX / VALID: ETD 221230 TO 221600 |
| 031 | HOU/ZHU | 11/22/26 11:53 | HOU AIRPORT BELOW USER MINS |
| 030 | LGA/ZNY | 11/22/26 11:46 | CDM GROUND STOP |
| 029 | DCC | 11/22/26 11:45 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 028 | DCC/ZJX | 11/22/26 11:30 | ZJX CAPPING/TUNNELING_RQD |
| 027 | DCC | 11/22/26 11:09 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 026 | DCC | 11/22/26 10:59 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 025 | DCC/ZNY | 11/22/26 10:57 | OCEANIC ROUTE CLOSURE_RQD |
| 024 | DCC | 11/22/26 10:41 | VOLCANIC ACTIVITY BULLETIN - POPOCATEPETL |
| 023 | DCC | 11/22/26 10:20 | OPERATIONS PLAN |
| 022 | DCC | 11/22/26 09:35 | ATCSCC ADVZY 022 DCC 11/22/26 FCA RQD / NAME: FCA008:HOLIDAY_GULF_ROUTES / CONSTRAINED AREA: ZHU ZJX ZMA / VALID: FCA ENTRY TIME FROM 221100 TO 230300 |
| 021 | DCC | 11/22/26 09:33 | ATCSCC ADVZY 021 DCC 11/22/26 FCA RQD / NAME: FCA007:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 221400 TO 222200 |
| 020 | DCC | 11/22/26 09:30 | ATCSCC ADVZY 020 DCC 11/22/26 FCA RQD / NAME: FCA006:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 221400 TO 222200 |
| 019 | DCC | 11/22/26 09:27 | ATCSCC ADVZY 019 DCC 11/22/26 FCA RQD / NAME: FCA005:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 221400 TO 222200 |
| 018 | DCC | 11/22/26 09:25 | ATCSCC ADVZY 018 DCC 11/22/26 FCA RQD / NAME: FCA005:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 221400 TO 232200 |
| 017 | DCC | 11/22/26 09:23 | ATCSCC ADVZY 017 DCC 11/22/26 FCA RQD / NAME: FCA005:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 221100 TO 230300 |
| 016 | DCC | 11/22/26 09:18 | ATCSCC ADVZY 016 DCC 11/22/26 FCA RQD / NAME: FCA004:LAS_F1_2026_PHX_NO_J92_PARTIAL / CONSTRAINED AREA: ZLA / VALID: FCA ENTRY TIME FROM 221500 TO 230300 |
| 015 | DCC | 11/22/26 09:16 | ATCSCC ADVZY 015 DCC 11/22/26 FCA RQD / NAME: FCA003:LAS_F1_2026_PHX_EAGUL_NO_ZUN_PARTIAL / CONSTRAINED AREA: ZLA / VALID: FCA ENTRY TIME FROM 221500 TO 230300 |
| 014 | DCC | 11/22/26 09:14 | ATCSCC ADVZY 014 DCC 11/22/26 FCA RQD / NAME: FCA002:LAS_AREA_AVOIDANCE_WEST / CONSTRAINED AREA: ZLA / VALID: FCA ENTRY TIME FROM 221500 TO 230300 |
| 013 | DCC | 11/22/26 09:12 | ATCSCC ADVZY 013 DCC 11/22/26 FCA RQD / NAME: FCA001:LAS_AREA_AVOIDANCE_EAST / CONSTRAINED AREA: ZLA / VALID: FCA ENTRY TIME FROM 221500 TO 230300 |
| 012 | DCC | 11/22/26 08:27 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 011 | DCC | 11/22/26 06:14 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 010 | DCC | 11/22/26 05:36 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 009 | DCC | 11/22/26 02:41 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 008 | DCC | 11/22/26 01:11 | OPERATIONS PLAN |
| 007 | CYYZ/CZY | 11/22/26 00:33 | CDM GS CNX |
| 006 | DCC | 11/22/26 00:26 | OPERATIONS PLAN |
| 005 | DCC | 11/22/26 00:24 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 004 | DCC/ZNY | 11/22/26 00:17 | OCEANIC ROUTE CLOSURE_RQD |
| 003 | DCC | 11/22/26 00:15 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 002 | CYYZ/CZY | 11/22/26 00:12 | CDM GROUND STOP |
| 001 | DCC | 11/22/26 00:04 | ZDC NRP SUSPENSION_RQD |

Ground-stop rows above, by number: 126, 117, 116, 110, 106, 101, 100, 088, 076, 069, 067, 049, 048, 047, 042, 039, 035, 033, 030, 002.

**Advisories on the index, 2026-11-23** — 11 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-23&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 011 | DCC/ZNY | 11/23/26 02:57 | OCEANIC ROUTE CLOSURE_RQD |
| 010 | DCC | 11/23/26 02:41 | ATCSCC ADVZY 010 DCC 11/23/26 FCA RQD / NAME: FCA020:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 231400 TO 232200 |
| 009 | DCC | 11/23/26 02:39 | ATCSCC ADVZY 009 DCC 11/23/26 FCA RQD / NAME: FCA019:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 231400 TO 232200 |
| 008 | DCC | 11/23/26 02:37 | ATCSCC ADVZY 008 DCC 11/23/26 FCA RQD / NAME: FCA018:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 231400 TO 232200 |
| 007 | DCC | 11/23/26 02:28 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 006 | LGA/ZNY | 11/23/26 01:56 | CDM GROUND DELAY PROGRAM CNX |
| 005 | DCC | 11/23/26 01:36 | ZDC NRP SUSPENSION_RQD |
| 004 | DCC | 11/23/26 01:28 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 003 | DCC | 11/23/26 01:10 | VOLCANIC ACTIVITY BULLETIN - TELICA |
| 002 | DCC | 11/23/26 00:21 | OPERATIONS PLAN |
| 001 | DCC | 11/23/26 00:10 | VOLCANIC ACTIVITY BULLETIN - FUEGO |

No row on this day's index is a ground-stop advisory.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-23**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Sat 21NOV26 | 138 (was 137 at 08:00) | 6,367 (was 6,058 at 08:00) | 711 (was 709 at 08:00) | 20,593 (was 20,306 at 08:00) |
| Sun 22NOV26 | 570 (was 86 at 08:00) | 7,915 (was 1,393 at 08:00) | 1,252 (was 470 at 08:00) | 22,483 (was 9,672 at 08:00) |
| Mon 23NOV26 | 123 | 237 | 686 | 2,744 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 17 watch item(s) fell outside this pass's cap of 30. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261120053059 | http://web.archive.org/web/20261120053059/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261121140112 | http://web.archive.org/web/20261121140112/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261122140037 | http://web.archive.org/web/20261122140037/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-19 | 20261119140035 | http://web.archive.org/web/20261119140035/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-20 | 20261120140120 | http://web.archive.org/web/20261120140120/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-21 | 20261121140115 | http://web.archive.org/web/20261121140115/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-22 | 20261122140057 | http://web.archive.org/web/20261122140057/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-22&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261120141232 | http://web.archive.org/web/20261120141232/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11222026/128 | 20261123053019 | https://web.archive.org/web/20261123053019/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11222026&advn=128 | saved this pass |
| 11222026/126 | 20261123053040 | https://web.archive.org/web/20261123053040/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11222026&advn=126 | saved this pass |
| 11222026/117 | no capture |  | no capture; save budget spent |
| 11222026/116 | no capture |  | no capture; save budget spent |
| 11222026/111 | no capture |  | no capture; save budget spent |
| 11222026/110 | no capture |  | no capture; save budget spent |
| 11222026/106 | no capture |  | no capture; save budget spent |
| 11222026/101 | no capture |  | no capture; save budget spent |
| 11222026/100 | no capture |  | no capture; save budget spent |
| 11222026/99 | no capture |  | no capture; save budget spent |
| 11222026/88 | no capture |  | no capture; save budget spent |
| 11222026/82 | no capture |  | no capture; save budget spent |
| 11222026/76 | no capture |  | no capture; save budget spent |

coverage: 146 advisory rows, 3 totals tables, 47 watch items (19 verified, 2 saved this pass)

### 23NOV26

**Collected** 23NOV26 23:30 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories on the index, 2026-11-23** — 51 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-23&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 051 | SAN/ZLA | 11/23/26 23:41 | CDM GROUND DELAY PROGRAM CNX |
| 050 | DCC | 11/23/26 23:36 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 049 | DCC/ZNY | 11/23/26 23:09 | OCEANIC ROUTE CLOSURE_RQD |
| 048 | JFK/ZNY | 11/23/26 23:01 | JFK AIRPORT ARRIVAL DELAYS |
| 047 | DCC | 11/23/26 21:49 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 046 | DCC | 11/23/26 20:26 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 045 | DCC | 11/23/26 20:25 | OPERATIONS PLAN |
| 044 | SAN/ZLA | 11/23/26 19:51 | SAN AIRPORT ARRIVAL DELAYS |
| 043 | DCC | 11/23/26 19:11 | OCEANIC ROUTE CLOSURE_RQD |
| 042 | DCC | 11/23/26 18:34 | OPERATIONS PLAN |
| 041 | ORD/ZAU | 11/23/26 18:09 | CDM GS CNX |
| 040 | DCC | 11/23/26 18:07 | VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| 039 | DCC | 11/23/26 17:40 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 038 | ORD/ZAU | 11/23/26 17:01 | CDM GROUND STOP |
| 037 | ORD/ZAU | 11/23/26 16:38 | ORD AIRPORT ARRIVAL DELAYS |
| 036 | DCC | 11/23/26 16:01 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 035 | DCC | 11/23/26 15:36 | VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| 034 | DCC/ZNY | 11/23/26 15:19 | OCEANIC ROUTE CLOSURE_RQD |
| 033 | DCC | 11/23/26 15:04 | TTCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 032 | DCC | 11/23/26 15:00 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 031 | SAN/ZLA | 11/23/26 14:38 | CDM GROUND DELAY PROGRAM |
| 030 | DCC | 11/23/26 14:34 | US/MEXICO OUTLOOK_FYI |
| 029 | DCC | 11/23/26 14:28 | OPERATIONS PLAN |
| 028 | SAN/ZLA | 11/23/26 14:27 | CDM PROPOSED GROUND DELAY PROGRAM |
| 027 | DCC | 11/23/26 14:27 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 026 | DCC/ZBW | 11/23/26 14:24 | NATOTS_RQD |
| 025 | DCC | 11/23/26 12:43 | OPERATIONS PLAN |
| 024 | DCC | 11/23/26 12:34 | VOLCANIC ACTIVITY BULLETIN - KILAUEA |
| 023 | CLT/ZTL | 11/23/26 12:30 | CLT AIRPORT ARRIVAL DELAYS |
| 022 | DCC | 11/23/26 12:12 | VOLCANIC ACTIVITY BULLETIN - SHEVELUCH |
| 021 | DCC | 11/23/26 11:59 | EN ROUTE TCA/HOTLINE ISSUE REQUEST PAGE ACTIVATION |
| 020 | DCC | 11/23/26 11:54 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 019 | DCC/ZJX | 11/23/26 11:53 | ZJX CAPPING/TUNNELING_RQD |
| 018 | DCC/ZNY | 11/23/26 10:46 | OCEANIC ROUTE CLOSURE_RQD |
| 017 | DCC | 11/23/26 10:06 | OPERATIONS PLAN |
| 016 | DCC | 11/23/26 10:00 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 015 | DCC | 11/23/26 09:29 | VOLCANIC ACTIVITY BULLETIN - PURACE |
| 014 | DCC | 11/23/26 08:46 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 013 | DCC | 11/23/26 06:55 | VOLCANIC ACTIVITY BULLETIN - TELICA |
| 012 | DCC | 11/23/26 06:01 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 011 | DCC/ZNY | 11/23/26 02:57 | OCEANIC ROUTE CLOSURE_RQD |
| 010 | DCC | 11/23/26 02:41 | ATCSCC ADVZY 010 DCC 11/23/26 FCA RQD / NAME: FCA020:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 231400 TO 232200 |
| 009 | DCC | 11/23/26 02:39 | ATCSCC ADVZY 009 DCC 11/23/26 FCA RQD / NAME: FCA019:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 231400 TO 232200 |
| 008 | DCC | 11/23/26 02:37 | ATCSCC ADVZY 008 DCC 11/23/26 FCA RQD / NAME: FCA018:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 231400 TO 232200 |
| 007 | DCC | 11/23/26 02:28 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 006 | LGA/ZNY | 11/23/26 01:56 | CDM GROUND DELAY PROGRAM CNX |
| 005 | DCC | 11/23/26 01:36 | ZDC NRP SUSPENSION_RQD |
| 004 | DCC | 11/23/26 01:28 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 003 | DCC | 11/23/26 01:10 | VOLCANIC ACTIVITY BULLETIN - TELICA |
| 002 | DCC | 11/23/26 00:21 | OPERATIONS PLAN |
| 001 | DCC | 11/23/26 00:10 | VOLCANIC ACTIVITY BULLETIN - FUEGO |

Ground-stop rows above, by number: 038.

**Advisories on the index, 2026-11-24** — 14 rows, fetched 23:30 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-24&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

| No. | Control | Sent | Title |
|---|---|---|---|
| 014 | DCC | 11/24/26 05:26 | VOLCANIC ACTIVITY BULLETIN - FUEGO |
| 013 | DCC | 11/24/26 03:31 | VOLCANIC ACTIVITY BULLETIN - REVENTADOR |
| 012 | DCC | 11/24/26 02:30 | VOLCANIC ACTIVITY BULLETIN - SANGAY |
| 011 | LAS/ZLA | 11/24/26 01:45 | CDM GROUND DELAY PROGRAM |
| 010 | LAS/ZLA | 11/24/26 01:23 | CDM PROPOSED GROUND DELAY PROGRAM |
| 009 | DCC | 11/24/26 00:31 | ATCSCC ADVZY 009 DCC 11/24/26 FCA RQD / NAME: FCA007:TTZP_TO_ZSU / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 241400 TO 242200 |
| 008 | DCC | 11/24/26 00:31 | ATCSCC ADVZY 008 DCC 11/24/26 FCA RQD / NAME: FCA006:ZNY_TO_TNCM_TQPF / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 241400 TO 242200 |
| 007 | DCC | 11/24/26 00:30 | ATCSCC ADVZY 007 DCC 11/24/26 FCA RQD / NAME: FCA005:ZSU_TO_TTZP / CONSTRAINED AREA: ZSU / VALID: FCA ENTRY TIME FROM 241400 TO 242200 |
| 006 | LEX/ZID | 11/24/26 00:27 | CDM GS CNX |
| 005 | DCC | 11/24/26 00:21 | OPERATIONS PLAN |
| 004 | LEX/ZID | 11/24/26 00:16 | CDM GROUND STOP |
| 003 | DCC | 11/24/26 00:11 | EN ROUTE TCA/HOTLINE WEB PAGE TERMINATION |
| 002 | DCC | 11/24/26 00:10 | TTCA/HOTLINE WEB PAGE TERMINATION |
| 001 | DCC | 11/24/26 00:01 | ZDC NRP SUSPENSION_RQD |

Ground-stop rows above, by number: 004.

**FlightAware totals** — fetched 23:30 CT. The tracker's own day is **2026-11-24**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Sun 22NOV26 | 585 (was 584 at 08:00) | 8,465 (was 8,301 at 08:00) | 1,274 (was 1,273 at 08:00) | 23,834 (was 23,655 at 08:00) |
| Mon 23NOV26 | 218 (was 182 at 08:00) | 4,925 (was 928 at 08:00) | 1,168 (was 922 at 08:00) | 20,206 (was 9,723 at 08:00) |
| Tue 24NOV26 | 22 | 168 | 340 | 2,927 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 23:30 CT. The advisory index keeps 15 days. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | 20261117053034 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 |  |
| 11132026/119 | 20261117053131 | http://web.archive.org/web/20261117053131/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 |  |
| 11132026/120 | 20261117053101 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 |  |
| 11142026/1 | 20261115140330 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 |  |
| 11142026/5 | 20261117023057 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 |  |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261120053059 | http://web.archive.org/web/20261120053059/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261121140112 | http://web.archive.org/web/20261121140112/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261122140037 | http://web.archive.org/web/20261122140037/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-19 | 20261123140021 | http://web.archive.org/web/20261123140021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-20 | 20261120140120 | http://web.archive.org/web/20261120140120/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-21 | 20261121140115 | http://web.archive.org/web/20261121140115/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-22 | 20261124053025 | https://web.archive.org/web/20261124053025/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-22&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | saved this pass |
| index 2026-11-23 | 20261123140046 | http://web.archive.org/web/20261123140046/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-23&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| faa-qa | 20261120141232 | http://web.archive.org/web/20261120141232/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |
| 11232026/45 | 20261124053045 | https://web.archive.org/web/20261124053045/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11232026&advn=45 | saved this pass |
| 11232026/42 | 20261124053105 | https://web.archive.org/web/20261124053105/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11232026&advn=42 | saved this pass |
| 11232026/38 | no capture |  | no capture; save budget spent |
| 11232026/29 | no capture |  | no capture; save budget spent |
| 11232026/25 | no capture |  | no capture; save budget spent |
| 11232026/17 | no capture |  | no capture; save budget spent |
| 11232026/2 | no capture |  | no capture; save budget spent |
| 11242026/5 | no capture |  | no capture; save budget spent |
| 11242026/4 | no capture |  | no capture; save budget spent |

coverage: 65 advisory rows, 3 totals tables, 27 watch items (20 verified, 3 saved this pass)

### 24NOV26

**Collected** 24NOV26 18:45 CT by `scripts/faa-ground-stop-pack.py`. Facts only: every line below was read off the page named, and nothing here is analysis.

**Advisories, 2026-11-24** — EMPTY, and that day is past: a parse or fetch break, not a quiet day. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-24&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

**Advisories, 2026-11-25** — the index returned no rows, fetched 18:45 CT. `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-25&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

**FlightAware totals** — fetched 18:45 CT. The tracker's own day is **2026-11-25**: its pages roll at 00:00Z, so between 18:00 CT and midnight it is already on tomorrow, and the date column is read from the day word each page prints. A figure that moved since the previous pass of this date is printed with the earlier reading, because the day settles.

| Day | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) |
|---|---|---|---|---|
| Sun 22NOV26 | 585 | 8,465 | 1,274 | 23,834 |
| Tue 24NOV26 | 221 (was 48 at 08:00) | 5,608 (was 738 at 08:00) | 1,180 (was 522 at 08:00) | 21,592 (was 9,723 at 08:00) |
| Wed 25NOV26 | 75 | 4,241 | 731 | 18,129 |

**Wayback captures** — every snapshot below was fetched and checked for the wording it should carry; `no capture` means no archive holds the document, and the note says whether a save was requested. Fetched 18:45 CT. The advisory index keeps 15 days. 

| Watch | Captured (UTC) | Snapshot | Note |
|---|---|---|---|
| 11132026/111 | unverified |  | snapshot did not serve (URLError); save failed (TimeoutError) |
| 11132026/119 | 20261125004806 | https://web.archive.org/web/20261125004806/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 | saved this pass |
| 11132026/120 | unverified |  | snapshot did not serve (URLError); save failed (TimeoutError) |
| 11142026/1 | unverified |  | snapshot did not serve (URLError); save failed (TimeoutError) |
| 11142026/5 | no capture |  | saved this pass, snapshot does not carry the wording |
| 11142026/18 | 20261116215302 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 |  |
| index 2026-11-13 | 20261119053021 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-14 | 20261116220803 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-15 | 20261120053059 | http://web.archive.org/web/20261120053059/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-16 | 20261121140112 | http://web.archive.org/web/20261121140112/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-17 | 20261117093837 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-18 | 20261122140037 | http://web.archive.org/web/20261122140037/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-19 | 20261125005027 | https://web.archive.org/web/20261125005027/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | saved this pass |
| index 2026-11-20 | 20261120140120 | http://web.archive.org/web/20261120140120/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-21 | 20261121140115 | http://web.archive.org/web/20261121140115/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-22 | 20261124053025 | http://web.archive.org/web/20261124053025/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-22&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-23 | 20261123140046 | http://web.archive.org/web/20261123140046/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-23&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true |  |
| index 2026-11-24 | no capture |  | no capture; save budget spent |
| faa-qa | 20261124142037 | http://web.archive.org/web/20261124142037/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers |  |

coverage: 0 advisory rows, 3 totals tables, 19 watch items (14 verified, 2 saved this pass)

## 20. Settled totals — every date read, merged and kept

Every date this job has read, merged and kept. FlightAware shows three days at a time, so a settled figure leaves its pages for good; this table is where it stays. A later reading replaces an earlier one for the same date, and a date is never dropped.

| Date | Cancels (US) | Delays (US) | Cancels (all) | Delays (all) | Last read (CT) |
|---|---|---|---|---|---|
| 2026-11-13 | 9,201 | 7,468 | 9,938 | 25,041 | 15NOV26 08:00 |
| 2026-11-14 | 6,695 | 8,969 | 7,349 | 22,498 | 15NOV26 08:00 |
| 2026-11-15 | 2,336 | 11,131 | 2,860 | 26,886 | 17NOV26 03:19 |
| 2026-11-16 | 375 | 7,218 | 896 | 22,198 | 17NOV26 23:30 |
| 2026-11-17 | 105 | 3,728 | 659 | 16,419 | 18NOV26 23:30 |
| 2026-11-18 | 142 | 4,754 | 737 | 20,430 | 19NOV26 23:30 |
| 2026-11-19 | 127 | 5,969 | 728 | 23,377 | 20NOV26 23:30 |
| 2026-11-20 | 149 | 6,706 | 819 | 27,259 | 21NOV26 23:30 |
| 2026-11-21 | 138 | 6,367 | 711 | 20,593 | 22NOV26 23:30 |
| 2026-11-22 | 585 | 8,465 | 1,274 | 23,834 | 24NOV26 18:45 |
| 2026-11-23 | 218 | 4,925 | 1,168 | 20,206 | 23NOV26 23:30 |
| 2026-11-24 | 221 | 5,608 | 1,180 | 21,592 | 24NOV26 18:45 |
| 2026-11-25 | 75 | 4,241 | 731 | 18,129 | 24NOV26 18:45 |

## 21. Verified citations — generated; do not edit by hand

Generated from §19's verified captures — **cite these URLs, not the ones in §15 or §16, which were written by hand before the snapshots were checked.** Every row here was fetched and had its wording checked when it was recorded; `python3 scripts/faa-ground-stop-pack.py --audit` re-checks all of them and exits nonzero if any stops serving its document.

| Document | Cite this URL | Captured (UTC) |
|---|---|---|
| 11132026/111 | http://web.archive.org/web/20261117053034/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111 | 20261117053034 |
| 11132026/119 | https://web.archive.org/web/20261125004806/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=119 | 20261125004806 |
| 11132026/120 | http://web.archive.org/web/20261117053101/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120 | 20261117053101 |
| 11142026/1 | http://web.archive.org/web/20261115140330/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=1 | 20261115140330 |
| 11142026/18 | http://web.archive.org/web/20261116215302/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=18 | 20261116215302 |
| 11142026/5 | http://web.archive.org/web/20261117023057/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5 | 20261117023057 |
| 11172026/20 | http://web.archive.org/web/20261117140355/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11172026&advn=20 | 20261117140355 |
| 11172026/29 | http://web.archive.org/web/20261117140226/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11172026&advn=29 | 20261117140226 |
| 11182026/70 | https://web.archive.org/web/20261119053124/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11182026&advn=70 | 20261119053124 |
| 11192026/69 | https://web.archive.org/web/20261120053122/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11192026&advn=69 | 20261120053122 |
| 11202026/42 | http://web.archive.org/web/20261120140211/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11202026&advn=42 | 20261120140211 |
| 11202026/97 | https://web.archive.org/web/20261121053044/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11202026&advn=97 | 20261121053044 |
| 11212026/22 | http://web.archive.org/web/20261121140153/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11212026&advn=22 | 20261121140153 |
| 11212026/46 | http://web.archive.org/web/20261121140134/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11212026&advn=46 | 20261121140134 |
| 11222026/126 | https://web.archive.org/web/20261123053040/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11222026&advn=126 | 20261123053040 |
| 11222026/48 | https://web.archive.org/web/20261122140141/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11222026&advn=48 | 20261122140141 |
| 11222026/49 | https://web.archive.org/web/20261122140122/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11222026&advn=49 | 20261122140122 |
| 11232026/42 | https://web.archive.org/web/20261124053105/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11232026&advn=42 | 20261124053105 |
| 11232026/45 | https://web.archive.org/web/20261124053045/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11232026&advn=45 | 20261124053045 |
| 11242026/18 | https://web.archive.org/web/20261124140117/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11242026&advn=18 | 20261124140117 |
| 11242026/25 | https://web.archive.org/web/20261124140053/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11242026&advn=25 | 20261124140053 |
| faa-qa | http://web.archive.org/web/20261124142037/https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers | 20261124142037 |
| index 2026-11-13 | http://web.archive.org/web/20261119053021/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-13&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261119053021 |
| index 2026-11-14 | http://web.archive.org/web/20261116220803/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261116220803 |
| index 2026-11-15 | http://web.archive.org/web/20261120053059/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-15&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261120053059 |
| index 2026-11-16 | http://web.archive.org/web/20261121140112/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-16&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261121140112 |
| index 2026-11-17 | http://web.archive.org/web/20261117093837/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-17&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261117093837 |
| index 2026-11-18 | http://web.archive.org/web/20261122140037/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-18&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261122140037 |
| index 2026-11-19 | https://web.archive.org/web/20261125005027/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-19&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261125005027 |
| index 2026-11-20 | http://web.archive.org/web/20261120140120/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-20&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261120140120 |
| index 2026-11-21 | http://web.archive.org/web/20261121140115/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-21&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261121140115 |
| index 2026-11-22 | http://web.archive.org/web/20261124053025/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-22&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261124053025 |
| index 2026-11-23 | http://web.archive.org/web/20261123140046/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-23&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261123140046 |
| index 2026-11-24 | https://web.archive.org/web/20261124140023/https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-24&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true | 20261124140023 |
