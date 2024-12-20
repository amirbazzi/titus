import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
data = pd.read_excel("C:\\Users\\amirb\\Desktop\\Personal\\titus_dashboard\\titus_data.xlsx", sheet_name="Data")
data.columns = data.iloc[0]  # Set first row as column names
data = data[1:]  # Drop first row
data.reset_index(drop=True, inplace=True)
data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')

# Numeric columns conversion
numeric_columns = ['Profit', 'Sales total', 'Cost total', 'WEIGHT', 'CBM', 'CTNS']
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Min/max dates
min_date = data['DATE'].min()
max_date = data['DATE'].max()

# Sidebar Filters
st.sidebar.header("Filters")

# Date Range Filter
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Quick Preset Periods (Optional, can implement further)
preset_period = st.sidebar.radio("Quick Date Periods", ["Last 7 Days", "Last 30 Days", "Year-to-Date", "Custom"])

# Destination Filter
destination = st.sidebar.multiselect("Select Destination", options=data['Destination'].unique())

# Client Filters
client_code = st.sidebar.multiselect("Select Client Code", options=data['Client code'].unique())
client_level = st.sidebar.multiselect("Select Client Level", options=data['Client level'].unique())

# Salesperson Filter
salesperson = st.sidebar.multiselect("Select Salesperson", options=data['Sales'].unique())

# Goods Type Filters
category1 = st.sidebar.multiselect("Select Main Category", options=data['Category1'].unique())
category2 = st.sidebar.multiselect("Select Subcategory", options=data['Category2'].unique())
goods_type = st.sidebar.multiselect("Select Goods Type", options=data['goods tpye'].unique())

# Transport Type Filter
transport_type = st.sidebar.multiselect("Select Transport Type", options=data['Type'].unique())

# Warehouse Location Filter
warehouse = st.sidebar.multiselect("Select Loading Warehouse", options=data['Loading warehouse'].unique())

# Profit Range Filter
profit_range = st.sidebar.slider("Profit Range", min_value=int(data['Profit'].min()), max_value=int(data['Profit'].max()),
                                  value=(int(data['Profit'].min()), int(data['Profit'].max())))

# Weight and CBM Ranges
weight_range = st.sidebar.slider("Weight Range", min_value=int(data['WEIGHT'].min()), max_value=int(data['WEIGHT'].max()),
                                  value=(int(data['WEIGHT'].min()), int(data['WEIGHT'].max())))
cbm_range = st.sidebar.slider("CBM Range", min_value=float(data['CBM'].min()), max_value=float(data['CBM'].max()),
                               value=(float(data['CBM'].min()), float(data['CBM'].max())))

# Filter Button
if st.sidebar.button("Filter Data"):
    filtered_data = data.copy()
    if date_range:
        filtered_data = filtered_data[(filtered_data['DATE'] >= pd.to_datetime(date_range[0])) &
                                      (filtered_data['DATE'] <= pd.to_datetime(date_range[1]))]
    if destination:
        filtered_data = filtered_data[filtered_data['Destination'].isin(destination)]
    if client_code:
        filtered_data = filtered_data[filtered_data['Client code'].isin(client_code)]
    if client_level:
        filtered_data = filtered_data[filtered_data['Client level'].isin(client_level)]
    if salesperson:
        filtered_data = filtered_data[filtered_data['Sales'].isin(salesperson)]
    if category1:
        filtered_data = filtered_data[filtered_data['Category1'].isin(category1)]
    if category2:
        filtered_data = filtered_data[filtered_data['Category2'].isin(category2)]
    if goods_type:
        filtered_data = filtered_data[filtered_data['goods tpye'].isin(goods_type)]
    if transport_type:
        filtered_data = filtered_data[filtered_data['Type'].isin(transport_type)]
    if warehouse:
        filtered_data = filtered_data[filtered_data['Loading warehouse'].isin(warehouse)]
    filtered_data = filtered_data[(filtered_data['Profit'] >= profit_range[0]) &
                                  (filtered_data['Profit'] <= profit_range[1])]
    filtered_data = filtered_data[(filtered_data['WEIGHT'] >= weight_range[0]) &
                                  (filtered_data['WEIGHT'] <= weight_range[1])]
    filtered_data = filtered_data[(filtered_data['CBM'] >= cbm_range[0]) &
                                  (filtered_data['CBM'] <= cbm_range[1])]
else:
    filtered_data = data.copy()

# Dashboard Sections
st.header("Shipment Overview")
kpi1, kpi2 = st.columns(2)
kpi1.metric(label="Total Shipments", value=len(filtered_data))
kpi2.metric(label="Total Profit", value=f"${filtered_data['Profit'].sum():,.2f}")

st.subheader("Profit Analysis")
fig1 = px.bar(filtered_data, x="Category1", y="Profit", color="Destination", title="Profit by Category")
fig2 = px.line(filtered_data, x="DATE", y="Profit", title="Profit Margin Over Time")
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Sales and Cost Analysis")
fig3 = px.line(filtered_data, x="DATE", y=["Sales total", "Cost total"], title="Sales vs. Cost Comparison")
fig4 = px.bar(filtered_data, x="Description in E", y="Sales total", title="Top Products by Sales")
st.plotly_chart(fig3, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Category Analysis")
fig5 = px.pie(filtered_data, names="Category1", values="Profit", title="Category Distribution")
fig6 = px.bar(filtered_data, x="Category2", y="Profit", title="Category Profitability")
st.plotly_chart(fig5, use_container_width=True)
st.plotly_chart(fig6, use_container_width=True)

# Data Table
st.subheader("Filtered Data")
st.dataframe(filtered_data)
