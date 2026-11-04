# Essay watch

The job that keeps a published essay from going quietly stale. It runs daily at
09:30 CT as `com.huffmanwrites.essay-watch`, reads a short registry of expiring
claims, and appends a dated note when one expires.

Philip, 2026-11-04, after the two midterm-day essays shipped: *"Keep those essays
current without any prompting from me."* A watcher that only alerts would make
the prompting his job again, so this one applies the amendment itself.

## What it amends, and what it never touches

An amendment is an **appended, dated note**, placed below the essay and above the
closing attribution line. It quotes the headline that carries the news, names the
outlet, dates it, and links to it.

It never edits a paragraph above it. That is the whole safety argument: the prose
that was fact-checked at publication stays exactly as verified, so no gate has to
adjudicate new argument, and the note's own claim is a string the online link
check can confirm is on the page it cites. A quotation is checkable; a paraphrase
is not.

## The two trigger kinds

| Kind | Fires when | Watches today |
|---|---|---|
| `call` | a feed carries a headline naming one of the watched candidates **and** a decisive verb (`wins`, `defeats`, `prevails`, `wins reelection`, `certifies`, `declared the winner`) **and** none of the not-yet words (`leads`, `separated`, `tossup`, `too close`, `uncalled`, `count`) | Mississippi Senate (`floor-ms`), Alaska Senate (`floor-ak`) |
| `series` | a day-count series has published nothing for **seven days**, or a headline naming the conflict says it ended | `US War on Iran` and `Ukraine War` day counts (`tally-iran`, `tally-ukraine`) |

The `call` classifier is deliberately two patterns rather than one clever regex,
because the headline this checker must not fire on is the one that was on the
page the morning the essay was written: *"43 votes separate Hyde-Smith and
Colom."* A margin is an order in the count. A call is a decision someone made.

Seven days is not four: a daily column that pauses over a long weekend has not
stopped, and a note saying it stopped would be false in a way no gate can see.

**`certifies` is in that verb list for a reason specific to Mississippi.**
Mississippi provides no recount, automatic or requested, and the election code's
Article 29 — "Election Contests" — reaches county offices and legislative seats
but not a U.S. Senate race, so the only forum left is the Senate under Article I,
Section 5. The count therefore ends in a certification, and a watcher that waited
for the word "recount" would wait forever. A headline about a challenge does not
veto the call: the challenge is news, the certification is the result.

## There is no model in this loop

The note is rendered from the finding's own fields — headline, outlet, date, URL.
There is no writer to gate, no allow-list to keep in step, and no way for a
language model to put a claim into a published essay at 09:30 without a reader.
If a future amendment needs prose judgement, that is a different job with a
writer, a skill, and the usual gates.

## Wiring

- `scripts/essay-watch.py` — the registry, the classifier, the note renderer.
  `--list` prints the registry, `--json` the findings, `--apply <id>` writes the
  note.
- `scripts/essay-watch-runner.sh` — applies, runs the gates, runs both builds,
  writes the SESSION_STATE entry, commits, pushes, and verifies delivery at the
  essay's own URL.
- `scripts/com.huffmanwrites.essay-watch.plist` — one fire a day at 09:30 CT,
  after `nord-stream-watch` at 09:15 and clear of the 06:00 SITREP.

Gates run on every touched essay: em-dashes, prepositions, quotations,
`check-links.py --file --online --titles`, then the frontmatter, hero-path and
attribution gates, then two builds. A failure **aborts the push and reverts the
edit**, because in a job with no human in the loop the gates are the review.

`ESSAY_WATCH_DRY=1` applies the notes and runs every gate without committing —
the only way to exercise the amend path without performing it.

## Adding a watch

Add one dict to `WATCHES` in `scripts/essay-watch.py`. For a `call` watch, name
the candidates and the feeds that would report it first — the outlets must be
readable without a browser. **Not AP:** its pages answer 403 to an automated
client, so an AP call is read by a human and this job learns it from the state
outlets that carry it. For a `series` watch, give the series title as it appears
in the headline and confirm the `DAY_NUMBER` pattern matches the actual shape
(`Ukraine War, Day 1,712` and `Days 1,713-1,714` are both real).

Then run `python3 scripts/essay-watch.py` and confirm it reports nothing on a
healthy day. A watch that fires the moment it is added is a pattern that matched
something it should not.

## Retiring a watch

Delete the dict. The marker comment it leaves in the essay
(`<!-- essay-watch:floor-ms -->`) is the record that a note was applied and the
reason a second application is a no-op; leave it in place.

## Files

| Path | What |
|---|---|
| `scripts/essay-watch.py` | registry, classifier, note renderer |
| `scripts/essay-watch-runner.sh` | gates, builds, publish, delivery check |
| `scripts/com.huffmanwrites.essay-watch.plist` | schedule |
| `~/Library/Logs/essay-watch.{out,err}.log` | the run's only authoritative record |
| `TestEssayWatch` in `scripts/test_gates.py` | the behaviour pinned above |
