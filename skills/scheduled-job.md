# Skill: Adding or Editing a Scheduled Job

The checklist for adding a launchd job to this repo, or editing one that runs. It
is CLAUDE.md's "Scheduled jobs (launchd)" section made walkable: each rule was
earned by shipping the failure it prevents, so read the file named with it before
you change what it covers.

A job is four files: `scripts/com.huffmanwrites.<job>.plist`,
`scripts/<job>-runner.sh`, a skill in `skills/`, and a wiring class in
`scripts/test_gates.py`.

## 1. Repo copy and installed copy must agree

The plist lives in `scripts/` and installs to `~/Library/LaunchAgents/`. What runs
is the installed copy, so a repo change takes effect only after a reinstall (`cp`
to `~/Library/LaunchAgents/`, then `launchctl bootout` and `launchctl bootstrap`).
`scripts/check-plists.py` warns when the two differ: a repo showing the schedule
you intend while the job keeps the schedule you had.

## 2. One dict for one time a day, an array for more than one

`StartCalendarInterval` takes a dict with `Hour` and `Minute`, plus `Weekday` for a
weekly run (`scripts/com.huffmanwrites.senate-report.plist`). It also takes an
**array** of such dicts, and then the job fires at every time in the list:
`com.huffmanwrites.docket-watch` has carried an array of two since 2026-09-20 and
its log shows 07:30 and 18:30 both firing, every day, with the installed copy
identical to the repo copy. `com.huffmanwrites.sitrep-watchdog` uses the array
form for four daily checks. Both forms work in a LaunchAgent — an earlier version
of this rule asserted that launchd ignores an array "silently, so the job parses
cleanly and never fires", and that was wrong; the failure it was written for is
rule 3's illegal comment. `test_gates.py` (TestDailySitrep) asserts the daily
plist carries a single dict, which is how "one time a day" is written down, and
no `Weekday` key.

## 3. A malformed plist fails silently

`launchctl bootstrap` does not always report a malformed plist, so a broken file
becomes a schedule that never fires. `scripts/check-plists.py` (CI and local)
requires a `Label`, `ProgramArguments`, a schedule key, and an existing file at
every repo path named in `ProgramArguments`.

**The defect it exists for: a `--` inside an XML comment.** XML forbids a double
hyphen inside `<!-- -->`, and an em-dash typed as `--` is how it gets in: the file
refuses to parse and `plistlib`'s error does not say why. `check-plists.py` names
the cause; a comma is normally the fix.

## 4. A start-date guard must exit 0 and log why

A job installed before its first due date, or one with a last-run date, must exit
0 with a line explaining the skip (`senate-report-runner.sh` after 2026-11-02; the
Chiefs season guard off season). A non-zero exit raises the alert every week for
months, which teaches the reader to ignore it. `test_gates.py`
(TestChiefsRunnerContract) asserts the season guard exits zero.

## 5. A model-calling job probes Ollama before its writer runs

Every AI job sets `ANTHROPIC_BASE_URL=http://localhost:11434`, sources
`scripts/ollama-probe.sh`, and calls `ollama_require "$JOB" "$OUT_LOG"` before
`claude -p`. The server is the **Ollama desktop app**, which
`com.huffmanwrites.ollama-app` opens at login (`RunAtLoad`, no `KeepAlive`, via
`scripts/ollama-app-launch.sh`, which confirms the port answered). Without the
probe, a crashed app is a connection error mid-draft and an article that never
appears. `test_gates.py` (TestPublishLibrary) asserts all eight AI runners probe
before the writer. Point no job at a server binary: an earlier one ran
`ollama serve` and duplicated the app's server.

## 6. The runner runs the verification, not the writer

The gates are absent from the writer's allow-list, so a gate result in its summary
is unverifiable and must never be taken on trust. The runner runs the builds and
gates itself and logs the real exit codes (`report_build`, `run_report_gates` in
`scripts/publish-report.sh`). **Two builds, always.** The production build
excludes `draft: true`, so it says nothing about the file a drafting job just
wrote; the second build (`hugo --gc --minify --buildDrafts --destination <tmp>`)
renders it to a scratch destination, never to `public/`, which deploys.

## 7. Publishing or drafting is decided by what a gate failure costs

In a **publishing** job (Senate, docket, Chiefs, Weekly Satire, daily SITREP) a
gate failure **aborts the push**, because the gates are the only review the piece
gets. In a **drafting** job (ninety-days, repair-plan) the piece stays a
`draft: true` file and a failure is a note for Philip.

A publishing job must run `python3 scripts/check-links.py --file <article>
--online --titles`, the only check here that catches a link resolving to the wrong
page, invisible to a status code because the URL returns 200. Scope it with
`--file`: a corpus sweep cannot see a brand-new file. The gate list lives once
(`run_report_gates`) so it cannot drift; the ninety-days runner once lacked
`check-gallery-pages`, and a 404 shipped unnoticed.

## 8. The publish tail lives once, in `scripts/publish-report.sh`

Five publishing runners share it: preflight guard, SESSION_STATE entry, commit,
push, push verification, and the SimpleBrain mirror. A runner supplies only what
is specific to its series. Two things a new runner must get right:

- **Bind `JOB` before sourcing** (the library expands it under `set -u`). The
  docket and Senate runners omitted it, so their first real publish died with
  `JOB: unbound variable` after the writer and every gate had already succeeded.
- **`REPORT_DRY_RUN=1` exercises everything but the commit;
  `REPORT_SKIP_SIMPLEBRAIN=1` skips only the mirror.** The Chiefs job's historical
  `CHIEFS_DRY_RUN` and `CHIEFS_SKIP_SIMPLEBRAIN` names still work.

The SESSION_STATE entry is written by the runner from the real gate results, never
by the agent, which could only assert a result it did not produce. (The one
exception is still a report, not a prediction: the SimpleBrain bullet is written
before the mirror runs, so it names the log rather than claiming success.)

## 9. One fixed hero plate per series, pinned with `--plate`

Every installment of a series carries the same hero pair, reused like a masthead.
The runner pins it in the frontmatter gate (`--plate 115-sitrep`, or
`105-senate-race-report`), which `scripts/check-report-frontmatter.py` enforces by
comparing the article's four hero fields against the named plate. Never give an
installment its own hero: two installments carrying the same image is intended.
`test_gates.py` asserts the plate files exist.

## 10. The writer's allow-list is the narrow one

A runner grants the writer exactly what its skill tells it to run: it may read the
briefing pack and the skill and write one article file. It **may not** run `git`,
run `hugo`, or touch `SESSION_STATE.md`, because the runner owns all three. Every
`python3 scripts/<x>.py` the skill names must appear in the grant. `test_gates.py`
asserts the allow-list is free of `git`, `hugo`, and `SESSION_STATE`, and that
every named script is granted.

## 11. Logs and alerts have one shape

The plist sets `StandardOutPath` and `StandardErrorPath` to
`~/Library/Logs/<job>.out.log` and `<job>.err.log`, and the runner timestamps each
line as it happens (`stamp()`). A failure raises the shared alert through
`scripts/alert-failure.sh <job> <rc> [detail]`, which writes a durable line to
`~/Library/Logs/huffmanwrites-alerts.log` and posts a Notification Center banner.
It is a no-op on success and never changes a caller's exit status.
`check-plists.py` warns on a log file that has never been created.

## 12. Pin the wiring in `scripts/test_gates.py`, not the prose

Add a class to `scripts/test_gates.py` for the new job, asserting against the
runner's text with comments stripped: the ordering (pack before writer, preflight
before writer, `ARTICLE` bound before any use), the allow-list, the guards (a
missing article aborts; a start-date guard exits zero), the plist schedule, and
the plate files. A job's prose cannot be tested; its wiring can, and this repo has
shipped the wiring failure three times (the unbound `JOB`, the missing gate in the
list, the entry that asserted a mirror result it had not seen).

## The mistakes that shipped

- **A `--` inside an XML comment**, so the plist refused to parse and `plistlib`'s
  error hid the cause (rule 3).
- **An array of dicts under `StartCalendarInterval`**, silently ignored, so a job
  parsed cleanly and never fired (rule 2).
- **An unguarded start date** whose non-zero exit raised the alert every week,
  which is how a real alert gets learned as noise (rule 4).
- **A runner asserting a gate result it never ran** (2026-09-20 Senate: "both
  pass" for two absent scripts) (rule 6).
- **The `JOB: unbound variable` death on the first real publish** (docket and
  Senate, 2026-10-03) (rule 8).
- **Five Senate reports without `featuredOnHome: true`**, invisible because the
  build passed and every page returned 200 (rule 8).
