import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl

st.title("📊 Favorite Run Line Coverage (MLB 2021)")

try:
    df = pd.read_excel("data.xlsx", engine='openpyxl')
    st.write("Data from stored file:")
    st.dataframe(df_stored)
except FileNotFoundError:
    st.error("Error: 'data.xlsx' not found. Ensure it's in the correct path and committed to your repository.")
except Exception as e:
    st.error(f"An error occurred while reading the stored file: {e}")

# Pair teams into games
df_sorted = df.sort_values(['Date', 'Rot'])
games = []

for _, group in df_sorted.groupby('Date'):
    rows = group.sort_values('Rot')
    for i in range(0, len(rows), 2):
        if i + 1 < len(rows):
            games.append(rows.iloc[i:i+2])

# Compute favorite coverage results
results = []

for game in games:
    close_ml = game['Close'].astype(float)

    fav_idx = close_ml.idxmin()   # favorite (most negative ML)
    dog_idx = close_ml.idxmax()

    fav = game.loc[fav_idx]
    dog = game.loc[dog_idx]

    margin = fav['Final'] - dog['Final']
    rl = fav['RunLine']

    covered = (margin + rl) > 0
    results.append(int(covered))

# Pie chart data
labels = ['Covered', 'Not Covered']
sizes = [sum(results), len(results) - sum(results)]

# Create matplotlib figure
fig, ax = plt.subplots(figsize=(6,6))
ax.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    startangle=90,
    pctdistance=0.85
)

centre_circle = plt.Circle((0,0),0.70,fc='white')
fig.gca().add_artist(centre_circle)

ax.set_title("Favorite Run Line Coverage (MLB 2021)")

# Display in Streamlit
st.pyplot(fig)

# Interpretation
st.info("""
**Interpretation**
- Based on our findings, the favorite only covers 43.9 percent of the time on the run line.
- This means in the long run, you are likely to lose money betting on only favorite run line bets.
- I chose to cover the runline because it's the handicap that tries to even out the betting odds on the bet.

""")



st.title("⚾ Correlation: Home Location vs. Total Runs")

# Build game-level dataset with HOME LOCATION determined by VH
game_data = []

for game in games:

    # total combined score
    total_runs = game["Final"].sum()

    # determine home team row using VH column
    home_row = game[game["VH"] == "H"].iloc[0]

    # use the home team name as home location proxy
    home_location = home_row["Team"]

    game_data.append({
        "Home Location": home_location,
        "Total Runs": total_runs
    })

totals_df = pd.DataFrame(game_data)

# Encode Home Location (one-hot)
encoded = pd.get_dummies(totals_df["Home Location"], prefix="LOC")

# Add total runs to data
corr_data = pd.concat([totals_df[["Total Runs"]], encoded], axis=1)

# Compute correlations
corr_matrix = corr_data.corr()

# Only show correlations of Total Runs vs home locations
corr_subset = corr_matrix.loc[["Total Runs"], encoded.columns]


# Plot Heatmap
st.subheader("🔥 Correlation Heatmap: Total Runs vs. Home Locations (Using VH)")

fig, ax = plt.subplots(figsize=(14, 4))
sns.heatmap(corr_subset, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
plt.title("Correlation of Home Location (Based on VH) vs Total Runs")
plt.yticks(rotation=0)

st.pyplot(fig)

# Interpretation
st.info("""
**Interpretation**
- Positive correlation → Higher total runs at this home location  
- Negative correlation → Lower total runs at that ballpark  
""")


st.title("⚾ Average Moneyline: Home vs. Away")

# Ensure Close line is numeric
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

# Split into home & away groups based on VH
home = df[df["VH"] == "H"]
away = df[df["VH"] == "V"]

# Compute average closing lines
avg_home_line = home["Close"].mean()
avg_away_line = away["Close"].mean()

# Display KPIs
st.subheader("📌 Key Metrics")
col1, col2 = st.columns(2)

col1.metric("Average Home Moneyline", f"{avg_home_line:.1f}")
col2.metric("Average Away Moneyline", f"{avg_away_line:.1f}")

# Bar Chart
st.subheader("📊 Comparison Chart")
fig, ax = plt.subplots(figsize=(6,4))

ax.bar(["Home", "Away"], [avg_home_line, avg_away_line], color=["blue", "orange"])
ax.set_ylabel("Average Closing Moneyline")
ax.set_title("Average Moneyline by Home/Away")

st.pyplot(fig)


# Raw values below
st.subheader("📄 Raw Values")
st.write(pd.DataFrame({
    "Team Type": ["Home", "Away"],
    "Average Closing Line": [avg_home_line, avg_away_line]
}))

# Interpretation
st.info("""
**Interpretation**
- Based on our findings, there is a bit of home field advantage in play when comparing moneyline odds.
- -60 represents that the home is more of a favorite throughout the matchups in 2021
- +34.3 represents that the away team is a little bit of an underdog due to positive moneyline.

""")


st.title("⚾ Monthly Total Runs (Using Custom Date Format)")

# ---------------------------------------------------------
# Convert custom date format
# Examples:
# "401"  -> month=4, day=01
# "927"  -> month=9, day=27
# "1012" -> month=10, day=12
# ---------------------------------------------------------
def parse_custom_date(val):
    s = str(int(val))  
    if len(s) == 3:    # MDD
        month = int(s[0])
        day = int(s[1:3])
    elif len(s) == 4:  # MMDD
        month = int(s[0:2])
        day = int(s[2:4])
    else:
        month, day = None, None
    return month, day

df["Month"], df["Day"] = zip(*df["Date"].apply(parse_custom_date))

df_sorted = df.sort_values(["Date", "Rot"])
games = []

for _, group in df_sorted.groupby("Date"):
    rows = group.sort_values("Rot")
    for i in range(0, len(rows), 2):
        if i + 1 < len(rows):
            games.append(rows.iloc[i:i+2])

# Build game totals + month
game_data = []

for game in games:
    total_runs = game["Final"].sum()
    month = game["Month"].iloc[0]

    game_data.append({
        "Month": month,
        "Total Runs": total_runs
    })

totals_df = pd.DataFrame(game_data)


# Compute monthly averages
monthly_avg = totals_df.groupby("Month")["Total Runs"].mean()

# Line Chart

st.subheader("📈 Average Total Runs by Month")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly_avg.index, monthly_avg.values, marker="o", linewidth=2)
ax.set_xlabel("Month")
ax.set_ylabel("Average Total Runs")
ax.set_title("Average Game Totals by Month (MLB 2021)")
ax.grid(True)

st.pyplot(fig)

# Raw Table
st.subheader("📄 Monthly Averages Table")
st.write(monthly_avg.reset_index())

# Interpretation
st.info("""
**Interpretation**
- Based on our findings, there is more runs during the summer, starting in June all the way
to September when the regular season ends
- The early months of April and May see a 1 point and 0.5 point decrease from the average during
the later months
- Probably cold weather and rested teams means there are less runs in a game during April and May
- Warm weather, team fatigue and teams hitting their stride would mean there's higher totals
in the later part of the season

""")
