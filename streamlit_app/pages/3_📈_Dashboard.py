import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="MLB Totals & Run Line Dashboard", layout="wide")

st.title("⚾ Load MLB Odds Dataset From GitHub")

RAW_URL = "https://raw.githubusercontent.com/Deeeego/Project_2/main/streamlit_app/pages/mlb-odds-2021.xlsx"

# ------------------------------------------------------
# Cached file loader
# ------------------------------------------------------
@st.cache_data
def load_mlb_data(url):
    response = requests.get(url)
    return pd.read_excel(BytesIO(response.content))

# Load data
df = load_mlb_data(RAW_URL)

st.title("⚾ MLB Totals & Run Line Coverage Dashboard")

# Convert custom date format

def parse_custom_date(val):
    s = str(int(val))  # convert to string
    if len(s) == 3:        # MDD (e.g., 401 → April 1)
        month = int(s[0])
        day = int(s[1:3])
    elif len(s) == 4:      # MMDD (e.g., 1012 → October 12)
        month = int(s[0:2])
        day = int(s[2:4])
    else:
        month, day = None, None
    return month, day

df["Month"], df["Day"] = zip(*df["Date"].apply(parse_custom_date))

# Pair rows into games
df_sorted = df.sort_values(["Date", "Rot"])
games = []

for _, g in df_sorted.groupby("Date"):
    rows = g.sort_values("Rot")
    for i in range(0, len(rows), 2):
        if i + 1 < len(rows):
            games.append(rows.iloc[i:i+2])


# Build full game-level dataset
game_records = []

for game in games:
    # total runs
    total_runs = game["Final"].sum()
    month = game["Month"].iloc[0]

    # determine favorite by closing line
    close_ml = game["Close"].astype(float)
    fav_idx = close_ml.idxmin()  # favorite = most negative ML
    dog_idx = close_ml.idxmax()

    fav = game.loc[fav_idx]
    dog = game.loc[dog_idx]

    # run line coverage
    margin = fav["Final"] - dog["Final"]
    rl = fav["RunLine"]
    covered = (margin + rl) > 0

    game_records.append({
        "Month": month,
        "Total Runs": total_runs,
        "Favorite Team": fav["Team"],
        "Run Line": rl,
        "Margin": margin,
        "Covered": covered
    })

games_df = pd.DataFrame(game_records)

# Monthly averages for totals
monthly_avg_totals = games_df.groupby("Month")["Total Runs"].mean()

# Run line coverage summary
total_games = len(games_df)
covers = games_df["Covered"].sum()
cover_rate = covers / total_games

# KPIs
st.subheader("📌 Key Metrics")

c1, c2, c3 = st.columns(3)
c1.metric("Total Games", total_games)
c2.metric("Run Line Coverage %", f"{cover_rate:.1%}")
c3.metric("Highest-Scoring Month", monthly_avg_totals.idxmax())

# VISUALIZATIONS

# Monthly totals line chart
st.subheader("📈 Average Total Runs by Month")

fig1, ax1 = plt.subplots(figsize=(10,4))
ax1.plot(monthly_avg_totals.index, monthly_avg_totals.values, marker="o", linewidth=2)
ax1.set_xlabel("Month")
ax1.set_ylabel("Average Total Runs")
ax1.set_title("Average Game Totals by Month")
ax1.grid(True)
st.pyplot(fig1)

# Run line coverage chart
st.subheader("📊 Run Line Coverage")

fig2, ax2 = plt.subplots(figsize=(6,4))
ax2.bar(["Covered", "Not Covered"], [covers, total_games - covers], color=["green", "red"])
ax2.set_ylabel("Number of Games")
ax2.set_title("Favorite Run Line Coverage")
st.pyplot(fig2)


# Raw tables
st.subheader("📄 Monthly Averages Table")
st.dataframe(monthly_avg_totals.reset_index(), use_container_width=True)

st.subheader("📄 Run Line Coverage Data")
st.dataframe(games_df[["Favorite Team", "Run Line", "Margin", "Covered"]], use_container_width=True)
