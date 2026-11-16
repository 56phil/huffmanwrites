#!/usr/bin/env python3
"""GitHub fork hygiene: fast-forward every fork to its upstream, keep its
security alerts on, and report what a fork cannot fix by itself.

Why this exists. A fork is a copy that silently rots. Nothing on GitHub tells
the owner that a fork of a patched project is itself unpatched, and the two
levers that would say so — Dependabot alerts and security updates — are
*disabled by default on a fork*. Measured 2026-10-17 across the eight forks
under this account: every one had `dependabot_security_updates: disabled`, one
was 1,252 commits behind its upstream, and nothing anywhere noticed.

Two halves, and they are different in kind:

  * **Up to date.** `POST /repos/{owner}/{repo}/merge-upstream` fast-forwards
    the fork's default branch onto its upstream. It is non-destructive by
    construction: GitHub refuses with 409 when the fork carries commits the
    upstream does not, so a fork with local work is never rewritten. Divergence
    is therefore a *finding for a human*, not something this script resolves —
    it is the one state in which the job cannot do its job, so it fails and
    alerts.

  * **Secure.** Enabling Dependabot alerts (`PUT .../vulnerability-alerts`) and
    security updates (`PATCH` `security_and_analysis.dependabot_security_updates`)
    is idempotent and is the whole of what "secure" means for a fork: the code
    comes from upstream, so the fix arrives by staying synced, and the alerts are
    what tell the owner when it has not.

What is deliberately NOT a failure: an open Dependabot alert. A fork cannot fix a
vulnerable dependency — upstream does, and the fix propagates through the sync
above. A job that exits non-zero for a condition its reader cannot act on is a
job whose alert gets learned as noise (the rule `skills/scheduled-job.md` states
for every start-date guard in this repo). Open alerts are reported, and the
report is where a human reads them.

**So the report has to be readable without redoing the work.** Measured
2026-11-16: the account carried 294 open alerts across three forks and the
report printed exactly one number for each — "141 Dependabot" — which is a count
whose reader must then open three security tabs, filter by severity, work out
whether any fix exists, and discover that GitHub had already opened nineteen
pull requests proposing the bumps. The same rule the quotation gate learned
applies here: a check that only says *no* is one whose reader repeats its work.
Each fork with alerts now prints the severity split, the ecosystems and
manifests, how many alerts have a released patched version, the open Dependabot
pull requests on the fork, the critical ones by name, and the one remedy that
holds — the bump belongs upstream, and merging it into a fork would diverge it
and make the next fast-forward refused.

Read-only unless `--apply` is given. The runner passes `--apply`; a hand run
reports and changes nothing.

    python3 scripts/check-forks.py                      # report only
    python3 scripts/check-forks.py --apply              # sync + enable alerts
    python3 scripts/check-forks.py --apply --report /tmp/f.md

Exit status: 0 when every fork is current (or ahead), 1 when a fork diverged or
could not be read. `--apply` does not change the exit status.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# The API is reached through `gh`, which handles authentication, pagination and
# the token stored in the login keychain. There is deliberately no second copy of
# a credential here: the repo's rule is one home per credential, and `gh` already
# owns this one.
GH = shutil.which("gh") or "/opt/homebrew/bin/gh"

# A fork list that comes back empty means the request broke, not that the account
# has no forks. Reporting "0 forks, all healthy" is the failure mode the repo's
# coverage rule exists for — a check that inspects nothing reports OK — so an
# empty enumeration is an error and not a clean run.
MIN_FORKS = 1


def gh(*args: str) -> "tuple[int, str]":
    """Run `gh` and return (returncode, first line of output or error).

    Only the first line is returned because `gh` appends a multi-line help hint
    to several API errors and the hint is not the finding.
    """
    proc = subprocess.run([GH, *args], capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        return proc.returncode, (err[0] if err else "unknown error")
    return 0, (proc.stdout or "").strip()


def gh_json(*args: str) -> "tuple[int, object, str]":
    """Run `gh api ... --jq ...` and parse the JSON it printed."""
    import json

    rc, out = gh(*args)
    if rc != 0:
        return rc, None, out
    try:
        return 0, json.loads(out), ""
    except json.JSONDecodeError:
        return 1, None, f"unparseable response: {out[:120]}"


def list_forks(owner: str) -> "tuple[int, list[str], str]":
    """Every repo under `owner` that is a fork, sorted.

    Enumerated from the API rather than from a list kept here: a fork made next
    month is covered without an edit, and a registry copied into a runner is how
    the docket's case list had to be centralised. The one thing a registry can do
    that this cannot is exclude a fork on purpose, which is what `--skip` is for.
    """
    rc, out = gh(
        "api", "--paginate", "/user/repos?per_page=100&affiliation=owner",
        "--jq", ".[] | select(.fork == true) | .full_name",
    )
    if rc != 0:
        return rc, [], out
    return 0, sorted({line.strip() for line in out.splitlines() if line.strip()}), ""


def decide(behind: int, ahead: int) -> str:
    """What a fork's default branch needs, from its compare against upstream.

    The four states are exhaustive on purpose, and `diverged` is the only one
    that needs a human: merge-upstream would refuse it, and forcing it would
    discard commits.
    """
    if ahead and behind:
        return "diverged"
    if behind:
        return "behind"
    if ahead:
        return "ahead"
    return "current"


def fork_state(full_name: str) -> dict:
    """Read one fork: its upstream, its position, and its security posture."""
    owner = full_name.split("/")[0]
    rc, meta, err = gh_json(
        "api", f"repos/{full_name}",
        "--jq", "{branch: .default_branch, archived: .archived, disabled: .disabled,"
                " fork: .fork, parent: (.parent.full_name // \"\"),"
                " sec: .security_and_analysis}",
    )
    if rc != 0:
        return {"repo": full_name, "error": err}

    parent = meta.get("parent") or ""
    if not parent:
        return {"repo": full_name, "error": "not a fork of a readable upstream"}

    branch = meta.get("branch") or "main"
    # The compare endpoint takes `OWNER:branch...OWNER:branch`, not
    # `owner/repo:branch`: the slash in the full name turns into a path segment
    # and the API answers 404 for a fork that exists. Measured here — the first
    # run reported "Not Found" for all eight forks, which reads like the account
    # losing its repositories rather than a malformed URL.
    upstream_owner = parent.split("/")[0]
    rc, cmp_, err = gh_json(
        "api", f"repos/{full_name}/compare/{upstream_owner}:{branch}...{owner}:{branch}",
        "--jq", "{status: .status, ahead: .ahead_by, behind: .behind_by}",
    )
    if rc != 0:
        return {"repo": full_name, "upstream": parent, "branch": branch, "error": err}

    state = decide(int(cmp_.get("behind") or 0), int(cmp_.get("ahead") or 0))
    return {
        "repo": full_name,
        "upstream": parent,
        "branch": branch,
        "ahead": int(cmp_.get("ahead") or 0),
        "behind": int(cmp_.get("behind") or 0),
        "state": state,
        "archived": bool(meta.get("archived")),
        "sec": meta.get("sec") or {},
    }


def count_from_pages(out: str) -> "int | None":
    """Sum the per-page counts `gh api --paginate --jq length` prints.

    `--paginate` runs the jq filter once per page and concatenates the results,
    so a repository with more alerts than one page yields two lines, `100` then
    `12`, and not one line reading `112`.
    Reading the first line reports a capped number as a total — measured here on
    2026-10-17: the fork `56phil/bigpowers` printed 100 from a real 112, and the
    report's summary line summed those caps into a figure that was simply wrong.
    A blank or non-numeric line is not a count; it is a failed read.
    """
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        return None
    try:
        return sum(int(ln) for ln in lines)
    except ValueError:
        return None


def alert_count(full_name: str, path: str) -> "tuple[int | None, str]":
    """Open alerts at `path`, or None and why they could not be read."""
    rc, out = gh("api", "--paginate", f"repos/{full_name}/{path}?state=open&per_page=100",
                 "--jq", "length")
    if rc != 0:
        return None, out
    n = count_from_pages(out)
    return (n, "") if n is not None else (None, f"unparseable count: {out[:80]}")


def security_counts(full_name: str) -> dict:
    """Open Dependabot and secret-scanning alerts, or why they could not be read.

    Neither call can fail the run. "Cannot read the alerts" is a statement about
    this script's access, never about the repository's safety, and collapsing the
    two is the false-accusation shape the repo's quotation gate documents.
    """
    out: dict = {}
    n, err = alert_count(full_name, "dependabot/alerts")
    out["dependabot"] = n
    if n is None:
        out["dependabot_error"] = err
    n, err = alert_count(full_name, "secret-scanning/alerts")
    out["secret_scanning"] = n
    if n is None:
        out["secret_scanning_error"] = err
    return out


ALERT_FIELDS = ("severity", "ecosystem", "package", "manifest", "version", "patched",
                "advisory")

# A report line is read, not parsed, so the lists are capped and say how many
# they left out. An unbounded manifest list for a fork carrying 141 alerts pushed
# the remedy line — the only sentence a reader acts on — off the bottom of the
# block.
MAX_MANIFESTS = 6
MAX_CRITICALS = 5


def alert_rows(full_name: str) -> "tuple[list[dict] | None, str]":
    """Every open Dependabot alert as one compact record, or None and why not.

    `--paginate` runs the jq filter once per page, so this is one call whatever
    the alert count. The fields are the six the report prints, and nothing else:
    the full objects are ~4 KB each, and 294 of them in a scheduled job's memory
    buys nothing a reader can see.
    """
    rc, out = gh(
        "api", "--paginate", f"repos/{full_name}/dependabot/alerts?state=open&per_page=100",
        "--jq",
        ".[] | [.security_advisory.severity,"
        " .dependency.package.ecosystem,"
        " .dependency.package.name,"
        " .dependency.manifest_path,"
        " .dependency.version_requirement,"
        " (.security_vulnerability.first_patched_version.identifier // \"\"),"
        " .security_advisory.ghsa_id] | @tsv",
    )
    if rc != 0:
        return None, out
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        # A row that is not six fields is a response this script does not
        # understand; carrying it as a half-record is how a breakdown silently
        # attributes an alert to the wrong manifest.
        if len(parts) != len(ALERT_FIELDS):
            return None, f"unparseable alert row: {line[:80]}"
        rows.append(dict(zip(ALERT_FIELDS, parts)))
    return rows, ""


def summarise_alerts(rows: "list[dict]") -> dict:
    """Counts a reader can act on, from the compact alert records."""
    from collections import Counter

    severity = Counter((r.get("severity") or "unknown") for r in rows)
    ecosystem = Counter((r.get("ecosystem") or "unknown") for r in rows)
    manifest = Counter((r.get("manifest") or "unknown") for r in rows)
    # `first_patched_version` is what separates "upstream has not released a fix"
    # from "upstream has shipped the fix and has not taken it". Only the second
    # is something a reader can chase, and the first is the one that would make
    # "ask upstream to bump" useless advice.
    fixable = sum(1 for r in rows if (r.get("patched") or "").strip())
    # One advisory can appear once per manifest — diagram-design's ten criticals
    # are five advisories counted twice, once in `uv.lock` and once in
    # `pyproject.toml`. Deduped by advisory id, because "10 criticals" reads as
    # ten distinct problems and is not.
    criticals, seen = [], set()
    for r in rows:
        if (r.get("severity") or "") != "critical":
            continue
        key = (r.get("advisory") or "", r.get("package") or "")
        if key in seen:
            continue
        seen.add(key)
        criticals.append(r)
    return {
        "total": len(rows),
        "severity": dict(severity),
        "ecosystem": dict(ecosystem),
        "manifest": dict(manifest),
        # Ordered, because a reader looks for critical first and a Counter's
        # insertion order is the API's, not the severity's.
        "criticals": criticals,
        "fixable": fixable,
    }


def open_dependabot_prs(full_name: str) -> "tuple[int | None, str]":
    """Open pull requests authored by Dependabot on `full_name`.

    GitHub has usually already opened the bump it proposes; saying so turns
    "141 alerts" into "eighteen pull requests, unmerged". Counted by author
    rather than by title: a title is a string the project can change, and the
    author is the account that opens them.

    The REST API names that account `dependabot[bot]`, not the `app/dependabot`
    that `gh pr list` prints — measured 2026-11-16, when an equality filter on
    the second spelling reported zero pull requests on a fork carrying eighteen.
    """
    rc, out, err = gh_json(
        "api", f"repos/{full_name}/pulls?state=open&per_page=100",
        "--jq", '[.[] | select(.user.login | startswith("dependabot"))] | length',
    )
    if rc != 0:
        return None, err
    try:
        return int(out), ""
    except (TypeError, ValueError):
        return None, f"unparseable pull request count: {str(out)[:80]}"


def enable_security(full_name: str, sec: dict, apply: bool) -> "list[str]":
    """Turn Dependabot alerts and security updates on. Idempotent; returns notes."""
    notes = []
    updated = ((sec or {}).get("dependabot_security_updates") or {}).get("status")
    if updated == "enabled":
        notes.append("security updates already on")
    elif not apply:
        notes.append("security updates OFF (would enable)")
    else:
        rc, err = gh("api", "-X", "PATCH", f"repos/{full_name}",
                     "-f", "security_and_analysis[dependabot_security_updates][status]=enabled")
        notes.append("security updates ON" if rc == 0 else f"security updates FAILED: {err}")

    # The PUT is idempotent, so with `--apply` it is issued unconditionally: a
    # 204 means the alerts are on either way, and a read-then-write pair would
    # only add a request that can disagree with the write. Without `--apply` it
    # is skipped entirely — a hand run reports and changes nothing. It was
    # issued unconditionally in the first draft of this file, which made
    # "report-only" a lie for exactly this one call.
    if not apply:
        notes.append("vulnerability alerts unverified (report-only run)")
    elif gh("api", "-X", "PUT", f"repos/{full_name}/vulnerability-alerts")[0] == 0:
        notes.append("vulnerability alerts ON")
    else:
        notes.append("vulnerability alerts FAILED")
    return notes


def sync_fork(full_name: str, branch: str, apply: bool) -> "tuple[bool, str]":
    """Fast-forward the fork onto its upstream. (ok, note)."""
    if not apply:
        return True, "would fast-forward (report-only run)"
    rc, out = gh("api", "-X", "POST", f"repos/{full_name}/merge-upstream", "-f", f"branch={branch}")
    if rc == 0:
        return True, "fast-forwarded"
    # 409 is GitHub refusing a merge that is not a fast-forward — the guard that
    # makes this call safe. Anything else is a real error.
    if "conflict" in out.lower() or "409" in out:
        return False, f"upstream refused the merge: {out}"
    return False, f"merge-upstream failed: {out}"


def render_alerts(row: dict) -> "list[str]":
    """The indented breakdown under a fork's alert line.

    Only emitted when the fork carries alert records: a fork with no alerts, or
    one whose records could not be read, has nothing to break down, and an empty
    block over "unreadable" is the shape that reads as "clean".
    """
    alerts = row.get("alerts")
    if not alerts:
        why = row.get("alerts_error")
        # A fork counted 141 alerts but whose detail could not be read must not
        # render as a fork with nothing under its count: that is the silent
        # blank this repo treats as a lie by omission.
        return [f"  (alert breakdown unreadable: {why})"] if why else []
    s = summarise_alerts(alerts)
    out = []
    order = ("critical", "high", "medium", "low", "unknown")
    sev = " · ".join(f"{k} {s['severity'][k]}" for k in order if s["severity"].get(k))
    if sev:
        out.append(f"  - severity: {sev}")
    out.append(f"  - a released fix exists for {s['fixable']} of {s['total']}")
    eco = " · ".join(f"{k} {v}" for k, v in sorted(s["ecosystem"].items(), key=lambda kv: -kv[1]))
    if eco:
        out.append(f"  - ecosystems: {eco}")
    mani = sorted(s["manifest"].items(), key=lambda kv: -kv[1])
    shown = " · ".join(f"`{k}` {v}" for k, v in mani[:MAX_MANIFESTS])
    rest = len(mani) - MAX_MANIFESTS
    if rest > 0:
        shown += f" · and {rest} more"
    if shown:
        out.append(f"  - manifests: {shown}")
    for c in s["criticals"][:MAX_CRITICALS]:
        arrow = f" → {c['patched']}" if c.get("patched") else ""
        out.append(f"  - CRITICAL: {c['package']} {c.get('version') or '?'} "
                   f"in `{c['manifest']}`{arrow} ({c.get('advisory') or 'no advisory id'})")
    rest = len(s["criticals"]) - MAX_CRITICALS
    if rest > 0:
        out.append(f"  - … and {rest} more critical advisor{'y' if rest == 1 else 'ies'}")

    prs = row.get("dep_prs")
    if prs is None:
        why = row.get("dep_prs_error")
        out.append("  - Dependabot pull requests: unreadable"
                   + (f" ({why})" if why else ""))
    elif prs:
        out.append(f"  - Dependabot pull requests open on this fork: {prs}")
    else:
        out.append("  - Dependabot pull requests open on this fork: none — the bump "
                   "has to be asked for upstream")

    state = row.get("state")
    if state == "current":
        # The remedy is only true while the fork is a mirror. A fork that is
        # behind has not yet taken an upstream fix that already exists, and
        # saying "the bump belongs upstream" over it would send the reader to
        # the wrong door.
        out.append("  - remedy: the bump belongs upstream "
                   f"(`{row.get('upstream')}`); this fork is current with it, so "
                   "nothing has been missed here. Merging the bump into the fork "
                   "would diverge it and `merge-upstream` refuses a non-fast-forward, "
                   "so the next run would report it diverged.")
    else:
        out.append("  - remedy: the fork is not current with upstream; the "
                   "fast-forward above is the first thing to wait for.")
    return out


def render(rows: "list[dict]", now: datetime) -> str:
    """The report a human reads in ~/Library/Logs/fork-sync-report.md."""
    synced = [r for r in rows if r.get("synced")]
    # An unreadable fork is a fork nothing is watching, so it counts as needing a
    # human alongside divergence. Counting only the `fatal` flag under-reported
    # it: that flag is set in main(), and the renderer is called with rows that
    # never went through it — the report said "0 needing a human" over a fork that
    # had failed to read at all.
    bad = [r for r in rows if r.get("fatal") or r.get("error")]
    open_alerts = sum(
        (r["sec_counts"].get("dependabot") or 0) + (r["sec_counts"].get("secret_scanning") or 0)
        for r in rows if r.get("sec_counts")
    )
    # Deduped: one critical advisory appears once per manifest, so the raw count
    # overstates it by however many lockfiles the project keeps.
    criticals = {}
    for r in rows:
        for c in summarise_alerts(r["alerts"])["criticals"] if r.get("alerts") else []:
            criticals[(c.get("advisory") or "", c.get("package") or "")] = c
    crit_note = f" ({len(criticals)} distinct critical advisor"\
                f"{'y' if len(criticals) == 1 else 'ies'})" if criticals else ""

    lines = [
        f"# GitHub fork report — {now.strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        f"{len(rows)} forks inspected · {len(synced)} fast-forwarded · "
        f"{len(bad)} needing a human · {open_alerts} open security alerts{crit_note}",
        "",
    ]

    for r in rows:
        if r.get("error"):
            lines.append(f"## {r['repo']}\n\n**ERROR — {r['error']}**\n")
            continue
        lines.append(f"## {r['repo']}")
        lines.append("")
        lines.append(f"- upstream: `{r['upstream']}` (branch `{r['branch']}`)")
        lines.append(f"- position: {r['state']} — "
                     f"{r['behind']} commit(s) behind, {r['ahead']} ahead")
        if r.get("archived"):
            lines.append("- NOTE: the upstream repository is archived; it will never move again")
        if r.get("notes"):
            for n in r["notes"]:
                lines.append(f"- {n}")
        sc = r.get("sec_counts") or {}
        dep = sc.get("dependabot")
        sec = sc.get("secret_scanning")
        lines.append(
            f"- open alerts: {dep if dep is not None else 'unreadable'} Dependabot, "
            f"{sec if sec is not None else 'unreadable'} secret-scanning"
        )
        for key in ("dependabot_error", "secret_scanning_error"):
            if sc.get(key):
                lines.append(f"  ({key.replace('_', ' ')}: {sc[key]})")
        lines.extend(render_alerts(r))
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Keep GitHub forks up to date and insecure-by-default off.")
    ap.add_argument("--apply", action="store_true",
                    help="perform the fast-forward and enable the security features")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicit no-op form of the default (kept for the runner's naming)")
    ap.add_argument("--user", default="",
                    help="GitHub account to enumerate; default is the authenticated one")
    ap.add_argument("--skip", action="append", default=[],
                    help="owner/repo to leave alone (repeatable)")
    ap.add_argument("--report", default="", help="write the markdown report here")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args()

    apply = args.apply and not args.dry_run
    now = datetime.now().astimezone()

    owner = args.user
    if not owner:
        # Not through `--jq '.login'`: that prints a bare string, which is not
        # JSON, so the shared parser rejects it. Read the object and take the
        # field.
        import json

        rc, out = gh("api", "user")
        if rc != 0:
            print(f"forks: ERROR: cannot read the authenticated account: {out}", file=sys.stderr)
            return 1
        try:
            owner = json.loads(out)["login"]
        except (json.JSONDecodeError, KeyError, TypeError):
            print("forks: ERROR: the account response carried no login", file=sys.stderr)
            return 1

    rc, forks, err = list_forks(owner)
    if rc != 0:
        print(f"forks: ERROR: cannot list forks for {owner}: {err}", file=sys.stderr)
        return 2
    skips = {s.strip() for s in args.skip if s.strip()}
    forks = [f for f in forks if f not in skips]

    if len(forks) < MIN_FORKS:
        print(f"forks: ERROR: no forks found for {owner} — the enumeration broke, it is not an "
              f"empty account", file=sys.stderr)
        return 2

    rows: "list[dict]" = []
    failures = 0
    for full_name in forks:
        row = fork_state(full_name)
        if row.get("error"):
            row["fatal"] = True
            failures += 1
            rows.append(row)
            continue

        row["sec_counts"] = security_counts(full_name)
        row["notes"] = enable_security(full_name, row.get("sec") or {}, apply)

        # The breakdown costs two calls and only when there is something to break
        # down. It is not allowed to fail the run: a fork whose alerts cannot be
        # read is already reported by the count as "unreadable", and turning a
        # second read of the same repository into a non-zero exit would give the
        # job a second way to alert about a condition its reader cannot fix.
        if (row["sec_counts"].get("dependabot") or 0) > 0:
            alerts, why = alert_rows(full_name)
            if alerts is None:
                row["alerts_error"] = why
            else:
                row["alerts"] = alerts
            prs, why = open_dependabot_prs(full_name)
            row["dep_prs"] = prs
            if prs is None:
                row["dep_prs_error"] = why

        if row["state"] == "behind":
            ok, note = sync_fork(full_name, row["branch"], apply)
            row["notes"].append(note)
            row["synced"] = ok
            if not ok:
                row["fatal"] = True
                failures += 1
        elif row["state"] == "diverged":
            row["fatal"] = True
            failures += 1
            row["notes"].append(
                "DIVERGED: the fork carries commits the upstream does not. "
                "Fast-forward is refused by design; rebase or reset it by hand."
            )
        rows.append(row)

    report = render(rows, now)
    if args.report:
        Path(args.report).expanduser().write_text(report, encoding="utf-8")

    synced = sum(1 for r in rows if r.get("synced"))
    behind_now = sum(1 for r in rows if not r.get("error") and r["state"] == "behind")
    if args.quiet:
        print(f"forks: {len(rows)} inspected, {synced} fast-forwarded, "
              f"{behind_now} still behind, {failures} failed")
    else:
        print(report)
    # The repo's coverage rule, in the shape every other gate here prints it: the
    # count is what was INSPECTED, so a selector that stops matching is visible as
    # a collapsing number rather than as a clean run over nothing.
    print(f"coverage: {len(rows)} forks")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
