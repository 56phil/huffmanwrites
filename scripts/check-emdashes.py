#!/usr/bin/env python3
"""Count em-dashes against the house limit, with the two documented exemptions.

The rule (CLAUDE.md): no more than 3 em-dashes in the prose you write. Two
categories do not count against that limit, because they are not the editor's
prose:

  1. A dash inside quotation marks. A quotation's internal punctuation belongs
     to its author or translator; rewriting it to save a mark would corrupt the
     quotation that check-quotes.py exists to protect. (The Thiel "franchise to
     women — two constituencies ... libertarians —" line is the model case.)
  2. A dash standing as a date or numeric range. This is a guard, not a licence:
     the en-dash is the correct mark for a range (1903–1977, 53–47) and is what
     the site already uses, so an em-dash between dates is a typo to fix.

Scope is body prose (after frontmatter). Frontmatter is reported separately and
not counted: its fields are display metadata (title, description, hero_caption,
hero_alt), and YAML quoting makes "inside quotes" ambiguous there in a way that
would exempt a caption but count the identical unquoted string.

Usage:
  check-emdashes.py                 # corpus summary
  check-emdashes.py --list          # every file over the limit, worst first
  check-emdashes.py --file <path>   # one file, with the offending lines
  check-emdashes.py --check         # baseline ratchet; exit 1 on regression
  check-emdashes.py --update-baseline   # re-record the current debt
"""
import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
BASELINE = REPO / "scripts" / "emdash-baseline.txt"
LIMIT = 3

EM = "\u2014"
EN = "\u2013"

_MONTHS = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?"
    r"|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
# A token that can sit on either side of a range: a year, a number, a month.
_RANGEISH = rf"(?:\d{{1,4}}|{_MONTHS})"
_RANGE = re.compile(rf"{_RANGEISH}\s*{EM}\s*{_RANGEISH}", re.IGNORECASE)

# Quotation spans. Curly pairs first, then straight double quotes (the corpus
# mixes them). Straight single quotes are deliberately NOT treated as
# quotation delimiters: in this corpus they are overwhelmingly apostrophes, and
# pairing them would swallow whole sentences as "quotations".
_QUOTES = re.compile(r"\u201c[^\u201d]*\u201d|\"[^\"]*\"")


def split_frontmatter(text: str) -> "tuple[str, str]":
    if text.startswith("---"):
        parts = text.split("---\n", 2)
        if len(parts) > 2:
            return parts[1], parts[2]
    return "", text


def classify(text: str) -> "dict[str, object]":
    """Count body-prose em-dashes, separating what the limit covers."""
    fm, body = split_frontmatter(text)

    counted = 0
    in_quote = 0
    in_range = 0
    lines = []

    for lineno, line in enumerate(body.split("\n"), 1):
        if EM not in line:
            continue
        spans = [m.span() for m in _QUOTES.finditer(line)]
        ranges = [m.span() for m in _RANGE.finditer(line)]
        line_counted = 0
        for i, ch in enumerate(line):
            if ch != EM:
                continue
            if any(a <= i < b for a, b in spans):
                in_quote += 1
            elif any(a <= i < b for a, b in ranges):
                in_range += 1
            else:
                counted += 1
                line_counted += 1
        if line_counted:
            lines.append((lineno, line_counted, line.strip()))

    return {
        "counted": counted,
        "in_quote": in_quote,
        "in_range": in_range,
        "frontmatter": fm.count(EM),
        "lines": lines,
    }


def content_files() -> "list[pathlib.Path]":
    if not CONTENT.is_dir():
        return []
    return sorted(CONTENT.rglob("*.md"))


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def load_baseline() -> "dict[str, int]":
    """Map 'file' -> the count recorded when the exemption amendment landed.

    Keyed by file with the count as the value, so the ratchet is on the number,
    not on mere presence: a file may be reduced freely, but may not grow past
    what it was. Files absent from the baseline get no allowance at all.
    """
    out: "dict[str, int]" = {}
    if not BASELINE.exists():
        return out
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 2 and parts[1].strip().isdigit():
            out[parts[0]] = int(parts[1])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", help="count one file and show its prose dashes")
    ap.add_argument("--list", action="store_true", help="list files over the limit")
    ap.add_argument("--check", action="store_true",
                    help="fail if any file exceeds its recorded baseline")
    ap.add_argument("--update-baseline", action="store_true",
                    help="re-record every file currently over the limit")
    args = ap.parse_args()

    if args.file:
        path = pathlib.Path(args.file)
        if not path.exists():
            print(f"emdashes: no such file: {path}", file=sys.stderr)
            return 2
        r = classify(path.read_text(encoding="utf-8"))
        n = r["counted"]
        verdict = "OK" if n <= LIMIT else f"OVER LIMIT ({n} > {LIMIT})"
        print(f"{rel(path)}: {n} counted em-dash(es) — {verdict}")
        print(f"  exempt: {r['in_quote']} inside quotations, "
              f"{r['in_range']} in a date/number range")
        print(f"  frontmatter (reported, not counted): {r['frontmatter']}")
        for lineno, k, text in r["lines"]:
            print(f"    L{lineno} x{k}: {text[:150]}")
        return 0 if n <= LIMIT else 1

    files = content_files()
    if not files:
        print("emdashes: no content files found — is this the site repo?", file=sys.stderr)
        return 2

    results = {rel(p): classify(p.read_text(encoding="utf-8")) for p in files}
    over = sorted(((r["counted"], k) for k, r in results.items() if r["counted"] > LIMIT),
                  reverse=True)
    total_counted = sum(r["counted"] for r in results.values())
    total_quote = sum(r["in_quote"] for r in results.values())
    total_range = sum(r["in_range"] for r in results.values())

    if args.update_baseline:
        body = [
            "# Em-dashes over the limit in content written before the exemption",
            "# amendment (CLAUDE.md, 2026-09-20). Keyed by file + the count at that",
            "# moment, so the ratchet is on the number: a file may be reduced freely",
            "# but may not grow past what it was. Editing a file to add prose dashes",
            "# is therefore caught; reducing them passes and the count is",
            "# re-recorded on the next --update-baseline.",
            "#",
            "# Regenerate with: scripts/check-emdashes.py --update-baseline",
            "#",
            "# file\tcount",
        ]
        for n, k in sorted(over, key=lambda x: x[1]):
            body.append(f"{k}\t{n}")
        BASELINE.write_text("\n".join(body) + "\n", encoding="utf-8")
        print(f"emdashes: baseline updated — {len(over)} file(s) recorded over the limit")
        return 0

    if args.check:
        baseline = load_baseline()
        regressions = []
        for n, k in over:
            allowed = baseline.get(k)
            if allowed is None:
                regressions.append(f"{k}: {n} over the limit, no baseline entry")
            elif n > allowed:
                regressions.append(f"{k}: {n}, was {allowed}")
        if regressions:
            print("emdashes: REGRESSIONS", file=sys.stderr)
            for r in regressions:
                print(f"  {r}", file=sys.stderr)
            return 1
        print(f"emdashes: OK — no file over its baseline "
              f"({len(baseline)} recorded, {len(over)} currently over the {LIMIT} limit)")
        return 0

    if args.list:
        print(f"{'n':>4}  file")
        for n, k in over:
            print(f"{n:>4}  {k}")
        print(f"\n{len(over)} file(s) over the limit of {LIMIT}.")

    print(f"emdashes: {len(files)} content files; {total_counted} counted prose "
          f"em-dash(es); {total_quote} exempt inside quotations; "
          f"{total_range} exempt as date/number ranges; {len(over)} file(s) over {LIMIT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # `--list | head` closes the pipe early. Python then raises on the final
        # flush at interpreter exit, printing a traceback for what is normal
        # shell behaviour. Point stdout at devnull so the shutdown flush is a
        # no-op, and exit with the conventional 128+SIGPIPE.
        import os

        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(141)
