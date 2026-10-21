# Crew Board

Top-5 tracker for a group of friends at a local pinball location, using Stern Insider Connected's public leaderboard feed.

- `index.html` – the board (served by GitHub Pages)
- `data.json` – scores, rebuilt by `refresh.py`
- `history.json` – crew top-5 spots from the last run, plus the log of new top-5s and climbs shown in the "New this week" banner
- `.github/workflows/refresh.yml` – runs the refresh every day around 2 a.m. Eastern; use **Actions → Refresh scores → Run workflow** for an update on demand

**New quarter:** add its leaderboard code to `QUARTERS` in `refresh.py` (set the finished quarter to `"past"` and the new one to `"current"`), then add a tab for it in `index.html`.
