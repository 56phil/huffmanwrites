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
# This probe is the other half, and it now HEALS as well as reports. The login
# job covers "the app was never open"; it cannot cover "the app was open and then
# died", because that is a state no login-time job is running to see. On
# 2026-10-11 the app was SIGTERMed at 05:49 and the 06:00 SITREP run found the
# port dead and aborted: an edition published two hours late, and a watchdog
# alert raised for an edition that did exist, just after the check. So before
# raising the alert the probe opens the app itself and waits — see `_ollama_wait`
# and the reopen block in `ollama_require` below. It is not a KeepAlive: it opens
# the app only when a job is actually blocked on it, at the minute that job runs.
#
# One definition, sourced by all eight runners. The repo has already learned
# this lesson twice — the featuredOnHome rule and the gate list each drifted
# when they existed in more than one place — so the probe is written once.
#
# Usage, after ANTHROPIC_BASE_URL is exported:
#   ollama_require "$JOB" "$OUT_LOG"
# It fast-passes when the server already answers (the common case, silent apart
# from one line); otherwise it reopens the app, waits up to
# OLLAMA_PROBE_START_WAIT for it, and only then, on failure, writes the reason to
# OUT_LOG, raises the shared alert, and returns 1 (callers run under `set -e`, so
# a bare call aborts the run; an explicit `|| exit 1` is also fine).

# Derived from this file's own location, never baked in: inside a sourced file
# `BASH_SOURCE[0]` is the sourced file, and the gate tests execute the runners
# that source this one from a CI checkout at a different path. Same rule as the
# runners — a hardcoded checkout path names a missing file (2026-10-08).
OLLAMA_PROBE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLLAMA_PROBE_ALERT="${OLLAMA_PROBE_ALERT:-$OLLAMA_PROBE_DIR/alert-failure.sh}"
OLLAMA_PROBE_TRIES="${OLLAMA_PROBE_TRIES:-10}"
OLLAMA_PROBE_TIMEOUT="${OLLAMA_PROBE_TIMEOUT:-5}"

# Self-heal. The login job (`com.huffmanwrites.ollama-app`) opens the app once,
# at login, and is deliberately NOT a KeepAlive: it must not fight a person who
# quits the app. That leaves a gap this probe now closes, and the gap cost a
# report on 2026-10-11: the app was SIGTERMed at 05:49 (its updater had the
# 0.40.3 update staged and was re-checking hourly), and the 06:00 SITREP run found
# :11434 dead and aborted — a published edition late by two hours, and a watchdog
# alert for an edition that did exist, just after the check. Nothing reopened the
# app, because "the app has quit" is exactly the state no login-time job can see.
#
# So before giving up, a job that is about to need the server opens the app
# itself and waits for it. This is NOT KeepAlive — it opens the app only when a
# job is actually blocked on it, never on a timer, so it cannot resurrect an app
# the user closed on purpose at any moment other than the minute a scheduled job
# runs. It reuses the login job's own move (`open -a`, which starts the app or
# brings it forward, never a second `ollama serve`).
OLLAMA_APP="${OLLAMA_APP:-/Applications/Ollama.app}"
# Indirection so a test can exercise the reopen path without launching the app.
OLLAMA_PROBE_OPEN="${OLLAMA_PROBE_OPEN:-/usr/bin/open -a}"
# How long to wait for the app after reopening it. Matches ollama-app-launch.sh's
# OLLAMA_APP_WAIT: the app took ~50 s to bind on a loaded login on 2026-10-07.
OLLAMA_PROBE_START_WAIT="${OLLAMA_PROBE_START_WAIT:-90}"

# Poll BASE until it answers or the deadline passes. Returns 0 on reachability.
# /api/version is the cheapest endpoint that proves the server is answering
# HTTP. It does not spend a model call, and it needs no auth: the local server
# answers /v1/messages with no valid key too, so a key check here would test the
# wrong thing. Reachability is the whole question.
_ollama_wait() {
  local base="$1" deadline="$2" timeout="$3" tries="$4"
  local start now attempt=0
  start="$(date +%s)"
  while :; do
    if curl -fsS -m "$timeout" "$base/api/version" >/dev/null 2>&1; then
      return 0
    fi
    now="$(date +%s)"
    [ $(( now - start )) -ge "$deadline" ] && return 1
    # `tries` bounds the fast pre-check; the deadline bounds the post-reopen
    # wait. Whichever is smaller stops the loop.
    if [ -n "$tries" ] && [ "$attempt" -ge "$tries" ]; then
      return 1
    fi
    attempt=$((attempt + 1))
    sleep 1
  done
}

ollama_require() {
  local job="${1:-unknown}" out_log="${2:-/dev/null}"
  local base="${ANTHROPIC_BASE_URL:-http://localhost:11434}"
  local stamp

  # Fast pass: if the server is already up (the common case), do nothing else.
  if _ollama_wait "$base" "$OLLAMA_PROBE_TRIES" "$OLLAMA_PROBE_TIMEOUT" "$OLLAMA_PROBE_TRIES"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): Ollama reachable at $base" >> "$out_log"
    return 0
  fi

  # Not up. Reopen the app and wait properly, rather than failing a job the app
  # could still serve. `open -a` exits 0 the instant LaunchServices accepts the
  # request, so the wait, not the open, is what proves the server came back.
  stamp="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "$stamp: Ollama not reachable at $base; opening $OLLAMA_APP" >> "$out_log"
  $OLLAMA_PROBE_OPEN "$OLLAMA_APP" >> "$out_log" 2>&1 || true

  local start now elapsed
  start="$(date +%s)"
  if _ollama_wait "$base" "$OLLAMA_PROBE_START_WAIT" "$OLLAMA_PROBE_TIMEOUT" ""; then
    elapsed=$(( $(date +%s) - start ))
    echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): Ollama reachable at $base after ${elapsed}s (app reopened)" >> "$out_log"
    return 0
  fi

  echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): ABORTING — Ollama is not reachable at $base." >> "$out_log"
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): the app was reopened and given ${OLLAMA_PROBE_START_WAIT}s, and still did not answer, so this is not the app simply having been closed. Check that it is installed and can bind the port: open Ollama by hand, or read ~/.ollama/logs/app.log. 'launchctl print gui/\$UID/com.huffmanwrites.ollama-app' shows the login-time launch." >> "$out_log"
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z'): Ollama unreachable at $base; the writer never ran. See $out_log" >&2
  "$OLLAMA_PROBE_ALERT" "$job" 1 "Ollama unreachable at $base; see $out_log" || true
  return 1
}
