#!/bin/bash
# Shared failure alert for the huffmanwrites scheduled jobs.
#
# Usage: alert-failure.sh <job-name> <exit-code> [detail]
#
# These jobs run unattended under launchd. Before this existed a failure left
# nothing but a log line: on 2026-09-06 the Senate job exited 127 and then 1,
# and the first real ninety-days run would have failed the same way — silently.
#
# Two channels on purpose. The durable record always lands, even if the machine
# is asleep, the GUI session is absent, or Notification Center drops the banner.
# The notification is the part that actually gets noticed.
#
# Contract: never changes the caller's exit status, never fails, and is a no-op
# on success. Safe to call under `set -euo pipefail`.
set +e

JOB="${1:-unknown}"
RC="${2:-1}"
DETAIL="${3:-}"

ALERT_LOG="$HOME/Library/Logs/huffmanwrites-alerts.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

# Success is not an alert. Exit quietly so callers can invoke this
# unconditionally with whatever code they ended up with.
#
# Validate RC before comparing: a non-numeric value would make `[ "$RC" -eq 0 ]`
# print "integer expression expected" to the caller's stderr log and then
# evaluate false, raising a spurious alert. Anything unparseable is treated as a
# failure, which is the safe direction — an alert on a bad code beats silence.
case "$RC" in
  ''|*[!0-9]*) ;;
  0) exit 0 ;;
esac

LINE="$STAMP: FAILED $JOB (exit $RC)"
[ -n "$DETAIL" ] && LINE="$LINE — $DETAIL"

# 1. Durable record. Written before the notification so a crash in osascript
#    still leaves evidence on disk.
printf '%s\n' "$LINE" >> "$ALERT_LOG" 2>/dev/null

# 2. Notification Center banner. LaunchAgents run inside the user's GUI session,
#    so this reaches the desktop. The body is passed as an argument rather than
#    interpolated into the AppleScript source, which keeps quotes and
#    backslashes in the log line from breaking the script.
/usr/bin/osascript \
  -e 'on run argv' \
  -e 'display notification (item 1 of argv) with title "huffmanwrites job failed" subtitle (item 2 of argv) sound name "Basso"' \
  -e 'end run' \
  "$LINE" "$JOB" >/dev/null 2>&1

exit 0
