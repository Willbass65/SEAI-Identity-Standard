#!/usr/bin/env python3
"""
SEAI Daily Steward

Pulls live data from the GitHub API for the SEAI Identity Standard repository
and:
  * refresh  -> updates SCORECARD.md with the latest daily data (auto cron)
  * summary  -> prints a human-readable daily summary for William (on-demand)

The scorecard preserves the existing manual format (cumulative summary, daily
breakdown, milestones, referrers, announcement timeline) and adds a
"Governance Scorecard" section tracking discussions and reviews.

Usage:
    python steward.py --mode refresh
    python steward.py --mode summary [--since-hours 24]
"""

import argparse
import datetime
import json
import os
import re
import sys

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO = os.environ.get("GITHUB_REPOSITORY", "Willbass65/SEAI-Identity-Standard")
# Prefer the steward PAT (full user token) over the Actions GITHUB_TOKEN:
# the traffic endpoints require push-level access that the Actions token
# does not reliably have, which froze the cumulative numbers in Aug 2026.
TOKEN = os.environ.get("STEWARD_PAT") or os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCORECARD_PATH = os.path.join(REPO_ROOT, "SCORECARD.md")
STATE_PATH = os.path.join(HERE, "state.json")
# Lifetime daily ledger: survives GitHub's 14-day traffic window so full
# history is preserved for any later review. Format:
#   {"days": {"2026-08-07": {"views": 45, "views_uniques": 38,
#                            "clones": 33, "clones_uniques": 20}, ...}}
HISTORY_PATH = os.path.join(HERE, "history.json")

OWNER, NAME = REPO.split("/", 1)
HEADERS = {}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"
HEADERS["Accept"] = "application/vnd.github.v3+json"


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def iso_to_dt(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as fh:
                return json.load(fh)
        except Exception:
            return {}
    return {}


def save_state(state):
    with open(STATE_PATH, "w") as fh:
        json.dump(state, fh, indent=2)


def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH) as fh:
                data = json.load(fh)
            if isinstance(data, dict) and isinstance(data.get("days"), dict):
                return data["days"]
        except Exception:
            pass
    return {}


def save_history(days):
    with open(HISTORY_PATH, "w") as fh:
        json.dump({"days": days}, fh, indent=2, sort_keys=True)


def merge_history(days, traffic_views, traffic_clones):
    """Fold the current 14-day traffic window into the lifetime ledger.

    Each run upserts per-day values; ``max`` is used so late revisions by
    GitHub (counts sometimes tick up hours later) are captured without ever
    double-counting. Days that age out of the API window keep their last
    recorded value forever.
    """
    def absorb(payload, list_key, count_field, uniques_field):
        if not (isinstance(payload, dict) and isinstance(payload.get(list_key), list)):
            return
        for entry in payload.get(list_key) or []:
            if not isinstance(entry, dict):
                continue
            day = (entry.get("timestamp") or "")[:10]
            if not day:
                continue
            d = days.setdefault(day, {})
            try:
                d[count_field] = max(d.get(count_field) or 0, int(entry.get("count") or 0))
                d[uniques_field] = max(d.get(uniques_field) or 0, int(entry.get("uniques") or 0))
            except (TypeError, ValueError):
                continue

    absorb(traffic_views, "views", "views", "views_uniques")
    absorb(traffic_clones, "clones", "clones", "clones_uniques")
    return days


def api_get(path, params=None):
    """Safe GET against the GitHub API with pagination."""
    url = f"{API}/{path}"
    items = []
    page = 0
    while True:
        page += 1
        p = dict(params or {})
        p["per_page"] = 100
        p["page"] = page
        resp = requests.get(url, headers=HEADERS, params=p, timeout=30)
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            return {"_error": resp.status_code}
        data = resp.json()
        if isinstance(data, list):
            items.extend(data)
            if len(data) < 100:
                break
        else:
            items = data
            break
    return items


def graphql(query, variables=None):
    if not TOKEN:
        return None
    resp = requests.post(
        f"{API}/graphql",
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    if resp.status_code != 200:
        return None
    return resp.json()


# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------

def collect_meta():
    d = api_get(f"repos/{REPO}")
    if isinstance(d, dict) and "_error" in d:
        return None
    return d


def collect_open_issues():
    return api_get(f"repos/{REPO}/issues", {"state": "open"})


def collect_prs():
    return api_get(f"repos/{REPO}/pulls", {"state": "open"})


def collect_advisories():
    return api_get(f"repos/{REPO}/security-advisories")


def collect_community_profile():
    return api_get(f"repos/{REPO}/community/profile")


def collect_branch_protection():
    return api_get(f"repos/{REPO}/branches/main/protection")


def collect_traffic_views():
    return api_get(f"repos/{REPO}/traffic/views")


def collect_traffic_clones():
    return api_get(f"repos/{REPO}/traffic/clones")


def collect_referrers():
    return api_get(f"repos/{REPO}/traffic/popular/referrers")

# Popular-path fragments that are provably admin-only pages: they require push
# access to view, so any views on them are owner (self) traffic and are excluded
# from the "Adjusted Page Views" figure. NOTE: "/community" is public, so it is
# deliberately NOT in this list even though it is likely owner traffic.
ADMIN_VIEW_PATH_FRAGMENTS = ("/pulse", "/graphs/")


def collect_popular_paths():
    return api_get(f"repos/{REPO}/traffic/popular/paths")


def compute_adjusted_views(traffic_views, popular_paths):
    """Return (adjusted_total, admin_views) or (None, None) without valid data.

    adjusted_total = raw total views minus views on provably admin-only pages
    (/pulse, /graphs/*). This gives an honest baseline for measuring the effect
    of announcements without owner browsing polluting the signal.
    """
    if not (isinstance(traffic_views, dict) and "count" in traffic_views
            and not traffic_views.get("_error")):
        return None, None
    views_total = traffic_views.get("count")
    admin_views = 0
    if isinstance(popular_paths, list):
        for p in popular_paths:
            path = p.get("path", "")
            if any(frag in path for frag in ADMIN_VIEW_PATH_FRAGMENTS):
                try:
                    admin_views += int(p.get("count", 0))
                except (TypeError, ValueError):
                    pass
    return max(views_total - admin_views, 0), admin_views


def collect_discussions():
    """Fetch discussions via GraphQL."""
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        discussions(first: 50, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes {
            number
            title
            url
            createdAt
            category { name }
            author { login }
            comments { totalCount }
          }
        }
      }
    }
    """
    data = graphql(query, {"owner": OWNER, "name": NAME})
    if not data:
        return None
    try:
        nodes = data["data"]["repository"]["discussions"]["nodes"]
    except Exception:
        return None
    return nodes


def filter_since(items, since_dt, date_field="created_at"):
    if not items or not since_dt:
        return items or []
    out = []
    for it in items:
        dt = iso_to_dt(it.get(date_field) or it.get("createdAt"))
        if dt and dt >= since_dt:
            out.append(it)
    return out
# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------

def build_summary(meta, issues, prs, discussions, advisories, since_dt):
    lines = []
    lines.append("# SEAI Daily Summary")
    lines.append("")
    lines.append(f"_Generated: {now_utc().strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append("")
    if meta:
        lines.append("## Repository Pulse")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| ⭐ Stars | {meta.get('stargazers_count', 0)} |")
        lines.append(f"| 🍴 Forks | {meta.get('forks_count', 0)} |")
        lines.append(f"| 👁 Watchers | {meta.get('subscribers_count', 0)} |")
        lines.append(f"| 📋 Open issues | {meta.get('open_issues_count', 0)} |")
        lines.append("")

    lines.append("## Open Issues & PRs")
    lines.append("")
    if not issues:
        lines.append("_No open issues._")
    else:
        for it in issues:
            labels = ", ".join(l["name"] for l in it.get("labels", []))
            lab = f" [{labels}]" if labels else ""
            lines.append(f"- **#{it['number']}** {it['title']}{lab}")
    lines.append("")
    if not prs:
        lines.append("_No open PRs._")
    else:
        for it in prs:
            lines.append(f"- **PR #{it['number']}** {it['title']}")
    lines.append("")

    lines.append("## Recent Discussions")
    lines.append("")
    if not discussions:
        lines.append("_No discussions._")
    else:
        for d in discussions[:12]:
            cat = d.get("category", {}).get("name", "")
            lines.append(
                f"- **#{d['number']}** [{cat}] {d['title']} "
                f"(by {d.get('author', {}).get('login', '?')}, "
                f"{d.get('comments', {}).get('totalCount', 0)} comments)"
            )
    lines.append("")

    lines.append("## Security Advisories")
    lines.append("")
    if not advisories or isinstance(advisories, dict):
        lines.append("_No open security advisories._")
    else:
        for a in advisories:
            lines.append(f"- **{a.get('summary', a.get('ghsa_id', 'advisory'))}** — {a.get('severity', '?')}")
    lines.append("")

    needs = []
    if issues:
        for it in issues:
            names = [l["name"].lower() for l in it.get("labels", [])]
            if any(k in names for k in ("security", "urgent", "critical", "question")):
                needs.append(f"Issue #{it['number']} — {it['title']}")
    if advisories and not isinstance(advisories, dict) and advisories:
        needs.append("Open security advisory requires review")
    if needs:
        lines.append("## ⚠️ Needs Your Direct Intervention")
        lines.append("")
        for n in needs:
            lines.append(f"- {n}")
        lines.append("")
    else:
        lines.append("## ✅ Nothing Needs Your Intervention")
        lines.append("")
        lines.append("The repo looks healthy. No issues, PRs, or advisories require your attention.")
        lines.append("")

    return "\n".join(lines)


def _build_gov_block(meta, issues, prs, discussions, advisories):
    date_key = now_utc().strftime("%Y-%m-%d")
    stars = (meta or {}).get("stargazers_count", 0)
    forks = (meta or {}).get("forks_count", 0)
    watchers = (meta or {}).get("subscribers_count", 0)
    open_issues = (meta or {}).get("open_issues_count", 0)
    discussion_count = len(discussions) if discussions else 0
    pr_count = len(prs) if prs else 0
    adv_count = len(advisories) if advisories and not isinstance(advisories, dict) else 0
    return [
        f"### Governance Scorecard | {date_key}",
        "",
        "| Item | Status |",
        "|---|---|",
        f"| Stars | {stars} |",
        f"| Forks | {forks} |",
        f"| Watchers | {watchers} |",
        f"| Open issues | {open_issues} |",
        f"| Open PRs | {pr_count} |",
        f"| Discussions | {discussion_count} |",
        f"| Security advisories | {adv_count} |",
        f"| Last refreshed (UTC) | {now_utc().strftime('%Y-%m-%d %H:%M')} |",
        "",
    ]


def _rebuild_cumulative_summary(content, meta, discussions, traffic_views, traffic_clones, popular_paths, history):
    """Rewrite the Cumulative Summary table from the lifetime ledger.

    Totals (clones/views counts) are LIFETIME figures summed from the daily
    ledger, so they never shrink when days age out of GitHub's 14-day window.
    Unique counts and adjusted views are only available per 14-day window and
    are labeled as such. If a metric has no valid data, its row is preserved.
    """
    stars = (meta or {}).get("stargazers_count")
    forks = (meta or {}).get("forks_count")
    watchers = (meta or {}).get("subscribers_count")
    open_issues = (meta or {}).get("open_issues_count")
    discussion_count = len(discussions) if discussions else None

    lifetime_views = lifetime_clones = None
    if history:
        lifetime_views = sum((d.get("views") or 0) for d in history.values())
        lifetime_clones = sum((d.get("clones") or 0) for d in history.values())

    views_unique = clones_unique = None
    if isinstance(traffic_views, dict) and "count" in traffic_views and not traffic_views.get("_error"):
        views_unique = traffic_views.get("uniques")
    if isinstance(traffic_clones, dict) and "count" in traffic_clones and not traffic_clones.get("_error"):
        clones_unique = traffic_clones.get("uniques")
    adjusted_views, _admin = compute_adjusted_views(traffic_views, popular_paths)

    rows = [
        ("⭐ Stars", stars),
        ("👁 Watchers", watchers),
        ("🍴 Forks", forks),
        ("📋 Open Issues", open_issues),
        ("💬 Discussions", discussion_count),
        ("👀 Unique Visitors (14-day window)", views_unique),
        ("📄 Page Views (lifetime)", lifetime_views),
        ("📄 Adjusted Page Views (14-day window)", adjusted_views),
        ("📥 Unique Cloners (14-day window)", clones_unique),
        ("📥 Total Clones (lifetime)", lifetime_clones),
    ]
    table_lines = ["| Metric | Value |", "|---|---|"]
    for label, value in rows:
        table_lines.append(f"| {label} | {value if value is not None else '—'} |")
    new_table = "\n".join(table_lines)

    # Replace only the table directly under the Cumulative Summary header.
    # The note (blockquote) and everything after it is preserved untouched,
    # which also protects the manual Daily Breakdown sections below.
    pattern = re.compile(
        r"(## Cumulative Summary[^\n]*\n\n)\| Metric \| Value \|\n\|---\|---\|\n(?:\|[^\n]*\n)+"
    )
    if pattern.search(content):
        content = pattern.sub(lambda m: m.group(1) + new_table + "\n", content, count=1)
    return content


HISTORY_BEGIN = "<!-- BEGIN daily-history (auto-maintained by the steward; do not edit) -->"
HISTORY_END = "<!-- END daily-history -->"


def _classify_day(d):
    """Classify a day's traffic signature.

    extraction — clones with zero views: automated/farming signature (git
                  clones never touch the web UI, so view-less clone days are
                  machine pulls, not human evaluation).
    engaged    — at least one page view alongside any activity.
    quiet      — no traffic at all.
    """
    views = d.get("views") or 0
    clones = d.get("clones") or 0
    if clones and not views:
        return "extraction"
    if views or clones:
        return "engaged"
    return "quiet"


def _build_daily_history_block(history):
    lines = [
        "## Daily History (Automated Ledger)",
        "",
        "> Maintained automatically by the daily steward from the GitHub Traffic API.",
        "> One row per day since launch. Rows never expire — unlike GitHub's own",
        "> 14-day traffic window, this ledger preserves the full history for review.",
        "> **Signal** column: `extraction` = clones with zero views (automated/farming",
        "> signature), `engaged` = views present, `quiet` = no traffic.",
        "",
        HISTORY_BEGIN,
        "",
        "| Date | Views | Uniq. Visitors | Clones | Uniq. Cloners | Signal |",
        "|---|---|---|---|---|---|",
    ]
    extraction_clones = 0
    total_clones = 0
    extraction_days = 0
    for day in sorted(history):
        d = history[day]
        signal = _classify_day(d)
        clones = d.get("clones") or 0
        total_clones += clones
        if signal == "extraction":
            extraction_clones += clones
            extraction_days += 1
        lines.append(
            f"| {day} | {d.get('views', 0)} | {d.get('views_uniques', 0)} "
            f"| {clones} | {d.get('clones_uniques', 0)} | {signal} |"
        )
    lines.append("")
    if total_clones:
        share = round(100.0 * extraction_clones / total_clones)
        lines.append(
            f"**Extraction share (lifetime):** {extraction_clones} of {total_clones} clones "
            f"({share}%) occurred on view-less days across {extraction_days} extraction days. "
            f"High extraction share indicates automated mirroring/farming rather than human adoption; "
            f"treat stars, forks, issues, and discussion participants — not raw clones — as adoption signal."
        )
        lines.append("")
    lines.append(HISTORY_END)
    return "\n".join(lines)


def _update_daily_history(content, history):
    """Insert or refresh the auto-maintained daily history table."""
    if not history:
        return content
    block = _build_daily_history_block(history)
    if HISTORY_BEGIN in content:
        pattern = re.compile(re.escape(HISTORY_BEGIN) + r".*?" + re.escape(HISTORY_END), re.S)
        return pattern.sub(lambda m: block, content, count=1)
    if "\n## Milestones" in content:
        return content.replace("\n## Milestones", "\n" + block + "\n\n## Milestones", 1)
    return content.rstrip() + "\n\n" + block + "\n"



def update_scorecard(meta, issues, prs, discussions, advisories, traffic_views, traffic_clones, referrers, popular_paths=None, history=None):
    """Update the cumulative summary, daily history ledger table, and governance block."""
    if not os.path.exists(SCORECARD_PATH):
        print("SCORECARD.md not found; skipping scorecard update.", file=sys.stderr)
        return False

    with open(SCORECARD_PATH) as fh:
        content = fh.read()

    # 1) Rebuild the cumulative summary from the lifetime ledger.
    content = _rebuild_cumulative_summary(content, meta, discussions, traffic_views, traffic_clones, popular_paths, history or {})

    # 1b) Refresh the auto-maintained daily history table.
    content = _update_daily_history(content, history or {})

    # 2) Remove ALL existing Governance Scorecard blocks (past and present).
    #    A block starts with a line beginning with "### Governance Scorecard"
    #    and runs until the footer marker or the next major header.
    lines = content.splitlines()
    out = []
    in_gov = False
    for ln in lines:
        if ln.startswith("### Governance Scorecard"):
            in_gov = True
            continue
        if in_gov:
            # End of the governance block when we hit the footer marker.
            if ln.startswith("*Scorecard maintained by Cline"):
                in_gov = False
                out.append(ln)
                continue
            # Skip blank lines and table content inside the block.
            # Stop skipping if we hit a new top-level or ### header.
            if ln.startswith("#") :
                in_gov = False
                out.append(ln)
                continue
            continue
        out.append(ln)
    content = "\n".join(out)

    # 3) Append a single fresh Governance block before the footer.
    content = content.rstrip()
    block_lines = _build_gov_block(meta, issues, prs, discussions, advisories)
    content += "\n\n" + "\n".join(block_lines)

    # 4) Ensure footer marker present.
    marker = "*Scorecard maintained by Cline"
    if marker not in content:
        content += "\n" + marker
    content = content.rstrip() + "\n"

    with open(SCORECARD_PATH, "w") as fh:
        fh.write(content)
    return True



def main():
    parser = argparse.ArgumentParser(description="SEAI Daily Steward")
    parser.add_argument("--mode", choices=["refresh", "summary"], default="refresh")
    parser.add_argument("--since-hours", type=int, default=24)
    args = parser.parse_args()

    state = load_state()
    history = load_history()
    since_dt = now_utc() - datetime.timedelta(hours=args.since_hours)

    meta = collect_meta()
    issues = collect_open_issues()
    prs = collect_prs()
    discussions = collect_discussions()
    advisories = collect_advisories()
    traffic_views = collect_traffic_views()
    traffic_clones = collect_traffic_clones()
    referrers = collect_referrers()
    popular_paths = collect_popular_paths()

    # Fold today's traffic window into the lifetime ledger BEFORE updating
    # the scorecard, so cumulative totals and the daily history table are
    # computed from the complete ledger.
    merge_history(history, traffic_views, traffic_clones)

    if args.mode == "summary":
        out = build_summary(meta, issues, prs, discussions, advisories, since_dt)
        print(out)
    else:
        ok = update_scorecard(
            meta, issues, prs, discussions, advisories,
            traffic_views, traffic_clones, referrers, popular_paths,
            history=history,
        )
        if ok:
            print("Scorecard refreshed.")
        else:
            print("Scorecard update failed.", file=sys.stderr)
            sys.exit(1)

    state["last_run"] = now_utc().isoformat()
    state["last_refresh"] = now_utc().isoformat()
    save_state(state)
    save_history(history)


if __name__ == "__main__":
    main()