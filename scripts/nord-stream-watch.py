#!/usr/bin/env python3
"""Watch for a reply from Jeffrey Sachs, or a verdict in the Hamburg Nord Stream trial.

WHY THIS EXISTS. "The Bet He Called a Fact" (content/posts/essays/
the-bet-he-called-a-fact.md, published 2026-11-04) makes two promises a reader is
entitled to see kept: that a verdict in the Hamburg trial would change what the
piece is entitled to say, and that a public reply from Sachs would belong in the
record. Both arrive on nobody's schedule. The trial's hearings run to February
2027 with no verdict date, and Sachs answers his critics within days when he
answers at all (the Lviv Herald reply of 19 October 2026 is the model case).

Nothing else in this repo can see either event: no job reads a site it does not
publish to, and a watcher that is not scheduled is a watcher that does not run.

WHAT IT WATCHES, and why only two sources:

  * jeffsachs.org/interviewsandmedia, through the site's own RSS feed, which
    lists every interview with its date and link. A new item is fetched and
    searched for "Nord Stream"; a reply that never names the pipeline in its
    title still names it in the transcript, so the page is the test, not the
    headline.
  * the Hanseatisches Oberlandesgericht press-release archive, which carries the
    trial's own announcements (the indictment's admission, the side-joinder
    ruling, and in time a verdict). Its item keys are the numeric ids at the end
    of each release's slug; a new id whose headline or page mentions Nord Stream
    is a finding.

The Bundesanwaltschaft is deliberately NOT a source. Its press index 404s at the
documented path, and its two Nord Stream releases (indictment, second arrest) are
already behind the article's argument; a third release would be a charging
decision, which the Hamburg court's own announcements carry first.

WHY THE FIRST RUN IS SILENT. A watcher that alerts on everything already on the
page raises a banner about four-year-old news on the day it is installed, which
is how a new alert gets learned as noise. The first run records what is there and
says so. Everything after it compares against that record.

Exit codes, matching the vocabulary the shared alert reads: 0 nothing new (or a
seed run), 1 a new item worth reading, 3 a source could not be fetched. A
finding is not a failure, and the runner says so in the alert's detail line.

Usage:
    python3 scripts/nord-stream-watch.py
    python3 scripts/nord-stream-watch.py --dry-run          # no state write
    python3 scripts/nord-stream-watch.py --state /tmp/x.json --seed
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

STATE_FILE = Path.home() / "Library" / "Logs" / "nord-stream-watch-state.json"

SACHS_FEED = "https://www.jeffsachs.org/interviewsandmedia?format=rss"
HAMBURG_ARCHIVE = (
    "https://justiz.hamburg.de/gerichte/oberlandesgericht/gerichtspressestelle/"
    "alle-pressemitteilungen"
)

# The pipeline is written three ways across the sources, and the German pages
# use both "Nord Stream" and "Nord-Stream" (including inside a compound).
KEYWORDS = ("nord stream", "nord-stream", "nordstream")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) huffmanwrites-watch"


def fetch(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def matches(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in KEYWORDS)


def sachs_items(xml: str) -> "list[tuple[str, str, str, str]]":
    """(key, title, page url, blurb) for every feed item.

    The feed is a plain RSS 2.0 document from Squarespace, so a regex over
    <item> blocks is enough and pulls in no parser dependency. A malformed
    entry is skipped rather than fatal: one bad item must not blind the watcher
    to the next one.

    Two details the feed forces. The <link> is usually a YOUTUBE url, and a
    YouTube page carries no transcript text to search, while the item's own
    Squarespace permalink sits in the first anchor of its <description> and does
    carry the summary or transcript. So the page tested is the permalink when
    the feed offers one, and <link> only as a fallback. The key is the <guid>,
    which is stable even when the link target changes.
    """
    out = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.S):
        link = re.search(r"<link>(.*?)</link>", block, re.S)
        title = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block, re.S)
        guid = re.search(r"<guid[^>]*>(.*?)</guid>", block, re.S)
        desc = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", block, re.S)
        if not (link or guid):
            continue
        raw_desc = desc.group(1) if desc else ""
        permalink = re.search(r'href="(https://www\.jeffsachs\.org/[^"]+)"', raw_desc)
        blurb = re.sub(r"<[^>]+>", " ", raw_desc)
        key = (guid.group(1).strip() if guid else (link.group(1).strip() if link else ""))
        out.append((
            key,
            (title.group(1).strip() if title else ""),
            (permalink.group(1) if permalink else (link.group(1).strip() if link else "")),
            blurb,
        ))
    return out


def hamburg_items(html: str) -> "list[tuple[str, str]]":
    """(release id, headline) for every press release on the archive page.

    The headline is an <h3> and the link is a later anchor whose href ends in
    the release's own slug and numeric id, so the two are paired by proximity:
    an h3, then the next gerichtspressestelle href before the following h3.
    The id is the key because the slug is re-typed when a headline changes and
    the id is not.
    """
    out = []
    parts = re.split(r"<h3[^>]*>", html)
    for part in parts[1:]:
        head_end = part.find("</h3>")
        if head_end < 0:
            continue
        headline = re.sub(r"<[^>]+>", " ", part[:head_end])
        headline = re.sub(r"\s+", " ", headline).strip()
        href = re.search(r'href="(/gerichte/oberlandesgericht/gerichtspressestelle/[^"]*?-(\d+))"', part[head_end:])
        if not href:
            continue
        out.append((href.group(2), headline))
    return out


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default=str(STATE_FILE), help="state file path")
    ap.add_argument("--dry-run", action="store_true", help="report findings but write no state")
    ap.add_argument("--seed", action="store_true", help="record what is there and report nothing")
    args = ap.parse_args(argv)

    state_path = Path(args.state)
    try:
        state = json.loads(state_path.read_text())
    except (OSError, ValueError):
        state = {}
    seen = {"sachs": state.get("sachs") or [], "hamburg": state.get("hamburg") or []}
    known = {"sachs": set(seen["sachs"]), "hamburg": set(seen["hamburg"])}
    first_run = "sachs" not in state and "hamburg" not in state

    failures: "list[str]" = []
    findings: "list[str]" = []

    try:
        feed = fetch(SACHS_FEED)
        items = sachs_items(feed)
        if not items:
            failures.append("jeffsachs.org feed parsed to zero items")
        for key, title, page_url, blurb in items:
            if key in known["sachs"]:
                continue
            known["sachs"].add(key)
            seen["sachs"].append(key)
            if first_run:
                continue
            try:
                page = fetch(page_url) if page_url else ""
            except Exception as e:  # a single unfetchable item is not a source failure
                print(f"nord-stream-watch: could not fetch {page_url}: {e}", file=sys.stderr)
                page = ""
            if matches(title) or matches(blurb) or matches(page):
                findings.append(f"NEW {title or page_url} — {page_url}")
    except Exception as e:
        failures.append(f"Sachs feed unavailable: {e}")

    try:
        html = fetch(HAMBURG_ARCHIVE)
        items = hamburg_items(html)
        if not items:
            failures.append("Hamburg archive parsed to zero releases")
        for rid, headline in items:
            if rid in known["hamburg"]:
                continue
            known["hamburg"].add(rid)
            seen["hamburg"].append(rid)
            if first_run:
                continue
            if matches(headline):
                findings.append(f"NEW {headline} — release id {rid}")
    except Exception as e:
        failures.append(f"Hamburg archive unavailable: {e}")

    if not args.dry_run:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(seen, indent=1, sort_keys=True) + "\n")

    if first_run:
        print(
            "nord-stream-watch: seeded "
            f"{len(seen['sachs'])} Sachs item(s) and {len(seen['hamburg'])} court release(s); no findings on a seed run"
        )
        return 0
    if failures:
        print("nord-stream-watch: could not verify — " + "; ".join(failures))
        return 3
    if findings:
        print(f"nord-stream-watch: {len(findings)} new item(s) worth reading")
        for f in findings:
            print(f"FINDING: {f}")
        return 1
    print("nord-stream-watch: nothing new")
    return 0


if __name__ == "__main__":
    sys.exit(main())
