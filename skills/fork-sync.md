# Skill: Fork Sync

The writer's-adjacent brief for `com.huffmanwrites.fork-sync`, the job that keeps
every GitHub fork under this account fast-forwarded onto its upstream and keeps
Dependabot switched on. It publishes nothing and touches no file under
`content/`; read `skills/scheduled-job.md` for the plist / runner / skill / test
contract this job also follows.

## What the job is for

A fork rots silently. Nothing on GitHub says that a fork of a patched project is
itself unpatched, and the two switches that would say so — Dependabot alerts and
Dependabot security updates — are **off by default on a fork**. Measured
2026-10-17 across the eight forks under `56phil`: every one had
`dependabot_security_updates: disabled`, one was **1,252 commits** behind its
upstream, and no job, no gate and no notification anywhere could see either fact.

The first run, with the switches on, surfaced **176 open Dependabot alerts** across
three of the eight forks — 16 critical, 84 high, 66 medium, 10 low:

| Fork | Alerts | Worst | Concentrated in |
|---|---|---|---|
| `56phil/bigpowers` | 112 | 8 critical, 48 high | `js-yaml`, `ip-address`, `fast-uri`, `hono`, `devalue` |
| `56phil/diagram-design` | 36 | 24 high | `pillow` / `Pillow` |
| `56phil/tuts` | 28 | 8 critical, 12 high | `golang.org/x/crypto`, `brace-expansion`, `minimatch` |

Every one of those advisories lives in the **upstream** project — the forks are
byte-identical to their upstreams — and every one of them had been sitting there
unpublished to its owner for as long as the fork had, because GitHub does not turn
Dependabot on for a fork. That is the whole case for this job: not a hypothetical
risk, 176 findings that no other surface in this repo or on GitHub could see.

**A count from `--paginate` is per page, and reading the first line reports a cap
as a total.** Measured on the same run: `56phil/bigpowers` printed `100` from a
real 112, and the summary line summed those caps into a figure that was simply
wrong. `count_from_pages()` sums the lines, and `TestForkSyncJob` pins both halves
— sum, and a blank read staying distinguishable from a repository with no alerts.

## The two halves, and why they are different in kind

**Up to date.** `POST /repos/{owner}/{repo}/merge-upstream` fast-forwards the
fork's default branch onto its upstream. It is non-destructive *by
construction*: GitHub refuses with 409 when the fork carries commits the
upstream does not, so a fork with local work is never rewritten. The script never
passes a force flag, and there is none to pass.

**Secure.** `PUT /repos/{owner}/{repo}/vulnerability-alerts` turns Dependabot
alerts on, and `PATCH /repos/{owner}/{repo}` with
`security_and_analysis[dependabot_security_updates][status]=enabled` turns
security updates on. Both are idempotent, both work with the `repo` scope the
`gh` token already carries, and neither needs a new credential — which matters,
because this repo's rule is one home per credential and `gh` already owns this
one (the login keychain, `gh:github.com`).

## The decision: reports do not fail, and divergence does

Exit non-zero only when the job could not do its work:

| State | Exit | Why |
|---|---|---|
| every fork current or ahead | 0 | nothing to do |
| a fork fast-forwarded | 0 | the job's purpose, done |
| **a fork diverged** | **1** | `merge-upstream` refuses by design and only a human can choose rebase or reset |
| **a fork unreadable** | **1** | a repository that cannot be read is a repository nothing is watching |
| an open Dependabot or secret-scanning alert | 0 | see below |

An open alert is deliberately **not** a failure. A fork cannot fix a vulnerable
dependency: the fix belongs upstream and arrives through the sync above. A job
that exits non-zero for a condition its reader cannot act on is a job whose alert
gets learned as noise — the rule `skills/scheduled-job.md` states for every
start-date guard here. The report is where a human reads them; the alert is for
the state where the job itself is broken.

**`MIN_FORKS` is the coverage floor.** A fork list that comes back empty means
the request broke, not that the account has no forks. Reporting "0 forks, all
healthy" is the failure mode this repo's coverage rule exists for — a check that
inspects nothing reports OK — so an empty enumeration is an error, not a clean
run. The script also prints `coverage: N forks`, the same shape every other gate
here uses.

**One interaction to know about before changing anything.** Dependabot *security
updates* being on means GitHub may open a fix PR against the fork. Merging one
diverges the fork from its upstream, and from that moment `merge-upstream`
refuses it forever — the two halves of this job would be working against each
other. It is left on deliberately: the user asked for the forks to be *secure*,
GitHub opens no PR on its own (measured: 0 open pull requests across the account
after the first run enabled both switches on all eight forks), and a merge is a
deliberate human choice whose consequence the sync half reports. If that trade
stops being worth it, the one-line change is to drop the `PATCH` in
`enable_security` and leave alerts on.

## Files

| File | Role |
|---|---|
| `scripts/check-forks.py` | enumerate, compare, sync, enable, report. Read-only without `--apply`. |
| `scripts/fork-sync-runner.sh` | preflight (`gh` present and authenticated), run the checker with `--apply`, alert on a non-zero exit |
| `scripts/com.huffmanwrites.fork-sync.plist` | Saturday 04:00 CT, one `StartCalendarInterval` dict |
| `test_gates.py` → `TestForkSyncJob` | the wiring, asserted against the runner's text |

## Manual use

```bash
python3 scripts/check-forks.py                     # report only, changes nothing
python3 scripts/check-forks.py --apply             # sync and enable
FORK_SYNC_DRY_RUN=1 bash scripts/fork-sync-runner.sh   # the whole pipeline, no writes
```

The report lands in `~/Library/Logs/fork-sync-report.md`; the log in
`~/Library/Logs/fork-sync.out.log`. `--skip owner/repo` (repeatable) leaves a fork
alone — the one thing a dynamic enumeration cannot express.

## Schedule

Saturday 04:00 CT, an hour the machine is usually awake and two hours after
`com.huffmanwrites.emergency-backup` (Saturday 02:00). `StartCalendarInterval`
uses local wall-clock time, so the fire follows the DST change by itself and
needs no second cron — unlike the Pages deploy, whose 07:00 CT embargo needed a
second entry in `.github/workflows/hugo.yml`.
