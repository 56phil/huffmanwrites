#!/usr/bin/env python3
"""Detect when a published essay's factual claims have expired.

WHY THIS EXISTS. Three essays published on 2026-11-04 carry claims that were
true when they were written and will not stay true: "The Year the Floor Moved"
opens on a Mississippi margin that a call will replace and closes on a Senate
balance of 54 to 44 that two calls will change; "The Tally" rests on two
day-count series, and a series that stops is a fact the reader cannot see. The
Sachs piece has `nord-stream-watch` because its triggers are named events; these
are the same shape, and without a watcher they go stale in silence.

WHAT IT DOES NOT DO. It does not rewrite a body paragraph. An amendment is an
appended, dated note that quotes the headline which carries the news and links
to it — the same shape the Sachs plan uses for a public reply. The verified
prose above the note is never touched, so no gate has to judge new argument, and
the note's own claim is a quotation the online link check can confirm.

DISCOVERY, NOT INFERENCE. A call is never derived from a margin, because a
margin is an order in the count and a call is a decision someone made. The
detector reads feeds the outlets publish and requires a headline that says a
candidate won; "43 votes separate" is a headline this checker must not fire on,
which is why the decisive and non-decisive patterns are separate lists rather
than one clever regex.

Exit codes: 0 nothing found, 1 a finding (not a failure), 3 a source could not
be read and the answer is unknown.

Usage:
    python3 scripts/essay-watch.py                 # report findings
    python3 scripts/essay-watch.py --list          # print the registry
    python3 scripts/essay-watch.py --json          # machine-readable findings
    python3 scripts/essay-watch.py --apply floor-ms [--now ISO]
"""

from __future__ import annotations

import argparse
import email.utils
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

# The repo root is injectable so a test can run the whole apply path against a
# throwaway tree; every other script here derives it from its own location, and
# a test that wrote into the live essays would be the defect, not the test.
REPO = Path(os.environ.get("ESSAY_WATCH_REPO") or Path(__file__).resolve().parent.parent)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

# --- the registry -----------------------------------------------------------
# One entry per claim that can expire. `since` is the moment the essay was
# published: an item older than it cannot be the news that expired the claim.
# `feeds` are the outlets that would carry a call first and are readable without
# a browser — AP's own feed answers 403 to a client, so its pages are read by a
# human and never by this job.
WATCHES = [
    {
        "id": "floor-ms",
        "essay": "content/posts/essays/the-year-the-floor-moved.md",
        "kind": "call",
        "race": "Mississippi Senate",
        "since": "2026-11-04T08:35:00-06:00",
        "feeds": [
            "https://www.wdam.com/arc/outboundfeeds/rss/?outputType=xml",
            "https://mississippitoday.org/feed/",
        ],
        "names": ["Hyde-Smith", "Colom"],
    },
    {
        "id": "floor-ak",
        "essay": "content/posts/essays/the-year-the-floor-moved.md",
        "kind": "call",
        "race": "Alaska Senate",
        "since": "2026-11-04T08:35:00-06:00",
        "feeds": ["https://alaskabeacon.com/feed/"],
        "names": ["Sullivan", "Peltola"],
    },
    {
        "id": "tally-iran",
        "essay": "content/posts/essays/the-tally.md",
        "kind": "series",
        "series": "US War on Iran",
        "label": "the Iran day count",
        "since": "2026-11-04T08:05:00-06:00",
        "feeds": ["https://eaworldview.com/author/eaworldview/feed/"],
    },
    {
        "id": "tally-ukraine",
        "essay": "content/posts/essays/the-tally.md",
        "kind": "series",
        "series": "Ukraine War",
        "label": "the Ukraine day count",
        "since": "2026-11-04T08:05:00-06:00",
        "feeds": ["https://eaworldview.com/author/eaworldview/feed/"],
    },
]

# A headline that says someone won. Anything else is an order in the count.
DECISIVE = re.compile(
    r"\b(wins?|won|victorious|victor(?:y|ies)|defeats?|defeated|prevails?|"
    r"is elected|projected (?:the )?winner|wins? reelection|"
    r"certif(?:y|ies|ied)|declared (?:the )?winner)\b",
    re.I,
)
# A headline that says the count is not finished. Checked first: an outlet writes
# "Colom leads, race uncalled", and "leads" inside a sentence about a decision
# must not turn into a call.
NOT_YET = re.compile(
    r"\b(separate[sd]?|separated|leads?|leading|trail(?:s|ing)?|"
    r"toss-?up|too close|uncalled|not called|await(?:s|ing)?|"
    r"margin|count(?:ing)? continues|yet to be|no winner)\b",
    re.I,
)
# A headline that says a war ended, for a series watch.
ENDED = re.compile(
    r"\b(ends?|ended|over|ceasefire|cease-fire|peace deal|truce|capitulat\w*|"
    r"surrenders?|armistice)\b",
    re.I,
)

# The Iran series is titled "UPDATES: US War on Iran, Day 251"; Ukraine's is
# "Ukraine War, Days 1,713-1,714" and "Ukraine War, Day 1,712" — both shapes.
DAY_NUMBER = {
    "US War on Iran": re.compile(r"US War on Iran,\s*Day\s*([\d,]+)"),
    "Ukraine War": re.compile(r"Ukraine War,\s*Days?\s*([\d,]+)"),
}

# The note anchors its link on the outlet, never on the date alone: a link whose
# visible text is a date tells the reader nothing about where it goes, which the
# house link rule forbids.
OUTLETS = {
    "wdam.com": "WDAM",
    "mississippitoday.org": "Mississippi Today",
    "alaskabeacon.com": "Alaska Beacon",
    "eaworldview.com": "EA WorldView",
}

# Seven days, not four. A daily series that pauses for a long weekend is not a
# series that stopped, and a note saying it stopped would be false in a way no
# gate can see; a week of silence in a column published every day is a stop.
STALE_AFTER = timedelta(days=7)
MARKER = "<!-- essay-watch:{} -->"
ATTRIBUTION = re.compile(r"^\*PRH \| .*\*$", re.M)


def log(msg: str) -> None:
    print(msg)


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def feed_items(url: str) -> list[dict]:
    """Titles, links and dates from an RSS or Atom feed, in document order."""
    raw = fetch(url)
    items: list[dict] = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return items
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        title = link = date = ""
        for child in node:
            name = child.tag.split("}")[-1]
            text = (child.text or "").strip()
            if name == "title":
                title = re.sub(r"\s+", " ", text)
            elif name == "link":
                link = text or child.get("href", "")
            elif name in ("pubDate", "published", "updated"):
                date = text
        items.append({"title": title, "link": link, "date": parse_date(date)})
    del ns
    return items


def parse_date(text: str) -> datetime | None:
    if not text:
        return None
    try:
        return email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def as_local(dt: datetime | None) -> str:
    if dt is None:
        return "date unknown"
    return dt.astimezone().strftime("%-d %B %Y")


def check_call(watch: dict, now: datetime) -> dict | None:
    since = datetime.fromisoformat(watch["since"])
    best = None
    for url in watch["feeds"]:
        for item in feed_items(url):
            title = item["title"]
            if not any(name in title for name in watch["names"]):
                continue
            if not DECISIVE.search(title):
                continue
            if NOT_YET.search(title):
                continue
            if item["date"] and item["date"] < since:
                continue
            if not item["link"]:
                continue
            if best is None or (item["date"] and best["date"] and item["date"] > best["date"]):
                best = {**item, "feed": url}
    if not best:
        return None
    return {
        "id": watch["id"],
        "race": watch["race"],
        "headline": best["title"],
        "url": best["link"],
        "date": best["date"],
    }


def check_series(watch: dict, now: datetime) -> dict | None:
    pattern = DAY_NUMBER[watch["series"]]
    latest = None
    ended = None
    for url in watch["feeds"]:
        for item in feed_items(url):
            m = pattern.search(item["title"])
            if m:
                day = int(m.group(1).replace(",", ""))
                if latest is None or day > latest["day"]:
                    latest = {**item, "day": day}
                continue
            # A headline that ends the war, naming it, and is newer than the
            # last count published: that is the trigger a day count cannot show.
            if watch["series"].split()[0].lower() in item["title"].lower() and ENDED.search(item["title"]):
                if ended is None or (item["date"] and ended["date"] and item["date"] > ended["date"]):
                    ended = item
    if latest is None:
        return None
    stale = now - latest["date"] if latest["date"] else None
    if ended and ended["date"] and latest["date"] and ended["date"] > latest["date"]:
        return {
            "id": watch["id"],
            "race": watch["label"],
            "headline": ended["title"],
            "url": ended["link"],
            "date": ended["date"],
            "reason": "ended",
        }
    if stale and stale > STALE_AFTER:
        return {
            "id": watch["id"],
            "race": watch["label"],
            "headline": latest["title"],
            "url": latest["link"],
            "date": latest["date"],
            "reason": "stopped",
            "days": stale.days,
        }
    return None


def findings(now: datetime) -> tuple[list[dict], int]:
    found: list[dict] = []
    errors = 0
    for watch in WATCHES:
        try:
            got = check_call(watch, now) if watch["kind"] == "call" else check_series(watch, now)
        except Exception as exc:  # a source that cannot be read is not a finding
            log(f"  {watch['id']}: SOURCE UNAVAILABLE — {exc}")
            errors += 1
            continue
        if got:
            found.append(got)
    return found, errors


def outlet_name(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    for key, name in OUTLETS.items():
        if key in host:
            return name
    return host.replace("www.", "")


def note_text(finding: dict) -> str:
    """The amendment: a dated note quoting the headline that carries the news.

    Quoting the headline rather than paraphrasing it is the whole safety
    argument. A paraphrase is a claim about the article; a quotation is a string
    the online link check can confirm is on the page.
    """
    date = as_local(finding["date"])
    outlet = outlet_name(finding["url"])
    marker = MARKER.format(finding["id"])
    if finding.get("reason") == "stopped":
        return (
            f'> **Update, {date}.** The count above is the last entry of its series: '
            f'"{finding["headline"]}" ([{outlet}, {date}]({finding["url"]})). Nothing newer has '
            f'appeared in the {finding["days"]} days since, so treat the figure as a final entry '
            f'rather than a live one.\n{marker}\n'
        )
    if finding.get("reason") == "ended":
        return (
            f'> **Update, {date}.** The war this count belongs to appears to be over: '
            f'"{finding["headline"]}" ([{outlet}, {date}]({finding["url"]})). The number above therefore '
            f'records where the counting stopped.\n{marker}\n'
        )
    return (
        f'> **Update, {date}.** The {finding["race"]} count above was the figure at the time of '
        f'writing, not a result. The outlet that carried the call reported it this way: '
        f'"{finding["headline"]}" ([{outlet}, {date}]({finding["url"]})).\n{marker}\n'
    )


def apply_finding(finding: dict) -> int:
    watch = next(w for w in WATCHES if w["id"] == finding["id"])
    path = REPO / watch["essay"]
    text = path.read_text()
    if MARKER.format(finding["id"]) in text:
        log(f"  {finding['id']}: already amended, nothing to do")
        return 0
    if not ATTRIBUTION.search(text):
        log(f"  {finding['id']}: REFUSED — {watch['essay']} has no closing attribution line")
        return 3
    # Insert before the attribution, so the canonical last line stays last.
    m = ATTRIBUTION.search(text)
    head, tail = text[: m.start()], text[m.start() :]
    path.write_text(head.rstrip("\n") + "\n\n" + note_text(finding) + "\n" + tail)
    log(f"  {finding['id']}: note appended to {watch['essay']}")
    return 0


def fixture_findings() -> tuple[list[dict], int]:
    """Findings from a JSON file, so the amend path can be exercised for real.

    `ESSAY_WATCH_FIXTURE=/tmp/f.json` with `ESSAY_WATCH_DRY=1` is how the runner's
    apply → gate → build chain is proved without waiting for a race to be called.
    The fixture supplies the whole finding, URL included, so the note it renders
    is checked against a real page like any other; it is a smoke path, never
    something the plist sets.
    """
    path = Path(os.environ["ESSAY_WATCH_FIXTURE"])
    raw = json.loads(path.read_text())
    out = []
    for item in raw if isinstance(raw, list) else [raw]:
        item = dict(item)
        if item.get("date"):
            item["date"] = datetime.fromisoformat(item["date"])
        out.append(item)
    return out, 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print the registry and exit")
    ap.add_argument("--json", action="store_true", help="machine-readable findings")
    ap.add_argument("--apply", metavar="ID", help="append the dated note for one finding")
    ap.add_argument("--now", help="ISO timestamp to judge staleness against (testing)")
    args = ap.parse_args()

    if args.list:
        for w in WATCHES:
            log(f"{w['id']:<16} {w['kind']:<7} {w['essay']}")
        log(f"coverage: {len(WATCHES)} watches")
        return 0

    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)

    if args.apply:
        found, errors = fixture_findings() if os.environ.get("ESSAY_WATCH_FIXTURE") else findings(now)
        match = next((f for f in found if f["id"] == args.apply), None)
        if not match:
            log(f"essay-watch: {args.apply} has no current finding; nothing to apply")
            return 0 if not errors else 3
        return apply_finding(match)

    found, errors = fixture_findings() if os.environ.get("ESSAY_WATCH_FIXTURE") else findings(now)
    if args.json:
        print(json.dumps(found, indent=2, default=str))
        return 1 if found else (3 if errors else 0)
    if found:
        log(f"essay-watch: {len(found)} finding(s)")
        for f in found:
            log(f"  [{f['id']}] {f['race']}: {f['headline']}")
            log(f"      {f['url']}")
        log(f"coverage: {len(WATCHES)} watches, {len(found)} finding(s)")
        return 1
    log("essay-watch: nothing to report")
    log(f"coverage: {len(WATCHES)} watches")
    return 3 if errors and not found and errors == len(WATCHES) else 0


if __name__ == "__main__":
    sys.exit(main())
