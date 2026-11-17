# Skill: the ground-stop source pack, kept current daily

`future-pieces/faa-ground-stop-source-notes.md` is the evidence record behind the
piece on the nationwide ground stop of 13NOV26. Philip, 15NOV26: "From now on,
update the source pack daily until further notice." This skill is how that is
done without a human remembering to do it.

## Why it is a job and not a good intention

Two kinds of fact in the pack decay on a clock:

- **The primary documents vanish.** `fly.faa.gov` retains ATCSCC advisories for
  **15 days**. The 13–14NOV26 advisories therefore die around **29NOV26**, and
  the piece window is Thanksgiving to Christmas. Every day without a capture is
  a day closer to having no citable original.
- **The numbers stop changing and start being wrong.** FlightAware's daily
  totals settle when the day closes. A snapshot taken at 9:52 p.m. on Friday is
  not a wrong reading; printed as the day's total, it is a wrong claim.

## What the job does

`scripts/com.huffmanwrites.faa-ground-stop-pack.plist` fires
`scripts/faa-ground-stop-pack-runner.sh` **twice a day, at 08:00 and 23:30 CT**,
which runs `scripts/faa-ground-stop-pack.py`. The collector:

1. reads the FAA ATCSCC advisory index for today and tomorrow, and writes every
   row as the index prints it — number, control, send time, title;
2. reads FlightAware's three day pages (two days back, yesterday, today) and
   writes the cancellation and delay totals for US and worldwide flights. A
   figure that moved since the previous pass of the same date is printed with
   the earlier reading — `2,336 (was 1,446 at 08:00)` — because the day
   settles and `upsert` replaces the block, so the earlier number would
   otherwise vanish;
3. checks every document that can carry the event — the six on the watch list,
   any row whose own title is a ground stop or an operations plan, **each day's
   index page**, and the FAA's own Q&A page — asks the Internet Archive what it
   holds, **opens the snapshot and requires it to carry the wording it should**,
   and when nothing holds the document **requests the save itself**, up to six
   saves per pass.

4. merges the day's figures into **§20. Settled totals**, a table keyed by date
   that is never dropped and never written backwards in time. FlightAware shows
   three days; a settled figure that scrolls out of them leaves its pages for
   ever, and this table is where it stays;
5. rewrites **§21. Verified citations** — the only list a writer should copy a
   URL from.

It appends one block per date under **§19. Daily collection log**, replacing that
date's block if it already exists, so a re-run is harmless. Each block ends with
a `coverage:` line — advisory rows, totals tables, watch items, verified
captures, saves this pass — for the same reason every `check-*.py` prints one: a
pass that inspects nothing still reports OK.

## Before the piece is drafted, and again before it publishes

```bash
python3 scripts/faa-ground-stop-pack.py --audit              # the pack's own list
python3 scripts/faa-ground-stop-pack.py --audit --file content/posts/essays/<piece>.md
```

**`--file` is the one that matters before a push.** It reads a finished piece
and checks two things: every archive URL in it opens **as its document** (a
capture the pack does not list is fine and is reported `UNLISTED`, because the
question is whether the reader can open it, not whether it is in a table), and
**every advisory the piece cites has an archived copy inside the same piece** —
the live `adv_otherdis` URL dies when the fifteen-day window closes, which falls
inside this series' drafting window. First run, on the published 15NOV26
installment: it cited Advisory 120 live with no archived copy, and 120 is the
one that carries `REASON: COMMUNICATIONS FAILURE`. The copy was added.

Exit **4** is a citation that serves the wrong document, or an advisory with no
archived copy; exit **3** is one that could not be read.

It re-opens every URL in §21 and exits **4** if one no longer serves its
document, printing the key and the reason. Run it on the day the piece is
written and once more before the push. It exists because the hand-written lists in §15 and
§16 had gone stale without saying so: measured 17NOV26, **two of the seven**
archived advisories §16 told the writer to cite serve a page with **no advisory
text in it**, and one could not be read at all. The four that do serve are the
ones §19 verified, which is why §21 is generated from them rather than
maintained by hand.
Exit **4** is a snapshot that serves the wrong document; exit **3** is one that
could not be read (the archive throttles, and an audit that hammers it turns its
own throttle into a finding — the first version of this item claimed four of the
seven were dead for exactly that reason). Both are failures a writer must
resolve; only the first is a defect in the citation.

## What it does not do, and must not start doing

**No model, no prose, no cause.** The block is facts with the page they came
from. The analysis lives in §18, written by whoever reads §19, because a
sentence about why the airspace closed is a claim that needs a fetched source
and a judgement about which of two official accounts to print. `TestGroundStopPack`
asserts the collector writes no analysis: it has no model call, no `claude`, and
no `git`.

**No commit.** The pack is a working file. A daily commit would trigger a Pages
build every morning for a note no reader can see. The job leaves the tree
dirty; `publish_preflight` logs a dirty tree as a NOTE and refuses only on
`SESSION_STATE.md`, so this cannot block a publish. The next real commit carries
the day's entry with it.

## How to run it by hand

```bash
python3 scripts/faa-ground-stop-pack.py --dry-run          # print, write nothing
python3 scripts/faa-ground-stop-pack.py --date 2026-11-14  # backfill a date
GROUND_STOP_PACK_DRY=1 scripts/faa-ground-stop-pack-runner.sh   # prove the alert path
```

Exit 3 means **nothing at all was collected** — both pages and the capture API
failed — and no block is written. A single source failing is not a failure: the
entry says `SOURCE UNAVAILABLE` with the URL and the exception, and the run
exits 0, because an entry that names its gap is honest and a missing day is not.

Exit 4 means **a page was read and a required figure did not come out of it** —
an empty index for a day already past, or a FlightAware page that answered with
no cancellation count. The block is still written, so the reader can see the
break, and the runner alerts. That distinction matters: `—` in the US
cancellation column would read as "no cancellations", which is a claim the pass
never made.

**Two fires, and the second is the point.** At 08:00 CT the previous day's
totals are final and the day's advisory index is being written, but the pass is
also looking at a US traffic day that has not started; 23:30 replaces that day's
block with one whose `today` row is nearly closed. Measured: Sunday's US
cancellations read 1,446 at 08:00 on 15NOV26 and 2,336 by the next morning. The
08:00 fire sits after the 06:00 SITREP and before the 09:15 and 09:30 watchers,
so three network jobs do not collide; 23:30 is clear of everything.

## Reading the log

**Prose goes under the block, and the block never touches it.** Each day's
machine-written block is followed by a `**Reading — <DATE>**` subsection written
by hand (or by an agent asked to write the delta), saying what the block means:
whether the airspace carried a restriction, which advisory titles changed,
which captures are missing, which numbers the page printed ambiguously. The
collector stops its own block at that marker, so a re-run replaces the facts and
leaves the prose — asserted by
`test_a_hand_written_reading_survives_a_rerun`, because a daily pass that
silently deleted the analysis would leave a record that looks current and is
shorter.

- **`no capture`** in the snapshot table is a finding, not a bug. No archive
  holds that document, and the note column says whether a save was requested
  this pass. **The save endpoint works and the job uses it:** `recorded, not
  created` was the first version, on the strength of a 45-second timeout
  measured on 15NOV26. Measured again on 16NOV26, a save answered in **18.4 s**
  and closed the advisory the pack had reported as uncapturable for two days —
  so the timeout was the constraint, not the service. `SAVE_BUDGET` keeps a
  pass to six, because this is somebody else's machine.
- **A capture is recorded only after its body is fetched and checked** for the
  wording it should carry (`ADVZY 018`; `ATCSCC ADVISORIES FOR 2026-11-13`; for
  the FAA Q&A page, a phrase from its answer about the data flood). The
  availability API answers with the *closest* capture of *some* URL and echoes
  the requested URL back, so a near-miss looks exactly like a hit: on 15NOV26
  the pack recorded `11142026/18` as captured at `20261114032528`, and that
  snapshot served **404** a day later. The verdicts are different claims and
  the note column says which: a timestamp (the document is held and opens),
  `no capture` (nothing holds it), `unverified` (something holds it and would
  not open, which is a claim about the checker — the archive throttles a client
  that has just asked it for nine saves), and `saved this pass, snapshot does
  not carry the wording` (something is held, and it is not the document).
- **The day index pages are watched, not just the advisories.** The cleanest
  proof that the airspace carried no restriction on 15NOV26 is that day's
  27-row index page, and nothing was archiving it. The three days before the
  daily pass existed (13–15NOV26) are captured in one go; every later day is
  captured by that day's own pass.
- **The watch list is ordered by value, and the order is the save budget's
  order.** The first live pass put the current day's eight airport ground
  stops first, spent the budget on them, and left all four index pages
  uncaptured. Now: the six event advisories, then event-day discoveries, then
  the day indexes, then the FAA Q&A page, then a day's own airport advisories
  as a tail with two saves of its own (`SAVE_BUDGET_TAIL`). Do not re-order it
  back.
- **Duplicate values** are printed as the page prints them. On 15NOV26 the
  FlightAware today page returned the same figure for US cancellations and US
  delays; that was recorded, not corrected, and §18.3 says not to print the
  Sunday delay figure from it.
- **The date column is the tracker's day, read from the page's own word.** Its
  pages roll at **00:00Z**, so between 18:00 CT and midnight FlightAware is
  already on tomorrow: at 23:30 CT on 16NOV26 its `minus2days` page was the
  15th. Labelling that page from the CT date put **Sunday's 2,336 US
  cancellations against Saturday**, and printed under a heading that read as a
  correction of an earlier figure. `tracker_day()` converts to UTC, and
  `resolve_page_day()` dates each page from the weekday it prints; a page whose
  word disagrees with the offset is a problem, not a silent relabel.
- **An empty tomorrow** is not a quiet day. The collector fetches the next date
  so that a later re-run can see it; it says nothing at 05:40 about a day that
  has not started.

## When to stop it

The instruction is "until further notice", and the plist carries no end date
because a guard that exits 0 forever is a scheduled no-op that logs a line a day
and is never removed. To stop: `launchctl bootout gui/$(id -u)
~/Library/LaunchAgents/com.huffmanwrites.faa-ground-stop-pack.plist`, delete the
installed plist, and update the table in `CLAUDE.md`. Leave the repo copy and
this skill in place as the record, the way the Senate and Sagan runners were
left.

The pack itself has a natural end: the 15-day advisory window closes around
**29NOV26**, and after that the daily pass can only add FlightAware totals and
capture timestamps. Say so when it happens rather than letting the log imply
the record is still growing.
