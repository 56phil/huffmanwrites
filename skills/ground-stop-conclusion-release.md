# Job: the ground-stop conclusion — written and published in one run, 1600Z 1DEC26

Philip, 17NOV26: "It is my wish that the article be written as part of the act of
publishing." So `com.huffmanwrites.ground-stop-conclusion-release` is a
**writing job**, not a release job: at 10:00 CT on 1 December 2026 (1600Z) it
runs the writer, then the full gate set, then the shared publish tail — commit,
push, delivery verification, SimpleBrain mirror — in one run. A failed gate
aborts the push. There is no review step, so the gates are the review.

The writer's brief is `skills/ground-stop-conclusion.md`. This file is the
runner's contract.

## Order of work, and why the last guard is before the expensive part

| Step | Failure exit | Why it is there |
|---|---|---|
| Date guard, `2026-12-01` | 0 | launchd has no `Year` key: `Month 12 / Day 1` fires every December forever. A yearly alert about a finished series trains its reader to ignore alerts. |
| Guard bypass, `IGNORE_GUARDS=1` | — | Forces `REPORT_DRY_RUN=1`. The bypass exists to exercise the pipeline off its date, and it used to be the whole of the guard: on 17NOV26 a hand run with that one variable set went past the date check with publish authority intact, and only the smoke prompt kept the piece off the site. A run the schedule did not authorise cannot reach `publish_article`. |
| The pack exists | 3 | Nothing to write from. |
| The pack has **§21** | 3 | The verified citation list is the only place the writer may take an archive URL. Without it the piece ships §16's stale URLs. |
| `faa-ground-stop-pack.py --audit` | 3 | Every §21 row opens as its document. Run **before** the writer, so a dead snapshot costs a log line rather than an hour of drafting. |
| Ollama reachable | 1 | `scripts/ollama-probe.sh` heals by reopening the app, then fails loudly. |
| `publish_preflight` | — | Deletes any stale file at the article path, so the post-condition is binary: the file exists because this run wrote it, or the run aborts. |
| The writer | its code | `claude -p` with the brief, the pack, web access, and the two read-only prose checkers. No hugo, no git, no gate scripts, no SESSION_STATE. |
| Two builds | 1 | The drafts build renders what this run wrote; the production build is what the deploy will do. |
| `run_report_gates --plate 163-ground-stop-conclusion` | 4 | The shared gate list in `scripts/publish-report.sh`, unchanged for every publishing job. |
| `--audit --file <article>` | 4 | Series-specific: every archive URL in the piece opens as its document, and every advisory it cites has an archived copy in the piece. The FAA drops a document fifteen days after the fact, which is before this piece publishes. |
| `publish_article` | — | SESSION_STATE entry, commit, push, push verification, delivery check, mirror. |

## The article

`content/posts/essays/ground-stop-conclusion.md`, dated
`2026-12-01T10:00:00-06:00`, `draft: false`, `featuredOnHome: true`, hero pair
`163-ground-stop-conclusion_{16x9,4x5}.webp` in both `static/` and `assets/`
(the plate is fixed; the writer must not generate or rename one).

## Rehearsing it

```bash
REPORT_DRY_RUN=1 GROUND_STOP_CONCLUSION_IGNORE_GUARDS=1 \
  GROUND_STOP_CONCLUSION_TODAY=2026-12-01 \
  bash scripts/ground-stop-conclusion-release-runner.sh
```

Everything runs and the publish tail stops before writing to git. A smoke prompt
(`GROUND_STOP_CONCLUSION_PROMPT="Reply with exactly SMOKE-OK. Write no file."`)
proves the path up to the writer and then exits 3 for the missing file, which is
the correct answer and not a failure of the job.

A rehearsal writes to `~/Library/Logs/ground-stop-conclusion-release.smoke.out.log`,
never to the file the schedule writes, and `IGNORE_GUARDS=1` now sets
`REPORT_DRY_RUN=1` by itself: the bypass is the date check, not the publish
authority. Both halves were added 17NOV26, when the smoke left a start line in
the schedule's log that read, played back, exactly like the job firing.

**Rehearse after Thanksgiving, not before.** §20's ledger is the piece's spine
for 20–30NOV26; a rehearsal on 17NOV26 can only produce a piece with an empty
period, which the gates will happily accept.

## Uninstall after the run

A one-off job is removed after it succeeds, not left to its date guard:

```bash
launchctl bootout gui/"$(id -u)"/com.huffmanwrites.ground-stop-conclusion-release
rm ~/Library/LaunchAgents/com.huffmanwrites.ground-stop-conclusion-release.plist
```

Then remove the row from the scheduled-jobs table in `CLAUDE.md`. The repo copy
of the plist, the runner and both skills stay as the record.
