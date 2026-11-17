import os
import string
import pandas as pd
from espn_api.football import League

LEAGUE_ID = 1061857099
YEAR = 2026
MY_TEAM_NAME = "EDPurdy445"

league = League(league_id=LEAGUE_ID, year=YEAR)
weeks_played = min(league.current_week - 1, league.settings.reg_season_count)

# Give each team an anonymous label (Team A, Team B, ...) based on ESPN's team ID order
teams_sorted = sorted(league.teams, key=lambda t: t.team_id)
label = {t.team_id: f"Team {string.ascii_uppercase[i]}" for i, t in enumerate(teams_sorted)}

# Label your own team "My Team"
my_team = next(t for t in league.teams if t.team_name.strip() == MY_TEAM_NAME)
label[my_team.team_id] = "My Team"

os.makedirs("data", exist_ok=True)

# Private lookup of label -> real team name (data/ is in .gitignore, so this never goes to GitHub)
pd.DataFrame(
    [{"label": label[t.team_id], "team_name": t.team_name.strip()} for t in teams_sorted]
).to_csv("data/team_labels_PRIVATE.csv", index=False)

rows = []
for team in league.teams:
    for week in range(weeks_played):
        opponent = team.schedule[week]
        rows.append({
            "week": week + 1,
            "team": label[team.team_id],
            "score": team.scores[week],
            "opponent": label[opponent.team_id],
            "opponent_score": opponent.scores[week],
            "result": team.outcomes[week],  # W, L, or T
        })

df = pd.DataFrame(rows)
df.to_csv("data/weekly_scores.csv", index=False)

print(f"Saved {len(df)} rows ({weeks_played} weeks x {len(league.teams)} teams)\n")
print(df[df["week"] == 1].to_string(index=False))

# Sanity check: do our counted wins match ESPN's official records?
counted = df[df["result"] == "W"].groupby("team").size()
official = {label[t.team_id]: t.wins for t in league.teams}
mismatches = {t: (counted.get(t, 0), w) for t, w in official.items() if counted.get(t, 0) != w}
print("\nWins match ESPN records:", "yes" if not mismatches else mismatches)