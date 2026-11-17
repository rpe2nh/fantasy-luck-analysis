import pandas as pd

games = pd.read_csv("data/weekly_scores.csv")
lineups = pd.read_csv("data/lineup_efficiency_weekly.csv")

df = games.merge(lineups[["week", "team", "best_possible"]], on=["week", "team"])
df["fixable_loss"] = (df["result"] == "L") & (df["best_possible"] > df["opponent_score"])

summary = df.groupby("team").agg(
    losses=("result", lambda r: (r == "L").sum()),
    fixable_losses=("fixable_loss", "sum"),
).sort_values("fixable_losses", ascending=False)

summary.to_csv("data/lineup_losses.csv")
print(summary.to_string())
print(f"\nLeague total: {summary['fixable_losses'].sum()} of {summary['losses'].sum()} losses "
      f"could have been wins with the best lineup")