#!/bin/bash
# Reachability guard for the local Ollama server every AI-driven job depends on.
#
# SOURCED, not executed: `. "$REPO/scripts/ollama-probe.sh"`.
#
# Why this exists. Eight unattended jobs (the six report runners, wiki-check,
# repair-plan) set ANTHROPIC_BASE_URL=http://localhost:11434 and call the model
# through it. That server is the **Ollama desktop app's**. Before 2026-10-07
# nothing checked it was there, and the app's server lived only while the app
# happened to be open. The failure mode is quiet — a connection error in a log
# and an article that never appears — which is why wiki-check failed at 13:30 on
# 2026-09-28 and nobody noticed until the log was read a week later. The pending
# list carried the fix ("add a port probe to the shared preflight so the jobs
# fail loudly and early rather than mid-run") from that day.
#
# The durability half is settled, but not by the app's own login item: that was
# added on 2026-10-07, verified enabled, then silently dropped when the app was
# restarted (it reconciles its own login items on start). The enrolment now lives
# in a repo plist instead — `com.huffmanwrites.ollama-app` opens the app at login
# (`open -a`, RunAtLoad, no KeepAlive), so the server is up before the 07:00 jobs
# and one `ollama serve` is still the only server. An earlier LaunchAgent ran
# `ollama serve` directly and duplicated the app's server on the same port; it was
# retired the same day.
#
# This probe is the other half, and stays useful independently: if the app has
# quit, crashed, or failed to start, the job says so in one line at the top of its
# log and raises the failure alert, instead of spending a model call on a
# connection-refused error halfway through a draft.
#
# One definition, sourced by all eight runners. The repo has already learned
# this lesson twice — the featuredOnHome rule and the gate list each drifted
# when they existed in more than one place — so the probe is written once.
#
# Usage, after ANTHROPIC_BASE_URL is exported:
#   ollama_require "$JOB" "$OUT_LOG"
# On failure it writes the reason to OUT_LOG, raises the shared alert, and
# returns 1 (callers run under `set -e`, so a bare call aborts the run; an
# explicit `|| exit 1` is also fine). On success it returns 0 and is silent.

OLLAMA_PROBE_ALERT="${OLLAMA_PROBE_ALERT:-/Users/prh/Developer/huffmanwrites/scripts/alert-failure.sh}"
OLLAMA_PROBE_TRIES="${OLLAMA_PROBE_TRIES:-10}"
OLLAMA_PROBE_TIMEOUT="${OLLAMA_PROBE_TIMEOUT:-5}"

ollama_require() {
  local job="${1:-unknown}" out_log="${2:-/dev/null}"
  local base="${ANTHROPIC_BASE_URL:-http://localhost:11434}"
  local attempt=0

  while [ "$attempt" -lt "$OLLAMA_PROBE_TRIES" ]; do
    # /api/version is the cheapest endpoint that proves the server is answering
    # HTTP. It does not spend a model call, and it needs no auth: the local
    # server answers /v1/messages with no valid key too, so a key check here
    # would test the wrong thing. Reachability is the whole question.
    if curl -fsS -m "$OLLAMA_PROBE_TIMEOUT" "$base/api/version" >/dev/null 2>&1; then
      echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): Ollama reachable at $base" >> "$out_log"
      return 0
    fi
    attempt=$((attempt + 1))
    sleep 1
  done

  echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): ABORTING — Ollama is not reachable at $base after $OLLAMA_PROBE_TRIES tries." >> "$out_log"
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): is the Ollama desktop app running? Its server serves $base. com.huffmanwrites.ollama-app opens it at login, so if this fires the app has quit, crashed, or failed to start — open Ollama, or check 'launchctl print gui/\$UID/com.huffmanwrites.ollama-app'." >> "$out_log"
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): Ollama unreachable at $base; the writer never ran. See $out_log" >&2
  "$OLLAMA_PROBE_ALERT" "$job" 1 "Ollama unreachable at $base; see $out_log" || true
  return 1
}
