import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="Luck vs. Skill | Fantasy Football", page_icon="🏈", layout="wide")

# ---------- Colors ----------
RED = "#AA0000"
GOLD = "#B3995D"
TEXT = "#E8E6E3"
SUBTLE = "#9A958E"
CARD = "#161616"
BORDER = "#2A2A2A"
GRID = "#262626"

# ---------- Page styling ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Inter:wght@400;500;600&display=swap');
.block-container {{ padding-top: 2.5rem; max-width: 1200px; }}
h1, h2, h3 {{ font-family: 'Oswald', sans-serif !important; letter-spacing: 0.5px; }}
.stMarkdown p, .stMarkdown li {{ font-family: 'Inter', sans-serif; line-height: 1.6; }}
.hero {{ border-left: 6px solid {RED}; padding: 6px 0 6px 20px; margin-bottom: 2rem; }}
.hero h1 {{ font-size: 3rem; margin: 0; padding: 0; color: {TEXT}; }}
.hero h1 span {{ color: {GOLD}; }}
.hero p {{ color: {SUBTLE}; margin: 6px 0 0; font-size: 1.05rem; }}
.section-label {{ font-family: 'Oswald', sans-serif; color: {GOLD}; text-transform: uppercase;
                  letter-spacing: 2px; font-size: 0.85rem; margin: 0.5rem 0 0.75rem; }}
[data-testid="stMetric"] {{ background: {CARD}; border: 1px solid {BORDER}; border-top: 3px solid {GOLD};
                            border-radius: 10px; padding: 16px 18px; }}
[data-testid="stMetricLabel"] p {{ color: {SUBTLE}; text-transform: uppercase; font-size: 0.78rem; letter-spacing: 1px; }}
[data-testid="stMetricValue"] {{ font-family: 'Oswald', sans-serif; }}
.insight {{ background: {CARD}; border: 1px solid {BORDER}; border-left: 4px solid {RED};
            border-radius: 10px; padding: 18px 20px; height: 100%; }}
.insight .big {{ font-family: 'Oswald', sans-serif; font-size: 2.1rem; color: {GOLD}; line-height: 1.1; }}
.insight .label {{ color: {TEXT}; font-size: 0.95rem; margin-top: 6px; }}
.insight .sub {{ color: {SUBTLE}; font-size: 0.85rem; margin-top: 4px; }}
.stTabs [data-baseweb="tab"] p {{ font-family: 'Oswald', sans-serif; font-size: 1.1rem; letter-spacing: 0.5px; }}
.footer {{ color: {SUBTLE}; font-size: 0.85rem; border-top: 1px solid {BORDER}; padding-top: 1rem; margin-top: 2.5rem; }}
</style>
""", unsafe_allow_html=True)


def style(chart, title, height=400):
    """Apply the dark red-and-gold look to an Altair chart."""
    return (chart.properties(title=title, height=height)
            .configure(background="transparent")
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor=SUBTLE, titleColor=SUBTLE, gridColor=GRID, domainColor=BORDER,
                            tickColor=BORDER, labelFontSize=12, titleFontSize=12, titlePadding=10)
            .configure_title(color=TEXT, fontSize=17, anchor="start", offset=14))


def insight(col, big, label, sub=""):
    col.markdown(f'<div class="insight"><div class="big">{big}</div>'
                 f'<div class="label">{label}</div><div class="sub">{sub}</div></div>',
                 unsafe_allow_html=True)


# ---------- Data ----------
weekly = pd.read_csv("data/weekly_scores.csv")
luck = pd.read_csv("data/luck_summary.csv")
sim = pd.read_csv("data/simulation_summary.csv", index_col=0).rename_axis("team").reset_index()
eff = pd.read_csv("data/lineup_efficiency_summary.csv")
losses = pd.read_csv("data/lineup_losses.csv")
sim_wins = np.load("data/sim_wins.npy")
sim_teams = weekly.pivot(index="team", columns="week", values="score").index.tolist()

df = (luck.merge(eff[["team", "efficiency_pct", "left_on_bench"]], on="team")
          .merge(losses[["team", "losses", "fixable_losses"]], on="team")
          .merge(sim[["team", "likely_low", "likely_high", "pct_as_good_or_better", "pct_as_bad_or_worse"]], on="team"))
weeks = int(weekly["week"].max())
n_teams = df["team"].nunique()

# ---------- League mode: real names behind a password ----------
# Real team names live only in Streamlit's private Secrets, never in the GitHub repo.
def load_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return None

names = {}
with st.sidebar:
    st.markdown("### League members")
    st.caption("Enter the league password to see real team names.")
    password = st.text_input("League password", type="password")
    if password:
        if load_secret("league_password") and password == load_secret("league_password"):
            names = dict(load_secret("team_names") or {})
            st.success("Showing real team names")
        else:
            st.error("Wrong password")
league_mode = bool(names)

if league_mode:
    df["team"] = df["team"].map(lambda t: names.get(t, t))
    sim_teams = [names.get(t, t) for t in sim_teams]
    my_team = names.get("My Team", "My Team")
else:
    my_team = "My Team"

# ---------- Header ----------
names_note = ("Real team names shown for league members." if league_mode
              else "Teams are anonymized; my team is labeled “My Team.”")
st.markdown(f"""
<div class="hero">
  <h1>Luck <span>vs.</span> Skill</h1>
  <p>How much of a fantasy football record comes down to the schedule? A {n_teams}-team ESPN league,
  2026 season, weeks 1–{weeks}. {names_note} <b style="color:{GOLD}">The selected team is in gold.</b></p>
</div>
""", unsafe_allow_html=True)

# ---------- Team picker (drives the whole page) ----------
teams_sorted = sorted(df["team"], key=str.lower)
pick_col, _ = st.columns([1, 2])
focus = pick_col.selectbox("Find your team", teams_sorted, index=teams_sorted.index(my_team))
team_color = alt.condition(alt.datum.team == focus, alt.value(GOLD), alt.value(RED))

me = df[df["team"] == focus].iloc[0]
exp_rank = int(df["expected_wins"].rank(ascending=False, method="min")[df["team"] == focus].iloc[0])
eff_rank = int(df["efficiency_pct"].rank(ascending=False, method="min")[df["team"] == focus].iloc[0])

st.markdown(f'<div class="section-label">{focus}</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Record", f"{me.actual_wins:.0f}-{me.losses:.0f}")
c2.metric(f"Deserved wins · #{exp_rank} of {n_teams}", f"{me.expected_wins:.1f}")
c3.metric("Schedule luck", f"{me.luck:+.2f} wins")
c4.metric(f"Efficiency · #{eff_rank} of {n_teams}", f"{me.efficiency_pct:.1f}%")

# ---------- League headlines ----------
luckiest = df.loc[df["luck"].idxmax()]
unluckiest = df.loc[df["luck"].idxmin()]
total_fixable, total_losses = int(df["fixable_losses"].sum()), int(df["losses"].sum())
typical_range = int((df["likely_high"] - df["likely_low"]).median())

st.markdown('<div class="section-label" style="margin-top:1.5rem">League headlines</div>', unsafe_allow_html=True)
h1, h2, h3, h4 = st.columns(4)
insight(h1, f"{luckiest.luck:+.1f}", f"wins of luck for {luckiest.team}",
        f"{luckiest.actual_wins:.0f} actual vs. {luckiest.expected_wins:.1f} deserved")
insight(h2, f"{unluckiest.luck:+.1f}", f"wins of luck for {unluckiest.team}",
        f"only {unluckiest.pct_as_bad_or_worse:.0f}% of schedules are this harsh")
insight(h3, f"{typical_range} wins", "typical swing from schedule alone",
        "90% range of simulated records")
insight(h4, f"{total_fixable}/{total_losses}", "losses a better lineup would have won",
        "using players on the bench that week")

st.write("")

# ---------- Tabs ----------
tab_luck, tab_sim, tab_lineup, tab_data = st.tabs(
    ["Schedule luck", "10,000 simulations", "Lineup decisions", "Data & methods"])

with tab_luck:
    st.markdown("**Expected wins** add up, week by week, the share of the league each team outscored. "
                "**Luck** is actual wins minus expected wins.")
    left, right = st.columns(2)
    bars = alt.Chart(df).mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X("luck:Q", title="Luck (actual − expected wins)"),
        y=alt.Y("team:N", sort="-x", title=None),
        color=team_color,
        tooltip=["team", "actual_wins", alt.Tooltip("expected_wins", format=".2f"), alt.Tooltip("luck", format="+.2f")],
    )
    left.altair_chart(style(bars, "Schedule luck by team"), theme=None)

    diagonal = alt.Chart(pd.DataFrame({"x": [0, weeks], "y": [0, weeks]})).mark_line(
        strokeDash=[5, 5], color=SUBTLE).encode(x="x:Q", y="y:Q")
    dots = alt.Chart(df).mark_circle(size=170, opacity=0.95, stroke="#0E0E0E", strokeWidth=1).encode(
        x=alt.X("expected_wins:Q", title="Expected wins (what the scores deserved)"),
        y=alt.Y("actual_wins:Q", title="Actual wins"),
        color=team_color,
        tooltip=["team", "actual_wins", alt.Tooltip("expected_wins", format=".2f")],
    )
    right.altair_chart(style(diagonal + dots, "Above the line = lucky, below = unlucky"), theme=None)

with tab_sim:
    st.markdown("Each team keeps its real weekly scores, but opponents are randomly re-drawn "
                "for 10,000 alternate seasons. Change teams with the picker at the top of the page.")
    pick = focus
    wins = pd.Series(sim_wins[:, sim_teams.index(pick)])
    dist = wins.value_counts(normalize=True).sort_index().mul(100).rename_axis("wins").reset_index(name="pct")
    row = df[df["team"] == pick].iloc[0]
    hist = alt.Chart(dist).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("wins:O", title="Wins in a simulated season", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("pct:Q", title="% of simulated schedules"),
        color=alt.condition(alt.datum.wins == row.actual_wins, alt.value(GOLD), alt.value(RED)),
        tooltip=["wins", alt.Tooltip("pct", format=".1f")],
    )
    st.altair_chart(style(hist, f"{pick}: actual record in gold ({row.actual_wins:.0f} wins)", 340), theme=None)
    s1, s2, s3 = st.columns(3)
    s1.metric("Likely range (90%)", f"{row.likely_low:.0f}–{row.likely_high:.0f} wins")
    s2.metric("Schedules this good or better", f"{row.pct_as_good_or_better:.1f}%")
    s3.metric("Schedules this bad or worse", f"{row.pct_as_bad_or_worse:.1f}%")

with tab_lineup:
    st.markdown(f"**{total_fixable} of {total_losses} losses** could have been wins if the team had started "
                "its best possible lineup from the players on its roster that week.")
    left, right = st.columns(2)
    eff_bars = alt.Chart(df).mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X("efficiency_pct:Q", title="Points started ÷ best possible points (%)",
                scale=alt.Scale(domain=[75, 95], zero=False)),
        x2=alt.X2(datum=75),
        y=alt.Y("team:N", sort="-x", title=None),
        color=team_color,
        tooltip=["team", alt.Tooltip("efficiency_pct", format=".1f"), alt.Tooltip("left_on_bench", format=".1f")],
    )
    left.altair_chart(style(eff_bars, "Lineup efficiency"), theme=None)
    fix_bars = alt.Chart(df).mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X("fixable_losses:Q", title="Losses a perfect lineup would have won", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("team:N", sort="-x", title=None),
        color=team_color,
        tooltip=["team", "losses", "fixable_losses"],
    )
    right.altair_chart(style(fix_bars, "Fixable losses"), theme=None)

with tab_data:
    table = df[["team", "actual_wins", "expected_wins", "luck", "points_for", "points_against",
                "efficiency_pct", "left_on_bench", "fixable_losses"]].sort_values("expected_wins", ascending=False)
    table.columns = ["Team", "Wins", "Expected wins", "Luck", "Points for", "Points against",
                     "Lineup efficiency %", "Points left on bench", "Fixable losses"]
    st.dataframe(table.round(2), hide_index=True)
    st.markdown("#### Methods and caveats")
    st.markdown(
        "- **Expected wins** use an all-play record: each week, a team's win share is the fraction of other teams it outscored.\n"
        "- **Simulation** keeps real scores and randomly re-pairs matchups 10,000 times (fixed random seed).\n"
        "- **Best possible lineup** fills the strictest positions first, then flex, using that week's roster. "
        "It relies on hindsight, so no manager could reach 100%.\n"
        "- With 14 teams, about one team is expected to look this lucky or unlucky by chance (multiple comparisons).\n"
        f"- One season, {weeks} weeks so far: a small sample that grows each week."
    )

st.markdown('<div class="footer">Built with Python, pandas, NumPy, Altair, and Streamlit · '
            'Data from the ESPN Fantasy Football API</div>', unsafe_allow_html=True)