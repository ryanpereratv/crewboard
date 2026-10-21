# Crew Board

Top-5 tracker for ORYAN, MRPKM, YUNGLION666 and MALINAV at Leaderboard Shad, using Stern Insider Connected's public leaderboard feed.

- `index.html` – the board (served by GitHub Pages)
- `data.json` – scores, rebuilt by `refresh.py`
- `.github/workflows/refresh.yml` – runs the refresh every Monday morning; use **Actions → Refresh scores → Run workflow** for an update on demand

**New quarter:** add its leaderboard code to `QUARTERS` in `refresh.py` (set the finished quarter to `"past"` and the new one to `"current"`), then add a tab for it in `index.html`.
