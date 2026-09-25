#!/usr/bin/env python3
"""Guard against a credential that exists in more than one place and disagrees.

Why this exists. On 2026-09-24 the fal.ai key was found to fail with HTTP 401
on every documented path — the login keychain item, ~/.secrets, and the
FAL_KEY that .zshrc exports from the keychain all held the same stale value —
while a gitignored `.fal_token` at the repo root held one that worked. A
session that read the docs failed; a session that happened to know about the
dotfile succeeded. It cost time in two consecutive sessions, and neither
session could see why, because the only way to discover it was to try the key
and watch it fail.

Nothing was watching for that shape, and the shape is general: **a credential
copied into a second home drifts from the first, and nothing announces it.** A
stale copy is invisible — it has the right length, the right prefix, and the
right home; it is only wrong in a way you learn by spending it.

So this checks two things, one offline and one online:

  1. DRIFT (offline, default). For every credential with more than one home,
     resolve each home and compare by hash. Two homes that disagree is a bug
     in either case — one of them is stale and the other is about to be
     overwritten by whatever reads the stale one. A listed legacy repo-local
     file that has reappeared is reported too: the repo is not a credential
     store, and a third copy is exactly how the two-home problem starts.

  2. LIVENESS (--online). Ask the provider whether the resolved key
     authenticates. For fal.ai this is a GET on a request id that cannot
     exist: a good key answers `404 Request not found`, a stale key answers
     `401 invalid key credentials`. It submits nothing, generates nothing, and
     costs nothing — the point is to detect a dead key without spending it.

Values are never printed. Only a short SHA-256 prefix, so a finding is
comparable across runs without putting a secret in a log file.

Exit codes: 0 clean, 1 problems found, 2 the check could not run.

Usage:
  check-secrets.py                 # drift only (no network)
  check-secrets.py --online        # drift + fal.ai liveness probe
  check-secrets.py --quiet
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECRETS_FILE = Path.home() / ".secrets"

# The registry. One entry per credential that has a keychain home. Adding a
# credential means adding it here and nowhere else — the same rule as the
# docket registry, so a new key never means editing the runner.
#
# `legacy_repo_files` names files that once held this credential in the repo
# and must not come back. `.fal_token` is the one that shipped; it is listed so
# its reintroduction fails here rather than waiting for the next 401.
CREDENTIALS: "list[dict]" = [
    {
        "name": "FAL_KEY",
        "keychain": "huffmanwrites-fal",
        "secrets_var": "FAL_KEY",
        "legacy_repo_files": [".fal_token"],
        "probe": "fal",
    },
    {
        "name": "OLLAMA_API_KEY",
        "keychain": "huffmanwrites-ollama",
        "secrets_var": "OLLAMA_API_KEY",
        "legacy_repo_files": [],
        "probe": None,
    },
    {
        "name": "SENDFOX_CLIENT_SECRET",
        "keychain": "huffmanwrites-sendfox",
        "secrets_var": "SENDFOX_CLIENT_SECRET",
        "legacy_repo_files": [],
        "probe": None,
    },
    {
        "name": "FIRECRAWL_API_KEY",
        "keychain": "huffmanwrites-firecrawl",
        "secrets_var": "FIRECRAWL_API_KEY",
        "legacy_repo_files": [],
        "probe": None,
    },
]


def fingerprint(value: "str | None") -> "str | None":
    """A short, stable label for a secret. Never returns the secret itself."""
    if not value:
        return None
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def keychain_available() -> bool:
    """Whether this machine has a login keychain to read.

    CI runs on Linux with no keychain and no secrets, and this check has
    nothing to say there. The distinction that matters is *facility present but
    item missing* (a real problem, reported) versus *no facility at all* (CI,
    skipped) — collapsing the two would either fail every CI build for the
    right reason at the wrong time, or hide a deleted key on the Mac.
    """
    if sys.platform != "darwin":
        return False
    from shutil import which
    return which("security") is not None


def keychain_lookup(service: str) -> "str | None":
    """Read a login-keychain generic password, the documented primary home."""
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", ""),
             "-s", service, "-w"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def secrets_lookup(var: str) -> "str | None":
    """Read a variable from ~/.secrets, the documented fallback home.

    Accepts `export VAR=...` or `VAR=...`, with or without surrounding quotes.
    """
    if not SECRETS_FILE.exists():
        return None
    for line in SECRETS_FILE.read_text(errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#") or "=" not in s:
            continue
        key, _, val = s.partition("=")
        if key.strip().removeprefix("export ").strip() != var:
            continue
        return val.strip().strip('"').strip("'") or None
    return None


def resolve_homes(cred: dict) -> "dict[str, str | None]":
    """Every place this credential is supposed to live, resolved to a value."""
    return {
        f"keychain:{cred['keychain']}": keychain_lookup(cred["keychain"]),
        f"~/.secrets:{cred['secrets_var']}": secrets_lookup(cred["secrets_var"]),
    }


def compare_homes(name: str, homes: "dict[str, str | None]") -> "list[str]":
    """The rule, as a pure function so it can be tested without a keychain.

    Given one credential's homes and their resolved values, return the problems
    with them. Two homes that are both present must agree; a home that is
    missing leaves the documented fallback dead.
    """
    problems = []
    present = {k: v for k, v in homes.items() if v}

    if not present:
        problems.append(
            f"{name}: no value in any home "
            f"(checked {', '.join(homes)}). If this key is retired, remove its "
            f"entry from CREDENTIALS in this script."
        )
    elif len(present) == 1:
        got = next(iter(present))
        missing = next(k for k in homes if k not in present)
        problems.append(
            f"{name}: present in {got} but missing from {missing}. "
            f"The runners fall back to ~/.secrets, so the fallback is dead."
        )
    else:
        fp = {k: fingerprint(v) for k, v in present.items()}
        if len(set(fp.values())) > 1:
            detail = ", ".join(f"{k}={v}" for k, v in fp.items())
            problems.append(
                f"{name}: homes DISAGREE — one of them is stale "
                f"({detail}). Reconcile with `security add-generic-password -U` "
                f"and update ~/.secrets to match."
            )
    return problems


def check_drift(cred: dict) -> "list[str]":
    """Problems with this credential's homes, as human-readable strings.

    The rule is that the homes must agree. Two homes that differ means one is
    stale, and which one is stale cannot be told from here — so both are
    reported with their fingerprints, and the fix is to reconcile them.
    """
    problems = compare_homes(cred["name"], resolve_homes(cred))

    for rel in cred.get("legacy_repo_files", []):
        path = REPO / rel
        if path.exists():
            problems.append(
                f"{cred['name']}: a repo-local copy exists at {rel}. The repo is "
                f"not a credential store — this is the third copy that starts the "
                f"drift. Delete it and read the keychain."
            )
    return problems


def probe_fal(key: str, timeout: float = 20.0) -> "tuple[str, str]":
    """Ask fal.ai whether this key authenticates, without spending anything.

    A GET on a request id that cannot exist is the cheapest possible auth
    check: a live key answers 404 (the request is not found), a stale key
    answers 401. No generation is submitted, so this cannot cost money or
    produce an image — which is what makes it safe to run every week.

    Returns (verdict, detail) where verdict is ok / auth-failed / unverified.
    """
    url = ("https://queue.fal.run/fal-ai/flux/"
           "requests/00000000-0000-0000-0000-000000000000")
    req = urllib.request.Request(url, headers={"Authorization": f"Key {key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return "ok", f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            try:
                body = json.loads(e.read().decode(errors="replace"))
                detail = body.get("detail", "")
            except (ValueError, OSError):
                detail = ""
            return "auth-failed", f"HTTP 401 {detail}".strip()
        if e.code >= 500:
            # The provider is broken, not the key. Reporting this as success
            # would be the exact shape of bug this gate exists to catch: a
            # verdict that says OK while blind to the thing it checks.
            return "unverified", f"HTTP {e.code} (provider error, key not judged)"
        # Any other 4xx means the key was accepted and the request reached the
        # API: 404 is the expected answer for a request id that cannot exist.
        return "ok", f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return "unverified", f"could not reach fal.ai ({e})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--online", action="store_true",
                    help="also probe each key's provider to confirm it authenticates")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    if not keychain_available():
        # CI (Linux): no keychain, no ~/.secrets, nothing to check and no
        # network sweep worth making. Pass with a note rather than fail — a
        # gate that cannot run is not a gate that found something.
        if not args.quiet:
            print("secrets: skipped — no login keychain on this platform (expected in CI)")
        return 0

    problems: "list[str]" = []
    unverified: "list[str]" = []

    for cred in CREDENTIALS:
        cred_problems = check_drift(cred)
        problems.extend(cred_problems)

        if args.online and cred.get("probe") == "fal":
            key = (keychain_lookup(cred["keychain"])
                   or secrets_lookup(cred["secrets_var"]))
            if not key:
                problems.append(f"{cred['name']}: nothing to probe (no value in any home)")
                continue
            verdict, detail = probe_fal(key)
            if verdict == "auth-failed":
                problems.append(
                    f"{cred['name']}: the resolved key does NOT authenticate "
                    f"({detail}). Every image-generation path will fail."
                )
            elif verdict == "unverified":
                unverified.append(f"{cred['name']}: {detail}")
            elif not args.quiet:
                print(f"  {cred['name']}: authenticates ({detail})")

    for u in unverified:
        print(f"  unverified: {u}")

    if problems:
        print("secrets: PROBLEMS FOUND")
        for p in problems:
            print(f"  - {p}")
        return 1

    if not args.quiet:
        tail = ", keys authenticate" if args.online else ""
        print(f"secrets: OK — {len(CREDENTIALS)} credential(s) checked, "
              f"homes agree{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
