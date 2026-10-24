#!/usr/bin/env python3
"""Guard the built site against template-escaping failures and broken refs.

Two defect classes, both invisible to every other check in this repo, because
neither the source nor the frontmatter is wrong — only the RENDERED output is:

1. **Hugo/Go template sentinels.** When a template puts a value into a URL
   attribute and Go's safety filter rejects it, the output is the literal
   string `ZgotmplZ` (or `<no value>`, `%!s(...)`). The build succeeds, the
   page returns 200, the source file is valid — and the attribute is garbage,
   so the image or link silently does not load.

   This is not hypothetical. Every mobile hero on `/books/stoic-backgammon/`
   was broken this way: the hero files have a space in their names
   (`sb-gtl 16x9.webp`), and while Hugo percent-encodes a space in `src` it
   does NOT in `srcset`. So `<source srcset="/img/articles/sb-gtl 4x5.webp">`
   hit the filter and rendered `srcset=/#ZgotmplZ`, meaning no mobile reader
   ever saw a hero image on that page. The desktop image loaded fine, which is
   exactly why nobody noticed.

2. **Local references to files that do not exist.** `src`, `srcset`, and
   `href` pointing at the site's own assets must resolve in `public/`.
   (External URLs are out of scope — `check-links.py` covers those.)

Requires a prior `hugo` build. Run after building.

Exit codes:
  0  clean
  1  sentinel or broken local reference found
  2  could not run (no build output)

Usage:
  check-render-integrity.py [--quiet]
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PUBLIC = REPO / "public"

# Minimum plausible build. The site renders ~380 pages; set well below that so
# ordinary growth never trips it, but high enough that a missing or partial
# build does. See the coverage-floor note in scan().
MIN_PAGES = 100

# Go's sentinel for "this URL failed the safety filter", plus the printf
# overflow markers that indicate a value arrived with the wrong type.
#
# Deliberately NOT included: `{{` / `}}`. Those are Go template delimiters, but
# they also appear legitimately in minified JS and CSS (`if(x){y}}`), so
# scanning for them flagged 340 healthy pages. A gate that cries wolf is worse
# than no gate — it trains the reader to ignore it. Unrendered `{{< shortcode >}}`
# is caught by the shortcode scan below instead, which is precise.
SENTINELS = ("ZgotmplZ", "<no value>", "%!s(", "%!v(", "%!d(")

# An unrendered Hugo shortcode in the OUTPUT. Matched only in the shape Hugo
# uses (`{{<` or `{{%`), never the bare braces that JS/CSS legitimately contain.
UNRENDERED_SHORTCODE = re.compile(r"\{\{[<%]\s*\S+")

# Attribute values that point at our own assets and must resolve.
LOCAL_ATTR = re.compile(
    r"""(?:src|srcset|href|data-src)\s*=\s*"?([^"\s>]+)""".replace('"', '"'),
    re.I,
)

# srcset may carry a comma-separated candidate list.
SRCSET_ATTR = re.compile(r"""srcset\s*=\s*"?([^">]+)""".replace('"', '"'), re.I)


def die(msg: str, code: int = 2) -> "None":
    print(f"render: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def is_local(url: str) -> bool:
    if not url or url.startswith(("http://", "https://", "//", "#", "mailto:", "data:", "tel:")):
        return False
    if not url.startswith("/"):
        return False
    return True


def resolves(url: str) -> bool:
    """Does a site-absolute path exist in the build output?"""
    path = urllib.parse.unquote(url.split("#")[0].split("?")[0])
    if path.endswith("/"):
        path = posixpath.join(path, "index.html")
    target = PUBLIC / path.lstrip("/")
    return target.exists()


def pages() -> "list[Path]":
    return sorted(PUBLIC.rglob("*.html"))


# --- Further Reading ranking ------------------------------------------------
#
# The related-posts block has failed silently once, and the failure was
# invisible to every other check: the build passed, the page returned 200, and
# the four links were all real. It selected on raw tag intersection plus
# recency, so a post sharing only the ubiquitous "civics" tag outranked one
# sharing "physics", and the block filled with the daily SITREP. What makes
# that checkable from the build output alone is a single invariant: the list is
# ordered by how many tags each recommendation shares with the post, and never
# increases down the list. A section fallback (zero shared tags) is legitimate
# only at the end.

TAG_HREF = re.compile(r"https://www\.huffmanwrites\.org/tags/([^/>]+)/")
POST_TAGS = re.compile(r"post-tags>(.*?)</ul>", re.S)
RELATED_ITEM = re.compile(r"related-item><h4><a href=([^ >]+)>")
RELATED_START = re.compile(r"class=related-posts>")


def extract_tags(text: str) -> "set[str]":
    """The post's own tags, read off the rendered post-tags list."""
    m = POST_TAGS.search(text)
    return set(TAG_HREF.findall(m.group(1))) if m else set()


def extract_block(text: str) -> "list[str]":
    """Recommendation URLs in render order, or [] when there is no block."""
    start = RELATED_START.search(text)
    if not start:
        return []
    window = text[start.end():start.end() + 8000]
    return [u.removeprefix("https://www.huffmanwrites.org") if u.startswith("http")
            else u for u in RELATED_ITEM.findall(window)]


def ranking_violations(tags: "set[str]", rec_tags: "list[set[str]]") -> "list[tuple[int, int]]":
    """(i, j) pairs where a later recommendation shares strictly more tags."""
    counts = [len(t & tags) for t in rec_tags]
    return [(i, i + 1) for i in range(len(counts) - 1) if counts[i] < counts[i + 1]]


def related_report(root: Path) -> "tuple[int, list[str]]":
    """Inspect every post's Further Reading block; return coverage and complaints."""
    posts = [p for p in sorted(root.glob("posts/**/index.html"))]
    tags_of: "dict[str, set[str]]" = {}
    text_of: "dict[str, str]" = {}
    for p in posts:
        url = "/" + p.parent.relative_to(root).as_posix() + "/"
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        text_of[url] = text
        tags_of[url] = extract_tags(text)

    inspected = 0
    complaints: "list[str]" = []
    for url, text in text_of.items():
        recs = extract_block(text)
        if not recs:
            continue
        inspected += 1
        if url in recs:
            complaints.append(f"{url} recommends itself")
        known = [r for r in recs if r in tags_of]
        for i, j in ranking_violations(tags_of[url], [tags_of[r] for r in known]):
            complaints.append(
                f"{url}: item {i + 1} shares fewer tags than item {j + 1} "
                f"({known[i]} -> {known[j]})")
    return inspected, complaints


def scan(quiet: bool) -> int:
    if not PUBLIC.is_dir():
        die("no public/ directory — run `hugo` first")

    # Coverage floor: refuse to report clean on a scan that saw no pages. A
    # wrong build output directory or an interrupted build would otherwise
    # produce a confident OK over nothing at all.
    built = pages()
    if len(built) < MIN_PAGES:
        die(f"found only {len(built)} built page(s); expected at least "
            f"{MIN_PAGES}. The scan is not seeing the build output, so a pass "
            f"would be meaningless.")

    sentinel_hits: "list[tuple[str, str]]" = []
    broken_hits: "list[tuple[str, str, str]]" = []

    for page in built:
        try:
            text = page.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = str(page.relative_to(REPO))

        for s in SENTINELS:
            n = text.count(s)
            if n:
                sentinel_hits.append((rel, f"{s} x{n}"))

        for m in UNRENDERED_SHORTCODE.finditer(text):
            sentinel_hits.append((rel, f"unrendered shortcode: {m.group(0)[:40]}"))
            break

        # Every local reference in an attribute or a srcset candidate list.
        urls = set()
        for m in LOCAL_ATTR.finditer(text):
            urls.add(m.group(1))
        for m in SRCSET_ATTR.finditer(text):
            for cand in m.group(1).split(","):
                u = cand.strip().split(" ")[0]
                if u:
                    urls.add(u)

        for u in sorted(urls):
            if is_local(u) and not resolves(u):
                broken_hits.append((rel, u, "missing in public/"))

    # Only report each distinct broken target once per page, not per occurrence.
    dedup: "dict[tuple[str, str], int]" = {}
    for rel, u, why in broken_hits:
        dedup[(rel, u)] = dedup.get((rel, u), 0) + 1

    blocks, related_hits = related_report(PUBLIC)

    if sentinel_hits:
        print(f"render: FAIL — {len(sentinel_hits)} page(s) contain a template "
              f"sentinel:", file=sys.stderr)
        for rel, s in sentinel_hits[:25]:
            print(f"  {rel}  [{s}]", file=sys.stderr)

    if dedup:
        print(f"render: FAIL — {len(dedup)} broken local reference(s):",
              file=sys.stderr)
        for (rel, u) in sorted(dedup)[:25]:
            print(f"  {rel}\n      {u}", file=sys.stderr)

    if related_hits:
        print(f"render: FAIL — {len(related_hits)} Further Reading ordering "
              f"problem(s):", file=sys.stderr)
        for c in related_hits[:25]:
            print(f"  {c}", file=sys.stderr)

    if sentinel_hits or dedup or related_hits:
        print(
            "\n  A rendered page can be broken while the build succeeds, the\n"
            "  source is valid, and the URL returns 200. Check URL attributes\n"
            "  for unescaped spaces or a rejected value (Go emits ZgotmplZ).",
            file=sys.stderr,
        )
        print(f"coverage: {len(built)} pages")
        print(f"related: {blocks} blocks inspected")
        return 1

    if not quiet:
        print(f"render: OK — {len(pages())} pages, no sentinels, "
              f"all local refs resolve, {blocks} related blocks ranked")
    print(f"coverage: {len(built)} pages")
    print(f"related: {blocks} blocks inspected")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Guard built output against template sentinels and broken local refs.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    return scan(args.quiet)


if __name__ == "__main__":
    sys.exit(main())
