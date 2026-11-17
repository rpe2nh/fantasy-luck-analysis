from collections import Counter
import pandas as pd
from espn_api.football import League

LEAGUE_ID = 1061857099
YEAR = 2026

league = League(league_id=LEAGUE_ID, year=YEAR)
weeks_played = min(league.current_week - 1, league.settings.reg_season_count)

labels = pd.read_csv("data/team_labels_PRIVATE.csv")
name_to_label = dict(zip(labels["team_name"], labels["label"]))

def starters(lineup):
    return [p for p in lineup if p.slot_position not in ("BE", "IR")]

def best_possible_points(lineup, slots):
    """Best score this roster could have started: fill the strictest slots first, flex spots last."""
    pool = [p for p in lineup if p.slot_position != "IR"]
    used, total = set(), 0.0
    for slot in sorted(slots, key=lambda s: sum(s in p.eligibleSlots for p in pool)):
        options = [p for p in pool if id(p) not in used and slot in p.eligibleSlots]
        if options:
            best = max(options, key=lambda p: p.points)
            used.add(id(best))
            total += best.points
    return total

# Figure out the league's starting lineup slots from Week 1 (the most common set of starter positions)
week1 = league.box_scores(1)
slot_sets = Counter()
for game in week1:
    for lineup in (game.home_lineup, game.away_lineup):
        slot_sets[tuple(sorted(p.slot_position for p in starters(lineup)))] += 1
SLOTS = list(slot_sets.most_common(1)[0][0])
print("Starting lineup slots:", SLOTS, "\n")

rows = []
for week in range(1, weeks_played + 1):
    for game in league.box_scores(week):
        for team, lineup in ((game.home_team, game.home_lineup), (game.away_team, game.away_lineup)):
            actual = sum(p.points for p in starters(lineup))
            best = best_possible_points(lineup, SLOTS)
            rows.append({"week": week,
                         "team": name_to_label[team.team_name.strip()],
                         "actual_points": round(actual, 2),
                         "best_possible": round(best, 2),
                         "left_on_bench": round(best - actual, 2)})

df = pd.DataFrame(rows)
df.to_csv("data/lineup_efficiency_weekly.csv", index=False)

summary = df.groupby("team").agg(
    actual_points=("actual_points", "sum"),
    best_possible=("best_possible", "sum"),
    left_on_bench=("left_on_bench", "sum"),
)
summary["efficiency_pct"] = summary["actual_points"] / summary["best_possible"] * 100
summary = summary.sort_values("efficiency_pct", ascending=False).round(1)
summary.to_csv("data/lineup_efficiency_summary.csv")
print(summary.to_string())