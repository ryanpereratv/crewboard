"""Rebuild data.json for the Crew Board from Stern Insider Connected's public feed.

Usage: python3 refresh.py [output_path]
Add a new quarter by adding its leaderboard code to QUARTERS.
"""
import json, sys, urllib.request
from datetime import datetime, timezone

API = "https://api.prd.sternpinball.io/api/v1/portal/leaderboards/?event_code={code}&event_state={state}"
QUARTERS = {  # label: (event code, state)
    "Q1": ("gZZi-fmzpw-HYT", "past"),
    "Q2": ("JfrkX-Fje-ebnQt", "past"),
    "Q3": ("DUuq-kLbA-PHU", "past"),
    "Q4": ("kSYx-BkgS-URyy", "current"),
}
CREW = ["ORYAN", "MRPKM", "YUNGLION666", "MALINAV"]


def fetch(code, state):
    with urllib.request.urlopen(API.format(code=code, state=state), timeout=30) as r:
        j = json.load(r)
    scores = (j.get("leaderboard") or {}).get("scores") or []
    if not scores:
        raise SystemExit(f"No scores for {code} ({state}): {j.get('message')}")
    return [(s["title_name"], s.get("username") or s.get("initials") or "?", s["score"]) for s in scores]


def build():
    raw = {q: fetch(*v) for q, v in QUARTERS.items()}
    all_scores = {}
    for rows in raw.values():
        for t, _, s in rows:
            all_scores.setdefault(t, []).append(s)

    data = {"q": {}, "y": {}}
    for q, rows in raw.items():
        by_t = {}
        for r in rows:
            by_t.setdefault(r[0], []).append(r)
        data["q"][q] = {}
        for t, arr in by_t.items():
            arr.sort(key=lambda r: -r[2])
            c = {}
            for i, (_, p, s) in enumerate(arr):
                u = p.upper()
                if u in CREW:
                    year_rank = sum(1 for x in all_scores[t] if x > s) + 1
                    c[u] = [i + 1, s, year_rank, len(all_scores[t])]
            data["q"][q][t] = {"n": len(arr), "t5": [[p, s] for _, p, s in arr[:5]], "c": c}

    for t in all_scores:
        best = {}
        for q, rows in raw.items():
            for tt, p, s in rows:
                if tt == t and (p.upper() not in best or best[p.upper()][1] < s):
                    best[p.upper()] = [p, s, q]
        lst = sorted(best.values(), key=lambda x: -x[1])
        c = {x[0].upper(): [i + 1, x[1], x[2]] for i, x in enumerate(lst) if x[0].upper() in CREW}
        data["y"][t] = {"t5": lst[:5], "c": c, "n": len(lst)}

    data["fetched"] = datetime.now(timezone.utc).isoformat()
    return data


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    d = build()
    with open(out, "w") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out}: " + ", ".join(f"{q} {len(v)} machines" for q, v in d["q"].items()))
