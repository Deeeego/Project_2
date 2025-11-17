import streamlit as st

st.set_page_config(page_title="Future Work", layout="centered")

st.title("Future Work")

st.write("""
Here are several potential next steps to further develop and refine this dashboard:

1. **Add forecasting models**  
   Incorporate forecasting to predict future totals

2. **Add data enrichment**  
   Bring in weather data, park factors, injury reports, betting closing/opening splits, or umpire data to improve insights.

3. **Add interactive statistical tools**  
   Let users run correlation tests, filter by date ranges, or simulate outcomes with Monte Carlo modeling.
""")

st.subheader("🔄 Reflection: From Prototype to Final Build")

st.write("""
Several changes emerged between the initial Lab 4.3 paper prototype and the final dashboard:


- **Charts evolved with real data**  
  Early sketches were based on handwritten notes. Once I started using real data I changed some of the metrics to better suit the charts.

- **More Formatting of the data**
  I had to format the date and use the VH to get the home location

""")



