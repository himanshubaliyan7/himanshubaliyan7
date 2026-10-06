#!/usr/bin/env python3
"""
Step 5a - fetch the real contribution calendar, no token needed.

GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions (the fragment the profile
page itself loads). Parse the day cells and write data/contributions.json
with the raw days plus derived stats.
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

from common import ROOT, USERNAME

URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = os.path.join(ROOT, "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, timeout=30, headers={
        "User-Agent": "profile-readme-art/1.0",
        "X-Requested-With": "XMLHttpRequest",
    })
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        m = re.match(r"(\d+)", tips.get(td.get("id"), ""))
        days.append({
            "date": date,
            "count": int(m.group(1)) if m else 0,
            "level": int(td.get("data-level") or 0),
        })
    if not days:
        sys.exit("no calendar cells found - GitHub's markup may have changed")
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    """Return (current, longest) streaks as dicts with length/start/end."""
    longest = {"length": 0, "start": None, "end": None}
    run_start = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run_start is None:
                run_start = i
            if i - run_start + 1 > longest["length"]:
                longest = {"length": i - run_start + 1,
                           "start": days[run_start]["date"], "end": d["date"]}
        else:
            run_start = None

    i = len(days) - 1
    if days[i]["count"] == 0:
        i -= 1  # today isn't over yet, so an empty today doesn't break the streak
    end = i
    while i >= 0 and days[i]["count"] > 0:
        i -= 1
    length = end - i
    current = {"length": length,
               "start": days[i + 1]["date"] if length else None,
               "end": days[end]["date"] if length else None}
    return current, longest


def build(days):
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"])
    best = max(days, key=lambda d: d["count"])
    current, longest = streaks(days)
    monthly = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]
    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": [{"month": k, "total": v} for k, v in sorted(monthly.items())],
        "days": days,
    }


if __name__ == "__main__":
    data = build(fetch_days())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT}: {data['total_contributions']} contributions, "
          f"current streak {data['current_streak']['length']}, "
          f"longest {data['longest_streak']['length']}")
