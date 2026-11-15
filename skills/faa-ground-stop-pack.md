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
`scripts/faa-ground-stop-pack-runner.sh` at **08:00 CT daily**, which runs
`scripts/faa-ground-stop-pack.py`. The collector:

1. reads the FAA ATCSCC advisory index for today and tomorrow, and writes every
   row as the index prints it — number, control, send time, title;
2. reads FlightAware's three day pages (two days back, yesterday, today) and
   writes the cancellation and delay totals for US and worldwide flights;
3. asks the Internet Archive's availability API for the nearest capture of each
   advisory that can carry the event — the six on the watch list plus any row
   whose own title is a ground stop or an operations plan — and records the
   snapshot URL.

It appends one block per date under **§19. Daily collection log**, replacing that
date's block if it already exists, so a re-run is harmless.

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
failed — and the shared alert fires. A single source failing is not exit 3: the
entry says `SOURCE UNAVAILABLE` with the URL and the exception, and the run
exits 0, because an entry that names its gap is honest and a missing day is not.

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
  holds that advisory yet. The Wayback save endpoint (`web.archive.org/save/`)
  timed out at 45 s when measured on 15NOV26, which is why the job records
  captures instead of creating them; closing a gap is a manual request.
- **Duplicate values** are printed as the page prints them. On 15NOV26 the
  FlightAware today page returned the same figure for US cancellations and US
  delays; that was recorded, not corrected, and §18.3 says not to print the
  Sunday delay figure from it.
- **The date column is CT**, this pass's date for that page. The tracker words
  its own pages by weekday, and the two have been known to disagree around
  midnight.
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
