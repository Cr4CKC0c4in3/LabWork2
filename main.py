import os
import urllib.request
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# NOAA Data
NOAA_TO_UA = {1: "Cherkasy", 2: "Chernihiv", 3: "Chernivtsi", 4: "Chernivtsi", 5: "Dnipropetrovs'k", 6: "Donets'k",
    7: "Ivano-Frankivs'k", 8: "Kharkiv`", 9: "Kherson", 10: "Khmel'nyts'kyy", 11: "Kyiv", 12: "Kyiv City",
    13: "Kirovohrad", 14: "Luhans'k", 15: "L'viv", 16: "Mykolayiv", 17: "Odessa", 18: "Poltava", 19: "Rivne",
    20: "Sevastopol", 21: "Sumy", 22: "Ternopil", 23: "Transcarpathia", 24: "Vinnytsya", 25: "Volyn",
    26: "Zaporizhzhya", 27: "Zhytomyr"}

# Data Loading
DATA_DIR = "vhi_data"
os.makedirs(DATA_DIR, exist_ok=True)

@st.cache_data
def load_data(directory):
    all_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]
    df_list = []
    for file in all_files:
        province = file.split("_")[2]
        df = pd.read_csv(file, index_col=False, header=1)
        df.columns = ["year", "week", "SMN", "SMT", "VCI", "TCI", "VHI"]
        df["region"] = province
        df = df[pd.to_numeric(df["VHI"], errors='coerce').notna()]
        df = df[pd.to_numeric(df['year'], errors='coerce').notna()]
        df['year'] = df['year'].astype(int)
        df['week'] = df['week'].astype(int)
        for key, val in NOAA_TO_UA.items():
            if val == province:
                df["id"] = key  
                break
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)

df = load_data(DATA_DIR)

# Interface
st.sidebar.header("Filters")
indicator = st.sidebar.selectbox("Select Indicator", ["VCI", "TCI", "VHI"], index=2)
region = st.sidebar.selectbox("Select Region", ["All"] + list(NOAA_TO_UA.values()))
year_range = st.sidebar.slider("Year Range", 1982, 2024, (2010, 2020))
week_range = st.sidebar.slider("Week Range", 1, 52, (1, 10))

sort_asc = st.sidebar.checkbox("Sort Ascending")
sort_desc = st.sidebar.checkbox("Sort Descending")

if st.sidebar.button("Reset Filters"):
    region = "All"
    year_range = (1982, 2024)
    week_range = (1, 52)
    sort_asc = False
    sort_desc = False

# Data Filtering
filtered_df = df[(df["year"].between(year_range[0], year_range[1])) & (df["week"].between(week_range[0], week_range[1]))]
if region != "All":
    filtered_df = filtered_df[filtered_df["region"] == region]
if sort_asc and not sort_desc:
    filtered_df = filtered_df.sort_values(by=[indicator])
elif sort_desc and not sort_asc:
    filtered_df = filtered_df.sort_values(by=[indicator], ascending=False)

# Tabs
tab1, tab2, tab3 = st.tabs(["Table", "Graph", "Region Comparison"])

with tab1:
    st.dataframe(filtered_df[["year", "week", "region", indicator]])

with tab2:
    fig = px.line(filtered_df, x="week", y=indicator, color="year", title=f"{indicator} by Week")
    st.plotly_chart(fig)

with tab3:
    comparison_df = df[(df["year"].between(year_range[0], year_range[1])) & (df["week"].between(week_range[0], week_range[1]))]
    fig = px.box(comparison_df, x="region", y=indicator, title=f"Comparison of {indicator} Across Regions")
    st.plotly_chart(fig)
