import pandas as pd  # pip install pandas openpyxlsteamlit
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit


# Set page config
st.set_page_config(page_title="Revenue Dashboard", page_icon=":bar_chart:", layout="wide")

# Read Excel
@st.cache
def get_data_from_excel():
    df = pd.read_excel(
        io="DoctorsRevenue.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        usecols="B:J",
        nrows=1000,
    )
    return df

df = get_data_from_excel()

# Sidebar
st.sidebar.header("Please Filter Here:")
department = st.sidebar.selectbox(
    "Select the OrderDepartment:",
    options=df["OrderDepartment"].unique(),
    index=0
)

# Filter doctors based on selected department
doctors_options = df[df["OrderDepartment"] == department]["Doctor_Name"].unique()
selected_doctors = st.sidebar.multiselect(
    "Select the Doctor(s):",
    options=doctors_options,
    default=doctors_options
)

# Filter data based on selections
df_selection = df[
    (df["OrderDepartment"] == department) &
    (df["Doctor_Name"].isin(selected_doctors))
]

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()  # This will halt the app from further execution.

# ---- MAINPAGE ----
st.title(":bar_chart: Revenue Dashboard")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Total"].sum())
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Revenue:")
    st.subheader(f"Rup {total_sales:,}")
with right_column:
    st.subheader("Average Revenue:")
    st.subheader(f"Rup {average_sale_by_transaction}")

st.markdown("---")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection.groupby(by=["Product line"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Revenue by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# Group by Doctor_Name and Product line and sum the total sales
sales_by_doctor_product_line = df_selection.groupby(by=["Doctor_Name", "Product line"])[["Total"]].sum().reset_index()

# Create bar chart with subplots for each doctor
fig_doctor_product_sales = px.bar(
    sales_by_doctor_product_line,
    x="Product line",
    y="Total",
    facet_col="Doctor_Name",
    title="<b>Revenue by Product Line for Each Doctor</b>",
    color="Product line",
    template="plotly_white",
)

fig_doctor_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

st.plotly_chart(fig_doctor_product_sales, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---- SEARCH SECTION ----
st.sidebar.header("Search Section:")
search_term = st.sidebar.text_input("Enter Search Item:")
search_button_clicked = st.sidebar.button("Search")

# Check if the search button is clicked
if search_button_clicked:
    if search_term:
        df_selection = df[df["Doctor_Name"].str.contains(search_term, case=False, na=False)]

        # Display the updated data
        st.write("Filtered Data:")
        st.write(df_selection)
    else:
        st.warning("Please enter a search term.")

# Limit the number of departments to display
departments_to_display = df_selection["OrderDepartment"].unique()[:10]  # Display only the first 5 departments

# Filter the data to include only the selected departments
df_filtered = df_selection[df_selection["OrderDepartment"].isin(departments_to_display)]

# Group by OrderDepartment, Doctor_Name, and month and sum the total sales
sales_by_department_doctor_month = df_filtered.groupby(by=["OrderDepartment", "Doctor_Name", "month"])[["Total"]].sum().reset_index()

# Create a line chart for each doctor's revenue over months for each department
fig_department_doctor_monthly_sales = px.line(
    sales_by_department_doctor_month,
    x="month",
    y="Total",
    color="Doctor_Name",
    facet_col="OrderDepartment",
    facet_col_wrap=2,  # Adjust the number of columns as needed
    title="<b>Revenue by Doctor over Months for Each OrderDepartment</b>",
    template="plotly_white",
)

fig_department_doctor_monthly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

st.plotly_chart(fig_department_doctor_monthly_sales, use_container_width=True)




#....................another type of code :..................................................#

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Revenue Dashboard", page_icon=":bar_chart:", layout="wide")

# Read Excel
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="Revenue.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:K",
        nrows=1000,
    )
    return df

df = get_data_from_excel()


#............................................................#

# Search function
def search(query):
    matches = df[df['OrderDepartment'].str.contains(query, case=False) |
                  df['OrderDoctor'].str.contains(query, case=False)]
    return matches

# Streamlit app
st.title("Search Data You Want")

# Search input
query = st.text_input("Enter department name or doctor name:")
search_button = st.button("Search")



# Perform search when button is clicked
if search_button:
    if query:
        results = search(query)
        if not results.empty:
            st.write("Search Results:")
            st.write(results)

            # Concatenate doctor names with department names
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

        
        #.......................................................................#

# Sidebar
st.sidebar.header("Please Filter Here:")
order_department = st.sidebar.selectbox(
    "Select the Department:",
    options=df["OrderDepartment"].unique(),
    index=0
)


# Filter data based on selected department
df_selection = df[df["OrderDepartment"] == order_department]

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()

# Display filtered doctors vertically in the sidebar
st.sidebar.subheader("Filtered Doctors:")
for doctor in df_selection["OrderDoctor"].unique():
    st.sidebar.write(doctor)

# Calculate net revenue for each doctor
df_doctors = df_selection.groupby("OrderDoctor")[["Net"]].sum().reset_index()

# Plotting
fig_doctors = px.bar(df_doctors, x='OrderDoctor', y='Net',
                     labels={'Net': 'Net Revenue'},
                     title='Net Revenue for Doctors',
                     color='Net',
                     color_continuous_scale='RdBu')
fig_doctors.update_layout(xaxis_title='Doctor', yaxis_title='Net Revenue')

st.plotly_chart(fig_doctors)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()

# ---- MAINPAGE ----
st.title(":bar_chart: Revenue Dashboard")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Net"].sum())
average_sale_by_transaction = round(df_selection["Net"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Net Revenue:")
    st.subheader(f"Rup {total_sales:,}")

with right_column:
    st.subheader("Average Revenue :")
    st.subheader(f"Rup {average_sale_by_transaction}")

st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = df_selection.groupby(by=["ServiceGroup"])[["Net"]].sum().sort_values(by="Net")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Net",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Service Group</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY DOCTOR [HORIZONTAL BAR CHART]
sales_by_doctor = df_selection.groupby(by=["OrderDoctor"])[["Net"]].sum().sort_values(by="Net", ascending=False)
fig_doctor_sales = px.bar(
    sales_by_doctor,
    x="Net",
    y=sales_by_doctor.index,
    orientation="h",
    title="<b>Sales by Doctor</b>",
    color_discrete_sequence=["#FFA07A"] * len(sales_by_doctor),
    template="plotly_white",
)
fig_doctor_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False))
)

# Convert index to datetime if it's not already
df_selection.index = pd.to_datetime(df_selection.index)

# Group by month
sales_by_month = df_selection.groupby(by=df_selection.index.to_period('M'))[["Net"]].sum()

# Plotting
fig_monthly_sales = px.bar(
    sales_by_month,
    x=sales_by_month.index.astype(str),  # Convert the index to string for proper labeling
    y="Net",
    title="<b>Sales by Month</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_month),
    template="plotly_white",
)

fig_monthly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_monthly_sales, use_container_width=True)
middle_column.plotly_chart(fig_product_sales, use_container_width=True)
right_column.plotly_chart(fig_doctor_sales, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

#...............................................#












