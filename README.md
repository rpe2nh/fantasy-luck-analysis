# Fantasy Football: Luck vs. Skill

How much of a fantasy football record comes down to the schedule? Using my 14-team ESPN league's 2026 season, this project separates **schedule luck** from **team strength** and **lineup decisions**, and shows the results in an interactive dashboard that updates every week.

**[Live dashboard →](https://oyfantasy.streamlit.app)**

## Key findings (weeks 1–10)

- **Schedule alone swings records by about 4 wins.** Replaying the season against 10,000 random schedules, most teams' 90% range of possible records spans 4 wins.
- **The unluckiest team deserved the 3rd-best record but sits at 4-6.** Only 7.8% of simulated schedules leave it that low, and it faced the most points against of any team.
- **Lineup decisions mattered more than schedule luck.** 30 of 70 losses (43%) could have been wins if the team had started its best lineup from players on its roster that week.
- **My team had the league's best "deserved" record** (7.7 expected wins vs. 7 actual) and the 2nd-most efficient lineups (90.6%).

## Dashboard features

- **Find your team:** pick any team to highlight it across every chart and see its luck, simulations, and lineup efficiency.
- **Schedule luck:** actual vs. expected wins for every team.
- **10,000 simulations:** the full range of records each team could have had with a different schedule.
- **Lineup decisions:** lineup efficiency and losses a better lineup would have won.
- **League mode:** league members can enter a password to see real team names. The public version stays anonymized.

## How it works

| Step | File | What it does |
|---|---|---|
| 1 | `01_connect.py` | Connects to the league through the ESPN Fantasy API |
| 2 | `02_get_weekly_scores.py` | Pulls every weekly matchup, anonymizes teams, and checks wins against ESPN's official records |
| 3 | `03_expected_wins.py` | Calculates expected (all-play) wins and luck for each team |
| 4 | `04_simulate_schedules.py` | Replays the season against 10,000 random schedules with NumPy |
| 5 | `05_lineup_efficiency.py` | Finds each team's best possible lineup each week and the points left on the bench |
| 6 | `06_lineup_losses.py` | Counts losses a better lineup would have won |
| — | `app.py` | Interactive Streamlit dashboard |
| — | `.github/workflows/weekly-update.yml` | GitHub Actions job that reruns the analysis every Tuesday and updates the dashboard |

## Caveats

- **One season so far:** a small sample that grows each week.
- **Multiple comparisons:** with 14 teams, about one is expected to look unusually lucky or unlucky by chance.
- **Lineup analysis uses hindsight,** since managers had to decide before seeing scores.
- **Team names are anonymized** to protect league members' privacy.

## Run it yourself

```bash
pip install -r requirements.txt
python3 02_get_weekly_scores.py   # then run 03 through 06 in order
streamlit run app.py
```

Built with Python, pandas, NumPy, Altair, Streamlit, GitHub Actions, and the `espn-api` package.