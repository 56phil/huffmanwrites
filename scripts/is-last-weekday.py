#!/usr/bin/env python3
"""Answer whether a date is the last given weekday of its month.

`StartCalendarInterval` cannot express "the last Tuesday of the month". It can
say Weekday 2, which fires every Tuesday and says nothing about which Tuesday is
the one meant. So `com.huffmanwrites.ninety-days-report` fires weekly and its
runner asks this script whether the fire is the real one.

It lives in a file, rather than in a line of shell arithmetic inside the runner,
for one reason: the answer depends on the calendar, and a guard that is wrong
ships one missed month at a time with nothing to see. Here the arithmetic can be
asserted against a pinned `--now` (see `TestNinetyDaysSchedule`) instead of by
waiting for a month to end on the right day.

Exit codes are deliberately three-valued. 0 is "this is the last <weekday>",
3 is "it is not", and anything else is a failure. A runner that read every
non-zero as "not today" would swallow a broken guard and quietly publish
nothing, which is the same absence the SITREP watchdog exists to catch.

Usage:
    python3 scripts/is-last-weekday.py --weekday Tuesday
    python3 scripts/is-last-weekday.py --weekday Tuesday --now 2026-11-24
"""

from __future__ import annotations

import argparse
import calendar
import sys
from datetime import date, timedelta

MATCH = 0
NO_MATCH = 3


def last_weekday(year: int, month: int, weekday: int) -> date:
    """The last `weekday` of the month. `weekday` is 0=Monday, as `date.weekday`."""
    last_day = calendar.monthrange(year, month)[1]
    d = date(year, month, last_day)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Exit 0 if the date is the last <weekday> of its month, 3 if not.")
    p.add_argument("--weekday", required=True,
                   help="weekday name, e.g. Tuesday")
    p.add_argument("--now", help="YYYY-MM-DD; defaults to today")
    args = p.parse_args(argv)

    names = [n.lower() for n in calendar.day_name]
    wanted = args.weekday.strip().lower()
    if wanted not in names:
        p.error(f"--weekday must be one of {', '.join(calendar.day_name)}")
    weekday = names.index(wanted)

    today = date.fromisoformat(args.now) if args.now else date.today()
    expected = last_weekday(today.year, today.month, weekday)
    label = calendar.day_name[weekday]

    if today == expected:
        print(f"last-weekday: {today} is the last {label} of {today:%B %Y}")
        return MATCH
    print(f"last-weekday: {today} is not the last {label} of {today:%B %Y}, "
          f"which is {expected}")
    return NO_MATCH


if __name__ == "__main__":
    sys.exit(main())
