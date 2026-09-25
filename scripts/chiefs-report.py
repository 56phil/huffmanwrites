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
def fetch(url: str, timeout: float = 30.0) -> dict:
    """GET a JSON endpoint. Raises FetchError, never returns a partial payload.

    No User-Agent: see the module docstring. ESPN 403s a browser UA here.
    """
    req = urllib.request.Request(url)
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
    L.append("Every number and URL above was read from the ESPN NFL API by "
             "`scripts/chiefs-report.py`. If a fact you want is not here, fetch it "
             "and cite the page you fetched — do not fill the gap from memory.")
    return "\n".join(L)


def validate_article(path: "Path | str", now: "datetime | None" = None,
                     slack_seconds: int = 300) -> "list[str]":
    """Pre-publication checks on the article itself. Returns a list of problems.

    Lives here rather than in the runner for two reasons: shell date parsing on
    macOS cannot read the frontmatter's own offset format (`date -j -f` accepts
    `-0500`, not the `-05:00` this repo writes, and it fails by printing usage to
    stderr and returning nothing), and a check that is a function can be tested.
    The runner calls this; `scripts/test_gates.py` tests it.

    Each rule is a defect this repo has actually shipped:
      - `draft: false` — a draft flag left true deploys nothing while looking
        like it published;
      - `featuredOnHome: true` — more than five posts already carry the flag, so
        an unflagged post never appears in the home feed at all;
      - the date is not ahead of the clock — Hugo's `buildFuture: false` skips a
        future-dated page *without failing the build*, which is the failure that
        hides (recorded three times in SESSION_STATE);
      - the closing attribution line;
      - and the tags/hero expectations the skill states.
    """
    p = Path(path)
    if not p.is_file():
        return [f"no article at {p}"]
    text = p.read_text(encoding="utf-8")
    problems: "list[str]" = []

    if not text.startswith("---"):
        problems.append("no frontmatter block")
        return problems
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        problems.append("frontmatter block is not closed")
        return problems
    front, body = parts[1], parts[2]

    def field(name: str) -> "str | None":
        m = re.search(rf"^{re.escape(name)}\s*:\s*(.*)$", front, re.M)
        return m.group(1).strip().strip("\"'") if m else None

    if field("draft") != "false":
        problems.append(f"draft is {field('draft')!r}, not false — nothing would publish")
    if field("featuredOnHome") != "true":
        problems.append(
            "featuredOnHome is not true — with more than five flagged posts already "
            "on the site, an unflagged post never reaches the home feed"
        )
    for name in ("title", "description", "date"):
        if not field(name):
            problems.append(f"no {name} in frontmatter")
    if not re.search(r"^\*PRH \|", body, re.M):
        problems.append("missing the closing attribution line (*PRH | …)")

    raw = field("date")
    if raw:
        try:
            stamp = datetime.fromisoformat(raw)
        except ValueError:
            problems.append(f"date {raw!r} is not ISO 8601")
        else:
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=CT)
            reference = now or datetime.now(CT)
            if reference.tzinfo is None:
                reference = reference.replace(tzinfo=CT)
            if stamp > reference + timedelta(seconds=slack_seconds):
                problems.append(
                    f"date {raw} is ahead of the clock "
                    f"({reference.isoformat(timespec='seconds')}); buildFuture "
                    f"would silently skip the page"
                )
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Collect the week's Chiefs data.")
    ap.add_argument("--season-state", action="store_true",
                    help="print the league phase; exit 3 when off season")
    ap.add_argument("--validate", metavar="PATH",
                    help="check an article's frontmatter before publishing; "
                         "exit 1 and print every problem if it is not publishable")
    ap.add_argument("--json", action="store_true", help="emit the structured pack")
    ap.add_argument("--today", help="evaluate as if run on YYYY-MM-DD (for testing)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.validate:
        problems = validate_article(args.validate)
        if problems:
            print(f"chiefs: NOT PUBLISHABLE — {len(problems)} problem(s) in "
                  f"{args.validate}", file=sys.stderr)
            for p in problems:
                print(f"  {p}", file=sys.stderr)
            return 1
        print(f"chiefs: {args.validate} is publishable (draft false, featuredOnHome "
              f"true, date not ahead of the clock, attribution present)")
        return 0

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
