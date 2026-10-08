#!/bin/bash
# Opens the Ollama desktop app at login and PROVES its server came up.
#
# Run by com.huffmanwrites.ollama-app (RunAtLoad). It replaces a bare
# `open -a /Applications/Ollama.app` in the plist for one reason: `open` exits 0
# the instant LaunchServices accepts the request, so it reports success whether
# or not the app ever comes up and whether or not :11434 ever answers. "Did
# Ollama start at login?" then has no answer in any log, and on 2026-10-07 that
# is exactly the question that could not be settled: the job had fired (runs=1,
# BTM Last Use 19:01:45) and the server was up, but nothing on disk said so, and
# the app had come up `hidden` ~50 s after login. This script makes each login
# self-verifying, the same way the report runners verify their own output.
#
# It is NOT a KeepAlive. It runs once at login, waits for the server, logs what
# happened, and exits. If the app is closed by hand later, nothing reopens it;
# scripts/ollama-probe.sh is what makes that visible to the jobs that need it.
#
# Exit 0 = server reachable (logged with the elapsed time).
# Exit 1 = the app never produced a server; the shared alert is raised.
set -euo pipefail

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Derived from this script's own location, never a path baked in here: in CI the
# checkout sits elsewhere, so a hardcoded "/Users/<who>/Developer/<repo>" names a
# missing file, python3 exits 2, and the Pages deploy goes red (2026-10-08). A
# test in scripts/test_gates.py holds the rule for every script under scripts/.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="/Applications/Ollama.app"
ALERT="$REPO/scripts/alert-failure.sh"
OUT_LOG="$HOME/Library/Logs/ollama-app.out.log"
ERR_LOG="$HOME/Library/Logs/ollama-app.err.log"

# The runners read localhost; that is the address that must answer, not
# 127.0.0.1 (which is the same socket here, but localhost is what they use).
BASE="${ANTHROPIC_BASE_URL:-http://localhost:11434}"

# The app can take a while on a loaded login. 90 s is generous; measured start
# was ~50 s on 2026-10-07 with a load average above 10, and the poll succeeds
# immediately in the common case where the app is already running.
DEADLINE="${OLLAMA_APP_WAIT:-90}"
INTERVAL=2

stamp() { date '+%Y-%m-%d %H:%M:%S %Z'; }

echo "$(stamp): opening $APP" >> "$OUT_LOG"
if ! /usr/bin/open -a "$APP" 2>>"$ERR_LOG"; then
  echo "$(stamp): open -a $APP failed" >> "$OUT_LOG"
  "$ALERT" "ollama-app" 1 "could not open the app; see $OUT_LOG" || true
  exit 1
fi

start="$(date +%s)"
while :; do
  if curl -fsS -m 3 "$BASE/api/version" >/dev/null 2>&1; then
    elapsed=$(( $(date +%s) - start ))
    echo "$(stamp): Ollama server reachable at $BASE after ${elapsed}s" >> "$OUT_LOG"
    exit 0
  fi
  now="$(date +%s)"
  [ $(( now - start )) -ge "$DEADLINE" ] && break
  sleep "$INTERVAL"
done

echo "$(stamp): Ollama server NOT reachable at $BASE after ${DEADLINE}s" >> "$OUT_LOG"
echo "$(stamp): the app was opened; check that it is running and that its server bound the port" >> "$OUT_LOG"
"$ALERT" "ollama-app" 1 "the app did not produce a server within ${DEADLINE}s; see $OUT_LOG" || true
exit 1
