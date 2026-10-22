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
            data["q"][q][t] = {"n": len(arr), "t5": [[p, s] for _, p, s in arr[:5]],
                                "s10": arr[9][2] if len(arr) >= 10 else None, "c": c}

    for t in all_scores:
        best = {}
        for q, rows in raw.items():
            for tt, p, s in rows:
                if tt == t and (p.upper() not in best or best[p.upper()][1] < s):
                    best[p.upper()] = [p, s, q]
        lst = sorted(best.values(), key=lambda x: -x[1])
        c = {x[0].upper(): [i + 1, x[1], x[2]] for i, x in enumerate(lst) if x[0].upper() in CREW}
        data["y"][t] = {"t5": lst[:5], "s10": lst[9][1] if len(lst) >= 10 else None, "c": c, "n": len(lst)}

    data["fetched"] = datetime.now(timezone.utc).isoformat()
    return data


def update_history(data, path="history.json", keep_days=90):
    """Compare crew top-5 spots in the live quarter(s) with the last run and log shoutouts.

    Event kinds: "new" (entered the top 5), "up" (climbed within the top 5).
    The first run only records positions, so it never floods the log.
    """
    try:
        with open(path) as f:
            hist = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        hist = None

    now = datetime.now(timezone.utc)
    live = [q for q, (_, state) in QUARTERS.items() if state == "current"]
    positions = {}
    for q in live:
        for t, v in data["q"][q].items():
            for u, x in v["c"].items():
                if x[0] <= 5:
                    positions[f"{q}|{t}|{u}"] = [x[0], x[1]]

    events = [] if hist is None else hist.get("events", [])
    if hist is not None:
        prev = hist.get("positions", {})
        for key, (rank, score) in positions.items():
            q, t, u = key.split("|")
            before = prev.get(key)
            if before is None:
                kind = "new"
            elif rank < before[0]:
                kind = "up"
            else:
                continue
            events.append({"at": now.isoformat(), "q": q, "t": t, "u": u, "rank": rank,
                           "prev": before[0] if before else None, "score": score, "kind": kind})

    cutoff = now.timestamp() - keep_days * 86400
    events = [e for e in events if datetime.fromisoformat(e["at"]).timestamp() >= cutoff]
    out = {"since": (hist or {}).get("since", now.isoformat()), "checked": now.isoformat(),
           "positions": positions, "events": events}
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return [e for e in events if e["at"] == now.isoformat()]


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    d = build()
    with open(out, "w") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out}: " + ", ".join(f"{q} {len(v)} machines" for q, v in d["q"].items()))
    new = update_history(d)
    print(f"Shoutouts this run: {len(new)}" + "".join(f"\n  {e['u']} #{e['rank']} {e['t']} ({e['kind']})" for e in new))
