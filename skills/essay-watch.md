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

## No ad-hominem, including in the headlines it quotes

**The rule: nothing this job writes, and nothing an amendment of any kind writes into
a published essay, argues that a person is bad. It argues that a claim is wrong.**

Philip, 2026-11-05, after reading the Musk essay: that piece made its case from
filings and incentives and left the man's character out entirely, and he named that
restraint as the piece's virtue. The reason it works is not delicacy. Character is
the exit a reader takes for free: name the drug use, the vanity, the posting, and a
reader who disagrees never has to answer the expenditure table, because they get to
say the piece is a grudge and keep the opinion with which they arrived. It is a *true*
exit, which is what makes it so valuable to whoever is arguing the other side. The subject's
worst conduct is usually public, verifiable, and irrelevant to the claim; that is
exactly when it is tempting.

What replaces it: the incentive that makes the conduct profitable, the filing that
records it, the consequence a reader can check. "He has never needed to win to get
what he pays for" is an argument. "He is a vain man who cannot help himself" is a
feeling with a byline. **A person may appear in a note as the actor in an event;
never as the object of a verdict.** No adjectives about anyone's mind, motives, body,
or habits, and no moral summary of a named individual, including one the reader is
expected to dislike.

**This rule reaches the quoted headline too.** A note reproduces an outlet's headline
verbatim, so a headline that attacks a person's character rather than reporting the
event would put the attack into a published essay with a link behind it, and the job
would be the one that carried it there. The test is what the sentence is *about*: a headline whose subject is a decision or a
result (`Mississippi certifies Hyde-Smith's win`) states the call; a headline whose
subject is a person's worth or conduct states a judgment. The preferred fix is the
one the classifier already uses for a margin: **wait.** The certification is the
result, and a state outlet reports it flatly within the day; a note that arrives a
day late is correct where a note that arrives early is a weapon.

**The classifier cannot make that distinction, and the runner currently applies every
finding it returns**, so the honest statement of the limit is this: `DECISIVE` asks
whether a headline carries a decisive verb, not what the sentence is about, and a
judgmental headline that also carries `wins` or `certifies` would be quoted. Two
things follow. Read the finding log before the day it matters. A note that has
quoted a verdict is visible in `~/Library/Logs/essay-watch.out.log` and in the
SESSION_STATE entry the runner writes, and it can be corrected the same morning. And
the durable fix, if this ever bites, is a **hold**: a narrow pattern for a character
verdict that suppresses the automatic apply and raises the shared alert, so the cost
of a false positive is a day's delay and a banner rather than a sneer on a published
page. The error is asymmetric enough that a narrow list earns its keep *as a hold*.
It does not earn its keep as a filter: do not add a keyword list to `essay-watch.py`
and call the rule enforced, because a list of insults flags a quotation and passes a
sneer, and the one thing worse than an unenforced rule is a rule that reports OK.

**Where the rule is fully binding.** In the note's own sentence, the alert copy, the
session-state entry, and the prose of any future writer added here (the case
`## There is no model in this loop` describes, which would bring a writer, a skill
and the usual gates). There is no ambiguity to resolve in those places: the prose
states the event and names the person as its actor, or it does not ship.


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
