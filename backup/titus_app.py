import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Load the dataset
data = pd.read_excel("C:\\Users\\amirb\\Desktop\\Personal\\titus_dashboard\\titus_data.xlsx", sheet_name="Data")
data.columns = data.iloc[0]  # Set first row as column names
data = data[1:]  # Drop first row
data.reset_index(drop=True, inplace=True)
data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')

# Convert numeric columns
numeric_columns = ['Profit', 'Sales total', 'Cost total', 'WEIGHT', 'CBM', 'CTNS']
for col in numeric_columns:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Min/max dates
min_date = data['DATE'].min()
max_date = data['DATE'].max()

# Load logo
logo_path = "C:\\Users\\amirb\\Desktop\\Personal\\titus\\titus\\titus_logo.jpg"
logo = Image.open(logo_path)

# Sidebar Filters
with st.sidebar:
    st.title("Titus Logistics")
    st.image(logo, width=100)
    st.markdown("---")

    # Date Range Filter
    with st.expander("Date Filters"):
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

    # Other Filters
    destination = st.multiselect("Select Destination", options=data['Destination'].unique())
    shipment_number = st.multiselect("Select Shipment Number", options=data['Shipment NO.'].unique())
    client_code = st.multiselect("Select Client Code", options=data['Client code'].unique())
    client_level = st.multiselect("Select Client Level", options=data['Client level'].unique())
    salesperson = st.multiselect("Select Salesperson", options=data['Sales'].unique())
    category1 = st.multiselect("Select Main Category", options=data['Category1'].unique())
    category2 = st.multiselect("Select Subcategory", options=data['Category2'].unique())
    goods_type = st.multiselect("Select Goods Type", options=data['goods tpye'].unique())
    transport_type = st.multiselect("Select Transport Type", options=data['Type'].unique())
    profit_range = st.slider(
        "Profit Range",
        min_value=int(data['Profit'].min()),
        max_value=int(data['Profit'].max()),
        value=(int(data['Profit'].min()), int(data['Profit'].max()))
    )

    # Filter Button
    filter_button = st.button("Filter Data")

# Apply Filters
filtered_data = data.copy()
if filter_button:
    # Apply date range filter
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
    if category1:
        filtered_data = filtered_data[filtered_data['Category1'].isin(category1)]
    if category2:
        filtered_data = filtered_data[filtered_data['Category2'].isin(category2)]
    if goods_type:
        filtered_data = filtered_data[filtered_data['goods tpye'].isin(goods_type)]
    if transport_type:
        filtered_data = filtered_data[filtered_data['Type'].isin(transport_type)]
    filtered_data = filtered_data[(filtered_data['Profit'] >= profit_range[0]) &
                                  (filtered_data['Profit'] <= profit_range[1])]

    # Display selected filter choices
    st.markdown("### Selected Filters")
    if date_range:
        st.markdown(f"- **Date Range**: {date_range[0]} to {date_range[1]}")
    if destination:
        st.markdown(f"- **Destination**: {', '.join(destination)}")
    if shipment_number:
        st.markdown(f"- **Shipment Numbers**: {', '.join(shipment_number)}")
    if client_code:
        st.markdown(f"- **Client Codes**: {', '.join(client_code)}")
    if client_level:
        st.markdown(f"- **Client Levels**: {', '.join(client_level)}")
    if salesperson:
        st.markdown(f"- **Salespersons**: {', '.join(salesperson)}")
    if category1:
        st.markdown(f"- **Main Categories**: {', '.join(category1)}")
    if category2:
        st.markdown(f"- **Subcategories**: {', '.join(category2)}")
    if goods_type:
        st.markdown(f"- **Goods Types**: {', '.join(goods_type)}")
    if transport_type:
        st.markdown(f"- **Transport Types**: {', '.join(transport_type)}")
    st.markdown("---")
else:
    st.info("No filters applied. Showing all data.")

# KPIs Section
st.header("Key Metrics")

total_sales = filtered_data['Sales total'].sum()
total_profit = filtered_data['Profit'].sum()

col1, col2 = st.columns(2)
col1.metric(label="Total Sales", value=f"${total_sales:,.2f}")
col2.metric(label="Total Profit", value=f"${total_profit:,.2f}")

