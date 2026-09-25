# Skill: Kansas City Chiefs Weekly Report

A comprehensive weekly report on the Kansas City Chiefs, produced every Tuesday
at 1830 CT and **published automatically** — this is the one scheduled job whose
output goes live without Philip reading it first.

## When this runs

- Scheduled by launchd: `com.huffmanwrites.chiefs-weekly-report` (plist source:
  `scripts/com.huffmanwrites.chiefs-weekly-report.plist`; runner:
  `scripts/chiefs-weekly-report-runner.sh`).
- The runner invokes Claude Code headless in this repo with this skill.
- **Season only.** The runner reads the league's own calendar and exits without
  doing anything during the Off Season phase. If a report for today's date
  already exists, update it in place (same-day re-run).

## The one thing that makes this job different

Every other scheduled report here files a `draft: true` page and leaves it
uncommitted for Philip to review. **This one publishes.** The runner commits and
pushes the page it wrote, and the site deploys on that push. So the standard you
are held to is the publishing standard, not the drafting standard: everything
below is a requirement, not a preference, and there is no human gate behind you.

Two consequences you should feel while writing.

**A fabricated fact ships.** No one reads this before it is live. The repo's
most dangerous failure class (CLAUDE.md §Citations) is a URL or a name that
looks checkable and is wrong, and here it would go straight to production.

**A thin report is worse than no report.** You cannot pad a slow week with
recalled history, generic analysis, or a "what this means for the season"
paragraph that says nothing. A quiet week with one real piece of news, written
honestly, is a good report. A loud report built on invented specifics is not.

## Step 1 — Read the briefing pack. It is the spine of the piece.

**The runner has already written the pack and given you its path in the prompt**
(`/tmp/chiefs-pack-<date>.md`). Read that file first, in full. Do not re-fetch
ESPN to reconstruct it.

If you need a field in structured form, re-run the collector, which is on your
allow-list:

```
python3 scripts/chiefs-report.py --json        # the same data, structured
python3 scripts/chiefs-report.py               # the pack again, as markdown
python3 scripts/chiefs-report.py --season-state  # the league phase only
```

It prints the league phase, the most recent completed game (score, both teams'
full box score, both teams' leaders, every scoring play, both injury reports,
both records, venue, broadcast), the next game (venue, broadcast, the feed's
own odds attributed to the provider it names, the feed's matchup projection,
the opponent's last five games, both injury reports), the AFC West standings,
the AFC seed list, the team's season statistics by category, and the last two
weeks of Chiefs-tagged coverage with its URLs.

- `--json` for the same data structured, if you want to pull specific fields.
- `--season-state` prints only the league phase.
- `--today YYYY-MM-DD` evaluates a past date (for testing).

**Every number in your piece comes from this pack or from a page you fetched
yourself.** You do not recall scores, records, stats, odds, or schedules. If a
number you want is not in the pack, run the pack again, fetch the page that
carries it, or leave it out. Do not fill the gap from memory.

Three things in the pack that need care:

- **The odds are the feed's, and they are attributed.** The pack names the
  provider (DraftKings, say). Write "DraftKings lists Kansas City at -10.5" or
  "the line is Kansas City -10.5 per DraftKings", never "the Chiefs are 10.5-point
  favorites" as if it were a fact about the teams. Lines move and the feed's
  line is a snapshot.
- **The matchup projection is ESPN's, not ours.** It prints the feed's own win
  percentages. If you use them, attribute them to ESPN and say plainly that the
  site does not endorse them. Do not present a win probability as this site's
  judgment.
- **The injury entries carry dates.** "Questionable" on the Wednesday before a
  game is not the same as a game-day designation. If you cite a designation,
  give its date, and prefer "listed as questionable on September 23" to
  "questionable" as a standing fact.

## Step 2 — Get what the pack cannot give you.

The pack is the ESPN feed. It is not reporting, and it is not the Chiefs
themselves. Search for the week's coverage and read what carries the story:

- **Preferred local sources** (Philip's standing preference): the **Kansas City
  Star** and **KCUR**, alongside the **Kansas City Business Journal** and the
  team's own site. ESPN's Chiefs beat reporter is a usable second voice.
- What you are looking for: a press conference, a transaction the feed does not
  carry (a signing, a trade, a coaching change), an injury with a real timeline,
  a depth-chart move, a scheme or snap-count finding, a league-wide rule or
  disciplinary action that touches the team.
- **The feed's own news list is a starting point, not coverage.** It is mostly
  league-wide stories tagged to Kansas City because a team name appeared in them
  (betting guides, power rankings, uniform roundups, "predicting the next five
  Super Bowl champions"). Read the tag with suspicion. A story that names the
  Chiefs once is not a story about the Chiefs, and one of those is not your lede.

## Step 3 — Write it.

### House style

- Tone: personal stakes + historical context + contemporary urgency. Not
  yelling, not lecturing. Think *with* the reader. That voice applies to
  football exactly as it does to civics: this is an essay about a team's week,
  not a wire story and not a stat dump.
- **Write football.** This report is about the games, the players, the
  personnel, the standings, and what the season looks like from here. Do not
  bolt Stoicism, civics, or the site's other subjects onto it. A metaphor that
  arrives on its own is fine; a philosophy paragraph that you inserted because
  the site has one is not.
- Prose is the spine. The pack is evidence. A reader should finish knowing what
  happened, what it means for the season, and what to watch on Sunday.
- Open with a bold **Question:** / **Answer:** pair framing the week. Same shape
  as the other weekly reports.
- Em-dash limit: no more than 3 in the prose you write. Not counted: a dash
  inside quotation marks, and a dash standing as a date or number range (the
  en-dash is the right mark for a range). Count with
  `python3 scripts/check-emdashes.py --file <path>`.
- **Never end a sentence with a preposition** (house rule, 2026-09-25). Applies
  to body prose and to the frontmatter display fields (`title`, `description`).
  Check with `python3 scripts/check-prepositions.py --file <path>`.
- Closing attribution: `*PRH | [huffmanwrites.org] | © Philip Huffman*`.

### Sourcing rules that are not negotiable

- **Every load-bearing claim (scores, records, figures, dates, names, quoted
  language) comes from the briefing pack or from a page you actually fetched.**
- **A URL may be written only after the page has been retrieved and confirmed
  to be the thing cited.** Never build a URL from the pattern of a real one,
  never infer a slug from a headline, never guess a date-and-slug. This is the
  failure the pack exists to prevent: the pack supplies observed URLs from the
  feed, and those are safe to cite. Anything you assemble is not.
- **The pack's links are safe to use and are the preferred citation.** They came
  out of the ESPN payload. Cite the game page, the recap, the preview.
- Cite coverage as coverage and the feed as the feed. A quotation from a
  coach or player needs a link that contains the wording; if you cannot link it,
  attribute the idea in prose without quotation marks.
- **Verify a quotation before you put it in quotation marks.** If you did not
  fetch a page containing those words, do not quote.
- **A quoted line needs its source link ON the attribution line, and the gate
  will stop the publish if it is missing.** This is the trap in this report's
  natural format, and it is worth reading twice. A blockquote credited with a
  bare dash attribution —

  ```
  > "We have to get better in every phase."

  — Andy Reid
  ```

  — **fails** `check-quotes.py`. It treats a short name-first line after a dash
  as a citation and requires a URL that contains the quoted wording, and the
  runner aborts the push on a gate failure. So write it as:

  ```
  > "We have to get better in every phase."

  — Andy Reid, [postgame press conference, September 27](https://…)
  ```

  Better still, name the work in prose and link it inline. The rule is the
  house rule and the standard is right: every direct quotation carries a
  resolvable source link in the piece's apparatus, and in a report nobody
  reviews before it ships, that link is the only thing a reader can check.
- **The line between quotation and reportage.** A short phrase the feed itself
  supplies (a headline fragment, a stat label) is fine inside quotation marks
  with the feed cited as the source. A sentence of a coach's speech is not: if
  you cannot find and fetch the page that carries it, do not quote it — say what
  the coach said in your own words and attribute it to the press conference.

### Structure

1. **The lede** — bold **Question:** / **Answer:** pair naming the week's most
   consequential development for the team.
2. **The game just played** — the score and the record, then what actually
   decided it: the drives, the plays, the personnel, the numbers that carried
   it. The pack's scoring plays and box score are the raw material, and picking
   the three or four that mattered is the writing.
3. **The state of the team** — where the Chiefs sit: division, conference seed,
   the streak, the season statistics that are genuinely telling (a run game that
   has changed the offense, a pass rush that has not, a kicker's range). Say
   what the numbers mean, not just what they are.
4. **Injuries and personnel** — who is out, who is back, what it changes, with
   dates. This is often the most consequential section and it is the one most
   often skipped.
5. **The next game** — opponent, venue, kickoff, how to watch, the opponent's
   recent form, the line (attributed), and what to watch for.
6. **What to watch beyond Sunday** — the standings math, the next few weeks,
   the trade deadline, a looming decision. Where the season is heading.
7. **Sources** — every link you used, in the piece's citation apparatus.

A bye week, a quiet week, or a week with one real story gets a shorter report
that says so. Do not manufacture length.

### Output

- File: `content/posts/sports/chiefs-report-YYYY-MM-DD.md` (date = run date).
- Frontmatter:
  ```yaml
  ---
  title: "Chiefs Report: <Month Day, Year>"
  description: "One sentence naming the week's most significant development."
  date: <run time, CT>
  author: Philip Huffman
  lastmod: <same as date>
  draft: false
  featuredOnHome: true
  tags: [sports, chiefs, nfl]
  ---
  ```
  - `draft: false` — this job publishes; the runner will push it.
  - `featuredOnHome: true` is **required**, and it is not decoration. The home
    page fills its Recent Posts slots from posts carrying that flag before it
    considers anything else, and more than five flagged posts already exist, so
    an unflagged post does not appear in the feed at all. Without the flag the
    report is written and published and nobody sees it.
- **Date guard:** the `date` must never be ahead of the wall clock when the file
  is written. Hugo's `buildFuture: false` silently skips future-dated content:
  the build succeeds and the page is simply absent, which is the failure that
  hides. At an 1830 CT run, stamp the run time; do not round it forward.
- No hero image. No newsletter/sendfox fields.
- **Do NOT run `hugo`, do NOT run the gate scripts, do NOT commit or push, and
  do NOT touch `SESSION_STATE.md`.** The gates are deliberately absent from your
  allow-list, so a gate result in your summary would be unverifiable, and the
  runner does all of it immediately after this session ends: two builds, six
  offline gates, the commit, the push, the SESSION_STATE entry, and the
  SimpleBrain sync. Do not claim in your summary that a gate passed.

## Step 4 — Report back, in this shape

End your run with a short summary the runner's log will carry:

- the file you wrote and its word count;
- the week (number, opponent, result) in one line;
- the lede's Question/Answer in one line;
- every URL you cited that did NOT come from the briefing pack;
- anything you could not verify and therefore left out.

Keep it under 200 words. The runner reads your file, not your prose.

## Fallbacks

- **No game played in the window** (bye week, or the feed has not posted the
  result): write the report around the personnel news and the next game, and say
  plainly that no game was played. Do not invent a recap.
- **The pack reports fetch failures:** it prints them at the top. Say in the
  piece that the source was unreachable and write around the gap. Do not
  silently omit the section, and do not fill it from memory.
- **No Chiefs news in the window:** say so, and make the piece about the next
  game and the season state. A short honest report is correct.
- **You cannot find a source for a claim:** leave the claim out. There is no
  version of this job where an unverifiable sentence ships.
