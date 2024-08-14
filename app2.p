import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_plotly_events import plotly_events
import matplotlib.pyplot as plt
from pypalettes import load_cmap
import seaborn as sns

st.set_page_config(
    page_title="Dr.Ilan's Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="auto",
)
st.markdown(
    "<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True
)
cmap = load_cmap("Abbott")

hide_st_style = """
                <style>
                MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #ffffff;
        color: white;
    }
    .main {
        background-color: #ffffff;
        color: black;
    }
    .title {
        color: #1C445F;
        text-align: center;
    }
    .scrollable-graph {
        overflow-x: auto;
        overflow-y: hidden;
        max-width: 100%;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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


def filter_data(df, start_date, end_date, departments, doctors):
    filtered_df = df[(df["BillDate"] >= start_date) & (df["BillDate"] <= end_date)]
    if departments:
        filtered_df = filtered_df[filtered_df["OrderDepartment"].isin(departments)]
    if doctors:
        filtered_df = filtered_df[filtered_df["OrderDoctor"].isin(doctors)]
    return filtered_df


def get_kpi_metrics(df):
    current_date = pd.to_datetime(datetime.now().date())
    current_month = current_date.to_period("M")
    current_year = current_date.year
    last_year = current_year - 1

    ftd_df = df[df["BillDate"] == current_date]
    ftd_revenue = ftd_df["Net"].sum()

    mtd_df = df[df["BillDate"].dt.to_period("M") == current_month]
    mtd_revenue = mtd_df["Net"].sum()

    lysmtd_df = df[
        (df["BillDate"].dt.year == last_year)
        & (df["BillDate"].dt.month == current_date.month)
    ]
    lysmtd_revenue = lysmtd_df["Net"].sum()

    ytd_df = df[df["BillDate"].dt.year == current_year]
    ytd_revenue = ytd_df["Net"].sum()

    lytd_df = df[df["BillDate"].dt.year == last_year]
    lytd_revenue = lytd_df["Net"].sum()

    return {
        "FTD": ftd_revenue,
        "MTD": mtd_revenue,
        "LYSMTD": lysmtd_revenue,
        "YTD": ytd_revenue,
        "LYTD": lytd_revenue,
    }


def main():
    df = load_data()

    st.sidebar.selectbox(
        "Select a Dashboard",
        ["OPs Dashboard", "Revenue Dashboard", "P & L", "Pharmacy"],
    )

    date_range = st.sidebar.date_input(
        "Date range", [df["BillDate"].min(), df["BillDate"].max()]
    )
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    # Department selection
    selected_department = st.sidebar.selectbox(
        "Select Department", ["All"] + df["OrderDepartment"].unique().tolist()
    )

    # Doctor selection based on selected department
    if selected_department == "All":
        doctors = st.sidebar.multiselect("Select Doctors", df["OrderDoctor"].unique())
    else:
        doctors = st.sidebar.multiselect(
            "Select Doctors",
            df[df["OrderDepartment"] == selected_department]["OrderDoctor"].unique(),
        )

    h_left, h_middle, h_right = st.columns(3)
    with h_middle:
        st.header("Dr.Ilan's Dashboard")
    with h_left:
        st.subheader("date")
    with h_right:
        search_term = st.text_input("Search")
        filtered_df = filter_data(df, start_date, end_date, [selected_department] if selected_department != "All" else [], doctors)
        if search_term:
            filtered_df = filtered_df[
                filtered_df.apply(
                    lambda row: search_term.lower()
                    in row.astype(str).str.lower().to_string(),
                    axis=1,
                )
            ]

    default_freq = "D"

    left, right = st.columns([1, 1])
    with left:
        col1, col2, col3 = st.columns(3)

        if "freq" not in st.session_state:
            st.session_state.freq = default_freq

        if col1.button("Day"):
            st.session_state.freq = "D"
        if col2.button("Month"):
            st.session_state.freq = "M"
        if col3.button("Year"):
            st.session_state.freq = "Y"

        freq = st.session_state.freq
        if freq:
            df_resampled = filtered_df.resample(freq, on="BillDate").sum().reset_index()
            fig = px.line(
                df_resampled,
                x="BillDate",
                y="Net",
                title=f"Revenue ({freq})",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.markdown('<div class="scrollable-graph">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    kpi_metrics = get_kpi_metrics(filtered_df)

    with right:
        st.markdown(
            """
            <style>
            .kpi-container {
                padding: 20px;
                border-radius: 10px;
            }
            .kpi-metric {
                color: #000000;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                margin-bottom: 10px;
                border-left: 5px solid;
            }
            .ftd { border-left-color: #ff4d4f; } /* Red */
            .mtd { border-left-color: #40a9ff; } /* Blue */
            .lysmtd { border-left-color: #73d13d; } /* Green */
            .ytd { border-left-color: #faad14; } /* Yellow */
            .lytd { border-left-color: #9254de; } /* Purple */
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="kpi-metric ftd">FTD: ₹{:.2f} Cr</div>'.format(
                kpi_metrics["FTD"] / 1e7
            ),
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                '<div class="kpi-metric mtd">MTD: ₹{:.2f} Cr</div>'.format(
                    kpi_metrics["MTD"] / 1e7
                ),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                '<div class="kpi-metric lysmtd">LYSMTD: ₹{:.2f} Cr</div>'.format(
                    kpi_metrics["LYSMTD"] / 1e7
                ),
                unsafe_allow_html=True,
            )

        col3, col4 = st.columns(2)
        with col3:
            st.markdown(
                '<div class="kpi-metric ytd">YTD: ₹{:.2f} Cr</div>'.format(
                    kpi_metrics["YTD"] / 1e7
                ),
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                '<div class="kpi-metric lytd">LYTD: ₹{:.2f} Cr</div>'.format(
                    kpi_metrics["LYTD"] / 1e7
                ),
                unsafe_allow_html=True,
            )
        fig = px.pie(
            filtered_df, values="Net", names="VisitType", title="Segment", hole=0.5
        )
        fig.update_traces(text=filtered_df["VisitType"], textposition="inside")

        st.plotly_chart(fig, use_container_width=True)

    filtered_df.sort_values(by=["OrderDepartment", "OrderDoctor"], inplace=True)

    # Department wise revenue starts here
    col1, col2 = st.columns(2)

    with col1:
    
        department_revenue = (
            filtered_df.groupby("OrderDepartment")["Net"]
            .sum()
            .reset_index()
            .sort_values(by="Net")
        )
        fig1 = px.bar(
            department_revenue,
            x="Net",
            y="OrderDepartment",
            orientation="h",
            title="Department wise Revenue",
            color_discrete_sequence=["#0083B8"] * len(department_revenue),
            template="plotly_white",
        )
        fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))

        selected_points = plotly_events(fig1)
     # st.plotly_chart(fig1, use_container_width=True)

        selected_department_name = None
        if selected_points:
            selected_department_name = selected_points[0]["y"]

    with col2:
        st.subheader("Doctor wise Revenue")
        if selected_department_name:
            filtered_doctor_df = filtered_df[
                (filtered_df["OrderDoctor"] != "Prof. Mohamed Rela")
                & (filtered_df["OrderDepartment"] == selected_department_name)
            ]
            doctor_revenue = (
                filtered_doctor_df.groupby("OrderDoctor")["Net"]
                .sum()
                .reset_index()
                .sort_values(by="Net", ascending=False)
            )
            fig2 = px.line(
                doctor_revenue,
                x="OrderDoctor",
                y="Net",
                title=f"Doctor wise Revenue - {selected_department_name}",
                markers=True,
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=(dict(showgrid=False)),
            )
            st.markdown('<div class="scrollable-graph">', unsafe_allow_html=True)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.write("Click on a department bar to see relevant doctor revenue.")

    # service wise revenue
    service_summary = (
        filtered_df.groupby("ServiceName")
        .agg({"UHID": "nunique", "Net": "sum"})
        .reset_index()
        .rename(columns={"UHID": "Volume"})
    )
    fig5 = px.treemap(
        service_summary,
        path=["ServiceName"],
        values="Net",
        hover_data=["ServiceName"],
        color="ServiceName",
        title="Service-wise Revenue Summary",
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("In-Patient Volume")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.write("Total In-Patient Volume")


if __name__ == "__main__":
    main()
