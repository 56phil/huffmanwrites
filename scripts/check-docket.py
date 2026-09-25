#!/usr/bin/env python3
"""Watch federal dockets relevant to the site and report anything new.

Philip, 2026-09-19: "I must keep an eye on this story." (Kennedy Center.)
Philip, 2026-09-24: "I want to start following the docket for Katie Fang's
suite against AG Tod Blanch regarding the Epstein files." — the names as given
were wrong; the case is *Phang v. Blanche*, No. 1:26-cv-01417 (EGS).

Two cases are watched, from the same primitive and the same report:

  beatty  — Beatty v. Trump, No. 1:25-cv-04480 (CRC), D.D.C. (Kennedy Center)
  phang   — Phang v. Blanche, No. 1:26-cv-01417 (EGS), D.D.C. (Epstein Files
            Transparency Act)

Each case moves in day-scale bursts, and the coverage of both is unreliable —
outlets conflate the Kennedy Center's two-year renovation closure with the
seven-day safety closure, and the Epstein-files coverage reports deadlines
Sullivan set by minute order that never appear in a news story. What can be
trusted is the docket. So watch the docket.

This reads the CourtListener Atom feed for each case and compares the newest
entries against stored watermarks. Two kinds of entry matter and both are
tracked:

  * ECF-numbered entries ("Entry #50"), watermarked by entry number; and
  * minute entries ("Minute entry from 2026-09-19"), which carry only an opaque
    id and no ECF number, watermarked by that id.

The split is not academic. In *Phang*, Judge Sullivan rules and sets deadlines
by minute order — the September 19 schedule for the stay motion and the order
setting the September 24 answer deadline are both minute entries — and in the
30-entry window currently served, 18 of 30 entries are minute entries. A
watcher that keyed only on "Entry #N" would silently drop every one of them,
which is the failure mode that matters most here: not a wrong report but a
missing one.

Exit codes:
  0 — nothing new (the common case; a no-op)
  0 — new material found AND the report was delivered
  2 — could not read a feed (network, or CourtListener changed shape)
  3 — new material found but delivery failed

A non-zero exit routes to scripts/alert-failure.sh via the runner, so a silent
failure to reach a docket does not look like "nothing happened" — which is the
failure mode that matters for a watch job.

Usage:
  check-docket.py                 # watch every case, update watermarks, report
  check-docket.py --case phang    # restrict to one case (repeatable)
  check-docket.py --dry-run       # report what WOULD change; touch nothing
  check-docket.py --no-update     # report but do not move the watermarks
  check-docket.py --quiet         # only report on change
  check-docket.py --status        # print watermarks and newest entries
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "scripts" / "docket-watch-state.json"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) huffmanwrites-docket-watch"


# --------------------------------------------------------------------------
# Registry. One entry per case. KNOWN is a map of ECF number -> one-line
# summary, so a report says what changed rather than just "entry 90 appeared".
# Kept short on purpose: this is a pointer to go read the document, not a
# substitute for reading it.
#
# CALENDAR is dates that force a fresh look regardless of whether anything is
# filed. The docket and the case calendar are different instruments and both
# matter. Past entries are kept as a record of what a date meant once it
# passed, and are marked DISCHARGED (or the like) in place.
# --------------------------------------------------------------------------
CASES: "dict[str, dict]" = {
    "beatty": {
        "case": "BEATTY v. TRUMP, 1:25-cv-04480",
        "docket_id": "72069932",
        "slug": "beatty-v-trump",
        "label": "Kennedy Center",
        "known": {
            48: "Preliminary injunction — bars effectuating the Mar 16 closure decision until the Board approves a conforming closure AND the court dissolves/modifies. STILL IN FORCE.",
            49: "Permanent injunction — the renaming is void; no signage on the building or grounds naming anyone but JFK. STILL IN FORCE.",
            50: "Memorandum opinion, Beatty v. Trump, 834 F. Supp. 3d 41 (D.D.C. 2026).",
            77: "Memo opinion & order — enjoins the renovation inscription and the Trump Plaza renaming; denies the $100M endowment plaque as unripe (60-day notice instead).",
            78: "Notice of board closure vote + Trump Truth Social statement.",
            79: "Notice of appeal -> D.C. Cir. No. 26-5322.",
            82: "Scheduling order (the Oct 16 / 23 / 27 briefing dates).",
            84: "Beatty emergency motion (staffer barred at 10:12 a.m.).",
            85: "Notice of supplemental authority (Trump 'ripped down' quote; Air Force One placard photo).",
            86: "DOJ response ('seven days, unless extended').",
            87: "Beatty reply (pretext).",
            88: "Motion to dissolve the PI (Rule 60(b)(5)) + 50-page memo.",
            89: "Renewed motion for partial summary judgment (+ Sep 18 Floca declaration, Delta Consulting report, Sep 15 board exhibits).",
            90: "Beatty reply in support of the motion to unseal the JLL Plan and Delta deck.",
            91: "DEFENDANTS' STATUS REPORT + Sep 23 Floca declaration (ECF 91-1). Closure extended to Sep 30. Says the temporary closure is a management safety measure 'separate from implementation of the Board's longer-term closure plan.'",
        },
        "calendar": [
            ("2026-09-23", "DISCHARGED — status report + sworn declaration filed as ECF 91 / 91-1. Discovery requests and deposition notices due. The 'seven-day' closure window expired and was extended."),
            ("2026-09-26", "NSO's first concert of its exile season (six DMV venues)."),
            ("2026-09-30", "Extended temporary closure runs to this date (ECF 91: Floca extended it one week); he says he will 'reevaluate on a weekly basis'. Discovery responses also due."),
            ("2026-10-08", "Board's own prior deferral date for returning the name to the façade."),
            ("2026-10-09", "Discovery closes."),
            ("2026-10-16", "Plaintiff opposition + cross-motion for summary judgment due."),
            ("2026-10-23", "Defendants' reply due."),
            ("2026-10-27", "Plaintiff's reply due."),
        ],
    },
    "phang": {
        "case": "PHANG v. BLANCHE, 1:26-cv-01417",
        "docket_id": "73246595",
        "slug": "phang-v-blanche",
        "label": "Epstein files (Phang v. Blanche)",
        "known": {
            1: "Complaint — APA challenge to the Justice Department's withholding, redacting, and non-disclosure of Epstein records under the Epstein Files Transparency Act (EFTA), Pub. L. 119-38. Judge Emmet G. Sullivan.",
            9: "Plaintiff's application for a preliminary injunction, on a limited list of apparent EFTA violations.",
            15: "PRELIMINARY INJUNCTION ORDER (June 25) — largely adopting Plaintiff's proposed order, which Defendant never addressed: by July 2, produce or show cause on the listed Bates-numbered emails (sender/recipient names unredacted) and DOJ documents (co-conspirator names unredacted); produce or show cause on the underlying FBI interview notes behind four FD-302 reports; initiate foreign-language review and notice; publish or show cause on the EFTA § 2(c)(2) redaction log.",
            16: "Memorandum opinion granting the preliminary injunction. Phang v. Blanche, 2026 WL 1831251 (D.D.C. 2026).",
            19: "Defendant's response to the order to show cause — says redactions are victims' names and law-enforcement email addresses, and that it did not review foreign-language documents because first-level reviewers could not assess responsiveness.",
            20: "Plaintiff's response + motion to enforce.",
            22: "Defendant's reply.",
            23: "Order requiring Defendant to submit unredacted copies to the Court for in camera review, with documentation supporting its 'victim' representation.",
            25: "Notice of compliance — Defendant timely submitted the in camera materials (July 30).",
            27: "Plaintiff's motion to compel an Answer and to produce the Administrative Record.",
            28: "Defendant's motion to stay all filing deadlines nunc pro tunc pending the PI motion, and to set a briefing schedule.",
            29: "Order scheduling the August 13 status hearing.",
            32: "Plaintiff's proposed order (the 'interim step': a declaration explaining what is being submitted and when).",
            34: "Hearing transcript (Aug 13). Defendant: the handwritten notes were withheld because 'the determination had been made that the handwritten notes were duplicative'. On the § 2(c)(2) Federal Register log, counsel could say only that publication was 'forthcoming'.",
            35: "Notice of appeal of the PI order -> D.C. Cir. No. 26-5299 (docketed Aug 25).",
            37: "Defendant's response to the proposed order — claims it published the EFTA § 2(c)(2) written justification in the Federal Register that day (Aug 27).",
            39: "Notice of withdrawal of appearance.",
            40: "Plaintiff's response to ECF 37.",
            42: "MEMORANDUM OPINION AND ORDER — grants the motion to compel; DENIES the motion to stay deadlines. Defendant's Answer was due June 26 and he never moved for an extension; the Court allows a late Answer but refuses a late motion to dismiss, which Defendant has conceded. Answer due 9/24; certified list of the Administrative Record due 10/1; Administrative Record produced to Plaintiff by 10/15.",
            43: "MEMORANDUM OPINION AND ORDER on the parties' responses to the June 25 PI Order. Discharges the show-cause orders as to five documents (including the draft SDNY indictment, marked 'OLD Draft', and the two Privacy Act email-address redactions); finds Defendant provided NO documentation that the redactions in EFTA01187999, EFTA02504630 and EFTA01022356 are victims' names, and orders in camera documentation by 9/24 at 11:00 am; orders the underlying FBI interview notes in redacted AND unredacted form by 9/24 at 11:00 am; orders Defendant to initiate foreign-language review and give notice by 9/24; DISCHARGES the § 2(c)(2) show-cause order, leaving the adequacy of the Section 3 Report for later proceedings.",
            44: "Notice of appeal of the September 16 Order -> D.C. Cir. No. 26-5334 (docketed Sept 21).",
            45: "Transmission of the Notice of Appeal to the D.C. Circuit (no fee — filed by the government).",
            46: "DEFENDANT'S MOTION FOR A PARTIAL STAY PENDING APPEAL — asks the Court to stay the portion of the September 16 Order requiring him to initiate review and production of foreign-language EFTA materials and certify by 9/24. Filed Friday Sept 18 at 8:45 pm, requesting a ruling by Monday 5:00 pm; signed by the Associate Attorney General's office.",
            47: "Plaintiff's memorandum in opposition to the partial stay.",
            48: "Defendant's reply — asks the Court to rule by 8:00 pm Sept 21.",
            49: "ORDER DENYING the partial stay — on the merits, and independently under Local Civil Rule 7(m): Defendant did not confer with Plaintiff before filing (motion filed 8:45 pm Friday, ruling demanded over Yom Kippur) and the rule's violation 'is, on its own, reason to deny'. The Court notes Defendant never responded to the merits of the PI motion and did not address the proposed order. BUT it TEMPORARILY STAYS the foreign-language-review portion so Defendant may move for a stay in the D.C. Circuit, and orders a joint Notice within three days of the circuit's ruling.",
            50: "DEFENDANT'S ANSWER TO THE COMPLAINT — filed on the court-ordered deadline. Denies most allegations as legal conclusions; admits the EFTA is a public-disclosure law requiring the Attorney General to make certain records public; says no files were withheld or redacted on 'national defense or foreign policy' grounds; and asserts the Department 'has complied with the law and produced millions of pages of records'.",
        },
        "calendar": [
            ("2026-09-24", "Answer to the Complaint due (ECF 42) — FILED as ECF 50. Also due at 11:00 am: in camera documentation that the EFTA01187999 / EFTA02504630 / EFTA01022356 redactions are victims' names, and the underlying FBI interview notes (redacted and unredacted) for four FD-302 reports (ECF 43). The notice that foreign-language review is underway is TEMPORARILY STAYED (ECF 49)."),
            ("2026-10-01", "Defendant's certified list of the contents of the Administrative Record due (ECF 42, LCivR 7(n)(1))."),
            ("2026-10-15", "Defendant to produce the Administrative Record to Plaintiff (ECF 42)."),
        ],
    },
    "cadc": {
        "case": "PHANG v. BLANCHE, D.C. Cir. No. 26-5299 (consolidated with 26-5334)",
        "docket_id": "74696600",
        "slug": "katie-phang-v-todd-blanche",
        "label": "Epstein files appeal (D.C. Circuit)",
        "known": {
            1208881795: "NOTICE OF APPEAL (protective) -> appeal docketed as No. 26-5299.",
            1208881798: "CLERK'S ORDER [2189799] — initial submissions due 9/24/2026 (certificate as to parties, docketing statement, entry of appearance, procedural motions, appendix-deferral statement, statement of issues, transcript report, underlying decision); DISPOSITIVE motions due 10/9/2026; transcript status report every 30 days; and BRIEFING DEFERRED pending further order of the court.",
            1208890202: "CLERK'S ORDER [2194153] — 26-5334 CONSOLIDATED with 26-5299; the Aug 25 deadlines now govern both. This is why watching 26-5299 sees both appeals.",
            1208890756: "Entry of appearance — Michael Weisbuch for Appellant Blanche.",
            1208890787: "Entry of appearance — Samuel T. Ward-Packard for Appellee Phang.",
            1208890917: "MOTION [2194494] — Appellant's motion to STAY the underlying order pending appeal, and to expedite. The motion this watch exists to follow.",
            1208891196: "PER CURIAM ORDER [2194635] — Srinivasan (C.J.), Pillard and Pan. Appellee's response to the stay motion due Fri 9/25/2026 at 11:59 p.m.; any reply due Tue 9/29/2026 at 4:00 p.m. The ruling itself will be a new entry on this docket.",
            1208891675: "Docketing statement (Appellant).",
            1208891687: "Certificate as to parties, rulings and related cases (Appellant).",
            1208891716: "Transcript status report — all transcripts needed for the appeal complete; next report due 30 days out.",
            1208891719: "Statement of issues (Appellant).",
            1208891733: "Underlying decision from which the appeal arises (Appellant).",
            1208891742: "Statement of intent re appendix deferral — deferred.",
            1208891760: "Entry of appearance — Brendan Ballou for Appellee Phang.",
            1208891769: "Certificate as to parties, rulings and related cases (Appellee Phang).",
        },
        "calendar": [
            ("2026-09-25", "Appellee Phang's response to the motion for stay pending appeal due at 11:59 p.m. (per curiam order 9/23). A STAY GRANTED would pause the district court's foreign-language obligation; a denial leaves it live."),
            ("2026-09-29", "Any reply in support of the stay motion due at 4:00 p.m."),
            ("2026-10-09", "Dispositive motions due in the consolidated appeals (clerk order 8/25). Briefing is otherwise DEFERRED pending further order."),
        ],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def feed_url(case: dict) -> str:
    return f"https://www.courtlistener.com/docket/{case['docket_id']}/feed/"


def docket_url(case: dict) -> str:
    return f"https://www.courtlistener.com/docket/{case['docket_id']}/{case['slug']}/"


def fetch_feed(url: str) -> str:
    # --compressed: see scripts/check-quotes.py. A gzip-forcing host would make
    # this read mojibake, the "<entry" test below would fail, and a live docket
    # would be reported as unreadable — the false-negative that makes a watch
    # job useless.
    r = subprocess.run(
        ["curl", "-sL", "--compressed", "--max-time", "30", "-A", USER_AGENT, url],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"curl exit {r.returncode}")
    body = r.stdout.decode("utf-8", "replace")
    if "<entry" not in body:
        raise RuntimeError("feed contained no <entry> elements — shape changed?")
    return body


def parse_entries(xml: str) -> "list[dict]":
    """Return one record per feed entry, newest-last.

    Two kinds of entry are recognized and both are returned:

      * ECF-numbered entries — "Entry #50 in PHANG v. BLANCHE" — carry a
        numeric ECF number in the title and are keyed by it; and
      * minute entries — "Minute entry from 2026-09-19" — which carry no ECF
        number and are keyed by the opaque `minute-entry-<id>` id.

    Dropping the second kind used to be this script's quiet defect: in *Phang*,
    Judge Sullivan sets deadlines and schedules briefing by minute order, so a
    watcher blind to them would report a quiet docket on the days the case
    actually moved. The feed interleaves the two and sorts each newest-first.
    """
    out = []
    for block in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        date_m = re.search(r"<published>([^<]+)</published>", block)
        date = (date_m.group(1) if date_m else "")[:10]
        summ_m = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
        summary = re.sub(r"\s+", " ", summ_m.group(1) if summ_m else "").strip()

        m = re.search(r"Entry #(\d+)", block)
        if m:
            num = int(m.group(1))
            summary = re.sub(
                r"^(?:MOTION|ORDER|NOTICE|RESPONSE|REPLY|MEMORANDUM|DECLARATION)[^.]{0,80}?\bby\s+"
                r"(?:[A-Z][A-Z.\s,'-]+,\s*){4,}",
                lambda mm: mm.group(0).split(" by ")[0] + " by [45 defendants] ",
                summary,
            )
            out.append({"kind": "entry", "num": num, "mid": None,
                        "date": date, "summary": summary[:400]})
            continue

        mid_m = re.search(r"minute-entry-(\d+)", block)
        if mid_m:
            out.append({"kind": "minute", "num": None, "mid": int(mid_m.group(1)),
                        "date": date, "summary": summary[:400]})
    return out


def _max_entry(entries: "list[dict]") -> int:
    return max((e["num"] for e in entries if e["kind"] == "entry"), default=0)


def _max_minute(entries: "list[dict]") -> int:
    return max((e["mid"] for e in entries if e["kind"] == "minute"), default=0)


def load_state() -> dict:
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")


def migrate_state(state: dict) -> dict:
    """Return the state in its per-case shape, converting the legacy flat file.

    The file used to hold one case at a single watermark:
    `{"last_entry": 91, "updated": "...", "case": "BEATTY v. TRUMP, ..."}`.
    That flat watermark is Beatty's — it is the only case the watcher had — so
    it migrates there rather than being discarded. Without this, adding a second
    case would either re-alert on Beatty's whole filing history (if the key
    were simply renamed) or force a manual first run, and the point of a
    watermark is that it survives a change to the file's shape.
    """
    if "dockets" in state:
        return state
    if "last_entry" in state:
        # `last_minute: None` rather than 0: the old watcher tracked no minute
        # entries at all, so 0 is not a watermark, it is the absence of one.
        # Recording 0 would make the next run report every minute entry in the
        # feed — Beatty's window currently holds 13 — as if it were a filing
        # burst that just happened.
        return {
            "dockets": {
                "beatty": {
                    "last_entry": int(state.get("last_entry", 0)),
                    "last_minute": None,
                    "updated": state.get("updated", ""),
                    "case": CASES["beatty"]["case"],
                }
            }
        }
    return {"dockets": {}}


def due_calendar(case: dict, today: str, horizon_days: int = 3) -> "list[tuple[str, str]]":
    """Calendar items due within the horizon, or already past but unreported."""
    out = []
    t0 = datetime.strptime(today, "%Y-%m-%d")
    for date, what in case["calendar"]:
        d = datetime.strptime(date, "%Y-%m-%d")
        delta = (d - t0).days
        if 0 <= delta <= horizon_days:
            tag = "TODAY" if delta == 0 else f"in {delta}d"
            out.append((f"{date} ({tag})", what))
    return out


def new_entries(entries: "list[dict]", last_entry: int, last_minute) -> "list[dict]":
    """Entries past either watermark — ECF-numbered by number, minute by id.

    A `last_minute` of None means the case has never tracked minute entries.
    The first time it does, those already in the feed are recorded silently
    instead of reported: they are history the watcher was not asked to follow
    yet, and reporting them would be a one-time false burst. From then on the
    watermark is an int and new minute entries report normally.
    """
    track_minutes = last_minute is not None
    lm = last_minute or 0
    out = []
    for e in entries:
        if e["kind"] == "entry":
            if e["num"] > last_entry:
                out.append(e)
        elif track_minutes and e["mid"] > lm:
            out.append(e)
    out.sort(key=lambda e: (e["date"], e["num"] or 10**9, e["mid"] or 0))
    return out


def describe(e: dict, known: "dict[int, str]") -> str:
    if e["kind"] == "entry":
        note = known.get(e["num"]) or e["summary"][:200]
        return f"ECF {e['num']} ({e['date']}): {note}"
    return f"Minute entry ({e['date']}): {e['summary'][:200] or '(no summary)'}"


def deliver(title: str, body: str, quiet: bool) -> bool:
    """Two channels, matching alert-failure.sh: durable log + notification."""
    log = Path.home() / "Library" / "Logs" / "huffmanwrites-docket.log"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"\n=== {_now()} ===\n{title}\n{body}\n")
    except Exception:
        pass
    if quiet:
        return True
    r = subprocess.run(
        ["/usr/bin/osascript",
         "-e", "on run argv",
         "-e", 'display notification (item 1 of argv) with title "Docket watch" '
               'subtitle (item 2 of argv) sound name "Glass"',
         "-e", "end run",
         body[:300], title],
        capture_output=True,
    )
    return r.returncode == 0


def watch(key: str, case: dict, state: dict, args) -> "tuple[int, bool, dict]":
    """Watch one case. Returns (exit_code, changed, updated_state)."""
    dockets = state.setdefault("dockets", {})
    cur = dockets.get(key, {})
    # First run for this case: record the watermark, do not alert on the whole
    # filing history. A missing key is the signal, so this keeps working when a
    # new case is registered without editing the state file by hand.
    first_run = "last_entry" not in cur
    last_entry = int(cur.get("last_entry", 0))
    # None (not 0) means this case has never tracked minute entries — see
    # migrate_state. 0 would be a real watermark and would flood the first run.
    last_minute = cur.get("last_minute")

    try:
        entries = parse_entries(fetch_feed(feed_url(case)))
    except Exception as exc:
        print(f"docket-watch [{key}]: ERROR: could not read feed: {exc}", file=sys.stderr)
        return 2, False, state

    if not entries:
        print(f"docket-watch [{key}]: ERROR: feed parsed to zero entries", file=sys.stderr)
        return 2, False, state

    newest = _max_entry(entries)
    newest_minute = _max_minute(entries)

    if args.status:
        wm_min = "untracked" if last_minute is None else last_minute
        print(f"docket-watch [{key}]: {case['case']}")
        print(f"  watermark : ECF {last_entry or '(unset)'} / minute {wm_min}")
        print(f"  newest    : ECF {newest or '(none)'} / minute {newest_minute or '(none)'}")
        print(f"  feed      : {feed_url(case)}")
        print(f"  docket    : {docket_url(case)}")
        return 0, False, state

    today = datetime.now().strftime("%Y-%m-%d")
    cal = due_calendar(case, today)

    if first_run:
        if not args.dry_run:
            cur["last_entry"] = newest
            cur["last_minute"] = newest_minute
            cur["updated"] = _now()
            cur["case"] = case["case"]
            dockets[key] = cur
        print(f"docket-watch [{key}]: first run — watermark set to "
              f"ECF {newest} / minute {newest_minute}; {len(cal)} calendar item(s) within 3 days")
        for when, what in cal:
            print(f"  {when}: {what}")
        return 0, False, state

    new = new_entries(entries, last_entry, last_minute)

    if not new and not cal:
        if not args.quiet:
            wm_min = "untracked" if last_minute is None else last_minute
            print(f"docket-watch [{key}]: no new filings "
                  f"(watermark ECF {last_entry} / minute {wm_min}; "
                  f"newest ECF {newest} / minute {newest_minute})")
        return 0, False, state

    lines = []
    if new:
        n_ecf = sum(1 for e in new if e["kind"] == "entry")
        n_min = len(new) - n_ecf
        bits = []
        if n_ecf:
            bits.append(f"{n_ecf} ECF filing(s)")
        if n_min:
            bits.append(f"{n_min} minute entr{'y' if n_min == 1 else 'ies'}")
        lines.append(f"{' and '.join(bits)} new in {case['case']}:")
        for e in new:
            lines.append("  " + describe(e, case["known"]))
    if cal:
        lines.append("Calendar due:")
        for when, what in cal:
            lines.append(f"  {when}: {what}")
    body = "\n".join(lines)

    head = new[-1] if new else None
    if head:
        title = f"{case['label']}: " + (
            f"ECF {head['num']}" if head["kind"] == "entry" else "minute order"
        )
    else:
        title = f"{case['label']}: deadline approaching"

    print(f"docket-watch [{key}]: {'CHANGE' if new else 'DEADLINE'}\n{body}")

    if args.dry_run:
        print(f"\ndocket-watch [{key}]: --dry-run, watermark unchanged")
        return 0, bool(new), state

    ok = deliver(title, body, args.quiet)
    if not ok:
        print(f"docket-watch [{key}]: ERROR: delivery failed", file=sys.stderr)
        return 3, bool(new), state

    if not args.no_update:
        cur["last_entry"] = max(last_entry, newest)
        # (last_minute or 0): when None, the case is being brought under minute
        # tracking for the first time, so the newest minute in the feed becomes
        # the watermark and the history behind it is never reported.
        cur["last_minute"] = max(last_minute or 0, newest_minute)
        cur["updated"] = _now()
        cur["case"] = case["case"]
        dockets[key] = cur

    return 0, bool(new), state


def main() -> int:
    ap = argparse.ArgumentParser(description="Watch the site's federal dockets.")
    ap.add_argument("--case", action="append", choices=sorted(CASES),
                    help="restrict to one case (repeatable; default: all)")
    ap.add_argument("--dry-run", action="store_true", help="report but change nothing")
    ap.add_argument("--no-update", action="store_true", help="report, keep watermarks")
    ap.add_argument("--quiet", action="store_true", help="only report on change")
    ap.add_argument("--status", action="store_true", help="show watermarks and newest entries")
    args = ap.parse_args()

    keys = args.case or sorted(CASES)
    state = migrate_state(load_state())

    worst = 0
    for key in keys:
        rc, _changed, state = watch(key, CASES[key], state, args)
        worst = max(worst, rc)

    # Persist once, after every case has been checked: a single run that reads
    # both dockets should leave one consistent state file, not two writes racing
    # the next scheduled run.
    if not args.dry_run and not args.status:
        save_state(state)

    return worst


if __name__ == "__main__":
    sys.exit(main())
