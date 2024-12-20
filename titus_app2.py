import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import numpy as np

# Load the dataset
data = pd.read_excel("titus_data.xlsx", sheet_name="Data")
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

# Load the logo
logo_path = "titus_logo.jpg"
logo = Image.open(logo_path)

# Sidebar with logo and menu
with st.sidebar:
    st.title("Titus Logistics")

    st.image(logo, width=100)
    st.markdown("---")

    page = st.sidebar.radio(
    "Navigation",
    ["Main Dashboard", "Comparison Report", "Business Assessment", "Comparison By Date"]
    )

    # Manage session state for filtering logic
    if "filters_applied" not in st.session_state:
        st.session_state.filters_applied = False

    # Reset Filters Button
    if st.button("Reset Filters"):
        st.session_state.filters_applied = False

    # Date Range Filter with Preset Options
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
        else:
            date_range = (min_date, max_date)

    # Destination Filter
    with st.expander("Destination Filters"):
        destination = st.multiselect("Select Destination", options=data['Destination'].unique())

    # Shipment Filters
    with st.expander("Shipment Filters"):
        shipment_number = st.multiselect("Select Shipment Number", options=data['Shipment NO.'].unique())
        warehouse = st.multiselect("Select Loading Warehouse", options=data['Loading warehouse'].unique())

    # Client Filters
    with st.expander("Client Filters"):
        client_code = st.multiselect("Select Client Code", options=data['Client code'].unique())
        client_level = st.multiselect("Select Client Level", options=data['Client level'].unique())

    # Sales and Goods Filters
    with st.expander("Sales and Goods Filters"):
        salesperson = st.multiselect("Select Salesperson", options=data['Sales'].unique())
        mark = st.multiselect("Select Mark (Label)", options=data['Mark'].unique())
        category1 = st.multiselect("Select Main Category", options=data['Category1'].unique())
        category2 = st.multiselect("Select Subcategory", options=data['Category2'].unique())
        description = st.multiselect("Select Description", options=data['Description in E'].unique())
        goods_type = st.multiselect("Select Goods Type", options=data['goods tpye'].unique())

    # Transport Type Filter
    with st.expander("Transport Filters"):
        transport_type = st.multiselect("Select Transport Type", options=data['Type'].unique())

    # Range Filters for Profit, Weight, and CBM
    with st.expander("Range Filters"):
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

    # Filter Button
    if st.button("Filter Data"):
        st.session_state.filters_applied = True

# Apply Filters
if st.session_state.filters_applied:
    filtered_data = data.copy()

    # Date Range Filter
    filtered_data = filtered_data[
        (filtered_data['DATE'] >= pd.to_datetime(date_range[0])) &
        (filtered_data['DATE'] <= pd.to_datetime(date_range[1]))
    ]

    # Destination Filter
    if destination:
        filtered_data = filtered_data[filtered_data['Destination'].isin(destination)]

    # Shipment Number Filter
    if shipment_number:
        filtered_data = filtered_data[filtered_data['Shipment NO.'].isin(shipment_number)]

    # Loading Warehouse Filter
    if warehouse:
        filtered_data = filtered_data[filtered_data['Loading warehouse'].isin(warehouse)]

    # Client Code Filter
    if client_code:
        filtered_data = filtered_data[filtered_data['Client code'].isin(client_code)]

    # Client Level Filter
    if client_level:
        filtered_data = filtered_data[filtered_data['Client level'].isin(client_level)]

    # Salesperson Filter
    if salesperson:
        filtered_data = filtered_data[filtered_data['Sales'].isin(salesperson)]

    # Mark Filter
    if mark:
        filtered_data = filtered_data[filtered_data['Mark'].isin(mark)]

    # Main Category Filter
    if category1:
        filtered_data = filtered_data[filtered_data['Category1'].isin(category1)]

    # Subcategory Filter
    if category2:
        filtered_data = filtered_data[filtered_data['Category2'].isin(category2)]

    # Description Filter
    if description:
        filtered_data = filtered_data[filtered_data['Description in E'].isin(description)]

    # Goods Type Filter
    if goods_type:
        filtered_data = filtered_data[filtered_data['goods tpye'].isin(goods_type)]

    # Transport Type Filter
    if transport_type:
        filtered_data = filtered_data[filtered_data['Type'].isin(transport_type)]

    # Profit Range Filter
    filtered_data = filtered_data[
        (filtered_data['Profit'] >= profit_range[0]) &
        (filtered_data['Profit'] <= profit_range[1])
    ]

    # Weight Range Filter
    filtered_data = filtered_data[
        (filtered_data['WEIGHT'] >= weight_range[0]) &
        (filtered_data['WEIGHT'] <= weight_range[1])
    ]

    # CBM Range Filter
    filtered_data = filtered_data[
        (filtered_data['CBM'] >= cbm_range[0]) &
        (filtered_data['CBM'] <= cbm_range[1])
    ]

    st.success(f"Filtered Data: {len(filtered_data)} records found!")
else:
    filtered_data = data.copy()

# Display Filtered Data
#st.subheader("Filtered Data")
#st.dataframe(filtered_data)


# Main Dashboard Page
if page == "Main Dashboard":
    # KPIs Section
    st.header("Key Metrics")
    total_sales = filtered_data['Sales total'].sum()
    total_profit = filtered_data['Profit'].sum()
    total_cost = filtered_data['Cost total'].sum()
    total_weight = filtered_data['WEIGHT'].sum()
    total_volume = filtered_data['CBM'].sum()
    total_shipments = len(filtered_data)

    # Display KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric(label="📈 Total Sales", value=f"${total_sales:,.2f}")
    col2.metric(label="💰 Total Profit", value=f"${total_profit:,.2f}")
    col3.metric(label="📦 Total Shipments", value=total_shipments)

    col4, col5, col6 = st.columns(3)
    col4.metric(label="🏷️ Total Cost", value=f"${total_cost:,.2f}")
    col5.metric(label="⚖️ Total Weight", value=f"{total_weight:,.2f} kg")
    col6.metric(label="📐 Total Volume", value=f"{total_volume:,.2f} m³")


    # Profit Analysis Section
    st.header("Profit Analysis")

    # User Choices for Metric and Aggregation in the same row
    col1, col2 = st.columns(2)

    with col1:
        numeric_metric = st.selectbox(
            "Select Numeric Metric to Analyze",
            options=["Sales total", "Cost total", "CBM", "WEIGHT", "Profit"],
            index=4  # Default to "Profit"
        )

    with col2:
        aggregation_basis = st.selectbox(
            "Aggregate By",
            options=["Destination", "Client code", "Client level", "Sales", 
                    "Category1", "Category2", "Type", "Loading warehouse"],
            index=0  # Default to "Destination"
        )

    # Generate Bar Chart Based on User Selections
    if not filtered_data.empty:  # Ensure there is data to display
        aggregated_data = (
            filtered_data.groupby(aggregation_basis)[numeric_metric].sum().reset_index()
        )
        bar_chart = px.bar(
            aggregated_data,
            x=aggregation_basis,
            y=numeric_metric,
            title=f"{numeric_metric} by {aggregation_basis}",
            labels={aggregation_basis: aggregation_basis, numeric_metric: numeric_metric},
            color=aggregation_basis,
        )
        st.plotly_chart(bar_chart, use_container_width=True)
    else:
        st.warning("No data available to generate the chart. Please adjust your filters.")


    # Sales vs. Cost Analysis Section
    st.header("Sales vs. Cost Analysis")

    # Dropdown to analyze trends by category
    trend_category = st.selectbox(
        "Analyze Trend By (Optional)",
        options=["None", "Destination", "Client code", "Client level", "Sales", 
                "Category1", "Category2", "Type", "Loading warehouse"],
        index=0  # Default to "None"
    )

    # Check if there is data to display
    if not filtered_data.empty:
        if trend_category == "None":
            # Group data by DATE and calculate the sum of Sales and Cost
            time_series_data = filtered_data.groupby("DATE")[["Sales total", "Cost total"]].sum().reset_index()

            # Create a line chart for overall trend
            sales_cost_chart = px.line(
                time_series_data,
                x="DATE",
                y=["Sales total", "Cost total"],
                labels={"value": "Amount (USD)", "variable": "Metric"},
                title="Sales vs. Cost Over Time",
            )
        else:
            # Group data by DATE and selected category
            time_series_data = filtered_data.groupby(["DATE", trend_category])[["Sales total", "Cost total"]].sum().reset_index()

            # Show all categories by default
            category_values = time_series_data[trend_category].unique().tolist()
            selected_category_values = st.multiselect(
                f"Filter by {trend_category} (Optional)",
                options=category_values,
                default=category_values  # Default to all values
            )

            # Filter data if specific category values are selected
            if selected_category_values:
                time_series_data = time_series_data[time_series_data[trend_category].isin(selected_category_values)]

            # Transform data for better distinction between Sales and Cost
            melted_data = time_series_data.melt(
                id_vars=["DATE", trend_category], 
                value_vars=["Sales total", "Cost total"], 
                var_name="Metric", 
                value_name="Amount"
            )

            # Create a combined column for unique coloring
            melted_data["Category_Metric"] = melted_data[trend_category] + " - " + melted_data["Metric"]

            # Create a line chart with distinct colors for each Category + Metric combination
            sales_cost_chart = px.line(
                melted_data,
                x="DATE",
                y="Amount",
                color="Category_Metric",  # Unique color for each category + metric
                labels={"Category_Metric": "Category and Metric", "Amount": "Amount (USD)"},
                title=f"Sales vs. Cost Over Time by {trend_category}" if len(selected_category_values) > 1 
                    else f"Sales vs. Cost Over Time for Selected {trend_category}",
            )

        # Display the chart
        st.plotly_chart(sales_cost_chart, use_container_width=True)
    else:
        st.warning("No data available to generate the chart. Please adjust your filters.")

    # Client Analysis Section
    st.header("Client Analysis")

    # Dropdown to select a client
    selected_client = st.selectbox(
        "Select a Client",
        options=filtered_data['Client level'].unique(),
        index=0  # Default to the first client
    )

    # Filter data for the selected client
    client_data = filtered_data[filtered_data['Client level'] == selected_client]

    # Group data by Category and calculate total profit
    category_profit = client_data.groupby("Category1")["Profit"].sum().reset_index()

    # Create a bar chart
    profit_bar_chart = px.bar(
        category_profit,
        x="Category1",
        y="Profit",
        title=f"Profit by Category for Client: {selected_client}",
        labels={"Category1": "Category", "Profit": "Total Profit (USD)"},
        color="Category1",  # Optional: Different colors for each category
        text="Profit"  # Show profit values on bars
    )

    # Display the chart
    st.plotly_chart(profit_bar_chart, use_container_width=True)


    # Dynamic Breakdown Analysis Section
    st.header("Dynamic Breakdown Analysis")

    # User Input for Metric and Aggregation Basis
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        numeric_metric = st.selectbox(
            "Select Numeric Metric to Analyze",
            options=["Sales total", "Cost total", "CBM", "WEIGHT", "Profit"],
            index=4,  # Default to "Profit"
            key="dynamic_breakdown_numeric_metric"
        )

    with col2:
        aggregation_basis = st.selectbox(
            "Aggregate By",
            options=["Destination", "Client code", "Client level", "Sales", 
                    "Category1", "Category2", "Type", "Loading warehouse"],
            index=0,  # Default to "Destination"
            key="dynamic_breakdown_aggregation_basis"
        )

    with col3:
        secondary_dimension = st.selectbox(
            "Secondary Breakdown By",
            options=["Destination", "Client code", "Client level", "Sales", 
                    "Category1", "Category2", "Type", "Loading warehouse"],
            index=4,  # Default to "Category1"
            key="dynamic_breakdown_secondary_dimension"
        )

    # Radar Selector for Display Option
    display_option = st.radio(
        "Choose Display Option",
        options=["Absolute Sum", "Percentage Share"],
        index=0  # Default to "Absolute Sum"
    )

    # Generate the Chart Based on User Selections
    if not filtered_data.empty:  # Ensure there is data to display
        # Group data by selected aggregation_basis and secondary_dimension
        aggregated_data = (
            filtered_data.groupby([aggregation_basis, secondary_dimension])[numeric_metric]
            .sum()
            .reset_index()
        )

        if display_option == "Percentage Share":
            # Calculate percentage share within each aggregation_basis group
            aggregated_data["Percentage"] = (
                aggregated_data.groupby(aggregation_basis)[numeric_metric]
                .transform(lambda x: x / x.sum() * 100)
            )
            y_axis = "Percentage"  # Use percentage column for chart
            y_label = "Percentage Share (%)"
            chart_title = f"{numeric_metric} Percentage Share by {aggregation_basis} and {secondary_dimension}"
        else:
            y_axis = numeric_metric  # Use the original numeric metric
            y_label = f"{numeric_metric} (Absolute)"
            chart_title = f"{numeric_metric} Breakdown by {aggregation_basis} and {secondary_dimension}"

        # Create a bar chart (stacked for absolute sum or 100% stacked for percentage)
        bar_chart = px.bar(
            aggregated_data,
            x=aggregation_basis,
            y=y_axis,
            color=secondary_dimension,  # Add color to differentiate secondary breakdown
            title=chart_title,
            labels={
                aggregation_basis: aggregation_basis,
                y_axis: y_label,
                secondary_dimension: "Secondary Breakdown",
            },
            barmode="stack",  # Stacked bar chart
        )

        # Display the chart
        st.plotly_chart(bar_chart, use_container_width=True)

    else:
        st.warning("No data available to generate the chart. Please adjust your filters.")

    # Bubble Chart: Volume and Weight Analysis
    st.header("Volume and Weight Analysis")

    # Check if data is available
    if not filtered_data.empty:
        # Create the bubble chart using Plotly Express
        bubble_chart = px.scatter(
            filtered_data,
            x="Cost total",  # X-axis: Cost
            y="Sales total",  # Y-axis: Sales
            size="CBM",  # Bubble size: Volume
            color="WEIGHT",  # Color intensity: Weight
            hover_data={
                "Cost total": ":.2f",
                "Sales total": ":.2f",
                "CBM": ":.2f",
                "WEIGHT": ":.2f"
            },
            title="Cost vs. Sales (Bubble Size: Volume, Color: Weight)",
            labels={
                "Cost total": "Cost (USD)",
                "Sales total": "Sales (USD)",
                "CBM": "Volume (CBM)",
                "WEIGHT": "Weight (kg)"
            },
        )

        # Update layout for better visualization
        bubble_chart.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color="DarkSlateGrey")))
        bubble_chart.update_layout(
            xaxis=dict(title="Cost (USD)", gridcolor="LightGrey"),
            yaxis=dict(title="Sales (USD)", gridcolor="LightGrey"),
            coloraxis_colorbar=dict(title="Weight (kg)"),
        )

        # Display the bubble chart
        st.plotly_chart(bubble_chart, use_container_width=True)
    else:
        st.warning("No data available to generate the chart. Please adjust your filters.")

    # Dynamic Bubble Chart Section
    #st.header("Dynamic Bubble Chart Analysis")

    # Define use cases dynamically
    use_cases = {
        "Profit vs. Sales by Destination": {
            "x": "Sales total",
            "y": "Profit",
            "size": "CBM",
            "color": "WEIGHT",
            "category": "Destination",
            "title": "Profit vs. Sales by Destination",
            "x_label": "Sales (USD)",
            "y_label": "Profit (USD)"
        },
        "Cost vs. Sales by Category": {
            "x": "Cost total",
            "y": "Sales total",
            "size": "CBM",
            "color": "WEIGHT",
            "category": "Category1",
            "title": "Cost vs. Sales by Category",
            "x_label": "Cost (USD)",
            "y_label": "Sales (USD)"
        },
        "Profit vs. Weight by Client Type": {
            "x": "WEIGHT",
            "y": "Profit",
            "size": "CBM",
            "color": "Sales total",
            "category": "Client level",
            "title": "Profit vs. Weight by Client Type",
            "x_label": "Weight (kg)",
            "y_label": "Profit (USD)"
        },
        "Volume (CBM) vs. Weight by Product Type": {
            "x": "CBM",
            "y": "WEIGHT",
            "size": "Profit",
            "color": "Sales total",
            "category": "Type",
            "title": "Volume vs. Weight by Product Type",
            "x_label": "Volume (CBM)",
            "y_label": "Weight (kg)"
        },
    }

        # Use Case Descriptions
    use_case_descriptions = {
        "Profit vs. Sales by Destination": """
        **Description**: This chart shows the relationship between sales and profit for each destination. 
        Larger bubbles represent higher shipment volumes (CBM), and darker colors represent heavier shipments (WEIGHT).
        **How to Interpret**: Look for destinations with high profit and sales. Larger bubbles indicate significant shipment volumes, while darker bubbles mean higher weights.""",
        
        "Cost vs. Sales by Category": """
        **Description**: This chart compares the cost incurred and the sales revenue across product categories. 
        Larger bubbles signify higher shipment volumes (CBM), and darker bubbles indicate heavier shipments (WEIGHT).
        **How to Interpret**: Identify categories with a favorable cost-to-sales ratio. Look for categories with high sales and relatively lower costs.""",
        
        "Profit vs. Weight by Client Type": """
        **Description**: This chart examines profit versus the weight of shipments for different client levels. 
        Larger bubbles represent higher shipment volumes (CBM), and darker colors show higher sales revenue (Sales total).
        **How to Interpret**: Focus on client levels that generate the most profit for a given shipment weight. Larger and darker bubbles indicate significant revenue and volume.""",
        
        "Volume (CBM) vs. Weight by Product Type": """
        **Description**: This chart compares the volume (CBM) and weight of shipments for various product types. 
        Larger bubbles represent higher profits, while darker bubbles indicate higher sales revenue.
        **How to Interpret**: Identify product types that are bulkier or heavier and their corresponding profitability and sales.""",
    }

    # Dynamic Bubble Chart Section
    st.header("Dynamic Multi-Dimension Analysis")

    # User selects a use case
    selected_use_case = st.selectbox("Choose a Use Case", options=list(use_cases.keys()))

    # Retrieve selected use case configuration
    config = use_cases[selected_use_case]

    # Display the use case description
    st.markdown(use_case_descriptions[selected_use_case])

    # Generate Bubble Chart
    if not filtered_data.empty:
        bubble_chart = px.scatter(
            filtered_data,
            x=config["x"],
            y=config["y"],
            size=config["size"],
            color=config["color"],
            facet_col=config["category"],
            title=config["title"],
            labels={
                config["x"]: config["x_label"],
                config["y"]: config["y_label"],
                config["size"]: "Bubble Size",
                config["color"]: "Color Intensity",
            },
            hover_data={
                config["x"]: ":.2f",
                config["y"]: ":.2f",
                config["size"]: ":.2f",
                config["color"]: ":.2f"
            },
        )
        # Style adjustments
        bubble_chart.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color="DarkSlateGrey")))
        bubble_chart.update_layout(
            xaxis=dict(title=config["x_label"], gridcolor="LightGrey"),
            yaxis=dict(title=config["y_label"], gridcolor="LightGrey"),
            coloraxis_colorbar=dict(title=config["color"]),
        )

        # Display the chart
        st.plotly_chart(bubble_chart, use_container_width=True)
    else:
        st.warning("No data available to generate the chart. Please adjust your filters.")


# Comparison Report Page
elif page == "Comparison Report":
    st.title("Comparison Report")
    st.write("This page is dedicated to comparing key metrics across branches or categories.")

    # Convert numeric columns
    numeric_columns = ["Sales total", "Profit", "Cost total", "CBM", "WEIGHT"]
    categorical_columns = ["Destination", "Client code", "Client level", "Category1", "Category2", "Type"]
   
    # Page Header
    #st.title("Creative Comparison Tool")
    st.write("Choose categories and metrics to create powerful comparisons.")

    # User Input for Comparison
    comparison_type = st.radio(
        "What do you want to compare?",
        ["Two Numerical Columns", "Two Categorical Columns", "Mix (Numerical and Categorical)"],
        index=0
    )

    if comparison_type == "Two Numerical Columns":
        # User selects two numerical columns
        num1, num2 = st.columns(2)
        with num1:
            numeric1 = st.selectbox("Select First Numerical Column", options=numeric_columns)
        with num2:
            numeric2 = st.selectbox("Select Second Numerical Column", options=numeric_columns)

        # Generate Scatter Plot
        st.header(f"Scatter Plot: {numeric1} vs {numeric2}")
        fig = px.scatter(filtered_data, x=numeric1, y=numeric2, title=f"{numeric1} vs {numeric2}", labels={numeric1: numeric1, numeric2: numeric2})
        st.plotly_chart(fig, use_container_width=True)

    elif comparison_type == "Two Categorical Columns":
        # User selects two categorical columns
        cat1, cat2 = st.columns(2)
        with cat1:
            categorical1 = st.selectbox("Select First Categorical Column", options=categorical_columns)
        with cat2:
            categorical2 = st.selectbox("Select Second Categorical Column", options=categorical_columns)

        # Generate Stacked Bar Chart
        st.header(f"Stacked Bar Chart: {categorical1} and {categorical2}")
        aggregated_data = filtered_data.groupby([categorical1, categorical2]).size().reset_index(name="Count")
        fig = px.bar(
            aggregated_data,
            x=categorical1,
            y="Count",
            color=categorical2,
            title=f"{categorical1} and {categorical2} Relationship",
            labels={categorical1: categorical1, categorical2: categorical2, "Count": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)

    elif comparison_type == "Mix (Numerical and Categorical)":
        # User selects numerical and one/two categorical columns
        num_col, cat1_col, cat2_col = st.columns([1, 1, 1])

        with num_col:
            numeric_column = st.selectbox("Select Numerical Column", options=numeric_columns)
        with cat1_col:
            categorical1 = st.selectbox("Select First Categorical Column", options=categorical_columns)
        with cat2_col:
            categorical2 = st.selectbox(
                "Select Second Categorical Column (Optional)", options=["None"] + categorical_columns, index=0
            )

        if categorical2 == "None":
            # Generate Grouped Bar Chart
            st.header(f"Grouped Bar Chart: {numeric_column} by {categorical1}")
            aggregated_data = filtered_data.groupby(categorical1)[numeric_column].sum().reset_index()
            fig = px.bar(
                aggregated_data,
                x=categorical1,
                y=numeric_column,
                title=f"{numeric_column} by {categorical1}",
                labels={categorical1: categorical1, numeric_column: numeric_column}
            )
        else:
            # Generate Stacked Bar Chart
            st.header(f"Stacked Bar Chart: {numeric_column} by {categorical1} and {categorical2}")
            aggregated_data = filtered_data.groupby([categorical1, categorical2])[numeric_column].sum().reset_index()
            fig = px.bar(
                aggregated_data,
                x=categorical1,
                y=numeric_column,
                color=categorical2,
                title=f"{numeric_column} by {categorical1} and {categorical2}",
                labels={categorical1: categorical1, categorical2: categorical2, numeric_column: numeric_column},
                barmode="stack"
            )

        st.plotly_chart(fig, use_container_width=True)

elif page == "Business Assessment":
    numeric_columns = ["Sales total", "Profit", "Cost total", "CBM", "WEIGHT"]
    categorical_columns = ["Destination", "Client code", "Client level", "Category1", "Category2", "Type"]

    # Create the Business Assessment page
    def business_assessment():
        st.title("Business Assessment")

        # Section 1: Profitability Analysis
        st.header("1. Profitability Analysis")
        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox("Select Metric", options=["Profit", "Sales total"], index=0)
        with col2:
            aggregation = st.selectbox("Aggregate By", options=categorical_columns, index=0)
        if metric and aggregation:
            agg_data = data.groupby(aggregation)[metric].sum().reset_index()
            fig = px.bar(agg_data, x=aggregation, y=metric, color=aggregation, title=f"{metric} by {aggregation}")
            st.plotly_chart(fig)

        # Section 2: Cost Efficiency
        st.header("2. Cost Efficiency")
        cost_efficiency = data.groupby("Category1")[["Cost total", "Sales total"]].sum().reset_index()
        fig2 = px.bar(
            cost_efficiency,
            x="Category1",
            y=["Cost total", "Sales total"],
            title="Cost vs Sales by Category",
            barmode="group",
            labels={"value": "Amount (USD)", "variable": "Metric"},
        )
        st.plotly_chart(fig2)

        # Section 3: Volume and Weight Analysis
        st.header("3. Volume and Weight Analysis")
        volume_weight = data.groupby("Category1")[["CBM", "WEIGHT"]].sum().reset_index()
        fig3 = px.scatter(
            volume_weight,
            x="CBM",
            y="WEIGHT",
            color="Category1",
            size="CBM",
            title="Volume vs Weight by Category",
            labels={"CBM": "Volume (CBM)", "WEIGHT": "Weight (kg)", "Category1": "Category"},
        )
        st.plotly_chart(fig3)

        # Section 4: Shipment Trends
        st.header("4. Shipment Trends")
        shipment_trend = data.groupby("DATE")[["Sales total", "Cost total"]].sum().reset_index()
        fig4 = px.line(
            shipment_trend,
            x="DATE",
            y=["Sales total", "Cost total"],
            title="Sales and Cost Trends Over Time",
            labels={"value": "Amount (USD)", "variable": "Metric"},
        )
        st.plotly_chart(fig4)

        # Section 5: Client Segmentation
        st.header("5. Client Segmentation")
        client_segmentation = data.groupby("Client level")[["Profit", "Sales total"]].sum().reset_index()
        fig5 = px.bar(
            client_segmentation,
            x="Client level",
            y=["Profit", "Sales total"],
            barmode="group",
            title="Profit and Sales by Client Level",
            labels={"value": "Amount (USD)", "variable": "Metric"},
        )
        st.plotly_chart(fig5)

        
    # Render the page
    business_assessment()

elif page == "Comparison By Date":
    st.title("Comparison By Date")

    # Step 1: User Input for Date Ranges
    st.subheader("Specify Date Ranges for Comparison")

    col1, col2 = st.columns(2)
    with col1:
        start_date_1 = st.date_input("Start Date for Period 1", value=min_date)
        end_date_1 = st.date_input("End Date for Period 1", value=max_date)
    with col2:
        start_date_2 = st.date_input("Start Date for Period 2", value=min_date)
        end_date_2 = st.date_input("End Date for Period 2", value=max_date)

    # Step 2: User Choices for Metric and Aggregation
    st.subheader("Select Metric and Aggregation Basis")

    col1, col2 = st.columns(2)
    with col1:
        numeric_metric = st.selectbox(
            "Select Numeric Metric to Analyze",
            options=["Sales total", "Cost total", "CBM", "WEIGHT", "Profit"],
            index=4  # Default to "Profit"
        )

    with col2:
        aggregation_basis = st.selectbox(
            "Aggregate By",
            options=["Destination", "Client code", "Client level", "Sales", 
                     "Category1", "Category2", "Type", "Loading warehouse"],
            index=0  # Default to "Destination"
        )

    # Step 3: Filter Data for Each Period
    if not filtered_data.empty:
        # Filter for Period 1
        period_1_data = filtered_data[
            (filtered_data['DATE'] >= pd.to_datetime(start_date_1)) &
            (filtered_data['DATE'] <= pd.to_datetime(end_date_1))
        ]
        # Aggregate data for Period 1
        period_1_agg = period_1_data.groupby(aggregation_basis)[numeric_metric].sum().reset_index()
        period_1_agg.rename(columns={numeric_metric: f"{numeric_metric} (Period 1)"}, inplace=True)

        # Filter for Period 2
        period_2_data = filtered_data[
            (filtered_data['DATE'] >= pd.to_datetime(start_date_2)) &
            (filtered_data['DATE'] <= pd.to_datetime(end_date_2))
        ]
        # Aggregate data for Period 2
        period_2_agg = period_2_data.groupby(aggregation_basis)[numeric_metric].sum().reset_index()
        period_2_agg.rename(columns={numeric_metric: f"{numeric_metric} (Period 2)"}, inplace=True)

        # Step 4: Merge Period 1 and Period 2 Data
        comparison_data = pd.merge(period_1_agg, period_2_agg, on=aggregation_basis, how="outer").fillna(0)

        # Calculate Percentage Difference
        comparison_data["% Difference"] = (
            (comparison_data[f"{numeric_metric} (Period 2)"] - comparison_data[f"{numeric_metric} (Period 1)"]) /
            comparison_data[f"{numeric_metric} (Period 1)"].replace(0, np.nan)
        ) * 100
        comparison_data["% Difference"].fillna(0, inplace=True)

        # Step 5: Visualize the Comparison
        st.subheader(f"Comparison of {numeric_metric} by {aggregation_basis}")

        # Bar chart for Period 1 and Period 2
        fig = px.bar(
            comparison_data,
            x=aggregation_basis,
            y=[f"{numeric_metric} (Period 1)", f"{numeric_metric} (Period 2)"],
            barmode="group",
            title=f"{numeric_metric} Comparison Between Two Periods",
            labels={aggregation_basis: aggregation_basis, "value": numeric_metric},
        )
        st.plotly_chart(fig, use_container_width=True)

        # Line chart for % Difference
        fig_diff = px.line(
            comparison_data,
            x=aggregation_basis,
            y="% Difference",
            title=f"Percentage Difference in {numeric_metric} by {aggregation_basis}",
            labels={aggregation_basis: aggregation_basis, "% Difference": "Percentage Difference (%)"},
            markers=True
        )
        st.plotly_chart(fig_diff, use_container_width=True)

        # Step 6: Display Data Table
        st.subheader("Comparison Data Table")
        st.dataframe(comparison_data)

    else:
        st.warning("No data available to generate the comparison. Please adjust your filters.")
