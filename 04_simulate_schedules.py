import numpy as np
import pandas as pd

N_SIMS = 10_000
rng = np.random.default_rng(42)  # fixed seed so results are reproducible

df = pd.read_csv("data/weekly_scores.csv")
luck = pd.read_csv("data/luck_summary.csv", index_col="team")

# Grid of scores: one row per team, one column per week
scores = df.pivot(index="team", columns="week", values="score")
teams = scores.index.tolist()
S = scores.to_numpy()
n_teams, n_weeks = S.shape

# Replay the season 10,000 times with random weekly matchups, keeping everyone's real scores
sim_wins = np.zeros((N_SIMS, n_teams))
for s in range(N_SIMS):
    for w in range(n_weeks):
        order = rng.permutation(n_teams)
        home, away = order[0::2], order[1::2]
        home_won = S[home, w] > S[away, w]
        sim_wins[s, home] += home_won
        sim_wins[s, away] += ~home_won

results = pd.DataFrame(index=teams)
results["actual_wins"] = luck.loc[teams, "actual_wins"]
results["avg_sim_wins"] = sim_wins.mean(axis=0)
results["likely_low"] = np.percentile(sim_wins, 5, axis=0)    # 5th percentile
results["likely_high"] = np.percentile(sim_wins, 95, axis=0)  # 95th percentile
actual = results["actual_wins"].to_numpy()
results["pct_as_good_or_better"] = (sim_wins >= actual).mean(axis=0) * 100
results["pct_as_bad_or_worse"] = (sim_wins <= actual).mean(axis=0) * 100

results = results.sort_values("avg_sim_wins", ascending=False).round(1)
results.to_csv("data/simulation_summary.csv")
np.save("data/sim_wins.npy", sim_wins)  # saved for charts later

print(results.to_string())