# Skill: the one-off release of the ground-stop conclusion, 1600Z 1 December 2026

Philip, 17NOV26: "Set up a one-time cronjob to publish the conclusion of the
ground stop pieces for 1600Z on 01DEC26."

`com.huffmanwrites.ground-stop-conclusion-release` fires
`scripts/ground-stop-conclusion-release-runner.sh` at **10:00 CT on 1 December
2026** — 1600Z, because December is standard time — dispatches a Pages build,
requires the page to answer, and hands the piece to the SimpleBrain mirror.

## Why a job and not a push

The piece is dated to the release minute, and Hugo builds with
`buildFuture: false`: a page dated 1600Z is skipped by every build that runs
before 16:00Z, silently, and appears only in a deploy that runs after it. No cron
in `.github/workflows/hugo.yml` covers 16:00Z (the nearest are `0 13 * * *` and
`0 5/6 * * *`), and the scheduled fires land about four hours late when they run
at all. The next push after 16:00Z would be the next morning's SITREP. So the
release gets a trigger that runs at the minute, the same contract
`digest-release`, `sagan-release` and `veterans-release` keep.

It mirrors as well, because a piece published this way never enters
`publish_article`, which is where the vault mirror lives. The Sagan reflection
went two days without a vault copy for exactly that reason.

## What the piece must look like by then

1. The file is at **`content/posts/essays/ground-stop-conclusion.md`**, or the
   plist sets `GROUND_STOP_CONCLUSION_ARTICLE` to wherever it actually is. The
   guard names whichever path it looked for, so a mismatch is a log line and an
   alert, never a silent no-op.
2. Frontmatter carries `date: 2026-12-01T10:00:00-06:00` (1600Z), `draft: false`,
   `featuredOnHome: true`, and a `lastmod`.
3. It is **committed and clean**. The deploy builds the push, not the disk, so an
   uncommitted edit is a page that will not be there; the runner refuses it.

## Guards, and why each one exists

| Condition | Exit | Why |
|---|---|---|
| Today is not 2026-12-01 | 0 | launchd has no `Year` key, so `Month 12 / Day 1` fires every year. A job that alerts every December about a piece it will never publish trains its reader to ignore the alert. |
| The article is missing | 3 | A release job that fires with nothing to release publishes nothing and says nothing. |
| `draft: false` absent | 3 | A draft builds to no page, and the failure is a 404 an hour later. |
| Untracked, or modified | 3 | The deploy builds the commit. Releasing a working file publishes whatever the tree held at 10:00. |
| `gh` missing or unauthenticated | 1 | The token lives in the login keychain, which a LaunchAgent reaches only in a logged-in session; without the check it surfaces as one opaque dispatch failure. |
| The page does not answer after the dispatch | the dispatch's code | `scripts/verify-published.py` requires the page's own `<title>` to carry the article's title. |

Exit 0 also covers "the page already answers", which is what a wake after a
missed fire looks like.

## Running it by hand

```bash
GROUND_STOP_CONCLUSION_TODAY=2026-12-01 scripts/ground-stop-conclusion-release-runner.sh
```

The clock is injectable for exactly this, and so a smoke run can prove the guards
on any afternoon. A run with the real date **will** dispatch a Pages build; that
is the release, not a rehearsal.

## Uninstall it after the run

A one-off job is uninstalled after it succeeds, not left to its date guard:

```bash
launchctl bootout gui/"$(id -u)"/com.huffmanwrites.ground-stop-conclusion-release
rm ~/Library/LaunchAgents/com.huffmanwrites.ground-stop-conclusion-release.plist
```

Then remove the row from the scheduled-jobs table in `CLAUDE.md`. The repo copy
of the plist, the runner and this skill stay as the record, as the Senate,
Sagan and Veterans runners did.
