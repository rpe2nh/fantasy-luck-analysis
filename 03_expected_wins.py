import pandas as pd

df = pd.read_csv("data/weekly_scores.csv")
n_teams = df["team"].nunique()

# For each team-week: how many of the other 13 teams did they outscore?
df["teams_beaten"] = df.groupby("week")["score"].rank(method="min") - 1
df["all_play_win_pct"] = df["teams_beaten"] / (n_teams - 1)

summary = df.groupby("team").agg(
    actual_wins=("result", lambda r: (r == "W").sum() + 0.5 * (r == "T").sum()),
    expected_wins=("all_play_win_pct", "sum"),
    points_for=("score", "sum"),
    points_against=("opponent_score", "sum"),
)
summary["luck"] = summary["actual_wins"] - summary["expected_wins"]
summary = summary.sort_values("luck", ascending=False).round(2)

summary.to_csv("data/luck_summary.csv")
print(summary.to_string())