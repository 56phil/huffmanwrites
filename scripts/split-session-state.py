#!/usr/bin/env python3
"""Split SESSION_STATE.md into a current file and a dated archive, repeatably.

The file reached 2,023 lines / 112 maintenance entries going back to May, and
reading it at session start meant reading three months of history to reach the
current entry. The fix is a date split, not a delete: older entries move to
`SESSION_STATE_ARCHIVE.md` verbatim, and nothing is dropped.

**This was a one-shot and is now a tool.** Philip, 2026-09-25: "you may split
SESSION_STATE.md whenever you want." Doing that more than once needed three
things the first version did not have, one of which was a data-loss bug:

  1. **The archive is APPENDED to, never rewritten.** The first version built
     `arch_lines` from only the sections it was moving this run and wrote that
     over the archive. A second run would therefore have replaced a 1,106-line,
     120-section archive with the 25 lines of its own header — measured, not
     feared. It was survivable exactly once because the archive was empty.
  2. **The safety check covers both files.** It compared every original line
     against the two OUTPUTS, so it was answering "did I keep everything I am
     writing" and was structurally blind to "did I destroy what was already
     there". It now also verifies every line already in the archive survives.
  3. **The cutoff is an argument, not a constant.** `--keep-months N` (default 3)
     keeps the last N calendar months in the live file, so the boundary moves on
     its own. The old hardcoded `>= (2026, 9)` was a one-shot by construction:
     re-running it would have moved nothing and reported success.

What stays in the live file regardless of date: the preamble (it explains the
word-count convention) and the reference sections a new session actually needs
(Project Overview, Pending / Next Actions, Architecture Notes, Visual Identity,
Content Inventory, User Preferences, Environment Notes, FLAGGED). `Last Updated`
also stays whole — it is a one-line-per-date index whose whole purpose is
scanning, so it is the one thing that must not be split.

Usage:
  split-session-state.py                # dry run: report what would move
  split-session-state.py --write        # move it
  split-session-state.py --keep-months 6 --write
  split-session-state.py --as-of 2026-12-01   # test what a future split would do

Exit codes: 0 ok (including "nothing to move"), 1 a line would be lost, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIVE = REPO / "SESSION_STATE.md"
ARCHIVE = REPO / "SESSION_STATE_ARCHIVE.md"

MONTHS = {
    m: i for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"], 1
    )
}

# Kept regardless of date: the sections a new session actually needs.
KEEP_ALWAYS = (
    "Project Overview", "Pending / Next Actions", "Architecture Notes",
    "Visual Identity", "Content Inventory", "User Preferences",
    "Environment Notes", "FLAGGED", "Last Updated",
)

# The archive's own top matter, used only when creating it from scratch.
ARCHIVE_HEAD = (
    "# Session State — Archive",
    "",
    "> Split out of [`SESSION_STATE.md`](SESSION_STATE.md) so that reading the live",
    "> file at session start does not mean reading months of history to reach the",
    "> current entry. **Complete and unedited** — every section that was in the file",
    "> at each split is here verbatim, newest split first within each block.",
    ">",
    "> Search this file when you need an earlier decision, commit hash, or rationale.",
    "",
)

# The pointer the live file carries to the archive.
HISTORY_NOTE = (
    "> **History.** Entries older than the last few months are in",
    "> [`SESSION_STATE_ARCHIVE.md`](SESSION_STATE_ARCHIVE.md) — nothing was",
    "> deleted, and the file is complete. Search it with `grep` when a decision or",
    "> a commit hash from an earlier month is what you need.",
)

# The pointer's wording is expected to change as the split boundary moves, so the
# pointer is identified by SHAPE rather than by matching today's string. That
# distinction is what makes a re-run idempotent and is also what keeps the safety
# check honest: the previous revision's pointer — which named a specific date and
# month — must be recognised as a pointer and replaced, not counted as content
# that is about to be lost.
#
# The match is the leading `**History.**` emphasis marker, not the bare word
# "History": a preamble blockquote that merely mentions history in prose must not
# be treated as the pointer and silently deleted.
def is_history_pointer(line: str) -> bool:
    s = line.lstrip()
    return s.startswith(">") and "**History.**" in s


def dated(heading: str) -> "tuple[int, int] | None":
    """Parse a month/day/year out of a heading, if there is one."""
    m = re.search(r"([A-Z][a-z]+)\s+\d{1,2},\s*(\d{4})", heading)
    if m and m.group(1) in MONTHS:
        return int(m.group(2)), MONTHS[m.group(1)]
    return None


def cutoff(as_of: date, keep_months: int) -> "tuple[int, int]":
    """The (year, month) at or after which a section stays in the live file.

    Counting back whole months from `as_of` rather than hardcoding a date is
    what makes this repeatable: the boundary advances by itself, so a split run
    a year from now keeps a year's newer entries without anyone editing this.
    """
    y, m = as_of.year, as_of.month - (keep_months - 1)
    while m <= 0:
        y, m = y - 1, m + 12
    return y, m


def sections_of(lines: "list[str]") -> "list[tuple[int, int, str]]":
    bounds = [i for i, l in enumerate(lines) if re.match(r"^#{2,3} ", l)]
    out = []
    for k, start in enumerate(bounds):
        end = bounds[k + 1] if k + 1 < len(bounds) else len(lines)
        out.append((start, end, lines[start]))
    return out


def is_reference(heading: str) -> bool:
    return any(key in heading for key in KEEP_ALWAYS)


def plan(text: str, as_of: date, keep_months: int) -> "dict":
    """Decide what stays and what moves. Pure; no writes."""
    lines = text.split("\n")
    secs = sections_of(lines)
    if not secs:
        raise ValueError("no section headings found")
    preamble = lines[: secs[0][0]]
    cut = cutoff(as_of, keep_months)

    keep, arch = [], []
    for start, end, heading in secs:
        if is_reference(heading):
            keep.append((start, end, heading))
        else:
            d = dated(heading)
            if d is not None and d >= cut:
                keep.append((start, end, heading))
            else:
                arch.append((start, end, heading))
    return {"lines": lines, "preamble": preamble, "keep": keep, "arch": arch, "cut": cut}


def build_live(pl: "dict") -> "list[str]":
    """The live file: preamble, exactly one history pointer, then the kept sections.

    The pointer is REPLACED, not appended. The first version of this always
    inserted one, so a second split added a second copy — measured: three
    `**History.**` blocks after two runs. Any run must leave the live file in the
    same shape it would have been in had it been the only run.
    """
    lines, preamble = pl["lines"], pl["preamble"]
    out = list(preamble)
    while out and not out[-1].strip():
        out.pop()

    # Drop any pointer a previous run left, and any separator that followed it,
    # so the preamble is emitted once however many times this has run. The
    # predicate is shared with the safety check so both agree on what a pointer
    # is — the previous revision's wording named a specific month and date, and
    # treating that as ordinary content would (correctly) fail the loss check.
    trimmed: "list[str]" = []
    i = 0
    while i < len(out):
        if is_history_pointer(out[i]):
            while i < len(out) and (is_history_pointer(out[i]) or not out[i].strip()):
                i += 1
            while trimmed and not trimmed[-1].strip():
                trimmed.pop()
            if i < len(out) and out[i].strip() == "---":
                i += 1
            continue
        trimmed.append(out[i])
        i += 1
    out = trimmed

    out += list(HISTORY_NOTE) + ["", "---", ""]
    for start, end, _ in pl["keep"]:
        out += lines[start:end]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="actually move the sections")
    ap.add_argument("--keep-months", type=int, default=3,
                    help="keep the most recent N calendar months in the live file (default 3)")
    ap.add_argument("--as-of", help="treat this date as today (YYYY-MM-DD), for testing")
    ap.add_argument("--archive", help="override the archive path (for tests)")
    ap.add_argument("--live", help="override the live path (for tests)")
    args = ap.parse_args()

    live_path = Path(args.live) if args.live else LIVE
    arch_path = Path(args.archive) if args.archive else ARCHIVE

    if not live_path.is_file():
        print(f"split: ERROR: no {live_path}", file=sys.stderr)
        return 2
    if args.keep_months < 1:
        print("split: ERROR: --keep-months must be >= 1", file=sys.stderr)
        return 2
    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    except ValueError:
        print(f"split: ERROR: --as-of is not a date: {args.as_of}", file=sys.stderr)
        return 2

    text = live_path.read_text(encoding="utf-8")
    existing = arch_path.read_text(encoding="utf-8") if arch_path.is_file() else ""
    try:
        pl = plan(text, as_of, args.keep_months)
    except ValueError as e:
        print(f"split: ERROR: {e}", file=sys.stderr)
        return 2

    y, m = pl["cut"]
    moved_lines = sum(e - s for s, e, _ in pl["arch"])
    print(f"split: as of {as_of} keeping >= {y}-{m:02d} "
          f"(--keep-months {args.keep_months})")
    print(f"split: {len(pl['arch'])} section(s) / {moved_lines} line(s) would move; "
          f"{len(pl['keep'])} section(s) stay")
    if not pl["arch"]:
        print("split: nothing to move — the live file is already within the window")
        return 0

    live_out = build_live(pl)

    # The archive is APPENDED to. Read what is already there and add to it; only
    # create the head when there is no archive yet. Rewriting it is the bug that
    # would have cost 1,106 lines on the second run.
    arch_out = existing.rstrip("\n").split("\n") if existing.strip() else list(ARCHIVE_HEAD)
    if existing.strip() and arch_out and arch_out[-1].strip() != "---":
        arch_out += ["", "---"]
    arch_out += [""]
    for start, end, heading in pl["arch"]:
        d = dated(heading)
        arch_out += [f"<!-- archived {as_of.isoformat()}"
                     + (f" (entry dated {d[0]}-{d[1]:02d})" if d else "") + " -->"]
        arch_out += pl["lines"][start:end]

    # --- safety: nothing may be lost, in EITHER file -----------------------
    live_body = "\n".join(live_out)
    arch_body = "\n".join(arch_out)
    missing = []
    for i, l in enumerate(pl["lines"]):
        if not l.strip():
            continue
        # A history pointer is the one thing a run is ALLOWED to rewrite: its
        # wording tracks the moving boundary by design. Everything else must
        # survive verbatim in one of the two files.
        if is_history_pointer(l):
            continue
        if l not in live_body and l not in arch_body:
            missing.append((i + 1, l[:90]))
    if missing:
        print(f"split: ERROR: {len(missing)} line(s) from the live file would be lost",
              file=sys.stderr)
        for ln, s in missing[:10]:
            print(f"  L{ln}: {s}", file=sys.stderr)
        return 1

    # The check the first version lacked: what is already archived must survive.
    lost_from_archive = []
    for i, l in enumerate(existing.split("\n")):
        if not l.strip() or l.startswith("<!-- archived"):
            continue
        if is_history_pointer(l):
            continue
        if l in arch_body:
            continue
        lost_from_archive.append((i + 1, l[:90]))
    if lost_from_archive:
        print(f"split: ERROR: {len(lost_from_archive)} existing archive line(s) would "
              f"be lost — refusing to write", file=sys.stderr)
        for ln, s in lost_from_archive[:10]:
            print(f"  archive L{ln}: {s}", file=sys.stderr)
        return 1

    if not args.write:
        print("split: DRY RUN — pass --write to move the sections")
        print(f"split: live    {len(pl['lines']):>5} -> {len(live_out):>5} lines")
        print(f"split: archive {len(existing.splitlines()):>5} -> {len(arch_out):>5} lines "
              f"(appended, not rewritten)")
        return 0

    arch_path.write_text("\n".join(arch_out).rstrip("\n") + "\n", encoding="utf-8")
    live_path.write_text("\n".join(live_out).rstrip("\n") + "\n", encoding="utf-8")
    print(f"split: live    {len(pl['lines']):>5} -> {len(live_out):>5} lines")
    print(f"split: archive {len(existing.splitlines()):>5} -> {len(arch_out):>5} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
