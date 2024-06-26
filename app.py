
import pandas as pd  # pip install pandas openpyxlsteamlit  
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide",)

# Read Excel
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="Revenue.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:K",
        nrows=558825,
    )
    df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce') 
    return df
df = get_data_from_excel()                                            

st.sidebar.image("./images/relalogo.jpg", width=5, use_column_width=True)


# Search  
st.sidebar.header("Search by Department or Doctor Name")
def search(query):
    matches = df[df['OrderDepartment'].str.contains(query, case=False) |
                 df['OrderDoctor'].str.contains(query, case=False)]
    return matches

query = st.sidebar.text_input("Enter department name or doctor name:")
search_button = st.sidebar.button("Search")

if search_button:
    if query:
        results = search(query)
        if not results.empty:
            results['Doctor_with_Department'] = results['OrderDoctor'] + ' (' + results['OrderDepartment'] + ')'
            fig_doctors = px.bar(results, x='Doctor_with_Department', y='Net',
                                 labels={'Net': 'Net Revenue'},
                                 title='Net Revenue for Doctors by Department',
                                 color='Net',
                                 color_continuous_scale='RdBu')
            fig_doctors.update_layout(xaxis_title='Doctor', yaxis_title='Net Revenue')
            st.plotly_chart(fig_doctors)
        else:
            st.write("No matching data found.")
    else:
        st.write("Please enter a search query.")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 0.5rem;} 
            .css-18e3th9 {padding-top: 0rem;} 
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# Sidebar filters
st.sidebar.header("Please Filter Here:")
order_department = st.sidebar.selectbox("Select the Department:",options=df["OrderDepartment"].unique(),index=0)

# Get doctors based on the selected department
doctors_options = df[df["OrderDepartment"] == order_department]["OrderDoctor"].unique()

# Here we remove 'default=doctors_options' to avoid pre-selecting all doctors
selected_doctors = st.sidebar.multiselect("Select the Doctor(s):",options=doctors_options)

# Filter data based on selected department and doctors
df_selection = df[(df["OrderDepartment"] == order_department) & (df["OrderDoctor"].isin(selected_doctors))]

# Display a warning and stop if no data is available
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()


# Display KPIs
st.title(":bar_chart: Revenue Dashboard")
st.markdown("##")
total_sales = int(df_selection["Net"].sum())
st.subheader(f"Total Revenue: INR {total_sales:,}")

# Date range filter and data preparation
min_date, max_date = st.sidebar.date_input("Select Date Range:", value=[df_selection['OrderDate'].min(), df_selection['OrderDate'].max()])
filtered_data = df_selection[(df_selection['OrderDate'] >= pd.to_datetime(min_date)) & (df_selection['OrderDate'] <= pd.to_datetime(max_date))]

# Monthly revenue calculation
revenue_by_month_doctor = filtered_data.groupby([pd.Grouper(key='OrderDate', freq='M'), 'OrderDoctor'])['Net'].sum().unstack(fill_value=0)

# Plotting bar chart with values at the bottom of each bar and larger text size
fig_revenue_by_month_doctor = go.Figure()
colors = px.colors.qualitative.Plotly
for i, doctor in enumerate(revenue_by_month_doctor.columns):
    fig_revenue_by_month_doctor.add_trace(go.Bar(
        x=revenue_by_month_doctor.index.strftime('%y-%m'),  # Date format
        y=revenue_by_month_doctor[doctor],
        name=doctor,
        marker_color=colors[i % len(colors)],
        text=revenue_by_month_doctor[doctor], 
        textposition='outside',  
        textfont=dict(family="Arial", size=14, color="black"),  
    ))


fig_revenue_by_month_doctor.update_layout(
    barmode='stack',
    title=f"<b>Net Revenue for {order_department} by Month</b>",
    xaxis=dict(title="Month", tickangle=-45),
    yaxis=dict(title="Total Net Revenue"),
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    font=dict(color="black", size=12),
    margin=dict(l=10, r=10, t=30, b=20),
)


st.plotly_chart(fig_revenue_by_month_doctor, use_container_width=True)

# Calculating net revenue for each doctor
df_doctors = df_selection.groupby("OrderDoctor")[["Net"]].sum().reset_index()

#------------------------------------------------------------------------------------------------------------------------------------#
# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection.groupby(by=["ServiceGroup"])[["Net"]].sum().sort_values(by="Net")
fig_product_sales = px.bar(
    sales_by_product_line, 
    x="Net",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Revenue by Service Group</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
#----------------------------------------------------------------------------------------------------------------------------------#

# SALES BY DOCTOR [HORIZONTAL BAR CHART]
sales_by_doctor = df_selection.groupby(by=["OrderDoctor"])[["Net"]].sum().sort_values(by="Net", ascending=False)
fig_doctor_sales = px.bar(
    sales_by_doctor,
    x="Net",
    y=sales_by_doctor.index,
    orientation="h",
    title="<b>Revenue by Doctor</b>",
    color_discrete_sequence=["#FFA07A"] * len(sales_by_doctor),
    template="plotly_white",
)

fig_doctor_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False))
)

#----------------------------------------------------------------------------------------------------------------------------------#
middle_column, right_column = st.columns(2)
middle_column.plotly_chart(fig_product_sales, use_container_width=True)
right_column.plotly_chart(fig_doctor_sales, use_container_width=True)
#........................................................................................#

# Plotting net revenue for doctors
fig_doctors = px.bar(df_doctors, x='OrderDoctor', y='Net',
                     labels={'Net': 'Net Revenue'},
                     title='Net Revenue for Doctors',
                     color='Net',
                     color_continuous_scale='RdBu')

fig_doctors.update_layout(xaxis_title='Doctor', yaxis_title='Net Revenue')

st.plotly_chart(fig_doctors, use_container_width=True)

#........................................................................................................#

       
#....................................................................................................................#


# Button to trigger pie chart generation
generate_pie_chart_button = st.button("Generate Last Three Months Revenue")

# Perform actions when the button is clicked
if generate_pie_chart_button:
    # Calculate the date range for the last three months
    today = datetime.today()
    three_months_ago = today - timedelta(days=90)

    # Filter data for the last three months
    last_three_months_data = df[df['OrderDate'] >= three_months_ago]

    # Group data by department and calculate total revenue for each department
    revenue_by_department = last_three_months_data.groupby('OrderDepartment')['Net'].sum().reset_index()

    # Plotting pie chart for revenue distribution across departments
    fig_department_revenue = px.pie(
        revenue_by_department,
        values='Net',
        names='OrderDepartment',
        title='Revenue Distribution Across Departments (Last 3 Months)',
        hole=0.3,  # Hole in the middle to make it a donut chart
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    # Display the pie chart
    st.plotly_chart(fig_department_revenue, use_container_width=True)


#----------------------------------------------------------------------------------------------------------------------------#
# Convert 'OrderDate' to datetime
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Add Year column
df['Year'] = df['OrderDate'].dt.year

# Sidebar
st.sidebar.header("Please Filter Here:")
available_years = sorted(df["Year"].unique())  # Get sorted unique years
selected_years = st.sidebar.multiselect(
    "Select Year(s):",
    options=available_years,
    default=available_years  # Set default to all available years
)

# Filter data based on selected years
df_selection = df[df["Year"].isin(selected_years)]

# Calculate total revenue for each selected year
revenue_by_year = df_selection.groupby('Year')['Net'].sum().reset_index()

# Plotting histogram chart
fig_histogram = px.bar(revenue_by_year, x='Year', y='Net', title='Total Revenue by Year', labels={'Net': 'Total Revenue'})
fig_histogram.update_layout(xaxis_title='Year', yaxis_title='Total Revenue')

# Plotting line chart
fig_line = px.line(revenue_by_year, x='Year', y='Net', title='Revenue Trend Over Years', labels={'Net': 'Total Revenue'})
fig_line.update_layout(xaxis_title='Year', yaxis_title='Total Revenue')

# Overlay line plot on histogram
for data in fig_line.data:
    fig_histogram.add_trace(data)

# Display the overlaid chart
st.plotly_chart(fig_histogram, use_container_width=True)
#----------------------------------------------------------------------------------------------------------------------#

df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Extract month from 'OrderDate'
df['Month'] = df['OrderDate'].dt.month

# Sidebar
st.sidebar.header("Please Filter here:")
available_months = sorted(df['Month'].unique())
selected_months = st.sidebar.multiselect(
    "Select the month(s):",
    options=available_months,
    default=available_months
)

df_selection = df[df['Month'].isin(selected_months)]

# Group by order date and calculate total net revenue for each day
revenue_by_day = df_selection.groupby('OrderDate')['Net'].sum().reset_index()

# Plotting line chart for revenue by date
fig_line = px.line(
    revenue_by_day,
    x='OrderDate',
    y='Net',
    title="Daily Revenue",
    labels={'OrderDate': 'Date', 'Net': 'Revenue'}
)

revenue_by_month = df_selection.groupby('Month')['Net'].sum().reset_index()

# Plotting bar chart for total revenue by month
fig_bar = px.bar(
    revenue_by_month,
    x='Month',
    y='Net',
    title="Total Revenue by Month",
    labels={'Month': 'Month', 'Net': 'Total Revenue'}
)

# Update layout of bar chart
fig_bar.update_layout(
    xaxis_title='Month',
    yaxis_title='Total Revenue',
    showlegend=False
)

# Display both charts
st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_line, use_container_width=True)
