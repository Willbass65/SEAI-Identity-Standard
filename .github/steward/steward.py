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
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCORECARD_PATH = os.path.join(REPO_ROOT, "SCORECARD.md")
STATE_PATH = os.path.join(HERE, "state.json")

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


def _update_cumulative_summary(content, meta, discussions, traffic_views, traffic_clones):
    """Rewrite the Cumulative Summary table values in place."""
    stars = (meta or {}).get("stargazers_count", 0)
    forks = (meta or {}).get("forks_count", 0)
    watchers = (meta or {}).get("subscribers_count", 0)
    open_issues = (meta or {}).get("open_issues_count", 0)
    discussion_count = len(discussions) if discussions else 0
    views_unique = 0
    views_total = 0
    if isinstance(traffic_views, dict) and "count" in traffic_views:
        views_total = traffic_views.get("count", 0)
        views_unique = traffic_views.get("uniques", 0)
    clones_unique = 0
    clones_total = 0
    if isinstance(traffic_clones, dict) and "count" in traffic_clones:
        clones_total = traffic_clones.get("count", 0)
        clones_unique = traffic_clones.get("uniques", 0)

    # Every row in the cumulative table ends with a value cell. Replace the
    # value (the last "| N |" on the line) for each metric by matching the
    # metric label text (which may include an emoji prefix).
    metrics = [
        ("Stars", stars),
        ("Watchers", watchers),
        ("Forks", forks),
        ("Open Issues", open_issues),
        ("Discussions", discussion_count),
        ("Total Unique Visitors", views_unique),
        ("Total Page Views", views_total),
        ("Total Unique Cloners", clones_unique),
        ("Total Clones", clones_total),
    ]
    for label, value in metrics:
        # Match a table row whose cell contains the label, then replace the
        # final numeric cell. Handles emoji-prefixed labels like "| ⭐ Stars |".
        pattern = r"(?m)^(\|(?:(?!\n).)*?" + re.escape(label) + r"[^\n]*\|\s*)(\d+)(\s*\|)"
        content = re.sub(pattern, lambda m: m.group(1) + str(value) + m.group(3), content)
    return content


def update_scorecard(meta, issues, prs, discussions, advisories, traffic_views, traffic_clones, referrers):
    """Update the cumulative summary and replace the single Governance block."""
    if not os.path.exists(SCORECARD_PATH):
        print("SCORECARD.md not found; skipping scorecard update.", file=sys.stderr)
        return False

    with open(SCORECARD_PATH) as fh:
        content = fh.read()

    # 1) Update the cumulative summary numbers.
    content = _update_cumulative_summary(content, meta, discussions, traffic_views, traffic_clones)

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
    since_dt = now_utc() - datetime.timedelta(hours=args.since_hours)

    meta = collect_meta()
    issues = collect_open_issues()
    prs = collect_prs()
    discussions = collect_discussions()
    advisories = collect_advisories()
    traffic_views = collect_traffic_views()
    traffic_clones = collect_traffic_clones()
    referrers = collect_referrers()

    if args.mode == "summary":
        out = build_summary(meta, issues, prs, discussions, advisories, since_dt)
        print(out)
    else:
        ok = update_scorecard(
            meta, issues, prs, discussions, advisories,
            traffic_views, traffic_clones, referrers,
        )
        if ok:
            print("Scorecard refreshed.")
        else:
            print("Scorecard update failed.", file=sys.stderr)
            sys.exit(1)

    state["last_run"] = now_utc().isoformat()
    state["last_refresh"] = now_utc().isoformat()
    save_state(state)


if __name__ == "__main__":
    main()