#!/usr/bin/env python3
"""Guard the NARROW, checkable half of quotation fidelity in reports.

Why this gate exists, and why it is narrow.

The 2026-10-04 Senate report quoted a name it had reconstructed: footnote 47
wrote "Daniel J. Sullivan Jr." where the cited Fox News page says "Daniel J.
Sullivan" and contains no "Jr." anywhere. Every gate reported OK and it would
have shipped unreviewed. The two obvious fixes do not work, and both were
MEASURED rather than assumed:

  * `check-quotes.py --online` is INERT here. That gate audits epigraph-shaped
    attributions (`"quote" — Author`, em dash). A newspaper footnote is not that
    shape, so it scans this report as "0 attributions" and verifies nothing.

  * A general "every quoted fragment must appear on a cited page" check is
    UNUSABLE. Run against the same report it reported 70 of 169 fragments
    "missing" — because footnotes quote link TITLES, use ellipses ("on top of
    $33 million ... bringing"), and cite paywalled or JS-rendered pages that an
    automated fetch cannot read. A gate that fails correct reports is worse than
    no gate.

So this gate checks only the fragments whose content is a DISCRETE FACT and can
be confirmed by a substring test: a quoted person-name DETAIL — a middle initial
("First M. Last") or a generational suffix (Jr, Sr, II, III, IV). A name is a
fixed string and its exact form is what the reconstruction failure corrupts. On
the same report this flagged 0 of 2 (the two are the correct "Daniel J.
Sullivan," and "Dan S. Sullivan"), and 1 of 1 on the injected defect; across all
8 published report installments it flagged nothing.

What it does NOT check: whether a prose quotation is accurate, whether a quoted
figure is right, or anything outside a name detail. Those remain the writer's
and the runner's `--online --titles` sweep's job.

Scope: designed for `--file <report>` in the publishing gate set, where it has
been measured clean. A corpus-wide run also surfaces quoted link TITLES and
sources-list quotations from essays and summaries — legitimately unverifiable
(they cite paywalled or JS-rendered pages), reported as "unverified", not fatal.

A fragment is confirmed if it appears on ANY page the same line cites, because a
footnote legitimately cites several outlets and the quoted name may come from
any of them. A page that refuses or fails is a statement about this checker, not
about the citation: it reports "unverified" and does not fail.

Exit codes: 0 nothing wrong, 1 a quoted name detail is absent from every page its
line cites.

  check-quote-names.py --file <path>            # one article
  check-quote-names.py --file <path> --online   # fetch and verify (the gate)
  check-quote-names.py                          # whole content/ corpus, online
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"

# A quoted person-name detail: a middle initial, or a generational suffix. Both
# are fixed strings whose exact form is what reconstruction corrupts, and both
# are rare enough in quoted prose that the gate stays quiet.
_MIDDLE_INITIAL = re.compile(r"\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b")
_SUFFIX = re.compile(r"\b(?:Jr|Sr|II|III|IV)\b\.?")

# Quoted spans. Both straight and curly quotes; the report writes straight.
_QUOTED = re.compile(r"[\"\u201c]([^\"\u201d]{4,})[\"\u201d]")

_URL = re.compile(r"https?://[^\s\)\]\>\"']+")
_FOOTNOTE_DEF = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")
_FOOTNOTE_REF = re.compile(r"\[\^([^\]]+)\]")


def normalize(text: str) -> str:
    """Whitespace and zero-width collapse, the same contract check-quotes uses.

    PDFs, HTML and hard-wrapped text break lines mid-sentence, so a literal
    substring test reports a false miss on a source that does contain the
    fragment; and some CMSs emit a zero-width space as a layout crutch, which
    splits a quotation for a substring test while being invisible on screen.
    """
    return re.sub(r"[\u200b-\u200f\ufeff]", "", re.sub(r"\s+", " ", text)).strip()


def has_name_detail(fragment: str) -> bool:
    """True if the fragment contains a middle initial or a generational suffix."""
    return bool(_MIDDLE_INITIAL.search(fragment) or _SUFFIX.search(fragment))


def extract_candidates(text: str) -> "list[dict]":
    """Quoted name-details, each with the URLs of the line it sits on.

    Pure and network-free, so the test suite can exercise it. A candidate is a
    quoted fragment containing a name detail. Its URLs are the ones on its own
    line if that line is a footnote definition, else the URLs of the footnote
    definitions it references by `[^n]`.

    Two spans are excluded, for the same reason the other gates exempt them and
    because a corpus scan showed both producing false candidates:

      * **Frontmatter.** A `description` is display text, not a quotation of a
        source; "Kenneth Walker III's workload" in a `description` is not a claim
        about a page.
      * **A fragment that contains a markdown link.** The quoted span is then a
        citation's ANCHOR — the source's own title, which `check-links.py
        --titles` already compares against the fetched page. Testing a title as
        a quotation flags correct citations (a corpus scan surfaced "John F.
        Kennedy: Domestic Affairs" and a Gutenberg epigraph line this way).
    """
    lines = text.split("\n")

    # The frontmatter ends at the second `---` when the file opens with one.
    fm_end = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                fm_end = j + 1
                break

    # The URL set of every footnote definition, keyed by its label.
    foot_urls: "dict[str, list[str]]" = {}
    for raw in lines:
        m = _FOOTNOTE_DEF.match(raw.strip())
        if m:
            foot_urls[m.group(1)] = [u.rstrip(".,;") for u in _URL.findall(m.group(2))]

    out = []
    for i, raw in enumerate(lines):
        if i < fm_end:
            continue
        urls: "list[str]" = []
        defm = _FOOTNOTE_DEF.match(raw.strip())
        if defm:
            urls = foot_urls.get(defm.group(1), [])
        else:
            for ref in _FOOTNOTE_REF.findall(raw):
                urls.extend(foot_urls.get(ref, []))
            urls.extend(u.rstrip(".,;") for u in _URL.findall(raw))
        # De-duplicate while keeping order.
        urls = list(dict.fromkeys(urls))
        for frag in _QUOTED.findall(raw):
            # A fragment that IS a markdown link (or contains one) is an anchor,
            # not a quotation of prose.
            if "](" in frag:
                continue
            if has_name_detail(frag):
                out.append({"line": i + 1, "fragment": frag.strip(), "urls": urls})
    return out


def fetch_text(url: str) -> "tuple[str, str]":
    """Return (http_code, text). Never raises; a fetch failure is ('000', '')."""
    try:
        proc = subprocess.run(
            ["curl", "-sL", "--compressed", "-A", "Mozilla/5.0", "--max-time", "25",
             "-w", "\n%{http_code}", url],
            capture_output=True,
        )
    except Exception:
        return "000", ""
    raw = proc.stdout.decode("utf-8", "ignore")
    body, _, code = raw.rpartition("\n")
    if not code.strip().isdigit():
        return "000", raw
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
    return code.strip(), normalize(html.unescape(re.sub(r"<[^>]+>", " ", body)))


def fragment_present(fragment: str, body: str) -> bool:
    """True if the fragment, or its punctuation-trimmed core, appears in body.

    Both sides are normalized: a hard-wrapped source breaks lines mid-name, so a
    literal test would report a false miss on a page that does contain the name.
    """
    frag = normalize(fragment)
    text = normalize(body)
    core = frag.strip(" .,;:!?\"'\u201c\u201d")
    return frag in text or (core and core in text)


def check_online(candidate: dict) -> "str":
    """Return 'ok', 'missing', or 'unverified' for one candidate."""
    if not candidate["urls"]:
        return "unverified"
    read_any = False
    for url in candidate["urls"]:
        code, body = fetch_text(url)
        if code == "200" and body:
            read_any = True
            if fragment_present(candidate["fragment"], body):
                return "ok"
    return "missing" if read_any else "unverified"


def audit(path: pathlib.Path, online: bool, quiet: bool) -> "tuple[int, int]":
    """Return (checked, problems) for one file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    candidates = extract_candidates(text)
    if not candidates:
        return 0, 0
    rel = path if not path.is_absolute() else path.relative_to(REPO)
    problems = 0
    for c in candidates:
        if not online:
            if not quiet:
                print(f"{rel}:{c['line']}: quoted name detail "
                      f"{c['fragment']!r} ({len(c['urls'])} url(s))")
            continue
        verdict = check_online(c)
        if verdict == "missing":
            problems += 1
            print(f"{rel}:{c['line']}: quoted name detail {c['fragment']!r} does "
                  f"not appear on any page this line cites:", file=sys.stderr)
            for u in c["urls"]:
                print(f"    {u}", file=sys.stderr)
        elif verdict == "unverified" and not quiet:
            print(f"{rel}:{c['line']}: unverified — could not read a cited page "
                  f"for {c['fragment']!r}")
    return len(candidates), problems


def content_files() -> "list[pathlib.Path]":
    if not CONTENT.is_dir():
        return []
    return sorted(CONTENT.rglob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", help="check a single file instead of the corpus")
    ap.add_argument("--online", action="store_true",
                    help="fetch each cited page and require the quoted name to appear")
    ap.add_argument("--quiet", action="store_true", help="only report problems")
    args = ap.parse_args()

    files = [pathlib.Path(args.file)] if args.file else content_files()
    checked = problems = 0
    for path in files:
        c, p = audit(path, args.online, args.quiet)
        checked += c
        problems += p

    if not args.online:
        if not args.quiet:
            print(f"quote-names: {checked} quoted name detail(s) found "
                  f"(run with --online to verify against their sources)")
        return 0

    if problems:
        print(f"quote-names: FAIL — {problems} quoted name detail(s) absent from "
              f"the page(s) their line cites:", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"quote-names: OK — {checked} quoted name detail(s) confirmed or "
              f"unverifiable (0 absent)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(141)
