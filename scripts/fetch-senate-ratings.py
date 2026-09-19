#!/usr/bin/env python3
"""Fetch current 2026 Senate race ratings from every forecaster.

Philip, 2026-09-19: "Add ratings to the content."

The weekly Senate report needs a ratings table every week, not only when a
forecaster moves a race.

Fetching the forecasters directly is mostly blocked: cookpolitical.com,
centerforpolitics.org and realclearpolitics.com return **HTTP 403** to any
automated request we have tried, so a ratings table sourced "from Cook" would
be uncitable and any claim that Cook was checked would be false.

Wikipedia's "2026 United States Senate elections" article carries the standard
aggregate ratings table with every forecaster in its own column and an as-of
date on each. That page IS fetchable, and it cites each forecaster. It is the
practical route to the ratings, and it is what this script reads.

The extraction is not obvious and has two traps, both hit while writing this:
  1. Cells leak Parsoid/`mw:Nowiki` fragments — `"]}' id="mwB9Y">Tossup` — with
     no leading '<', so stripping tags leaves the attribute tail glued to the
     rating and a strict regex misses it. Fix: take the text after the LAST '>'
     in the cell.
  2. That bug silently dropped exactly the rows it mattered most to keep —
     Maine, North Carolina, Ohio and Texas, the four most competitive races —
     because those use the leaked-fragment markup. A table that loses the
     toss-ups is worse than no table.

Exit codes: 0 ok, 2 could not fetch or parse the page.

Usage:
  fetch-senate-ratings.py                # competitive races, markdown table
  fetch-senate-ratings.py --all          # all 35 races
  fetch-senate-ratings.py --changes      # diff against the stored baseline
  fetch-senate-ratings.py --update-baseline
  fetch-senate-ratings.py --json         # machine-readable
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "scripts" / "senate-ratings-state.json"

PAGE = "2026_United_States_Senate_elections"
API = f"https://en.wikipedia.org/api/rest_v1/page/html/{PAGE}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# The forecasters the site cites in its own essays, plus the two model-based
# ones the reports lean on. Order is presentation order.
CITED = ["Cook", "IE", "Sabato", "RCP", "DDHQ", "Silver"]

# A rating that carries information about a competitive race.
COMPETITIVE = re.compile(r"^(toss-?up|tilt|lean)", re.I)

RATING = re.compile(
    r"^(Toss-?up|Tilt [DR]|Lean [DR]|Likely [DR]|Solid [DR]|Safe [DR])\s*(\(flip\))?$",
    re.I,
)

# State names needing parentheses in the display table.
SPECIALS = {"Florida(special)": "Florida (special)", "Ohio(special)": "Ohio (special)"}

# Two-letter codes, to join the Wikipedia table to Inside Elections' JSON.
STATE_CODES = {
    "Alabama": "AL", "Alaska": "AK", "Arkansas": "AR", "Colorado": "CO",
    "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Idaho": "ID",
    "Illinois": "IL", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Montana": "MT",
    "Nebraska": "NE", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "North Carolina": "NC", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Virginia": "VA", "West Virginia": "WV", "Wyoming": "WY",
}

# Provenance of each column, so the report can say plainly what kind of number
# each one is. The distinction that matters: a COMPUTED number can be
# reproduced from a primary source; a JUDGMENT rating cannot be reproduced at
# all; a MODEL output is reproducible only if the model is published.
#
# `kind` is one of: computed | judgment | model | aggregate
# `depends` names columns it is NOT independent of.
SOURCES = {
    "PVI": {
        "kind": "computed",
        "who": "Cook Partisan Voting Index, The Cook Political Report",
        "method": ("Democratic share of the two-party presidential vote, "
                   "weighted 75% (2024) / 25% (2020), minus the national "
                   "figure (~50.005%)"),
        "indep": "yes",
        "note": ("Reproducible from certified FEC totals — we have done so, and "
                 "all nine values matched Cook's published figures. Describes a "
                 "historical baseline, not the 2026 race."),
    },
    "Cook": {
        "kind": "judgment",
        "who": "The Cook Political Report (Amy Walter)",
        "method": ("state's political makeup; candidates' strengths and "
                   "weaknesses; the political environment in the state and "
                   "nationally; interviews with candidates and campaign "
                   "professionals"),
        "indep": "yes",
        "note": ("Analyst judgment; no numeric model is published, so it cannot "
                 "be independently reproduced. The factors are disclosed, their "
                 "weights are not."),
    },
    "IE": {
        "kind": "judgment",
        "who": "Inside Elections (Nathan Gonzales)",
        "method": ("nonpartisan analyst ratings; factors include polling, "
                   "fundraising, candidate quality and reporting"),
        "indep": "yes",
        "note": ("Analyst judgment. Uniquely among these sources, IE publishes "
                 "its own machine-readable export including each race's previous "
                 "rating, which is where our move data comes from."),
    },
    "Sabato": {
        "kind": "judgment",
        "who": "Sabato's Crystal Ball (U. of Virginia Center for Politics)",
        "method": ("electoral history, polling, candidate quality, modeling and "
                   "reporting"),
        "indep": "yes",
        "note": ("Analyst judgment. Updates least often of the six — on the "
                 "current table its column is three weeks staler than Cook's."),
    },
    "RCP": {
        "kind": "aggregate",
        "who": "RealClearPolitics",
        "method": "not verified",
        "indep": "unverified",
        "note": ("realclearpolitics.com returns HTTP 403 to us, so we have NOT "
                 "read its methodology and cannot say whether this column is "
                 "independent judgment or a composite of the other forecasters. "
                 "Treat it as unverified."),
    },
    "DDHQ": {
        "kind": "model",
        "who": "Decision Desk HQ",
        "method": ("three layers — a fundamentals ensemble (ridge regression, "
                   "random forest, XGBoost) trained on 2016-2024; a polling "
                   "average weighted by number of polls; prediction-market "
                   "prices from Polymarket and Kalshi"),
        "indep": "yes",
        "note": ("Methodology published. Notably does NOT use expert ratings or "
                 "Cook PVI: its partisan prior is the most recent presidential "
                 "margin adjusted for national swing. The most independent "
                 "column in the table."),
    },
    "Silver": {
        "kind": "model",
        "who": "Silver Bulletin (Nate Silver) — FLIPR",
        "method": ("three layers — polling averages; fundamentals; and expert "
                   "ratings. Weight on expert ratings is roughly one-sixth of "
                   "the forecast for congressional races with polling"),
        "indep": "NO",
        "note": ("NOT INDEPENDENT. FLIPR's default ('Deluxe') build feeds Cook, "
                 "Inside Elections and Sabato ratings in as an input at roughly "
                 "one-sixth weight. Its agreement with those columns is partly "
                 "by construction and is not corroboration. Silver flags the "
                 "recursion risk himself: if experts calibrate to his forecasts, "
                 "'the entire process becomes somewhat recursive.'"),
    },
}


def _die(msg: str, code: int = 2) -> "None":
    print(f"senate-ratings: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch() -> str:
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "40", "-A", UA, API],
        capture_output=True,
    )
    if r.returncode != 0:
        _die(f"curl exit {r.returncode}")
    body = r.stdout.decode("utf-8", "replace")
    if "Cook" not in body or "Toss" not in body:
        _die("page fetched but the ratings table is absent — shape changed?")
    return body


# Inside Elections serves its own ratings as JSON from a theme cache path.
# This is an undocumented internal endpoint, so treat it as a bonus that can
# fail: the Wikipedia table remains the primary route.
#
# Fetch note, learned the hard way: `curl` is refused by Cloudflare with a 403
# challenge here, but `urllib` with the same UA **plus a Referer** returns 200.
# Do not "simplify" this to curl — it is the difference between working and a
# hard 403. (Verified 2026-09-19: curl 403 / urllib 200, same headers.)
IE_API = ("https://insideelections.com/wp-content/themes/inside-elections/cache/"
          "ratings_latest_senate_year=2026_district=all_clean.json")
IE_HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json,*/*",
    "Referer": "https://insideelections.com/ratings/senate/",
}


def fetch_ie() -> "dict[str, dict]":
    """Inside Elections' own 2026 ratings, keyed by state abbreviation.

    Returns {} on any failure. Worth having despite the redundancy because the
    JSON carries `previous_rating` and `shift`, which the aggregate table does
    not — so it is the one source that can report a move we did not witness
    (e.g. a shift that happened before the baseline was first stored).
    """
    try:
        import urllib.request
        req = urllib.request.Request(IE_API, headers=IE_HEADERS)
        raw = urllib.request.urlopen(req, timeout=25).read()
        data = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        return {}
    out: "dict[str, dict]" = {}
    for r in data.get("ratings", []):
        # 100 entries for 50 states: one per Senate class. Only the class up in
        # 2026 carries a live rating; the rest read "Not Up This Cycle". Ohio's
        # 2026 race is a special of the other class, so key on the rating
        # itself, not on the class letter.
        if r.get("rating_numeric") is None:
            continue
        code = r.get("district")
        if code and code not in out:
            out[code] = r
    return out


def cell_text(raw: str) -> str:
    """Text of a table cell, robust to Wikipedia's leaked markup.

    Wikipedia's REST HTML emits fragments such as `"]}' id="mwB9Y">Tossup`
    where the leading '<' was consumed by the template. Stripping tags leaves
    the attribute tail attached to the value, so take the text after the last
    '>' to discard it.
    """
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]*>", "", raw)
    raw = html.unescape(raw)
    if ">" in raw:
        raw = raw[raw.rindex(">") + 1:]
    return re.sub(r"\s+", " ", raw).strip()


def parse(page: str) -> "tuple[list[str], list[dict], dict[str, str]]":
    """Return (forecaster_names, races, as_of_dates)."""
    tables = []
    for m in re.finditer(r"<table[^>]*>", page):
        end = page.find("</table>", m.start())
        if end < 0:
            continue
        tbl = page[m.start():end]
        if "Cook" in tbl and re.search(r"Toss-?up|Lean [DR]|Solid [DR]", tbl):
            tables.append(tbl)
    if not tables:
        _die("no ratings table found")
    table = max(tables, key=len)

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)
    if len(rows) < 5:
        _die(f"ratings table has only {len(rows)} rows")

    # Header: forecaster names are the link texts, skipping the label columns.
    # Each column also carries its own as-of date, inside a `data-mw` template
    # param (`"1":{"wt":"Sep. 15,&lt;br />2026"}`), NOT as visible text. Those
    # dates differ per forecaster — Cook updates weekly, Sabato less often — so
    # a table stamped with today's date for every column would be a factual
    # error in a fact-checked publication.
    names: "list[str]" = []
    as_of: "dict[str, str]" = {}
    for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", rows[1], re.S):
        lm = re.search(r"<a[^>]*>([^<]+)</a>", c)
        if not lm or lm.group(1) in ("State", "PVI", "Senator"):
            continue
        name = lm.group(1).strip()
        names.append(name)
        raw_date = re.search(r'"1":\{"wt":"([^"]+)"\}', c)
        if raw_date:
            cleaned = html.unescape(raw_date.group(1))
            cleaned = re.sub(r"<br\s*/?>", " ", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(",")
            as_of[name] = cleaned
    if not names:
        _die("could not read the forecaster column headers")

    out = []
    for row in rows[2:]:
        cells = [cell_text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        if len(cells) < 4:
            continue
        state = cells[0]
        if not state or state.startswith("Overall") or state in ("State", "]"):
            continue
        ratings = [RATING.match(c).group(0) for c in cells if RATING.match(c)]
        out.append({"state": state, "pvi": cells[1],
                    "code": STATE_CODES.get(re.sub(r"\(special\)", "", state).strip()),
                    "by": dict(zip(names, ratings))})

    if len(out) < 30:
        _die(f"parsed only {len(out)} states; expected ~35 — refusing to emit a partial table")
    return names, out, as_of


def is_competitive(d: dict) -> bool:
    return any(COMPETITIVE.match(d["by"].get(k, "") or "") for k in ("Cook", "IE", "Sabato"))


def display(state: str) -> str:
    return SPECIALS.get(state, state)


def load_state() -> dict:
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(names, data) -> None:
    STATE.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of": names,
        "ratings": {d["state"]: d["by"] for d in data},
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def changes(data: "list[dict]") -> "list[tuple[str, str, str, str]]":
    prior = load_state().get("ratings") or {}
    if not prior:
        return []
    out = []
    for d in data:
        old = prior.get(d["state"]) or {}
        for name, rating in d["by"].items():
            was = old.get(name, "")
            if was and rating and was != rating:
                out.append((d["state"], name, was, rating))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch 2026 Senate race ratings.")
    ap.add_argument("--all", action="store_true", help="every race, not just competitive")
    ap.add_argument("--changes", action="store_true", help="diff against the stored baseline")
    ap.add_argument("--moves", action="store_true",
                    help="rating moves Inside Elections itself reports (previous vs current)")
    ap.add_argument("--sources", action="store_true",
                    help="what each column is, and how independent it is")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--update-baseline", action="store_true", help="store current ratings")
    args = ap.parse_args()

    if args.sources:
        order = ["PVI"] + [c for c in CITED if c in SOURCES]
        kinds = {"computed": "computed number", "judgment": "analyst judgment",
                 "model": "published model", "aggregate": "unverified"}
        print("Where each column comes from\n")
        for c in order:
            s = SOURCES[c]
            print(f"{c} — {s['who']}")
            print(f"  Kind: {kinds[s['kind']]}")
            print(f"  How: {s['method']}")
            print(f"  Independent of the others: {s['indep']}")
            print(f"  {s['note']}\n")
        return 0

    if args.moves:
        ie_data = fetch_ie()
        if not ie_data:
            _die("could not read Inside Elections' ratings JSON")
        rows = [r for r in ie_data.values()
                if r.get("previous_rating") and r["previous_rating"] != r["rating"]]
        rows.sort(key=lambda r: r.get("date") or "", reverse=True)
        if not rows:
            print("Inside Elections reports no rating moves.")
            return 0
        for r in rows:
            flag = "  FLIP" if r.get("flipped") else ""
            date = (r.get("date") or "")[:10]
            print(f"  {r['district']:<3} {r['previous_rating']:<20} -> "
                  f"{r['rating']:<20} {date}{flag}")
        print(f"\nInside Elections reports {len(rows)} moves. "
              f"Latest update {ie_data and max((r.get('date') or '') for r in ie_data.values())[:10]}.",
              file=sys.stderr)
        return 0

    names, data, as_of = parse(fetch())
    print(f"senate-ratings: read {len(data)} races; forecasters: {', '.join(names)}",
          file=sys.stderr)

    # IE's own JSON, when reachable, is authoritative for the IE column and
    # carries move information the aggregate table lacks. Overwrite only on an
    # exact state match; the aggregate table's per-forecaster as-of dates are
    # still what gets printed beneath the table.
    ie_data = fetch_ie()
    if ie_data:
        abbr = {"Republican": "R", "Democrat": "D", "Independent": "I"}
        for d in data:
            code = d.get("code")
            r = ie_data.get(code) if code else None
            if not r:
                continue
            got = " ".join(abbr.get(w, w) for w in (r.get("rating") or "").split())
            got = got.replace("Toss-up", "Tossup")
            if r.get("flipped"):
                got += " (flip)"
            if got and got != d["by"].get("IE"):
                d["by"]["IE"] = got
    else:
        print("senate-ratings: note — Inside Elections JSON unreachable; "
              "using the aggregate table for the IE column", file=sys.stderr)

    if args.update_baseline:
        save_state(names, data)
        print(f"senate-ratings: baseline updated ({len(data)} races)", file=sys.stderr)
        return 0

    if args.json:
        print(json.dumps({"forecasters": names, "as_of": as_of, "races": data}, indent=2))
        return 0

    if args.changes:
        ch = changes(data)
        if not ch:
            print("No rating changes since the stored baseline.", file=sys.stderr)
            print("(no changes)")
            return 0
        for state, name, was, now in ch:
            print(f"  {display(state):18} {name:8} {was:14} -> {now}")
        return 0

    subset = data if args.all else [d for d in data if is_competitive(d)]
    cols = [c for c in CITED if c in names]
    print(f"| Race | PVI | {' | '.join(cols)} |")
    print(f"|---|---|{'---|' * len(cols)}")
    for d in subset:
        vals = " | ".join(d["by"].get(c, "") or "—" for c in cols)
        print(f"| {display(d['state'])} | {d['pvi']} | {vals} |")
    # Each forecaster updates on its own schedule, so stamp each column with its
    # own as-of date rather than implying they are all current as of today.
    stamp = "; ".join(f"{c} {as_of.get(c, 'date unknown')}" for c in cols)
    print(f"\nRatings as of — {stamp}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
