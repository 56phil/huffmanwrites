#!/bin/bash
# Weekly GitHub fork hygiene.
# Invoked by launchd (com.huffmanwrites.fork-sync) every Saturday at 04:00 CT.
#
# Fast-forwards every fork under the account onto its upstream and turns on the
# Dependabot alerts and security updates that are off by default on a fork.
# Writes a report to ~/Library/Logs/fork-sync-report.md.
#
# What is deliberately NOT here, and why: a Hugo build, a content gate, and the
# publish tail. This job touches no file in content/, so the two-build rule and
# the frontmatter gate have no subject. It also does not commit — it changes
# state on GitHub, which is where the report's evidence lives.
#
# The failure that means something: a fork that has DIVERGED (commits upstream
# does not) cannot be fast-forwarded, so the job reports it and exits non-zero.
# An OPEN dependabot alert does not fail the run: a fork cannot fix a vulnerable
# dependency, the fix arrives through the sync above, and a job that alerts on a
# condition its reader cannot act on is a job whose alert gets ignored.
set -euo pipefail

# launchd does not source the shell, so PATH misses /opt/homebrew/bin (gh,
# python3). Export the full interactive PATH explicitly.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, so a hardcoded "/Users/<who>/Developer/<repo>" names a
# missing file, python3 exits 2, and the Pages deploy goes red (2026-10-08). A
# test in scripts/test_gates.py holds the rule for every script under scripts/.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$REPO/scripts/check-forks.py"
LOG_DIR="$HOME/Library/Logs"
OUT_LOG="$LOG_DIR/fork-sync.out.log"
ERR_LOG="$LOG_DIR/fork-sync.err.log"
REPORT="$LOG_DIR/fork-sync-report.md"

# Timestamp each event as it happens, so the log shows how long each phase took
# rather than stamping every line with the run's start time.
stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

cd "$REPO"

echo "$(stamp): starting fork sync" >> "$OUT_LOG"

# 0. Preflight: `gh` must exist and be authenticated. Every API call below goes
#    through it, and its token lives in the login keychain, which a LaunchAgent
#    reaches only inside a logged-in GUI session. Without this check a locked
#    keychain surfaces as eight unrelated "cannot read repository" errors and a
#    report that reads like the account lost its forks.
if ! command -v gh >/dev/null 2>&1; then
  echo "$(stamp): gh not found on PATH, aborting" >> "$OUT_LOG"
  "$REPO/scripts/alert-failure.sh" "fork-sync" 1 "gh not found on PATH; see $OUT_LOG" || true
  exit 1
fi

set +e
AUTH_OUT="$(gh auth status 2>&1)"
AUTH_RC=$?
set -e
if [ "$AUTH_RC" -ne 0 ]; then
  echo "$(stamp): gh is not authenticated, aborting" >> "$OUT_LOG"
  echo "$AUTH_OUT" >> "$ERR_LOG"
  "$REPO/scripts/alert-failure.sh" "fork-sync" 1 "gh not authenticated; see $ERR_LOG" || true
  exit 1
fi
echo "$(stamp): gh authenticated" >> "$OUT_LOG"

# 1. Sync and report. `FORK_SYNC_DRY_RUN=1` exercises the whole path — auth,
#    enumeration, compare, report — and performs no write, so the pipeline is
#    provable without being run against the account. Mirrors REPORT_DRY_RUN in
#    scripts/publish-report.sh.
APPLY=(--apply)
[ -n "${FORK_SYNC_DRY_RUN:-}" ] && APPLY=(--dry-run)
[ -n "${FORK_SYNC_DRY_RUN:-}" ] && echo "$(stamp): DRY RUN — no repository will be changed" >> "$OUT_LOG"

set +e
python3 "$CHECKER" "${APPLY[@]}" --report "$REPORT" >> "$OUT_LOG" 2>> "$ERR_LOG"
RC=$?
set -e

echo "$(stamp): fork sync finished (exit $RC)" >> "$OUT_LOG"

# Unattended job: a non-zero exit leaves more than a log line. No-op on success.
# `|| true` keeps a missing/failing alert from replacing the job's real exit code.
"$REPO/scripts/alert-failure.sh" "fork-sync" "$RC" "see $REPORT and $OUT_LOG" || true

exit "$RC"
