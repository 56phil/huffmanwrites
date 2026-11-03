#!/bin/bash
# install-secret.sh — install one credential into the two homes
# `check-secrets.py` reads, without the value ever reaching a transcript, a
# shell history, a repository file, or a process argument list.
#
# Usage:
#   scripts/install-secret.sh FEC_API_KEY            # prompts; nothing echoes
#   printf '%s' "$KEY" | scripts/install-secret.sh FEC_API_KEY
#   scripts/install-secret.sh --list
#   scripts/install-secret.sh --help
#
# Why this exists (2026-11-02). The convenient way to give an agent a key is to
# paste it into the conversation, and that puts it in the session transcript and
# sends it to whatever model endpoint is serving the session — on this machine a
# cloud one. The key still works, still authenticates, and nothing in the gate
# set can see that it has been exposed. This script is the alternative: you type
# the value once at a prompt the agent never sees, and it is written straight to
# the keychain and `~/.secrets`.
#
# Two rules it inherits from the repo:
#
#   * **The registry is `check-secrets.py`'s `CREDENTIALS` and nothing else.**
#     This script reads it rather than carrying a second copy, so a credential
#     is declared in one place and its keychain service cannot drift.
#   * **The value is never printed.** Success reports the fingerprint the gate
#     already uses, which is a hash prefix, not the secret.
#
# Options:
#   --no-keychain   write `~/.secrets` only. For tests and for CI, where there
#                   is no login keychain; macOS writes both homes by default.
#   --no-verify     skip the liveness probe (the gate run at the end).
#
# Environment:
#   INSTALL_SECRET_SECRETS   override the `~/.secrets` path (tests use this);
#                            `HOME` also works, since the default is `$HOME/.secrets`.
#   INSTALL_SECRET_STATE     override `security`'s keychain search list (unused
#                            in normal runs; present so a test can point the
#                            keychain somewhere disposable).
#
# There is no `-k` option on `security add-generic-password` — measured
# 2026-11-02, `security: illegal option -- k` — so a test cannot redirect this
# script's keychain write to a throwaway file. `TestInstallSecret` puts a stub
# `security` on PATH instead, which is also the stronger assertion: it pins the
# service name, the `-U` flag and the fact that the value arrives on stdin and
# not in argv.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"
SECRETS="${INSTALL_SECRET_SECRETS:-$HOME/.secrets}"
USE_KEYCHAIN=1
VERIFY=1

usage() {
    sed -n '2,34p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# Look a credential up in the registry. Prints "<keychain service>\t<env var>".
# Exits 4 for a name the registry does not carry, so a typo can never write a
# new variable into `~/.secrets` that nothing reads.
registry_lookup() {
    python3 -c '
import importlib.util, sys
path, name = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("check_secrets", path)
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)
for c in cs.CREDENTIALS:
    if c["name"] == name:
        print(c["keychain"] + "\t" + c["secrets_var"])
        raise SystemExit(0)
sys.stderr.write("unknown credential: " + name + "\n")
raise SystemExit(4)
' "$HERE/check-secrets.py" "$1"
}

registry_list() {
    python3 -c '
import importlib.util, sys
spec = importlib.util.spec_from_file_location("check_secrets", sys.argv[1])
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)
for c in cs.CREDENTIALS:
    print("  " + c["name"].ljust(26) + c["keychain"])
' "$HERE/check-secrets.py"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --list) registry_list; exit 0 ;;
        --help|-h) usage; exit 0 ;;
        --no-keychain) USE_KEYCHAIN=0 ;;
        --no-verify) VERIFY=0 ;;
        --*) echo "error: unknown option $1" >&2; exit 2 ;;
        *) [ -z "${NAME:-}" ] || { echo "error: one credential per run" >&2; exit 2; }; NAME="$1" ;;
    esac
    shift
done

if [ -z "${NAME:-}" ]; then
    echo "error: name the credential to install, or --list." >&2
    echo >&2
    registry_list >&2
    exit 2
fi

entry="$(registry_lookup "$NAME")" || exit 4
SERVICE="${entry%%$'\t'*}"
VAR="${entry##*$'\t'}"

# Read the value. From a terminal: twice, unrounded, echoing nothing. From a
# pipe: one line, which is what a caller that already holds it will send.
value=""
if [ -t 0 ]; then
    printf 'value for %s: ' "$VAR" >&2
    IFS= read -rs value || true
    printf '\n' >&2
    printf 'again, to confirm: ' >&2
    IFS= read -rs again || true
    printf '\n' >&2
    if [ "$value" != "$again" ]; then
        echo "error: the two entries differ; nothing written." >&2
        exit 3
    fi
else
    IFS= read -r value || true
fi

# A key is one line of non-blank text. Rejecting whitespace here rather than
# trimming it means an accidental trailing space is reported, not silently
# corrected into a key that fails at the provider and reads as a stale one.
case "$value" in
    '') echo "error: empty value; nothing written." >&2; exit 3 ;;
    *[[:space:]]*) echo "error: the value contains whitespace or a newline; nothing written." >&2; exit 3 ;;
esac

# ~/.secrets: replace this variable's line if it exists, append it if not, and
# never write a second copy. Atomic replace so an interrupted run cannot leave a
# half-written file where the credential used to be.
printf '%s' "$value" | NAME="$VAR" SECRETS="$SECRETS" python3 -c '
import os, pathlib, sys
value = sys.stdin.read()
path = pathlib.Path(os.environ["SECRETS"])
name = os.environ["NAME"]
lines = path.read_text(errors="replace").splitlines() if path.exists() else []
kept = [l for l in lines if not l.startswith(name + "=")]
kept.append(name + "=" + value)
tmp = path.with_name(path.name + ".tmp")
tmp.write_text("\n".join(kept) + "\n")
tmp.chmod(0o600)
tmp.replace(path)
path.chmod(0o600)
'

if [ "$USE_KEYCHAIN" = 1 ] && command -v security >/dev/null 2>&1; then
    # Two lines on stdin: `security` reads the item's password and its
    # confirmation, which is the only mode of this command that keeps the value
    # out of argv. `-U` updates an existing item rather than failing on it.
    printf '%s\n%s\n' "$value" "$value" |
        security add-generic-password -U -s "$SERVICE" -a "$USER" -w >/dev/null
    echo "installed $VAR -> keychain $SERVICE + $SECRETS"
else
    echo "installed $VAR -> $SECRETS (keychain skipped)"
fi

unset value again

if [ "$VERIFY" = 1 ]; then
    echo
    python3 "$HERE/check-secrets.py" --online
fi
