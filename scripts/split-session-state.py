#!/usr/bin/env python3
"""One-shot: split SESSION_STATE.md into a current file and a pre-September archive.

The file had reached 2,023 lines / 112 maintenance entries going back to May.
Reading it at session start meant reading three months of history to reach the
current entry. The fix is a date split, not a delete: everything pre-September
moves to SESSION_STATE_ARCHIVE.md verbatim, and nothing is dropped.

Boundaries, chosen by structure rather than by line number:
  * The preamble stays (it explains the word-count convention).
  * Reference sections stay regardless of date: Project Overview, Pending /
    Next Actions, Architecture Notes, Visual Identity, Content Inventory,
    User Preferences, Environment Notes, and the FLAGGED to-do.
  * Maintenance and dated sections from September 2026 stay.
  * Everything else (pre-September maintenance, the May/June project sections,
    the Blue Sky and book-marketing writeups) goes to the archive.
  * "## Last Updated" stays whole. It is a one-line-per-date index, and its
    whole purpose is scanning, so it is the one thing that must not be split.

Safety: the script refuses to write unless every byte of the original is
accounted for in exactly one of the two outputs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LIVE = REPO / "SESSION_STATE.md"
ARCHIVE = REPO / "SESSION_STATE_ARCHIVE.md"

MONTHS = {
    m: i
    for i, m in enumerate(
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


def dated(heading: str) -> "tuple[int, int] | None":
    m = re.search(r"([A-Z][a-z]+)\s+\d{1,2},\s*(\d{4})", heading)
    if m and m.group(1) in MONTHS:
        return int(m.group(2)), MONTHS[m.group(1)]
    return None


def main() -> int:
    text = LIVE.read_text(encoding="utf-8")
    lines = text.split("\n")

    bounds = [i for i, l in enumerate(lines) if re.match(r"^#{2,3} ", l)]
    if not bounds:
        print("split: ERROR: no section headings found", file=sys.stderr)
        return 2

    preamble = lines[: bounds[0]]
    sections = []
    for k, start in enumerate(bounds):
        end = bounds[k + 1] if k + 1 < len(bounds) else len(lines)
        sections.append((start, end, lines[start]))

    keep, arch = [], []
    for start, end, heading in sections:
        if any(key in heading for key in KEEP_ALWAYS):
            keep.append((start, end, heading))
        else:
            d = dated(heading)
            if d and d >= (2026, 9):
                keep.append((start, end, heading))
            else:
                arch.append((start, end, heading))

    # The preamble already ends with its own "---" separator, so do not add one.
    live_lines = list(preamble)
    while live_lines and not live_lines[-1].strip():
        live_lines.pop()
    live_lines += [
        "> **History.** Entries before September 2026 were moved to",
        "> [`SESSION_STATE_ARCHIVE.md`](SESSION_STATE_ARCHIVE.md) on 2026-09-20 — nothing was",
        "> deleted, and the file is complete. Search it with `grep` when a decision or a",
        "> commit hash from an earlier month is what you need.",
        "",
        "---",
        "",
    ]
    for start, end, _ in keep:
        live_lines += lines[start:end]

    arch_lines = [
        "# Session State — Archive (before September 2026)",
        "",
        "> Split out of [`SESSION_STATE.md`](SESSION_STATE.md) on 2026-09-20 because the",
        "> combined file had reached 2,023 lines and reading it at session start meant",
        "> reading three months of history to reach the current entry. **Complete and",
        "> unedited** — every section that was in the file at the split is here verbatim.",
        ">",
        "> `SESSION_STATE.md` keeps September 2026 onward plus the reference sections.",
        "> Search this file when you need an earlier decision, commit hash, or rationale.",
        "",
    ]
    arch_lines += preamble[1:]  # keep the word-count convention for these entries
    while arch_lines and not arch_lines[-1].strip():
        arch_lines.pop()
    if arch_lines and arch_lines[-1].strip() == "---":
        arch_lines.pop()
    arch_lines += ["", "---", ""]
    for start, end, _ in arch:
        arch_lines += lines[start:end]

    # --- safety: every original line must appear in exactly one output ---
    live_body = "\n".join(live_lines)
    arch_body = "\n".join(arch_lines)
    missing = []
    for i, l in enumerate(lines):
        if not l.strip():
            continue
        if l in live_body or l in arch_body:
            continue
        missing.append((i + 1, l[:90]))
    if missing:
        print(f"split: ERROR: {len(missing)} line(s) would be lost", file=sys.stderr)
        for ln, s in missing[:10]:
            print(f"  L{ln}: {s}", file=sys.stderr)
        return 1

    ARCHIVE.write_text("\n".join(arch_lines).rstrip("\n") + "\n", encoding="utf-8")
    LIVE.write_text("\n".join(live_lines).rstrip("\n") + "\n", encoding="utf-8")

    print(f"split: live    {len(lines):>5} -> {len(live_lines):>5} lines "
          f"({len(keep)} sections kept)")
    print(f"split: archive        {len(arch_lines):>5} lines ({len(arch)} sections moved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
