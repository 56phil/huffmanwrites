# Skill: Quarterly Repair-Plan Revision

Maintains `future-pieces/repair-plan-48th-president.md` — a governing plan for a president inaugurated January 20, 2027 who wants to repair the institutional damage of the second Trump administration.

Produced on the **first day of each quarter** at 07:00 CT: January 1, April 1, July 1, October 1. The plan is a living document; its whole value is that its dated claims are current. A repair plan built on a December status report is a plan built on a dead fact.

## When this runs

- Scheduled by launchd: `com.huffmanwrites.repair-plan` (plist source: `scripts/com.huffmanwrites.repair-plan.plist`; runner: `scripts/repair-plan-runner.sh`).
- The runner invokes Claude Code headless in this repo with this skill.
- If a revision for today's date is already recorded in the plan's revision log, stop. Do not run twice in a day.

## What this job is NOT

It is **not** a rewrite. The plan's argument, structure, and instrument-tier spine are settled and should survive many revisions. A quarterly run that produces a new essay each quarter has failed; a run that produces a shorter, more accurate document has succeeded.

It **is** a fact-check-and-update pass with these specific duties:

1. **Re-verify every dated claim.** The plan's load-bearing facts all move on known clocks. Check each and update to current.
2. **Re-check every litigating posture.** Cases pending at drafting may have been decided.
3. **Re-check every deadline and window.** Some expire. When one does, the plan must stop recommending an action that is no longer possible.
4. **Re-check every bill's status.** Introduced bills get committee action, floor votes, or die.
5. **Flag anything the plan recommends that has become moot, impossible, or superseded.**

## The checks that matter most, in order

Run these first. They are the claims whose expiry would most damage the plan.

### 1. The UNFCCC window (the hardest deadline, and the first one to expire)

- The withdrawal takes effect **February 27, 2027**. If today is on or after that date, the revocation window has closed: **rewrite Phase 0** to remove the revocation recommendation and lead with the re-entry sequence instead (UNFCCC Art. 23(2) 90 days, then Paris Art. 21(3) 30 days). Do not leave a recommendation for an act that can no longer be performed.
- Before that date, verify the notification is still pending at the depositary and that no earlier revocation has been filed.
- Also check whether the U.S. has deposited a **new** withdrawal notice for any of the other bodies in the January 2026 memorandum.

### 2. UNESCO

Withdrawal takes effect **December 31, 2026**. After that date, re-entry is the only route: confirm the U.S. is out, confirm the arrears figure, and update the mechanism paragraph.

### 3. The Schedule Policy/Career litigation

Four cases were pending with no merits ruling: *PEER v. Trump* (D. Md.), *NTEU v. Trump* (D.D.C.), *Government Accountability Project v. OPM*, *NTEU v. OPM* (FOIA). Check each docket for a ruling. **A merits ruling changes the plan's recommendation**: if a court voids the schedule, Phase 1's rulemaking recommendation becomes a compliance task; if a court upholds it, the statutory fix in Phase 2 becomes the only route and should be promoted in emphasis.

### 4. The emergency declarations

The border and energy emergencies both come up for continuation on **January 20, 2027**. If a continuation notice was published in the preceding 90 days, the emergency is still in force and the plan's list must say so. If not, it lapsed and the plan should say that too. Also re-count the continuation notices published in the trailing twelve months — the plan cites 43 notices covering 45 subjects as of September 2026.

### 5. The bills

For each of H.R. 10132 (ARTICLE ONE Act), H.R. 3908, S.134 / H.R. 492, H.R. 5724, and S. 2838: fetch status. Note any that passed a chamber, were reported out of committee, or died with the 119th Congress. **Bills from a prior Congress do not carry over**: if the 119th has ended, the plan must say so and name the successor vehicles if any exist.

### 6. The MSPB and removal-power holdings

Check for any ruling that extends or limits *Harris v. Bessent* or *Trump v. Slaughter*. Check the Board's membership and quorum, and its case backlog (the plan cites 9,457 open cases and 249 pending petitions for review as of mid-2026).

### 7. GAO impoundment decisions

Check for new decisions. The plan lists six by docket number; add new ones and note any the administration complied with.

### 8. The workforce and capacity figures

OPM's workforce data is monthly and was flagged incomplete (a Department of War processing failure left roughly 6,211 records outstanding as of the July 2026 release). Check whether the gap was closed and whether the net figure moved from 271,363.

## Method — the repo's rules bind this job

- **NEVER construct a URL.** Fetch it first or cite in prose without a link. The plan's own subject matter is full of fabricated-URL traps (Federal Register slugs, docket numbers, ECF patterns). This is the single most dangerous failure here.
- **Verify every quotation against the source you fetched**, normalizing whitespace first. Do not re-quote a passage you did not re-fetch this run; if you cannot reach the source, leave the existing wording and add a note that it was not re-verified.
- **PDFs**: `pdftotext` before searching. The reader truncates large PDFs silently.
- **Federal Register HTML pages return 403 to `curl`** but work through the documented API (`federalregister.gov/api/v1/documents/...`) and via the `read` tool. Use the API.
- **Distinguish enacted from proposed.** The plan's whole argument depends on this line; do not blur it in an update.
- **Do not blend figures from different sources** into a synthetic total. Where the plan presents competing counts (the emergency-notice count, the workforce measures), keep them separate and attributed.

## How to edit the file

- **Edit in place.** Preserve the section structure, the instrument-tier framing, and the closing section on what the plan cannot do.
- **Update the `lastmod` line and the "Prepared" date** in the front matter.
- **Append a revision-log entry** at the end of the file, before the Sources section, in this form:

```
### Revision history

- **2026-09-24** — Initial draft.
- **YYYY-MM-DD** — <what changed and why, in one or two sentences. Name what you re-verified and what moved.>
```

- **Never delete a factual claim whose status changed**; correct it and note the correction in the revision log. The plan argues that repairs are judged by whether they bind an unwilling successor; it should hold itself to a comparable standard about its own record.
- **Trim rather than pad.** If a section's subject has expired, cut it. A shorter plan is a better plan.

## Verification (the runner does the heavy part)

- Run `python3 scripts/check-emdashes.py --file future-pieces/repair-plan-48th-president.md` and keep counted em-dashes at or below 3 (dashes inside quotations and in numeric ranges are exempt).
- Run `python3 scripts/check-links.py --check`. There is no front matter on this file, but the gate scans the repo corpus and will catch placeholder or blocklisted URLs.
- Do **not** run `hugo`; the runner performs the verification builds and records the results. `future-pieces/` is not rendered.
- Do **not** run the whole-corpus `check-quotes.py --online`; it exceeds the tool ceiling. Use `--file` if needed.

## Output contract

- **Drafts for Philip to review.** Do NOT commit and do NOT push. The runner leaves the working tree dirty on purpose and reports it; Philip reviews the diff and commits.
- Report at the end: what you re-verified and found unchanged, what you changed, what you could not reach, and anything that made a recommendation moot.
