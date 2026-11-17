from espn_api.football import League

LEAGUE_ID = 1061857099

league = League(league_id=LEAGUE_ID, year=2026)

print("League:", league.settings.name)
print("Teams:", len(league.teams))
print("Regular season weeks:", league.settings.reg_season_count)
print("Current week:", league.current_week)
print()
for team in league.teams:
    print(f"{team.team_name}: {team.wins}-{team.losses}, {team.points_for:.1f} points")