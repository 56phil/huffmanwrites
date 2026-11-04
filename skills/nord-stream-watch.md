# Skill: Nord Stream Watch

The job that watches for the two events that would change a published essay.

`com.huffmanwrites.nord-stream-watch` exists because of one article.
*[The Bet He Called a Fact](content/posts/essays/the-bet-he-called-a-fact.md)*
(2026-11-04) tells the reader two things: that a verdict in the Hamburg trial
would change what the piece is entitled to say, and that a public reply from
Jeffrey Sachs would belong in the record. Neither event has a date. The trial's
scheduled hearings run to February 2027; Sachs answers his critics within days
when he answers them at all (his Lviv Herald reply of 19 October 2026 is the
model case). Nothing else in this repo reads a site it does not publish to, so
without this the article goes stale in silence — the failure `sitrep-watchdog`
was built for, in a different shape.

## What it watches, and why only two sources

| Source | What a hit means |
|---|---|
| `jeffsachs.org/interviewsandmedia?format=rss` | A new interview. The item's own Squarespace page is fetched and searched for "Nord Stream"; a reply that never names the pipeline in its title still names it in the text |
| The Hanseatisches Oberlandesgericht press archive | A new release — the side-joinder ruling, the verdict, a scheduling change. Keyed on the numeric id at the end of each release's slug, and matched on the headline |

The Bundesanwaltschaft is deliberately **not** a source. Its press index 404s at
the documented path, and its two Nord Stream releases (the indictment, the second
arrest) are already behind the article's argument; a third would be a charging
decision the Hamburg court announces first.

## The three rules that make it usable

**The first run is silent.** A watcher that alerts on everything already on the
page raises a banner about four-year-old news on the day it is installed, which
is how a new alert gets learned as noise. It records what is there, says so in
the log, and compares against that record from then on.

**A finding is not a failure.** Exit 1 means "read this, then decide"; exit 3
means a source could not be fetched, which is a real failure. The shared banner
reads *job failed*, so the runner's detail line opens with `FINDING (not a
failure)` before the finding itself. One notification path, two meanings, said
plainly. A second path is how an alert gets missed.

**It ends when its question does.** The runner exits 0 after 2027-04-30 with a
line saying why. A watcher outliving its subject logs a line a day forever, and
the plist comes out when the piece is settled (skills/scheduled-job.md rule 4).

## Operation

```bash
python3 scripts/nord-stream-watch.py                 # one look, state in ~/Library/Logs
python3 scripts/nord-stream-watch.py --dry-run       # report, write no state
python3 scripts/nord-stream-watch.py --state /tmp/x.json --seed
NORD_STREAM_WATCH_DRY=1 bash scripts/nord-stream-watch-runner.sh   # prove the alert path
```

State is `~/Library/Logs/nord-stream-watch-state.json`: the ids and links already
seen. Deleting it re-seeds silently on the next run, which is the right recovery
from a corrupted file and the wrong way to force an alert — use `--dry-run` with
a pruned state for that.

## When it fires

The banner is the cue to edit the article, not to publish a new one:

1. **A reply from Sachs** — read it, then decide whether it belongs in the piece.
   If it does, append a dated paragraph and move `lastmod`; the argument stands
   or it does not, and a reply that lands a real objection should be quoted.
2. **A verdict, or a ruling that changes the case** — the piece currently says the
   prosecution is untested. A conviction, an acquittal, or a collapse of the
   evidence changes that sentence and probably the closing paragraph.
3. **Neither source moved** — nothing to do. The log records that it looked.

## Wiring, per skills/scheduled-job.md

Four files, plus a row in `CLAUDE.md`'s scheduled-jobs table: this skill,
`scripts/com.huffmanwrites.nord-stream-watch.plist` (09:15 daily, one dict, no
`RunAtLoad`), `scripts/nord-stream-watch-runner.sh`, and
`TestNordStreamWatch` in `scripts/test_gates.py`, which asserts the schedule, the
end-date guard, the finding-versus-failure wording, and the checker's seed-then-
report behaviour against a fixture feed rather than against the live site.
