import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Load the dataset
data = pd.read_excel("C:\\Users\\amirb\\Desktop\\Personal\\titus_dashboard\\titus_data.xlsx", sheet_name="Data")

# Set the first row as header if necessary
data.columns = data.iloc[0]  # Set the first row as the header
data = data[1:]  # Drop the first row
data.reset_index(drop=True, inplace=True)

# Convert DATE column to datetime
data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')

# Convert numeric columns if necessary
numeric_columns = ['Profit', 'Sales total', 'Cost total', 'WEIGHT', 'CBM', 'CTNS']
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Determine the minimum and maximum dates in the dataset
min_date = data['DATE'].min()
max_date = data['DATE'].max()



# Load the logo
logo_path = "C:\\Users\\amirb\\Desktop\\Personal\\titus\\titus\\titus_logo.jpg"
logo = Image.open(logo_path)


# Sidebar with the logo and menu options
with st.sidebar:
    st.title("Titus Logistics")
    st.image(logo, width=100)  # Adjust the width to make the logo smaller
    st.markdown("---")  # Add a line separator

# Sidebar Filters
st.sidebar.header("Filters")

# Date Range Filter with Preset Options
with st.sidebar.expander("Date Filters"):
    preset_period = st.radio(
        "Quick Preset Periods",
        options=["Custom", "Last 7 Days", "Last 30 Days", "Year-to-Date"],
        index=0
    )
    
    if preset_period == "Custom":
        date_range = st.date_input(
            "Custom Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    elif preset_period == "Last 7 Days":
        date_range = (max_date - pd.Timedelta(days=7), max_date)
    elif preset_period == "Last 30 Days":
        date_range = (max_date - pd.Timedelta(days=30), max_date)
    elif preset_period == "Year-to-Date":
        date_range = (pd.Timestamp(f"{max_date.year}-01-01"), max_date)

# Destination Filter
with st.sidebar.expander("Destination Filters"):
    destination = st.multiselect("Select Destination", options=data['Destination'].unique())

# Shipment Filters
with st.sidebar.expander("Shipment Filters"):
    shipment_number = st.multiselect("Select Shipment Number", options=data['Shipment NO.'].unique())
    warehouse = st.multiselect("Select Loading Warehouse", options=data['Loading warehouse'].unique())

# Client Filters
with st.sidebar.expander("Client Filters"):
    client_code = st.multiselect("Select Client Code", options=data['Client code'].unique())
    client_level = st.multiselect("Select Client Level", options=data['Client level'].unique())

# Sales and Goods Filters
with st.sidebar.expander("Sales and Goods Filters"):
    salesperson = st.multiselect("Select Salesperson", options=data['Sales'].unique())
    mark = st.multiselect("Select Mark (Label)", options=data['Mark'].unique())
    category1 = st.multiselect("Select Main Category", options=data['Category1'].unique())
    category2 = st.multiselect("Select Subcategory", options=data['Category2'].unique())
    description = st.multiselect("Select Description", options=data['Description in E'].unique())
    goods_type = st.multiselect("Select Goods Type", options=data['goods tpye'].unique())

# Transport Type Filter
with st.sidebar.expander("Transport Filters"):
    transport_type = st.multiselect("Select Transport Type", options=data['Type'].unique())

# Range Filters for Profit, Weight, and CBM
with st.sidebar.expander("Range Filters"):
    profit_range = st.slider(
        "Profit Range",
        min_value=int(data['Profit'].min()),
        max_value=int(data['Profit'].max()),
        value=(int(data['Profit'].min()), int(data['Profit'].max()))
    )
    weight_range = st.slider(
        "Weight Range",
        min_value=int(data['WEIGHT'].min()),
        max_value=int(data['WEIGHT'].max()),
        value=(int(data['WEIGHT'].min()), int(data['WEIGHT'].max()))
    )
    cbm_range = st.slider(
        "CBM Range",
        min_value=float(data['CBM'].min()),
        max_value=float(data['CBM'].max()),
        value=(float(data['CBM'].min()), float(data['CBM'].max()))
    )

# Filter Button with Record Count Feedback
if st.sidebar.button("Filter Data"):
    # Apply all filters
    filtered_data = data.copy()

    # Apply Date Range Filter
    if date_range:
        filtered_data = filtered_data[(filtered_data['DATE'] >= pd.to_datetime(date_range[0])) &
                                      (filtered_data['DATE'] <= pd.to_datetime(date_range[1]))]

    # Apply other filters
    if destination:
        filtered_data = filtered_data[filtered_data['Destination'].isin(destination)]
    if shipment_number:
        filtered_data = filtered_data[filtered_data['Shipment NO.'].isin(shipment_number)]
    if client_code:
        filtered_data = filtered_data[filtered_data['Client code'].isin(client_code)]
    if client_level:
        filtered_data = filtered_data[filtered_data['Client level'].isin(client_level)]
    if salesperson:
        filtered_data = filtered_data[filtered_data['Sales'].isin(salesperson)]
    if mark:
        filtered_data = filtered_data[filtered_data['Mark'].isin(mark)]
    if category1:
        filtered_data = filtered_data[filtered_data['Category1'].isin(category1)]
    if category2:
        filtered_data = filtered_data[filtered_data['Category2'].isin(category2)]
    if description:
        filtered_data = filtered_data[filtered_data['Description in E'].isin(description)]
    if goods_type:
        filtered_data = filtered_data[filtered_data['goods tpye'].isin(goods_type)]
    if warehouse:
        filtered_data = filtered_data[filtered_data['Loading warehouse'].isin(warehouse)]
    if transport_type:
        filtered_data = filtered_data[filtered_data['Type'].isin(transport_type)]
    filtered_data = filtered_data[(filtered_data['Profit'] >= profit_range[0]) &
                                  (filtered_data['Profit'] <= profit_range[1])]
    filtered_data = filtered_data[(filtered_data['WEIGHT'] >= weight_range[0]) &
                                  (filtered_data['WEIGHT'] <= weight_range[1])]
    filtered_data = filtered_data[(filtered_data['CBM'] >= cbm_range[0]) &
                                  (filtered_data['CBM'] <= cbm_range[1])]
    
    st.success(f"Filtered Data: {len(filtered_data)} records found!")
else:
    filtered_data = data.copy()
    st.info("No filters applied. Showing all data.")

# Display Filtered Data for Context
st.subheader("Filtered Data")
st.dataframe(filtered_data)


# Charts Section
st.header("Charts")

# Profit by Destination (Bar Chart)
profit_by_dest = filtered_data.groupby("Destination")["Profit"].sum().reset_index()
fig_bar = px.bar(profit_by_dest, x="Destination", y="Profit", title="Profit by Destination")
st.plotly_chart(fig_bar, use_container_width=True)

# Sales Trend Over Time (Line Chart)
if 'DATE' in filtered_data.columns:
    sales_trend = filtered_data.groupby("DATE")["Sales total"].sum().reset_index()
    fig_line = px.line(sales_trend, x="DATE", y="Sales total", title="Sales Trend Over Time")
    st.plotly_chart(fig_line, use_container_width=True)

# Goods Type Distribution (Pie Chart)
goods_type_dist = filtered_data["goods tpye"].value_counts().reset_index()
goods_type_dist.columns = ['Goods Type', 'Count']
fig_pie = px.pie(goods_type_dist, names="Goods Type", values="Count", title="Goods Type Distribution")
st.plotly_chart(fig_pie, use_container_width=True)

# Profit vs. Weight (Scatter Plot)
fig_scatter = px.scatter(filtered_data, x="WEIGHT", y="Profit", size="Profit", color="Destination",
                         title="Profit vs Weight", hover_data=["Description in E"])
st.plotly_chart(fig_scatter, use_container_width=True)

# Data Table
st.subheader("Filtered Data")
st.dataframe(filtered_data)

# Download Filtered Data
st.sidebar.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_shipping_data.csv",
    mime="text/csv"
)