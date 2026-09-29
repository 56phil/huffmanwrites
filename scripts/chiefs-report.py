#!/usr/bin/env python3
"""Collect the week's Kansas City Chiefs data into a briefing pack.

Philip, 2026-09-25: "Every Tuesday, at 1830 CT, publish a comprehensive report
on the Kansas City Chiefs."

This script exists so the report is REPRODUCIBLE and its numbers are observed
rather than remembered. It answers the same question `check-docket.py --report`
answers for the dockets — "what is true this week" rather than "what is new
since I last looked" — and it is the single source of truth for the facts the
weekly article is built on. The writer reads this output; it does not recall
scores, records, or schedules.

Two design decisions worth naming.

**No User-Agent header, deliberately, and this is the opposite of every other
script in this repo.** ESPN's API answers a default client with 200 and answers
a browser User-Agent string with 403 — measured across all four endpoints used
here (standings, team schedule, news, game summary). `check-links.py` and
`fetch-senate-ratings.py` both set a Chrome UA because the hosts they read
refuse the default one. Copying that habit here would 403 every request. The
403 is a bot-management rule keyed on the header, not on the client, so the fix
is to send no UA at all. Do not "normalize" this to match the other scripts.

**Every URL in the output comes from a payload.** The repo's most dangerous
failure is a constructed URL that returns 200 and lands on the wrong page
(CLAUDE.md). A link handed over by the feed is an observed URL; one assembled
from a game id or a headline slug is exactly that fabrication. `collect_urls`
and the pack's own links are therefore read out of the ESPN response, and a test
asserts that every URL printed here appears in the input payload.

Usage:
  chiefs-report.py                    # the week's briefing pack (markdown)
  chiefs-report.py --season-state     # exit 0 in season, 3 off season, 2 unknown
  chiefs-report.py --json             # the pack's structured form
  chiefs-report.py --today 2027-03-01 # evaluate as if run on a past date

Exit codes: 0 ok, 2 could not fetch or parse (the run cannot be trusted),
3 off season (the runner skips, which is not an error).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TEAM = "kc"
TEAM_ID = "12"
TEAM_NAME = "Kansas City Chiefs"

API = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"

# The site's clock is Central Time; every dated line in the pack is stamped in
# it so a Tuesday 18:30 run cannot be read as a Wednesday game.
try:
    from zoneinfo import ZoneInfo

    CT = ZoneInfo("America/Chicago")
except Exception:  # noqa: BLE001 - a missing tz database must not break the run
    CT = timezone(timedelta(hours=-5))

# News older than this is not this week's news. Two weeks, not one, because a
# bye week or a quiet stretch should still yield a report rather than an empty
# section, and the writer is told to lead with whatever is genuinely newest.
NEWS_WINDOW_DAYS = 14
NEWS_LIMIT = 25


class FetchError(RuntimeError):
    """The feed could not be read. Never conflated with 'nothing to report'."""


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------
def fetch(url: str, timeout: float = 30.0, ua: str = "") -> dict:
    """GET a JSON endpoint. Raises FetchError, never returns a partial payload.

    No User-Agent by default: see the module docstring. ESPN 403s a browser UA
    here. `ua` exists for the prediction-market venues, which are the opposite
    rule — Polymarket's Gamma API answers a default client with 403 and a named
    client with 200 (measured 2026-09-28), so the caller passes one explicitly.
    """
    req = urllib.request.Request(url, headers={"User-Agent": ua} if ua else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} for {url}") from e
    except Exception as e:  # noqa: BLE001 - any transport failure is the same finding
        raise FetchError(f"{type(e).__name__} for {url}: {e}") from e
    try:
        return json.loads(body)
    except ValueError as e:
        raise FetchError(f"non-JSON response from {url}: {e}") from e


def sources(year: int | None = None) -> "dict[str, str]":
    """The endpoints the pack is built from, in one place.

    Same discipline as the docket registry: the list of what is read lives here
    and nowhere else, so a change of source never means editing the runner, the
    skill, and the plist together.

    `year=None` asks for the feed's own current season, which is the right
    default and the safe one: an NFL season straddles the new year (September
    2026 through February 2027), so a run on 2027-01-06 belongs to the 2026
    season and `today.year` would ask for the wrong one. `--today` passes an
    explicit year for testing, and `assert_season` refuses to report a season
    the feed did not actually serve.
    """
    q = f"?season={year}" if year else ""
    # `level=3` is required, not cosmetic. Without it the standings endpoint
    # returns the conference's sixteen teams as one flat list and NO division
    # children at all, so the division table comes back empty and the section
    # silently disappears from the pack. Measured 2026-09-25:
    #   standings?season=2026           -> AFC children: [], entries: 16
    #   standings?season=2026&level=3   -> AFC children: [East, North, South, West]
    # This is exactly the class of bug the gates exist for — a source that
    # answers 200 with a plausible payload that is missing what you asked for.
    standings_q = "level=3" + (f"&season={year}" if year else "")
    return {
        "league": f"{API}/scoreboard",
        "schedule": f"{API}/teams/{TEAM}/schedule{q}",
        "team": f"{API}/teams/{TEAM}",
        "standings": f"https://site.api.espn.com/apis/v2/sports/football/nfl/standings?{standings_q}",
        "news": f"{API}/news?limit=50&team={TEAM_ID}",
        "season_stats": f"{API}/teams/{TEAM}/statistics{q}",
    }


def assert_season(payload: dict, asked: int | None, what: str) -> None:
    """Refuse to report a season the feed did not serve.

    This exists because ESPN fails OPEN on an unknown season, which is the
    worst possible behaviour for a scheduled job. Measured on 2026-09-25:
    `standings?season=2027` does not error — it returns 200 with the **2026**
    standings, sixteen teams and all. `teams/kc/schedule?season=2027` returns
    an empty event list and `requestedSeason: null`. A writer handed either
    payload would produce a report about the wrong season, and nothing in it
    would look wrong.

    So the requested year must appear in the response. `requestedSeason` is the
    reliable field where the endpoint sets it; `season.year` is the fallback.
    When neither is present and a year was asked for, that is a failure, not a
    blank to fill in.
    """
    if asked is None:
        return
    req = (payload.get("requestedSeason") or {}).get("year")
    served = (payload.get("season") or {}).get("year")
    if req == asked or served == asked:
        return
    raise FetchError(
        f"{what} did not serve season {asked} (requestedSeason={req!r}, "
        f"season.year={served!r}); ESPN answers an unknown season with the "
        f"current one instead of an error, so this cannot be used"
    )


def game_summary_url(event_id: str) -> str:
    return f"{API}/summary?event={event_id}"


def opponent_schedule_url(abbr: str, year: int | None = None) -> str:
    q = f"?season={year}" if year else ""
    return f"{API}/teams/{abbr.lower()}/schedule{q}"


# ---------------------------------------------------------------------------
# Pure helpers (tested directly in scripts/test_gates.py)
# ---------------------------------------------------------------------------
def parse_date(value: str) -> date:
    """'2026-09-27T17:00Z' -> date. ISO only; anything else is a hard failure."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value or "")
    if not m:
        raise ValueError(f"unparseable date: {value!r}")
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def league_calendar(payload: dict) -> "list[dict]":
    """The league's own calendar: [{'label', 'type', 'start', 'end', 'periods'}]."""
    leagues = payload.get("leagues") or []
    if not leagues:
        raise FetchError("scoreboard payload carries no leagues array")
    cal = leagues[0].get("calendar")
    if not cal:
        raise FetchError("scoreboard payload carries no league calendar")
    out = []
    for entry in cal:
        out.append(
            {
                "label": entry.get("label") or "",
                "type": str(entry.get("value") or ""),
                "start": parse_date(entry.get("startDate") or ""),
                "end": parse_date(entry.get("endDate") or ""),
                "periods": [
                    {
                        "label": p.get("label") or "",
                        "value": str(p.get("value") or ""),
                        "start": parse_date(p.get("startDate") or ""),
                        "end": parse_date(p.get("endDate") or ""),
                        "detail": p.get("detail") or "",
                    }
                    for p in (entry.get("entries") or [])
                ],
            }
        )
    if not out:
        raise FetchError("league calendar parsed to nothing")
    return out


def season_state(cal: "list[dict]", today: date) -> "dict":
    """Where `today` sits in the league calendar.

    'Off Season' is the only phase the job skips, and it is taken from the
    league's own calendar rather than from a hardcoded month range, so the
    schedule rolls over by itself next year instead of quietly going stale.
    """
    for entry in cal:
        if entry["start"] <= today < entry["end"]:
            period = None
            for p in entry["periods"]:
                if p["start"] <= today < p["end"]:
                    period = p
                    break
            return {
                "phase": entry["label"],
                "type": entry["type"],
                "starts": entry["start"].isoformat(),
                "ends": entry["end"].isoformat(),
                "period": period["label"] if period else "",
                "period_detail": period["detail"] if period else "",
                "in_season": entry["label"].strip().lower() != "off season",
            }
    raise FetchError(
        f"{today.isoformat()} falls outside every calendar window the league "
        f"publishes ({cal[0]['start']} to {cal[-1]['end']}); the calendar has "
        f"probably rolled over and needs a look"
    )


def event_side(event: dict, abbr: str) -> "dict | None":
    """Pull one team's side out of a competition, plus the opponent's."""
    comps = event.get("competitions") or [{}]
    comp = comps[0]
    sides = comp.get("competitors") or []
    me = next((c for c in sides if (c.get("team") or {}).get("abbreviation") == abbr.upper()), None)
    if me is None:
        return None
    them = next((c for c in sides if c is not me), None)
    return {"comp": comp, "me": me, "them": them}


def _score(side: "dict | None") -> "str | None":
    if not side:
        return None
    s = side.get("score")
    if isinstance(s, dict):
        return s.get("displayValue")
    return s


def _record(side: "dict | None") -> "str | None":
    if not side:
        return None
    rec = side.get("record")
    if isinstance(rec, list) and rec:
        return rec[0].get("displayValue") or rec[0].get("summary")
    return None


def game_links(event: dict) -> "list[str]":
    """Every URL the feed itself attached to this event, deduplicated, in order.

    Read out of the payload. Nothing here is assembled from the game id, which
    is how a constructable-but-wrong link would otherwise get in.
    """
    out: "list[str]" = []
    for link in event.get("links") or []:
        href = link.get("href") if isinstance(link, dict) else None
        if href and href.startswith("http") and href not in out:
            out.append(href)
    for comp in event.get("competitions") or []:
        for link in comp.get("links") or []:
            href = link.get("href") if isinstance(link, dict) else None
            if href and href.startswith("http") and href not in out:
                out.append(href)
    return out


def pick_games(events: "list[dict]", abbr: str, today: date) -> "dict":
    """The most recent completed game, the next scheduled one, and the window.

    `days_back` sets how far back a completed game still counts as "this week's"
    game. Eight days covers a Monday-night game reported on the following
    Tuesday with a day to spare.
    """
    done: "list[tuple[date, dict]]" = []
    ahead: "list[tuple[date, dict]]" = []
    for ev in events:
        side = event_side(ev, abbr)
        if side is None:
            continue
        try:
            when = parse_date(ev.get("date") or "")
        except ValueError:
            continue
        status = ((side["comp"].get("status") or {}).get("type") or {})
        if status.get("completed"):
            done.append((when, ev))
        elif (status.get("state") or "") == "pre":
            ahead.append((when, ev))
    done.sort(key=lambda x: x[0])
    ahead.sort(key=lambda x: x[0])
    return {
        "last": done[-1][1] if done else None,
        "last_date": done[-1][0].isoformat() if done else None,
        "next": ahead[0][1] if ahead else None,
        "next_date": ahead[0][0].isoformat() if ahead else None,
        "played": len(done),
    }


def describe_game(event: dict, abbr: str) -> "dict | None":
    """Flatten one game into the facts a writer needs, all from the payload."""
    side = event_side(event, abbr)
    if side is None:
        return None
    comp = side["comp"]
    status = (comp.get("status") or {}).get("type") or {}
    me, them = side["me"], side["them"]
    mine, theirs = _score(me), _score(them)
    home = (me.get("homeAway") or "") == "home"
    return {
        "id": event.get("id"),
        "date": event.get("date"),
        "week": (event.get("week") or {}).get("number"),
        "name": event.get("name"),
        "short_name": event.get("shortName"),
        "status": status.get("description"),
        "detail": status.get("detail"),
        "completed": bool(status.get("completed")),
        "home": home,
        "opponent": (them or {}).get("team", {}).get("abbreviation"),
        "opponent_name": (them or {}).get("team", {}).get("displayName"),
        "team_score": mine,
        "opponent_score": theirs,
        "team_record": _record(me),
        "opponent_record": _record(them),
        "won": bool((me or {}).get("winner")) if status.get("completed") else None,
        "venue": (comp.get("venue") or {}).get("fullName"),
        "broadcasts": [
            ((b.get("media") or {}).get("shortName"))
            for b in (comp.get("broadcasts") or [])
            if (b.get("media") or {}).get("shortName")
        ],
        "links": game_links(event),
    }


def urls_in(value) -> "set[str]":
    """Every http(s) URL anywhere inside a nested structure.

    Used by the test that proves the pack never prints a URL the feed did not
    supply — the machine-checkable half of the no-constructed-URL rule.
    """
    out: "set[str]" = set()
    if isinstance(value, str):
        out.update(re.findall(r"https?://[^\s\)\]\"'<>]+", value))
    elif isinstance(value, dict):
        for v in value.values():
            out |= urls_in(v)
    elif isinstance(value, list):
        for v in value:
            out |= urls_in(v)
    return out


def _news_links(article: dict) -> "list[str]":
    links = article.get("links") or {}
    web = links.get("web") if isinstance(links, dict) else None
    if isinstance(web, dict) and web.get("href", "").startswith("http"):
        return [web["href"]]
    return []


def recent_news(payload: dict, today: date, days: int = NEWS_WINDOW_DAYS) -> "list[dict]":
    """KC-tagged articles inside the window, newest first, with observed URLs."""
    out = []
    for a in payload.get("articles") or []:
        tagged = any(
            (c.get("type") == "team" and (c.get("uid") or "").endswith(f"t:{TEAM_ID}"))
            for c in (a.get("categories") or [])
        )
        if not tagged:
            continue
        try:
            published = parse_date(a.get("published") or "")
        except ValueError:
            continue
        if (today - published).days > days or published > today + timedelta(days=1):
            continue
        out.append(
            {
                "headline": (a.get("headline") or "").strip(),
                "description": (a.get("description") or "").strip(),
                "type": a.get("type") or "",
                "published": a.get("published"),
                "date": published.isoformat(),
                "byline": a.get("byline") or "",
                "links": _news_links(a),
            }
        )
    out.sort(key=lambda x: x["published"] or "", reverse=True)
    return out[:NEWS_LIMIT]


def division_standings(standings: dict, abbr: str) -> "dict":
    """The team's own division table, plus the conference seed list.

    The conference seed list is rebuilt from the DIVISION entries rather than
    from `afc['standings']['entries']`. With `level=3` the conference node
    carries children and no entries of its own (measured 2026-09-25: AFC
    children = four divisions, entries = 0), so reading the conference node's
    entries returns an empty list and the seed line silently vanishes from the
    pack — the same "200 with a plausible payload missing what you asked for"
    failure as the missing `level=3` itself.
    """
    afc = next((c for c in standings.get("children") or []
                if c.get("abbreviation") == "AFC"), None)
    if afc is None:
        raise FetchError("standings payload carries no AFC conference")
    divisions = afc.get("children") or []
    mine = None
    conference: "list[dict]" = []
    for d in divisions:
        for e in (d.get("standings") or {}).get("entries") or []:
            stats = {s.get("name"): s.get("displayValue") for s in (e.get("stats") or [])}
            team = e.get("team") or {}
            if team.get("abbreviation") == abbr.upper():
                mine = d
            conference.append(
                {
                    "team": team.get("abbreviation"),
                    "name": team.get("displayName"),
                    "id": str(team.get("id") or ""),
                    "overall": stats.get("overall"),
                    "seed": stats.get("playoffSeed"),
                }
            )
    if mine is None:
        raise FetchError(f"{abbr} not found in any AFC division")
    rows = []
    for e in (mine.get("standings") or {}).get("entries") or []:
        stats = {s.get("name"): s.get("displayValue") for s in (e.get("stats") or [])}
        team = e.get("team") or {}
        rows.append(
            {
                "team": team.get("abbreviation"),
                "name": team.get("displayName"),
                "id": str(team.get("id") or ""),
                "overall": stats.get("overall"),
                "division": stats.get("vs. Div."),
                "conference": stats.get("vs. Conf."),
                "points_for": stats.get("pointsFor"),
                "points_against": stats.get("pointsAgainst"),
                "differential": stats.get("differential"),
                "streak": stats.get("streak"),
                "seed": stats.get("playoffSeed"),
            }
        )
    if not conference:
        raise FetchError("no conference entries parsed from any AFC division")
    return {"division": mine.get("name"), "rows": rows, "conference": conference}


def box_score(summary: dict, abbr: str) -> "dict":
    """Team stat lines and the passing/rushing/receiving leaders, both sides."""
    box = summary.get("boxscore") or {}
    teams = {}
    for t in box.get("teams") or []:
        teams[(t.get("team") or {}).get("abbreviation")] = {
            s.get("label"): s.get("displayValue") for s in (t.get("statistics") or [])
        }
    sides = {}
    for t in box.get("players") or []:
        ab = (t.get("team") or {}).get("abbreviation")
        cats = {}
        for cat in t.get("statistics") or []:
            labels = cat.get("labels") or []
            rows = []
            for a in (cat.get("athletes") or [])[:4]:
                stats = a.get("stats") or []
                rows.append(
                    {
                        "athlete": (a.get("athlete") or {}).get("displayName"),
                        "line": ", ".join(
                            f"{v} {labels[i]}" for i, v in enumerate(stats) if i < len(labels)
                        ),
                    }
                )
            cats[cat.get("name")] = rows
        sides[ab] = cats
    return {"team_stats": teams, "leaders": sides, "mine": abbr.upper()}


def scoring_plays(summary: dict) -> "list[dict]":
    out = []
    for p in summary.get("scoringPlays") or []:
        out.append(
            {
                "period": (p.get("period") or {}).get("number"),
                "clock": (p.get("clock") or {}).get("displayValue"),
                "text": p.get("text"),
                "away": p.get("awayScore"),
                "home": p.get("homeScore"),
            }
        )
    return out


def injuries(summary: dict, abbr: str) -> "dict":
    """Both teams' injury reports, name and status only."""
    out = {}
    for t in summary.get("injuries") or []:
        ab = (t.get("team") or {}).get("abbreviation")
        rows = []
        for i in t.get("injuries") or []:
            rows.append(
                {
                    "player": (i.get("athlete") or {}).get("displayName"),
                    "position": ((i.get("athlete") or {}).get("position") or {}).get("abbreviation"),
                    "status": i.get("status"),
                    "date": i.get("date"),
                }
            )
        out[ab] = rows
    if abbr.upper() not in out and out:
        raise FetchError(f"no injury block for {abbr} in the summary payload")
    return out


def pickcenter(summary: dict) -> "list[dict]":
    """Odds lines, attributed to the provider the feed names. Never re-derived."""
    out = []
    for p in summary.get("pickcenter") or []:
        out.append(
            {
                "provider": (p.get("provider") or {}).get("name"),
                "details": p.get("details"),
                "spread": p.get("spread"),
                "over_under": p.get("overUnder"),
                "home_money_line": ((p.get("homeTeamOdds") or {}).get("moneyLine")),
                "away_money_line": ((p.get("awayTeamOdds") or {}).get("moneyLine")),
            }
        )
    return out


def team_form(summary: dict, abbr: str) -> "list[dict]":
    """The last five games the summary payload itself lists, with its own URLs."""
    out = []
    for grp in summary.get("lastFiveGames") or []:
        if (grp.get("team") or {}).get("abbreviation") != abbr.upper():
            continue
        for e in grp.get("events") or []:
            out.append(
                {
                    "date": (e.get("gameDate") or "")[:10],
                    "week": e.get("week"),
                    "result": e.get("gameResult"),
                    "at_vs": e.get("atVs"),
                    "opponent": (e.get("opponent") or {}).get("abbreviation"),
                    "score": e.get("score"),
                    "links": [l.get("href") for l in (e.get("links") or [])
                              if (l.get("href") or "").startswith("http")],
                }
            )
    return out


# ---------------------------------------------------------------------------
# Prediction markets (Kalshi and Polymarket)
#
# Philip, 2026-09-28: "add a Kalshi/Polymarket table … to the weekly Chiefs
# Report." The report is about the games, so the markets here are the season-
# long ones that frame the games (championship, conference, division, playoff
# odds, win total) plus the one player market a reader follows. The single-game
# spread stays where it already lives — in the ESPN `pickcenter` block, which is
# the feed's own line and is attributed to the book it names.
#
# Three decisions worth naming, because each is a way this goes wrong.
#
# **Nothing here is constructed.** Every figure is read from the venues' own
# public JSON, and the two venue names are the only strings this module writes
# that are not in a payload. This is the repo's most dangerous rule (CLAUDE.md
# §Citations): a quote that looks checkable and is wrong. The failure it is
# exposed to here is subtler than an invented URL — a market that has gone
# STALE reads exactly like a live one, because the bid, the ask and the last
# trade all remain valid-looking long after the last trade. So every quote
# carries `updated_time`, the section prints it, and the writer is told to
# distrust a Kalshi season market that has not moved in weeks. That is not
# hypothetical: on 2026-09-28 the Kalshi AFC West and AFC title markets had not
# updated since 2026-07-13, two months before the season, while Polymarket's
# equivalent carried current prices. One venue's number is not the other's, and
# which one is stale is the reader's only defence.
#
# **A failure is a gap, not a zero.** Neither venue is required for the report
# to ship. If Kalshi times out, the Polymarket table still prints; if both fail,
# the section says so in the pack and the writer is told to omit the table
# rather than write around absent numbers. `market_sources` returns per-venue
# errors and the renderer prints them, so "the venue was unreachable" can never
# be misread as "the market is quiet".
#
# **Markets are matched by meaning, not by season.** Kalshi encodes the season
# in the event ticker (`KXSB-27`, `KXNFL1SEED-AFC26`) and Polymarket bakes a
# creation timestamp into the slug for some events
# (`…-2027-champion-20260729185915366`) but not others. Hardcoding either would
# be wrong by next season and wrong quietly. So Kalshi is discovered through the
# SERIES ticker with `status=open` (the open event is selected; a series has one
# open event at a time) and Polymarket through the NFL tag listing by slug
# shape. A market that disappears is reported as absent, never guessed at.
# ---------------------------------------------------------------------------

# Polymarket's Gamma API refuses a default client; a named one is answered.
MARKET_UA = "huffmanwrites-chiefs-report/1.0 (+https://huffmanwrites.org)"

# A bid/ask spread this wide is a thin book, not a price. The midpoint of a
# 0.32/0.64 book is 0.48, which reads as a real 48% forecast and is not one —
# measured on the Kalshi win-total ladder 2026-09-28, it made the ladder
# non-monotonic. Such a row is printed with its spread and marked.
WIDE_SPREAD = 0.10

KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2"
GAMMA_API = "https://gamma-api.polymarket.com"

# The Kalshi series the report reads, keyed by the label the pack prints. The
# value is (series_ticker, market_sub_title_match or None). `match` selects one
# row out of a multi-market event: the win-total series carries a ladder of
# fourteen thresholds, and the AFC seed series carries both conferences.
KALSHI_SERIES = [
    ("Super Bowl champion", "KXSB", "Kansas City"),
    ("AFC champion", "KXNFLAFCCHAMP", "Kansas City"),
    ("AFC West champion", "KXNFLAFCWEST", "Kansas City"),
    ("Playoff qualifier", "KXNFLPLAYOFF", "Kansas City"),
    ("AFC No. 1 seed", "KXNFL1SEED", "Kansas City"),
    ("MVP", "KXNFLMVP", "Patrick Mahomes"),
]
# The win total is a separate shape (a ladder, not a named team), so it is read
# on its own and summarised at the thresholds that bracket the median rather
# than printed fourteen rows deep.
KALSHI_WIN_TOTAL_SERIES = "KXNFLWINS"
KALSHI_WIN_TOTAL_EVENT = "KXNFLWINS-27KC"

# Polymarket events, keyed by the label the pack prints, matched by slug shape.
# `None` means the event carries one row per team and the Chiefs row is
# selected by `groupItemTitle`; a string selects the event outright.
POLYMARKET_EVENTS = [
    ("Super Bowl champion", "-2027-champion-", "Kansas City Chiefs"),
    ("AFC champion", "-2027-afc-champion", "Kansas City Chiefs"),
    ("AFC West champion", "-afc-west-champion", "Kansas City Chiefs"),
    ("Playoff qualifier", "nfl-team-to-make-postseason", "Kansas City Chiefs"),
    # The MVP event label is "2026 MVP Winner" while the season it prices is
    # 2026-27; the slug is matched on its shape rather than the year.
    ("MVP", "-mvp-winner", "Patrick Mahomes"),
]


def market_sources() -> "dict[str, str]":
    """The two venue listing endpoints, in one place."""
    return {
        "kalshi": f"{KALSHI_API}/events?series_ticker={{series}}&status=open&limit=20",
        "polymarket": f"{GAMMA_API}/events?tag_slug=nfl&limit=100&active=true&closed=false",
    }


def _dollars(value) -> "float | None":
    """Kalshi's `*_dollars` strings -> float. A null or unparseable value is None.

    The API serves prices as decimal STRINGS in dollars ('0.5300'), and the
    older integer-cents fields (`yes_bid`) are null on current payloads, so
    reading those would report every market as blank. None is the honest result
    for a market with no quote: it is not zero.
    """
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def kalshi_quote(event: dict, match: "str | None") -> "dict | None":
    """One market out of a Kalshi event, or None when it is not there.

    `match` selects by `yes_sub_title` (the team or player the row is about).
    A market with no bid and no ask is returned with None prices rather than
    dropped: an open market nobody is quoting is a fact about the market, and
    silently omitting it would make the table look more complete than it is.

    **`volume_24h_fp` and `moved`, never `updated_time`.** Kalshi's
    `updated_time` is not a trade time and must not be read as freshness. The
    evidence, measured 2026-09-28: thirty-two markets across the whole playoff
    series share one `updated_time` to the microsecond
    (`2026-09-03T15:33:13.064423Z`), whole series batches share others, and the
    AFC West market was stamped `2026-07-13` while its `volume_24h_fp` read
    2,842 — it was trading. It is a series-level metadata write. The field that
    actually answers "is this current" is `volume_24h_fp`, with `moved` (today's
    quote against the venue's own `previous_*`) as corroboration: on the same
    market the book went 0.53/0.55 to 0.52/0.53 between two calls minutes apart.
    Kalshi publishes no last-trade timestamp at all, so none is invented here.
    """
    markets = event.get("markets") or []
    row = None
    if match is None:
        row = markets[0] if markets else None
    else:
        row = next((m for m in markets if (m.get("yes_sub_title") or "") == match), None)
    if row is None:
        return None
    bid = _dollars(row.get("yes_bid_dollars"))
    ask = _dollars(row.get("yes_ask_dollars"))
    last = _dollars(row.get("last_price_dollars"))
    # The midpoint is the fair read when both sides are quoted; when the book is
    # empty it is None (not the last trade), because a stale last trade is the
    # exact failure this section warns about. A WIDE book is the third case and
    # the one that misleads: on 2026-09-28 the Kalshi 13+ wins rung quoted
    # 0.32/0.64, whose midpoint (48%) sat above the tighter 12+ rung's (46%) and
    # made the win-total ladder non-monotonic — an artifact of one thin book,
    # read as a real inversion. So the spread is measured and a wide one is
    # flagged rather than averaged.
    mid = round((bid + ask) / 2, 3) if bid is not None and ask is not None else None
    spread = round(ask - bid, 3) if bid is not None and ask is not None else None
    # How much the quote has moved since the venue's own previous print. This is
    # the honest motion signal: `previous_*` is part of the same payload as the
    # live quote, so comparing them needs no timestamp.
    prev_bid = _dollars(row.get("previous_yes_bid_dollars"))
    prev_ask = _dollars(row.get("previous_yes_ask_dollars"))
    moved = None
    if bid is not None and prev_bid is not None:
        moved = round(bid - prev_bid, 3)
    elif ask is not None and prev_ask is not None:
        moved = round(ask - prev_ask, 3)
    return {
        "label": row.get("yes_sub_title") or row.get("title") or "",
        "title": row.get("title") or "",
        "yes_bid": bid,
        "yes_ask": ask,
        "last": last,
        "mid": mid,
        "spread": spread,
        "wide": bool(spread is not None and spread > WIDE_SPREAD),
        "volume": _dollars(row.get("volume_fp")),
        "open_interest": _dollars(row.get("open_interest_fp")),
        "volume_24h": _dollars(row.get("volume_24h_fp")),
        "previous_bid": prev_bid,
        "moved": moved,
        "status": row.get("status") or "",
        "ticker": row.get("ticker") or "",
        # Kept for the record but NOT used as a freshness signal; see above.
        "updated": row.get("updated_time") or "",
    }


def kalshi_markets() -> "tuple[list[dict], list[str]]":
    """Every KC-relevant Kalshi market, plus the failures. Never raises.

    Discovery is per series with `status=open`: a series carries one open event
    per season and the closed ones from prior seasons stay in the listing, so
    filtering on status is what keeps last February's market out of today's
    table. The nested-markets form is requested alongside it so one request per
    series returns the quotes as well as the event.
    """
    out: "list[dict]" = []
    failures: "list[str]" = []
    tpl = market_sources()["kalshi"]
    for label, series, match in KALSHI_SERIES:
        url = tpl.format(series=series) + "&with_nested_markets=true"
        try:
            payload = fetch(url, ua=MARKET_UA)
        except FetchError as e:
            failures.append(f"Kalshi {label}: {e}")
            continue
        events = payload.get("events") or []
        if not events:
            failures.append(f"Kalshi {label}: no open event for series {series}")
            continue
        quote = kalshi_quote(events[0], match)
        if quote is None:
            failures.append(f"Kalshi {label}: series {series} has no market for {match!r}")
            continue
        quote["label_short"] = label
        quote["venue"] = "Kalshi"
        # The URL that was actually fetched, kept as the citation the writer can
        # point at. A market page URL is NOT constructed here: kalshi.com serves
        # 429 to automated clients and the payload carries no page URL, so a
        # guessed path could not be checked (CLAUDE.md §Citations).
        quote["source_url"] = url
        out.append(quote)
    return out, failures


def kalshi_history(event_ticker: str, market_ticker: str, days: int = 45) -> "tuple[list[dict], str]":
    """Daily closes for one Kalshi market. Returns (points, error).

    **This is why the chart needs no accumulating history file.** Kalshi's
    candlestick endpoint serves the whole published series on demand, so the
    first run draws a full chart rather than starting a line from today and
    filling in over a season. Measured 2026-09-28: 45 daily candles for the AFC
    West market, each with `close_dollars` and `volume_fp`.

    `period_interval=1440` is minutes, i.e. daily. The chart is a weekly report,
    so a daily resolution is already more than it needs; hourly would be a
    thousand points of noise.
    """
    end = int(datetime.now(timezone.utc).timestamp())
    start = end - days * 86400
    url = (f"{KALSHI_API}/series/{event_ticker}/markets/{market_ticker}"
           f"/candlesticks?start_ts={start}&end_ts={end}&period_interval=1440")
    try:
        payload = fetch(url, ua=MARKET_UA)
    except FetchError as e:
        return [], str(e)
    out: "list[dict]" = []
    for c in payload.get("candlesticks") or []:
        ts = c.get("end_period_ts")
        # The mid of the candle's own quoted bid/ask, NOT `price.close_dollars`.
        # The `price` block is a traded-price series and disagrees with the book
        # (measured 2026-09-28: price.close 0.63 against a 0.58/0.61 book on the
        # same candle), while the live table in this same pack reports a bid/ask
        # mid. Using the same quantity in both is what keeps the chart and the
        # table from contradicting each other.
        bid_close = _dollars((c.get("yes_bid") or {}).get("close_dollars"))
        ask_close = _dollars((c.get("yes_ask") or {}).get("close_dollars"))
        if bid_close is not None and ask_close is not None:
            close = round((bid_close + ask_close) / 2, 3)
        else:
            close = _dollars((c.get("price") or {}).get("close_dollars"))
        if ts is None or close is None:
            continue
        out.append({
            "ts": int(ts),
            "date": datetime.fromtimestamp(int(ts), timezone.utc).date().isoformat(),
            "close": close,
            "volume": _dollars(c.get("volume_fp")) or 0.0,
        })
    out.sort(key=lambda p: p["ts"])
    return out, ""


def week_delta(points: "list[dict]", days: int = 7) -> "dict | None":
    """The change over `days`, comparing the newest close to the nearest older
    close at least `days` back.

    Comparing to a fixed calendar date would return None on the first run of a
    series that has only a few days of history; comparing to the oldest point
    that is far enough back lets a young series still report a delta, and `span`
    says how many days it actually covers so the writer never presents a
    three-day move as a week.
    """
    if len(points) < 2:
        return None
    newest = points[-1]
    cutoff = newest["ts"] - days * 86400
    older = [p for p in points if p["ts"] <= cutoff]
    ref = older[-1] if older else points[0]
    if ref is newest:
        return None
    return {
        "from_date": ref["date"],
        "to_date": newest["date"],
        "from": ref["close"],
        "to": newest["close"],
        "change": round(newest["close"] - ref["close"], 3),
        "span_days": round((newest["ts"] - ref["ts"]) / 86400),
    }


def _svg_escape(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_chart_svg(series: "list[dict]", width: int = 720, height: int = 340) -> str:
    """A static line chart of the season-long market prices, as inline SVG.

    **Hand-rolled, deliberately, and with no JavaScript and no external request.**
    Three reasons, each of which decides the design:

    1. `goldmark.renderer.unsafe` is `false` in `hugo.toml`, so a hand-written
       `<svg>` in a post body would be escaped to text. The chart is therefore
       an `<img>` pointing at a file, which Hugo serves without touching the
       markup (the same reason `hero_desktop` is a file path, not inline SVG).
    2. A charting library would be a script tag on a site whose CSP and whose
       whole posture is script-light, and an auto-published page is the last
       place to add a third-party fetch that can fail silently in production.
    3. It is ~60 lines of arithmetic. A dependency would cost more than it saves.

    Colours are the locked palette from `skills/hero-image-workflow.md`:
    midnight-navy ground, Parian-cream line, deep-amber accent. The chart is
    decorative in the literal sense — every number it draws is printed in the
    table beside it — so it carries `role="img"` with a text alternative rather
    than being interactive.
    """
    # Geometry. The right margin is sized for the end labels, which are drawn
    # OUTSIDE the plot; too narrow and they are clipped by the viewBox, which is
    # what shipped on the first render ("AFC West champion 52%" cut mid-label).
    ml, mr, mt, mb = 54, 150, 30, 40
    pw, ph = width - ml - mr, height - mt - mb
    palette = {"navy": "#131E39", "cream": "#F2EDD8", "amber": "#D4820A",
               "muted": "#8A93A8", "grid": "#2A3554"}

    usable = [s for s in series if len(s.get("points") or []) >= 2]
    if not usable:
        return ""

    all_ts = [p["ts"] for s in usable for p in s["points"]]
    t0, t1 = min(all_ts), max(all_ts)
    if t1 <= t0:
        return ""
    values = [p["close"] for s in usable for p in s["points"]]
    vmin, vmax = min(values), max(values)
    # A little headroom so the extremes are not painted on the frame edge, and a
    # floor on the span so a flat series does not divide by zero.
    span = max(vmax - vmin, 0.02)
    lo, hi = max(0.0, vmin - span * 0.15), min(1.0, vmax + span * 0.15)
    if hi - lo < 1e-9:
        hi = lo + 0.02

    def x(ts: float) -> float:
        return ml + (ts - t0) / (t1 - t0) * pw

    def y(v: float) -> float:
        return mt + (hi - v) / (hi - lo) * ph

    L: "list[str]" = []
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
             f'width="{width}" height="{height}" role="img" '
             f'aria-label="Kansas City Chiefs championship, conference, division, '
             f'playoff and MVP market prices over the last several weeks.">')
    L.append(f'<rect width="{width}" height="{height}" fill="{palette["navy"]}"/>')

    # Horizontal gridlines at 20-point intervals, labelled as percentages.
    step = 0.1 if (hi - lo) > 0.25 else 0.05
    v = (int(lo / step) + 1) * step
    while v < hi:
        yy = y(v)
        L.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + pw}" y2="{yy:.1f}" '
                 f'stroke="{palette["grid"]}" stroke-width="1"/>')
        L.append(f'<text x="{ml - 8}" y="{yy + 4:.1f}" fill="{palette["muted"]}" '
                 f'font-family="system-ui,sans-serif" font-size="11" '
                 f'text-anchor="end">{v * 100:.0f}%</text>')
        v += step

    # Axis frame + first/last date labels.
    L.append(f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" '
             f'stroke="{palette["muted"]}" stroke-width="1"/>')
    for ts, anchor in ((t0, "start"), (t1, "end")):
        xx = x(ts)
        label = datetime.fromtimestamp(ts, timezone.utc).date().isoformat()
        L.append(f'<text x="{xx:.1f}" y="{mt + ph + 20}" fill="{palette["muted"]}" '
                 f'font-family="system-ui,sans-serif" font-size="11" '
                 f'text-anchor="{anchor}">{label}</text>')

    # One polyline per series, then all the end labels in a single pass.
    #
    # Label placement is done top-down after the lines are drawn, rather than
    # nudging each label against the ones already placed. The nudge approach
    # shipped a clipped label on each edge: pushed down past the frame, and cut
    # off by the viewBox. A top-down pass with a minimum gap cannot overlap by
    # construction, and clamping the whole column into the plot's vertical band
    # cannot clip.
    drawn: "list[dict]" = []
    for s in usable:
        pts = " ".join(f"{x(p['ts']):.1f},{y(p['close']):.1f}" for p in s["points"])
        colour = s.get("colour") or palette["amber"]
        L.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" '
                 f'stroke-width="2" stroke-linejoin="round"/>')
        end_value = s.get("now")
        if end_value is None:
            end_value = s["points"][-1]["close"]
        drawn.append({"s": s, "colour": colour, "value": end_value})

    drawn.sort(key=lambda d: -d["value"])
    gap, top, bottom = 15, mt + 8, mt + ph - 2
    ys: "list[float]" = []
    cursor = top - gap
    for d in drawn:
        cursor = max(y(d["value"]), cursor + gap)
        ys.append(cursor)
    # If the column overflowed the lower bound, lift the whole stack by the
    # overflow so the bottom label sits on the floor and the rest follow.
    overflow = ys[-1] - bottom if ys else 0
    if overflow > 0:
        ys = [yy - overflow for yy in ys]

    for d, yy in zip(drawn, ys):
        L.append(f'<text x="{ml + pw + 8}" y="{yy + 4:.1f}" fill="{d["colour"]}" '
                 f'font-family="system-ui,sans-serif" font-size="11">'
                 f'{_svg_escape(d["s"]["label"])} {d["value"] * 100:.0f}%</text>')

    L.append("</svg>")
    return "\n".join(L)


def write_chart(series: "list[dict]", path: Path) -> "str":
    """Render and write the chart. Returns '' on success, a reason on failure.

    A failure here is not fatal to the report: the chart is a visual aid and
    every number in it is printed in the table. So this returns a reason the
    pack can carry rather than raising, and the writer is told to omit the
    figure rather than reference a file that was never written — which would be
    a broken image on a page nobody reviews.
    """
    svg = build_chart_svg(series)
    if not svg:
        return "not enough history to draw a chart"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8")
    except OSError as e:
        return f"could not write {path}: {e}"
    return ""


def kalshi_win_total_ladder() -> "tuple[list[dict], list[str]]":
    """The Chiefs win-total ladder: every rung, cheapest first.

    This is a threshold ladder (`9+ wins`, `10+ wins`, … `17 wins`), not a set of
    competing outcomes, so it is reported whole rather than reduced to one
    number. The writer reads the 50% crossing off it for the market's expected
    win total. Finalized rungs (a threshold already cleared by the games played)
    are dropped: `2+ wins` is settled, not a forecast.
    """
    url = (f"{KALSHI_API}/events/{KALSHI_WIN_TOTAL_EVENT}"
           "?with_nested_markets=true")
    try:
        payload = fetch(url, ua=MARKET_UA)
    except FetchError as e:
        return [], [f"Kalshi win total: {e}"]
    markets = (payload.get("event") or {}).get("markets") or []
    out: "list[dict]" = []
    for m in markets:
        if (m.get("status") or "") != "active":
            continue
        bid = _dollars(m.get("yes_bid_dollars"))
        ask = _dollars(m.get("yes_ask_dollars"))
        # A rung the market prices as certain is not a forecast. Three rungs sat
        # at ask 1.00 on 2026-09-28 (4+, 5+, 6+ wins), and printing them made the
        # ladder read backwards at the top: 98%, 96%, 99%. Dropping them leaves
        # the rungs that still carry information about the season's shape.
        if ask is not None and ask >= 0.99:
            continue
        spread = round(ask - bid, 3) if bid is not None and ask is not None else None
        prev_bid = _dollars(m.get("previous_yes_bid_dollars"))
        out.append({
            "label": m.get("yes_sub_title") or "",
            "floor": m.get("floor_strike"),
            "yes_bid": bid,
            "yes_ask": ask,
            "mid": round((bid + ask) / 2, 3) if bid is not None and ask is not None else None,
            "spread": spread,
            "wide": bool(spread is not None and spread > WIDE_SPREAD),
            "volume": _dollars(m.get("volume_fp")),
            "volume_24h": _dollars(m.get("volume_24h_fp")),
            "moved": (round(bid - prev_bid, 3)
                      if bid is not None and prev_bid is not None else None),
            # Same warning as `kalshi_quote`: this is a series metadata write,
            # not a trade time, and it is not used as a freshness signal.
            "updated": m.get("updated_time") or "",
        })
    out.sort(key=lambda r: (r["floor"] is None, r["floor"]))
    return out, []


def polymarket_number(value, index: int = 0) -> "float | None":
    """Gamma serves outcomes and prices as JSON-encoded STRINGS in a list.

    `outcomePrices` is `'["0.575", "0.425"]'` — a string, not an array — so it
    must be decoded before it can be indexed. A malformed value yields None
    rather than raising, because one bad market must not fail the whole table.
    """
    if value is None:
        return None
    seq = value
    if isinstance(value, str):
        try:
            seq = json.loads(value)
        except ValueError:
            return None
    if not isinstance(seq, list) or index >= len(seq):
        return None
    try:
        return float(seq[index])
    except (TypeError, ValueError):
        return None


def polymarket_event_map() -> "tuple[dict[str, dict], list[str]]":
    """Every active NFL event on Polymarket, keyed by slug. Plus failures.

    One paginated listing rather than a request per market: the tag listing is
    the venue's own index of what it currently offers, so a market that has been
    withdrawn simply is not in it, and nothing has to be guessed from a slug.
    The listing is capped (three pages of 100) so a runaway tag cannot turn a
    weekly job into an unbounded crawl.
    """
    tpl = market_sources()["polymarket"]
    out: "dict[str, dict]" = {}
    failures: "list[str]" = []
    for offset in (0, 100, 200):
        try:
            page = fetch(f"{tpl}&offset={offset}", ua=MARKET_UA)
        except FetchError as e:
            failures.append(f"Polymarket listing offset {offset}: {e}")
            break
        if not isinstance(page, list) or not page:
            break
        for e in page:
            if e.get("slug"):
                out[e["slug"]] = e
        if len(page) < 100:
            break
    return out, failures


def polymarket_quote(event: dict, match: "str | None") -> "dict | None":
    """One team's row out of a Polymarket event, or None.

    `outcomePrices[0]` is the YES price. The bid/ask are used for the fair read
    where both are quoted; the YES price is the fallback, and it is reported as
    `last` rather than as a midpoint so a reader can tell a traded price from a
    quoted spread.
    """
    markets = event.get("markets") or []
    row = None
    if match is None:
        row = markets[0] if markets else None
    else:
        row = next((m for m in markets
                    if (m.get("groupItemTitle") or "") == match), None)
    if row is None:
        return None
    yes = polymarket_number(row.get("outcomePrices"), 0)
    bid = _dollars(row.get("bestBid"))
    ask = _dollars(row.get("bestAsk"))
    mid = round((bid + ask) / 2, 3) if bid is not None and ask is not None else None
    slug = event.get("slug") or ""
    # Polymarket, unlike Kalshi, does publish real activity: `volume24hr` is
    # traded volume over the last day and `oneHourPriceChange` is the move over
    # the last hour (measured 2026-09-28: the AFC West market carried
    # volume24hr 168.54 and oneHourPriceChange -0.005). `updatedAt` here is the
    # event's book-refresh stamp, which for a live market is seconds old, so the
    # two venues' activity fields are NOT comparable and the pack says so.
    return {
        "label": row.get("groupItemTitle") or event.get("title") or "",
        "question": row.get("question") or "",
        "yes": yes,
        "yes_bid": bid,
        "yes_ask": ask,
        "mid": mid,
        "volume": _dollars(row.get("volumeNum") if row.get("volumeNum") is not None
                           else row.get("volume")),
        "volume_24h": _dollars(row.get("volume24hr")
                               if row.get("volume24hr") is not None
                               else event.get("volume24hr")),
        "price_change_1h": _dollars(row.get("oneHourPriceChange")),
        "last_trade": _dollars(row.get("lastTradePrice")),
        "updated": event.get("updatedAt") or "",
        "slug": slug,
        # The API URL that will actually be fetched, not the human page. A
        # constructed `polymarket.com/event/<slug>` would be unverifiable:
        # the site serves HTTP 200 and its generic title for a slug that does
        # not exist (measured 2026-09-28), so the citation gate could not tell a
        # real market page from an invented one. The Gamma endpoint returns the
        # market's own JSON and is checkable.
        "source_url": (f"{GAMMA_API}/events?slug={slug}" if slug else ""),
    }


def polymarket_markets() -> "tuple[list[dict], list[str]]":
    """Every KC-relevant Polymarket market, plus the failures. Never raises.

    Discovery goes through the tag listing (the venue's own index of what it
    currently offers) and the quote is then read from a **per-slug fetch of the
    exact URL the pack prints**. That second fetch is not redundant: it is what
    makes the citation observed rather than constructed. CLAUDE.md allows a URL
    only after the page has been retrieved and confirmed to be the thing cited,
    and the listed slug is a fact from one payload while the URL is written from
    it — so the URL is fetched before it is printed.
    """
    events, failures = polymarket_event_map()
    out: "list[dict]" = []
    for label, slug_key, match in POLYMARKET_EVENTS:
        event = None
        for slug, e in events.items():
            if slug_key in slug:
                event = e
                break
        if event is None:
            failures.append(f"Polymarket {label}: no active event matching {slug_key!r}")
            continue
        url = f"{GAMMA_API}/events?slug={event.get('slug')}"
        try:
            fetched = fetch(url, ua=MARKET_UA)
        except FetchError as e:
            failures.append(f"Polymarket {label}: {e}")
            continue
        if not isinstance(fetched, list) or not fetched:
            failures.append(f"Polymarket {label}: {url} returned no event")
            continue
        quote = polymarket_quote(fetched[0], match)
        if quote is None:
            failures.append(
                f"Polymarket {label}: event {event.get('slug')} has no row for {match!r}")
            continue
        quote["label_short"] = label
        quote["venue"] = "Polymarket"
        out.append(quote)
    return out, failures


# The chart's series, by the pack label each one draws. Four lines is the most
# that stays readable at this size; the win-total ladder is deliberately not a
# line (it is a threshold ladder, not a probability over time) and MVP is left
# off because a fifth line overprints the others at the top of the range.
#
# Every colour is one the repo already documents, not one chosen here —
# `#D4820A` is the accent amber, `#F2EDD8` the Parian cream (`--primary`),
# `#7DC4FF` the high-contrast link blue, and `#E31837` the Chiefs red the series
# plate is built on (`skills/hero-image-workflow.md`). The first draft of this
# used an invented blue and green, which is exactly the drift a locked identity
# exists to prevent.
CHART_SERIES = [
    ("Super Bowl champion", "KXSB", "KXSB-27-KC", "#D4820A"),
    ("AFC champion", "KXNFLAFCCHAMP", "KXNFLAFCCHAMP-27-KC", "#F2EDD8"),
    ("AFC West champion", "KXNFLAFCWEST", "KXNFLAFCWEST-27-KC", "#7DC4FF"),
    ("Playoff qualifier", "KXNFLPLAYOFF", "KXNFLPLAYOFF-27-KC", "#E31837"),
]

# Where the chart is written. Absolute, because the collector may be run from any
# cwd by a test or by hand, and the chart must land in the tree the runner commits.
CHART_PATH = REPO / "static" / "img" / "articles" / "103-chiefs-markets.svg"


def collect_markets() -> "dict":
    """Assemble the market block. Never raises; failures are the block's content.

    Both venues are optional. A total failure of one leaves the other's table
    intact, and a total failure of both is reported so the writer omits the
    section rather than writing around numbers that are not there.
    """
    kalshi, kalshi_fail = kalshi_markets()
    ladder, ladder_fail = kalshi_win_total_ladder()
    poly, poly_fail = polymarket_markets()

    # History is fetched per chart series and is optional in the same way: the
    # tables stand without it.
    live_by_label = {m["label_short"]: m for m in kalshi}
    chart_series: "list[dict]" = []
    history_fail: "list[str]" = []
    today = datetime.now(CT).date().isoformat()
    for label, event_ticker, market_ticker, colour in CHART_SERIES:
        points, err = kalshi_history(event_ticker, market_ticker)
        if err:
            history_fail.append(f"Kalshi history {label}: {err}")
            continue
        # Drop the CURRENT day's candle: it covers a partial period, so its
        # "close" is the book as of the last update inside the candle and can
        # differ from the live quote by many points (measured 2026-09-28: candle
        # 0.63 against a live 0.52/0.53). Drawing a partial day as if it were a
        # settled close is how a chart and its own table end up disagreeing. The
        # live quote carries today instead, appended as the final point.
        points = [p for p in points if p["date"] < today]
        live = live_by_label.get(label)
        live_mid = (live or {}).get("mid")
        if live_mid is not None:
            points.append({"ts": int(datetime.now(timezone.utc).timestamp()),
                           "date": today, "close": live_mid, "volume": 0.0,
                           "live": True})
        if len(points) < 2:
            history_fail.append(f"Kalshi history {label}: only {len(points)} point(s)")
            continue
        chart_series.append({
            "label": label,
            "colour": colour,
            "points": points,
            "now": live_mid,
            "delta_7d": week_delta(points, 7),
        })

    chart_error = write_chart(chart_series, CHART_PATH) if chart_series else \
        "no series had enough history"
    return {
        "kalshi": kalshi,
        "kalshi_win_total": ladder,
        "polymarket": poly,
        "chart_series": chart_series,
        "chart_path": str(CHART_PATH.relative_to(REPO)) if not chart_error else "",
        "chart_url": "/img/articles/103-chiefs-markets.svg" if not chart_error else "",
        "chart_error": chart_error,
        "failures": kalshi_fail + ladder_fail + poly_fail + history_fail,
    }


def season_stats(payload: dict) -> "dict":
    """Team season totals, category by category, straight from the payload."""
    results = payload.get("results") or {}
    stats = ((results.get("stats") or {}).get("categories")) or []
    out = {}
    for cat in stats:
        out[cat.get("displayName") or cat.get("name")] = [
            (s.get("abbreviation"), s.get("displayValue")) for s in (cat.get("stats") or [])
        ]
    return out


# ---------------------------------------------------------------------------
# Collection and rendering
# ---------------------------------------------------------------------------
def collect(today: date, season_year: int | None = None) -> "dict":
    """Fetch every source and assemble the structured pack. Raises FetchError.

    `season_year=None` lets the feed pick the current season, which is correct
    across the new year; an explicit year (from `--today`) is asserted against
    what the feed actually served.
    """
    urls = sources(season_year)
    failures = []

    def grab(key: str, what: str) -> dict:
        try:
            payload = fetch(urls[key])
        except FetchError as e:
            failures.append(str(e))
            return {}
        try:
            assert_season(payload, season_year, what)
        except FetchError as e:
            failures.append(str(e))
            return {}
        return payload

    league = grab("league", "the league scoreboard")
    schedule = grab("schedule", "the team schedule")
    standings = grab("standings", "the standings")
    news = grab("news", "the news feed")
    stats = grab("season_stats", "the season statistics")

    if not league or not schedule:
        raise FetchError("; ".join(failures) or "the league or schedule feed is empty")

    cal = league_calendar(league)
    state = season_state(cal, today)

    events = schedule.get("events") or []
    picks = pick_games(events, TEAM, today)

    last = describe_game(picks["last"], TEAM) if picks["last"] else None
    nxt = describe_game(picks["next"], TEAM) if picks["next"] else None

    last_summary: dict = {}
    if picks["last"] is not None:
        try:
            last_summary = fetch(game_summary_url(picks["last"]["id"]))
        except FetchError as e:
            failures.append(str(e))

    next_summary: dict = {}
    if picks["next"] is not None:
        try:
            next_summary = fetch(game_summary_url(picks["next"]["id"]))
        except FetchError as e:
            failures.append(str(e))

    served_season = (schedule.get("season") or {}).get("year")

    pack = {
        "generated": datetime.now(CT).isoformat(timespec="seconds"),
        "today": today.isoformat(),
        "season": state,
        "season_year": served_season,
        "team": {"abbreviation": TEAM.upper(), "id": TEAM_ID, "name": TEAM_NAME},
        "bye_week": schedule.get("byeWeek"),
        "games_played": picks["played"],
        "last_game": last,
        "next_game": nxt,
        "last_summary": {
            "box_score": box_score(last_summary, TEAM) if last_summary else {},
            "scoring_plays": scoring_plays(last_summary) if last_summary else [],
            "injuries": injuries(last_summary, TEAM) if last_summary else {},
            "recap": ((last_summary.get("article") or {}).get("headline")
                      if last_summary else None),
            "recap_description": ((last_summary.get("article") or {}).get("description")
                                  if last_summary else None),
            "article_links": sorted(urls_in((last_summary.get("article") or {}).get("links") or {})),
        },
        "next_summary": {
            "pickcenter": pickcenter(next_summary) if next_summary else [],
            "predictor": next_summary.get("predictor") if next_summary else None,
            "injuries": injuries(next_summary, TEAM) if next_summary else {},
            "opponent_form": (
                team_form(next_summary, (nxt or {}).get("opponent") or "") if next_summary else []
            ),
            "preview": ((next_summary.get("article") or {}).get("headline")
                        if next_summary else None),
            "article_links": sorted(urls_in((next_summary.get("article") or {}).get("links") or {})),
        },
        "standings": division_standings(standings, TEAM) if standings else {},
        "season_stats": season_stats(stats) if stats else {},
        "markets": collect_markets(),
        "news": recent_news(news, today) if news else [],
        "fetch_failures": failures,
    }
    return pack


def _li(items: "list[str]") -> str:
    return "\n".join(f"- {i}" for i in items) if items else "- (none)"


def team_name_for(idmap: dict, team_id: str, fallback: str) -> str:
    """Resolve an ESPN team id to a name using ids the pack already observed.

    The matchup predictor identifies its two teams by numeric id (and the ids
    it uses are not always the ones the standings endpoint uses), so printing
    the raw id would leave the writer to guess which side is which. This maps
    only from ids the standings payload actually supplied; an unknown id falls
    back to the id itself rather than to a guessed name, which is the honest
    failure: a wrong team name reads as a fact.
    """
    if team_id and team_id in idmap:
        return idmap[team_id]
    return fallback


def team_id_map(pack: dict) -> "dict[str, str]":
    """{team id -> name} from the division and conference rows, observed only."""
    out: "dict[str, str]" = {}
    st = pack.get("standings") or {}
    for row in (st.get("rows") or []) + (st.get("conference") or []):
        tid, name = row.get("id"), row.get("name")
        if tid and name:
            out[str(tid)] = name
    return out


def render(pack: dict) -> str:
    """The briefing pack the writer reads. Every line traces to a payload."""
    idmap = team_id_map(pack)
    L: "list[str]" = []
    s = pack["season"]
    L.append(f"# Chiefs briefing pack — {pack['today']}")
    L.append("")
    L.append(f"Generated {pack['generated']} (Central Time) from the ESPN NFL API.")
    L.append("")
    L.append("## Where the season stands")
    L.append("")
    L.append(f"- **League phase:** {s['phase']}"
             + (f", {s['period']}" if s.get("period") else "")
             + (f" ({s['period_detail']})" if s.get("period_detail") else ""))
    L.append(f"- **Phase window:** {s['starts']} to {s['ends']}")
    L.append(f"- **{pack['team']['name']}:** {pack['games_played']} game(s) played"
             + (f", bye week {pack['bye_week']}" if pack.get("bye_week") else ""))
    if pack.get("fetch_failures"):
        L.append("")
        L.append("**Fetch failures — say so in the report, do not paper over them:**")
        L.append(_li(pack["fetch_failures"]))

    lg = pack.get("last_game")
    L.append("")
    L.append("## The most recent completed game")
    L.append("")
    if not lg:
        L.append("No completed game in the schedule payload. If this is week 1 or a "
                 "fresh season, say exactly that; do not reach for last season.")
    else:
        ha = "vs" if lg["home"] else "at"
        L.append(f"- **{pack['team']['abbreviation']} {ha} {lg['opponent']}** "
                 f"({lg['opponent_name']}), week {lg['week']}, {lg['date']}")
        L.append(f"- **Status:** {lg['status']} ({lg['detail']})")
        L.append(f"- **Score:** {pack['team']['abbreviation']} {lg['team_score']} — "
                 f"{lg['opponent']} {lg['opponent_score']}")
        L.append(f"- **Result:** {'win' if lg['won'] else 'loss' if lg['won'] is False else 'not final'}")
        L.append(f"- **Records at the time:** {pack['team']['abbreviation']} "
                 f"{lg['team_record']}, {lg['opponent']} {lg['opponent_record']}")
        L.append(f"- **Venue:** {lg['venue']}")
        if lg["broadcasts"]:
            L.append(f"- **Broadcast:** {', '.join(lg['broadcasts'])}")
        if lg["links"]:
            L.append(f"- **Feed-supplied links:** {' | '.join(lg['links'][:6])}")

        ls = pack["last_summary"]
        if ls.get("recap"):
            L.append("")
            L.append(f"**Recap headline (as the feed titles it):** {ls['recap']}")
            if ls.get("recap_description"):
                L.append("")
                L.append(f"> {ls['recap_description']}")
        if ls.get("article_links"):
            L.append("")
            L.append("**Recap URL(s) from the feed:**")
            L.append(_li(ls["article_links"]))

        bs = ls.get("box_score") or {}
        if bs.get("team_stats"):
            L.append("")
            L.append("### Team statistics, both sides")
            L.append("")
            for ab, stats in bs["team_stats"].items():
                L.append(f"**{ab}**")
                L.append("")
                L.append(_li([f"{k}: {v}" for k, v in stats.items()]))
                L.append("")
        if bs.get("leaders"):
            L.append("### Leaders")
            L.append("")
            for ab, cats in bs["leaders"].items():
                L.append(f"**{ab}**")
                L.append("")
                for name, rows in cats.items():
                    if not rows:
                        continue
                    L.append(f"- *{name}*: " + "; ".join(
                        f"{r['athlete']} — {r['line']}" for r in rows if r["athlete"]))
                L.append("")
        if ls.get("scoring_plays"):
            L.append("### Scoring plays")
            L.append("")
            L.append(_li([
                f"Q{p['period']} {p['clock']}: {p['text']} "
                f"({p['away']}-{p['home']} away-home)" for p in ls["scoring_plays"]
            ]))
        if ls.get("injuries"):
            L.append("")
            L.append("### Injury report, both sides")
            L.append("")
            for ab, rows in ls["injuries"].items():
                L.append(f"**{ab}**")
                L.append("")
                L.append(_li([f"{r['player']} ({r['position']}): {r['status']} — {r['date']}"
                              for r in rows]))

    ng = pack.get("next_game")
    L.append("")
    L.append("## The next game")
    L.append("")
    if not ng:
        L.append("No scheduled game left in the payload — the season is over or the "
                 "schedule has not been released. Say so; do not speculate.")
    else:
        ha = "vs" if ng["home"] else "at"
        L.append(f"- **{pack['team']['abbreviation']} {ha} {ng['opponent']}** "
                 f"({ng['opponent_name']}), week {ng['week']}, {ng['date']}")
        L.append(f"- **Venue:** {ng['venue']}")
        if ng["broadcasts"]:
            L.append(f"- **Broadcast:** {', '.join(ng['broadcasts'])}")
        if ng["opponent_record"]:
            L.append(f"- **Opponent record:** {ng['opponent_record']}")
        if ng["links"]:
            L.append(f"- **Feed-supplied links:** {' | '.join(ng['links'][:6])}")
        ns = pack["next_summary"]
        if ns.get("preview"):
            L.append("")
            L.append(f"**Preview headline (as the feed titles it):** {ns['preview']}")
        if ns.get("article_links"):
            L.append("")
            L.append("**Preview URL(s) from the feed:**")
            L.append(_li(ns["article_links"]))
        if ns.get("pickcenter"):
            L.append("")
            L.append("### Odds, attributed to the provider the feed names")
            L.append("")
            L.append(_li([
                f"{p['provider'] or 'unnamed provider'}: {p['details']}"
                + (f", over/under {p['over_under']}" if p.get("over_under") else "")
                + (f", money lines {p['away_money_line']}/{p['home_money_line']}"
                   if p.get("away_money_line") or p.get("home_money_line") else "")
                for p in ns["pickcenter"]
            ]))
        if ns.get("predictor"):
            pred = ns["predictor"]
            L.append("")
            L.append(f"### Feed's matchup projection ({pred.get('header')})")
            L.append("")
            home_id = str((pred.get("homeTeam") or {}).get("id") or "")
            away_id = str((pred.get("awayTeam") or {}).get("id") or "")
            L.append(_li([
                f"{team_name_for(idmap, home_id, home_id)} (home): "
                f"{((pred.get('homeTeam') or {}).get('gameProjection'))}",
                f"{team_name_for(idmap, away_id, away_id)} (away): "
                f"{((pred.get('awayTeam') or {}).get('gameProjection'))}",
            ]))
            L.append("")
            L.append("These are the feed's own win percentages. They are not a "
                     "prediction this site makes or endorses; attribute them to ESPN.")
        if ns.get("opponent_form"):
            L.append("")
            L.append(f"### {ng['opponent']}: last five games (the feed's own list)")
            L.append("")
            L.append(_li([
                f"{g['date']} Wk{g['week']}: {g['result']} {g['at_vs']} {g['opponent']} "
                f"{g['score']}" for g in ns["opponent_form"]
            ]))
        if ns.get("injuries"):
            L.append("")
            L.append("### Injury report, both sides")
            L.append("")
            for ab, rows in ns["injuries"].items():
                L.append(f"**{ab}**")
                L.append("")
                L.append(_li([f"{r['player']} ({r['position']}): {r['status']}"
                              for r in rows]))

    st = pack.get("standings") or {}
    if st.get("rows"):
        L.append("")
        L.append(f"## {st.get('division')} standings")
        L.append("")
        L.append("| Team | Overall | Div | Conf | PF | PA | Diff | Streak | Seed |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for r in st["rows"]:
            L.append(f"| {r['team']} | {r['overall']} | {r['division']} | {r['conference']} "
                     f"| {r['points_for']} | {r['points_against']} | {r['differential']} "
                     f"| {r['streak']} | {r['seed']} |")
        if st.get("conference"):
            seeds = sorted(
                [c for c in st["conference"] if c.get("seed")],
                key=lambda c: int(c["seed"]),
            )
            L.append("")
            L.append("**AFC seeds as the feed lists them:** "
                     + ", ".join(f"{c['seed']}. {c['team']} ({c['overall']})" for c in seeds))

    if pack.get("season_stats"):
        L.append("")
        L.append("## Team season statistics")
        L.append("")
        for cat, pairs in pack["season_stats"].items():
            L.append(f"- **{cat}:** "
                     + ", ".join(f"{k} {v}" for k, v in pairs if v not in (None, "")))

    mk = pack.get("markets") or {}
    L.append("")
    L.append("## Prediction markets (season-long)")
    L.append("")
    L.append("Read from Kalshi and Polymarket's own public APIs by this script. "
             "These are the venues' prices, not this site's opinion; quote them "
             "and attribute them to the venue. They move continuously, and each "
             "row carries the field that shows it is live.")
    if not (mk.get("kalshi") or mk.get("polymarket") or mk.get("kalshi_win_total")):
        L.append("")
        L.append("Neither venue returned a usable market. Omit the table from the "
                 "report and say the venues were unreachable; do not write around "
                 "absent numbers.")
    def _pct(v):
        return "—" if v is None else f"{v * 100:.0f}%"

    def _pct1(v):
        """One decimal, for the delta table.

        Whole-number percentages hide a real move: a series going 13.5% to 14.5%
        prints as "14% → 14%, +1pt", which reads as a contradiction. The level
        and the change have to be shown at the same precision for the row to be
        checkable by eye.
        """
        return "—" if v is None else f"{v * 100:.1f}%"

    def _signed(v, unit=""):
        """A signed move, or an em dash. Never '+' on a None."""
        if v is None:
            return "—"
        return f"{v:+.0f}{unit}" if abs(v) >= 1 else f"{v:+.2f}{unit}"

    if mk.get("polymarket"):
        L.append("")
        L.append("**Polymarket** (bid/ask midpoint; `last` is the YES price; "
                 "`24h` is traded volume in the last day; `1h` is the price move "
                 "over the last hour):")
        L.append("")
        L.append("| Market | KC | bid | ask | last | 24h vol | 1h move | book updated |")
        L.append("|---|---|---|---|---|---|---|---|")
        for m in mk["polymarket"]:
            mv = m.get("price_change_1h")
            mv_pts = None if mv is None else mv * 100
            L.append(f"| {m['label_short']} | {_pct(m.get('mid'))} "
                     f"| {m.get('yes_bid') if m.get('yes_bid') is not None else '—'} "
                     f"| {m.get('yes_ask') if m.get('yes_ask') is not None else '—'} "
                     f"| {_pct(m.get('yes'))} "
                     f"| {round(m['volume_24h']) if m.get('volume_24h') else '—'} "
                     f"| {_signed(mv_pts, 'pt')} "
                     f"| {(m.get('updated') or '')[:16]} |")
        L.append("")
        L.append("Event pages: " + " | ".join(
            f"{m['label_short']} {m['source_url']}" for m in mk["polymarket"] if m.get("source_url")))

    if mk.get("kalshi"):
        L.append("")
        L.append("**Kalshi** (yes bid/ask as a probability; `mid` is the bid/ask "
                 "midpoint unless the book is wide; `24h` is traded volume in the "
                 "last day; `moved` is the bid's change against the venue's own "
                 "previous print):")
        L.append("")
        L.append("| Market | bid | ask | mid | wide? | 24h vol | total vol | moved | open interest |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for m in mk["kalshi"]:
            mv = m.get("moved")
            L.append(f"| {m['label_short']} | {m.get('yes_bid') if m.get('yes_bid') is not None else '—'} "
                     f"| {m.get('yes_ask') if m.get('yes_ask') is not None else '—'} "
                     f"| {'wide' if m.get('wide') else _pct(m.get('mid'))} "
                     f"| {'WIDE' if m.get('wide') else ''} "
                     f"| {round(m['volume_24h']) if m.get('volume_24h') else '—'} "
                     f"| {round(m['volume']) if m.get('volume') else '—'} "
                     f"| {_signed(mv)} "
                     f"| {round(m['open_interest']) if m.get('open_interest') else '—'} |")
        L.append("")
        L.append("Series sources (the endpoints this script fetched): " + " | ".join(
            f"{m['label_short']} {m['source_url']}" for m in mk["kalshi"] if m.get("source_url")))

    if mk.get("kalshi_win_total"):
        L.append("")
        L.append("**Kalshi win-total ladder** (a threshold ladder, not competing "
                 "outcomes; the ~50% rung is the market's expected win total):")
        L.append("")
        L.append(_li([
            f"{m['label']}: "
            + ("WIDE BOOK — no price" if m.get("wide") else _pct(m.get('mid')))
            + f" (bid {m.get('yes_bid') if m.get('yes_bid') is not None else '—'}/"
            f"ask {m.get('yes_ask') if m.get('yes_ask') is not None else '—'}"
            + f", 24h vol {round(m['volume_24h']) if m.get('volume_24h') else '—'}"
            + f", total vol {round(m['volume']) if m.get('volume') else '—'})"
            for m in mk["kalshi_win_total"]
        ]))
        L.append("")
        L.append("Win-total source: "
                 f"{KALSHI_API}/events/{KALSHI_WIN_TOTAL_EVENT}?with_nested_markets=true")

    if mk.get("chart_series"):
        L.append("")
        L.append("**Weekly change (the line chart on the page).** The chart is "
                 f"written to `{mk.get('chart_path')}` and referenced in the post "
                 f"as `{mk.get('chart_url')}`.")
        L.append("")
        L.append("| Series | now | 7 days ago | change | span |")
        L.append("|---|---|---|---|---|")
        for s in mk["chart_series"]:
            d = s.get("delta_7d") or {}
            now = s.get("now")
            if now is None:
                now = s["points"][-1]["close"]
            L.append(f"| {s['label']} | {_pct1(now)} "
                     f"| {_pct1(d.get('from')) if d else '—'} "
                     f"| {_signed(d['change'] * 100, 'pt') if d else '—'} "
                     f"| {str(d.get('span_days')) + ' days' if d else '—'} |")
        L.append("")
        L.append("The `now` column is the live book quote from the tables above, "
                 "so the chart and the table cannot disagree. Quote a change only "
                 "from this table, and quote the span with it: a series with only "
                 "three days of history reports a three-day change, not a week.")
    elif mk.get("chart_error"):
        L.append("")
        L.append(f"**No chart this week:** {mk['chart_error']}. Write the market "
                 "section from the tables above and do not reference a chart "
                 "image, because none was written.")

    if mk.get("failures"):
        L.append("")
        L.append("**Market fetch failures — one venue failing does not invalidate "
                 "the other; say so rather than papering over it:**")
        L.append(_li(mk["failures"]))

    if mk.get("kalshi") or mk.get("polymarket"):
        L.append("")
        L.append("**On currency, and the trap in Kalshi's timestamps.** These "
                 "markets trade continuously and their prices do move — but "
                 "**do not read Kalshi's `updated_time` as a trade time; it is "
                 "not one.** Measured 2026-09-28: thirty-two markets across the "
                 "entire playoff series share a single `updated_time` to the "
                 "microsecond, whole series batches share others, and the AFC "
                 "West market was stamped 2026-07-13 while trading $2,842 in the "
                 "prior day. It is a series-level metadata write.")
        L.append("")
        L.append("The honest currency signals are the ones printed above: "
                 "**`24h vol`** (traded volume in the last day) and **`moved`** "
                 "(today's bid against the venue's own previous print). A market "
                 "with 24h volume is live, whatever its `updated_time` says. "
                 "Kalshi publishes no last-trade timestamp, so none is invented "
                 "here — cite the price and, if you want to convey motion, cite "
                 "the volume and the move. Polymarket's `book updated` is a real "
                 "book-refresh time and its `1h move` is a real price change; "
                 "the two venues' activity fields are not comparable to each "
                 "other, so quote each on its own terms.")

    news = pack.get("news") or []
    L.append("")
    L.append(f"## Chiefs-tagged coverage, last {NEWS_WINDOW_DAYS} days (newest first)")
    L.append("")
    if not news:
        L.append("Nothing in the window. A quiet news week is a finding, not a gap: "
                 "say so rather than padding the report.")
    for a in news:
        L.append(f"- **{a['date']}** [{a['type']}] {a['headline']}")
        if a["description"]:
            L.append(f"  {a['description']}")
        for u in a["links"]:
            L.append(f"  {u}")
    L.append("")
    L.append("---")
    L.append("")
    L.append("Every number and URL above was read from the ESPN NFL API, Kalshi's "
             "trade API, and Polymarket's Gamma API by `scripts/chiefs-report.py`. "
             "If a fact you want is not here, fetch it and cite the page you "
             "fetched — do not fill the gap from memory.")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Collect the week's Chiefs data.")
    ap.add_argument("--season-state", action="store_true",
                    help="print the league phase; exit 3 when off season")
    ap.add_argument("--validate", metavar="PATH",
                    help="check an article's frontmatter before publishing "
                         "(delegates to scripts/check-report-frontmatter.py)")
    ap.add_argument("--json", action="store_true", help="emit the structured pack")
    ap.add_argument("--today", help="evaluate as if run on YYYY-MM-DD (for testing)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.validate:
        # The rules moved to `scripts/check-report-frontmatter.py` when the
        # Senate and docket jobs started publishing too: one gate for all three
        # rather than three copies, because the duplication is how the
        # `featuredOnHome` requirement went missing from one skill and not
        # another. This flag is kept as a thin delegate so the existing habit and
        # any script that calls it keep working.
        gate = Path(__file__).with_name("check-report-frontmatter.py")
        sys.stderr.write(
            "chiefs: --validate now delegates to scripts/check-report-frontmatter.py; "
            "call that directly.\n"
        )
        return subprocess.call([sys.executable, str(gate), "--file", args.validate])

    if args.json and args.season_state:
        print("chiefs: --json and --season-state are mutually exclusive", file=sys.stderr)
        return 2

    today = date.fromisoformat(args.today) if args.today else datetime.now(CT).date()

    try:
        if args.season_state:
            state = season_state(league_calendar(fetch(sources()["league"])), today)
            period = f", {state['period']}" if state.get("period") else ""
            print(f"chiefs: {state['phase']}{period} ({state['starts']} to {state['ends']})"
                  f" — {'in season' if state['in_season'] else 'off season'}")
            return 0 if state["in_season"] else 3
        # `--today` is an explicit claim about which season to report, so it is
        # asserted against what the feed served. A real run passes no year and
        # takes the feed's current one, because the season straddles the new
        # year and `today.year` would be wrong every January.
        year = today.year if args.today else None
        pack = collect(today, season_year=year)
    except FetchError as e:
        print(f"chiefs: ERROR — {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(pack, indent=2, default=str))
    elif args.quiet:
        print(f"chiefs: pack for {today} — "
              f"{len(pack['news'])} news item(s), "
              f"last game {pack.get('last_game', {}).get('id') if pack.get('last_game') else 'none'}")
    else:
        print(render(pack))
    return 0


if __name__ == "__main__":
    sys.exit(main())
