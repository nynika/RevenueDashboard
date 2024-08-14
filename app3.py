import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="Dr.Ilan's Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="auto",
)


@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "PRmayjun.csv",
            encoding="utf-8",
            dtype={"BillDate": "object"},
            parse_dates=["BillDate"],
            dayfirst=True,
            date_parser=lambda x: pd.to_datetime(x, dayfirst=True),
        )
        df["BillDate"] = pd.to_datetime(df["BillDate"], format="%d/%m/%Y")
    except UnicodeDecodeError:
        df = pd.read_csv(
            "PRmayjun.csv",
            encoding="latin1",
            dtype={"BillDate": "object"},
            parse_dates=["BillDate"],
            dayfirst=True,
            date_parser=lambda x: pd.to_datetime(x, dayfirst=True),
        )
        df["BillDate"] = pd.to_datetime(df["BillDate"], format="%d/%m/%Y")
    return df


# Load Data
df = load_data()

# Sidebar
leftcol, midcol, rightcol = st.columns(3)

with leftcol:
    date_range = st.date_input(
        "Date range", [df["BillDate"].min(), df["BillDate"].max()]
    )
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

with midcol:
    departments = st.multiselect(
        "Select Departments", ["All"] + df["OrderDepartment"].unique().tolist()
    )

with rightcol:
    if "All" in departments or not departments:
        doctors = st.multiselect(
            "Select Doctors", ["All"] + df["OrderDoctor"].unique().tolist()
        )
    else:
        doctors = st.multiselect(
            "Select Doctors",
            ["All"]
            + df[df["OrderDepartment"].isin(departments)]["OrderDoctor"]
            .unique()
            .tolist(),
        )

# Filter Data
filtered_df = df[(df["BillDate"] >= start_date) & (df["BillDate"] <= end_date)]

if "All" not in departments:
    filtered_df = filtered_df[filtered_df["OrderDepartment"].isin(departments)]

if "All" not in doctors:
    filtered_df = filtered_df[filtered_df["OrderDoctor"].isin(doctors)]

# Header and Search
col1, col2 = st.columns([1, 2])
with col1:
    st.header("Dr.Ilan's Dashboard")
with col2:
    search_term = st.text_input("Search")
