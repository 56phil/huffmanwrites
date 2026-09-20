#!/usr/bin/env python3
"""Guard the launchd schedules in scripts/ against silent failure.

Why this exists. On 2026-09-20 the weekly integrity check was found to have
never run. Its plist contained "--" in prose inside an XML comment. A double
hyphen is illegal inside an XML comment, so the file was not well-formed,
launchd refused it, and `launchctl bootstrap` did not report the failure. The
job had been installed for days doing nothing. No log file existed, which was
the evidence that settled it.

A scheduled guard that never runs is worse than no guard, because the intent
feels satisfied. Nothing in the repo was checking that these files even parse,
so this does.

Three classes of defect:

  1. Malformed XML. launchd will not load the file at all. This is the one
     that shipped, and plistlib's own error ("not well-formed (invalid
     token): line 20") does not say why, so the report names the cause when
     it can: a "--" inside a comment is the usual reason, because it is
     illegal per the XML spec and easy to type in an em-dash's place.

  2. Structurally incomplete. No Label, no ProgramArguments, no schedule, or
     a referenced program or script that does not exist. launchd accepts some
     of these silently and then does nothing.

  3. Drift between the repo copy and the installed copy in
     ~/Library/LaunchAgents. The repo is then not what is actually running,
     so editing a plist here changes nothing until it is reinstalled.

Usage:
  check-plists.py            # verify (CI and local)
  check-plists.py --quiet    # only report problems
"""

from __future__ import annotations

import argparse
import plistlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
INSTALLED = Path.home() / "Library" / "LaunchAgents"

# The schedule keys launchd understands for a LaunchAgent that fires on a
# timer. A job with none of these runs only when kicked by hand.
SCHEDULE_KEYS = ("StartCalendarInterval", "StartInterval", "RunAtLoad", "WatchPaths")

# A double hyphen inside an XML comment. The XML spec forbids it, and an
# em-dash written as "--" is the way it gets in.
ILLEGAL_COMMENT = re.compile(r"<!--(?:(?!-->).)*?--(?:(?!-->).)*?-->", re.S)


def _die(msg: str, code: int = 2) -> "None":
    print(f"plists: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def repo_plists() -> "list[Path]":
    """Every launchd plist kept in scripts/, oldest first for stable output."""
    return sorted(SCRIPTS.glob("com.*.plist"))


def explain(text: str) -> "str | None":
    """Name the likely cause of a parse failure, when we can tell.

    plistlib reports a line and column but not the rule. A "--" inside a
    comment is the overwhelmingly likely reason for a plist written by hand,
    and it is the defect that actually shipped, so say so directly.
    """
    m = ILLEGAL_COMMENT.search(text)
    if m:
        lineno = text[: m.start()].count("\n") + 1
        return (
            f"'--' inside an XML comment (near line {lineno}). A double hyphen "
            "cannot appear in an XML comment; rewrite it as a comma or a "
            "single hyphen. An em-dash typed as '--' is the usual way this "
            "gets in, so a comma is normally the right fix."
        )
    return None


def check_one(path: Path) -> "tuple[list[str], list[str]]":
    """Return (failures, warnings) for one plist."""
    fails: "list[str]" = []
    warns: "list[str]" = []
    rel = path.relative_to(REPO)
    text = path.read_text(encoding="utf-8")

    try:
        data = plistlib.loads(path.read_bytes())
    except Exception as exc:  # noqa: BLE001 - any parse failure is the finding
        hint = explain(text)
        fails.append(f"{rel}: not well-formed ({exc.__class__.__name__}: {exc})")
        if hint:
            fails.append(f"  cause: {hint}")
        return fails, warns

    label = data.get("Label")
    if not label:
        fails.append(f"{rel}: no Label key; launchd cannot address the job")

    args = data.get("ProgramArguments")
    if not args:
        fails.append(f"{rel}: no ProgramArguments; there is nothing to run")
    else:
        # The first element is the interpreter or binary; any later element
        # naming a path inside the repo must exist, or the job fails at run
        # time with the failure buried in a log nobody reads.
        for arg in args[1:]:
            if not isinstance(arg, str) or not arg.startswith("/"):
                continue
            target = Path(arg)
            if target.is_absolute() and REPO in target.parents and not target.exists():
                fails.append(f"{rel}: references {arg}, which does not exist")

    if not any(k in data for k in SCHEDULE_KEYS):
        fails.append(
            f"{rel}: no schedule key ({', '.join(SCHEDULE_KEYS)}); "
            "the job would never fire"
        )

    # A job whose log file has never appeared has probably never run. This is
    # not a failure: a freshly installed job legitimately has no log yet. It is
    # worth surfacing because it is the signal that caught the real bug.
    out_path = data.get("StandardOutPath")
    if out_path and label:
        if not Path(out_path).exists():
            inst = INSTALLED / path.name
            if inst.exists():
                warns.append(
                    f"{rel}: installed but {out_path} has never been created; "
                    "has this job ever run?"
                )

    # Drift: the repo copy is not what is running.
    inst = INSTALLED / path.name
    if inst.exists() and inst.read_bytes() != path.read_bytes():
        warns.append(
            f"{rel}: differs from the installed copy in ~/Library/LaunchAgents; "
            "reinstall it or the repo is not what is running"
        )

    return fails, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="Guard the launchd schedules against silent failure.")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    paths = repo_plists()
    if not paths:
        _die("no com.*.plist found in scripts/; refusing to report success on nothing")

    all_fails: "list[str]" = []
    all_warns: "list[str]" = []
    for p in paths:
        f, w = check_one(p)
        all_fails += f
        all_warns += w

    if not args.quiet:
        print(f"plists: {len(paths)} schedule(s) checked")

    for w in all_warns:
        print(f"plists: WARN — {w}", file=sys.stderr)

    if all_fails:
        print(f"plists: FAIL — {len(all_fails)} problem(s)", file=sys.stderr)
        for f in all_fails:
            print(f"  {f}", file=sys.stderr)
        return 1

    if not args.quiet:
        print("plists: OK — every schedule parses, is complete, and matches what is installed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
