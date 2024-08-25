import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(layout="wide", page_title="Supply Chain Management Dashboard")

# Create two columns for the layout
left_column, right_column = st.columns([1, 2])

# Left column content
with left_column:
    st.title("Supply Chain Management Dashboard")
    st.markdown("""
    This dashboard provides insights into key supply chain metrics, including inventory levels, 
    lead times, supplier performance, and more.
    """)
    # rtyhtrurtu
    st.markdown("### Required Columns")
    st.markdown("""
    Your CSV file should include the following columns:
    1. Product Category
    2. Inventory Level
    3. Supplier
    4. Lead Time
    5. Order Quantity
    6. Sales
    7. Quality Rating
    8. On-Time Delivery Rate
    9. Date
    10. Warehouse/Location
    11. Shipping Cost
    12. Delivery Time
    13. COGS (Cost of Goods Sold)
    """)
    
    # Add a footer
    st.markdown("---")
    st.markdown("Created by [Your Name] | [Your Portfolio/GitHub Link]")

# Right column content
with right_column:
    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            # Load data
            df = pd.read_csv(uploaded_file)
            
            # Convert all column names to lowercase for case-insensitive matching
            df.columns = df.columns.str.lower().str.strip()
            
            st.write("Columns in the uploaded file:")
            st.write(df.columns.tolist())

            # Define required columns with lowercase names
            required_columns = ['product category', 'inventory level', 'supplier', 'lead time', 
                                'order quantity', 'sales', 'quality rating', 'on-time delivery rate', 
                                'date', 'warehouse/location', 'shipping cost', 'delivery time', 'cogs (cost of goods sold)']

            # Check for required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
                st.markdown("### Manual Column Mapping")
                st.write("Please map your columns to the required fields:")
                
                column_mapping = {}
                for col in missing_columns:
                    display_name = col.replace('_', ' ').title()
                    column_mapping[col] = st.selectbox(f"Select column for {display_name}", options=df.columns)

                # Rename columns based on user mapping
                df = df.rename(columns=column_mapping)
                
                st.write("Columns after renaming:")
                st.write(df.columns.tolist())
                
                # Re-check for missing columns
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    st.error(f"Still missing the following columns: {', '.join(missing_columns)}")
                    st.stop()
            
            # Display raw data
            if st.checkbox("Show raw data"):
                st.subheader("Raw Data")
                st.write(df)
            
            # Convert date column to datetime
            try:
                df['date'] = pd.to_datetime(df['date'])
            except ValueError:
                st.error("Error converting date column to datetime. Please ensure your dates are in a standard format.")
                st.stop()
            
            # Sort by date
            df = df.sort_values('date')
            
            # Convert numeric columns to appropriate types
            numeric_columns = ['inventory level', 'lead time', 'order quantity', 'sales', 
                               'quality rating', 'shipping cost', 'delivery time', 'cogs (cost of goods sold)']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert 'on-time delivery rate' to numeric (removing % sign if present)
            df['on-time delivery rate'] = pd.to_numeric(df['on-time delivery rate'].astype(str).str.rstrip('%'), errors='coerce') / 100.0
            
            # Check for missing values
            missing_values = df[required_columns].isnull().sum()
            if missing_values.sum() > 0:
                st.warning("The following columns have missing values:")
                st.write(missing_values[missing_values > 0])
                if st.checkbox("Continue with analysis (missing values will be handled automatically)"):
                    df = df.dropna()
                    st.info(f"Rows with missing values have been removed. Remaining rows: {len(df)}")
                else:
                    st.stop()
            
            # Inventory Analysis
            st.header("Inventory Management")
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock Levels by Product Category
                fig_stock = px.bar(df.groupby('product category')['inventory level'].sum().reset_index(), 
                                   x='product category', y='inventory level',
                                   title="Stock Levels by Product Category")
                st.plotly_chart(fig_stock, use_container_width=True)
            
            with col2:
                # Stock Turnover Rate
                df['stock turnover rate'] = df['sales'] / df['inventory level']
                fig_turnover = px.box(df, x='product category', y='stock turnover rate',
                                      title="Stock Turnover Rate by Product Category")
                st.plotly_chart(fig_turnover, use_container_width=True)

            # Days of Inventory (DOI)
            st.subheader("Days of Inventory (DOI)")
            df['days of inventory'] = df['inventory level'] / df['sales']
            fig_doi = px.line(df, x='date', y='days of inventory', color='product category',
                              title="Days of Inventory Over Time")
            st.plotly_chart(fig_doi, use_container_width=True)

            # Procurement Metrics
            st.header("Procurement Metrics")
            col3, col4 = st.columns(2)
            
            with col3:
                # Supplier Performance
                fig_supplier = px.bar(df.groupby('supplier').agg({
                    'lead time': 'mean', 
                    'quality rating': 'mean', 
                    'on-time delivery rate': 'mean'
                }).reset_index().melt(id_vars='supplier'), 
                x='supplier', y='value', color='variable', barmode='group',
                title="Supplier Performance Metrics")
                st.plotly_chart(fig_supplier, use_container_width=True)
            
            with col4:
                # Purchase Order Cycle Time
                df['purchase order cycle time'] = df['delivery time'] + df['lead time']
                fig_po_cycle = px.bar(df.groupby('supplier')['purchase order cycle time'].mean().reset_index(),
                                      x='supplier', y='purchase order cycle time',
                                      title="Average Purchase Order Cycle Time by Supplier")
                st.plotly_chart(fig_po_cycle, use_container_width=True)

            # Logistics & Transportation
            st.header("Logistics & Transportation")
            col5, col6 = st.columns(2)
            
            with col5:
                # Shipping Costs
                fig_shipping = px.bar(df.groupby('warehouse/location')['shipping cost'].sum().reset_index(),
                                      x='warehouse/location', y='shipping cost',
                                      title="Total Shipping Costs by Location")
                st.plotly_chart(fig_shipping, use_container_width=True)
            
            with col6:
                # Delivery Time
                fig_delivery = px.box(df, x='warehouse/location', y='delivery time',
                                      title="Delivery Time by Location")
                st.plotly_chart(fig_delivery, use_container_width=True)

            # Supplier Risk Management
            st.header("Supplier Risk Management")
            df['supplier risk score'] = (df['lead time'] * 0.5 + (1 - df['quality rating']) * 0.3 + 
                                         (1 - df['on-time delivery rate']) * 0.2) * 100
            fig_risk = px.bar(df.groupby('supplier')['supplier risk score'].mean().reset_index(),
                              x='supplier', y='supplier risk score',
                              title="Supplier Risk Score")
            st.plotly_chart(fig_risk, use_container_width=True)

            # Demand Management
            st.header("Demand Management")
            col7, col8 = st.columns(2)
            
            with col7:
                # Order Backlog
                df['order backlog'] = df['order quantity'] - df['sales']
                fig_backlog = px.area(df.groupby('date')['order backlog'].sum().reset_index(),
                                      x='date', y='order backlog',
                                      title="Order Backlog Over Time")
                st.plotly_chart(fig_backlog, use_container_width=True)
            
            with col8:
                # Customer Order Cycle Time
                fig_order_cycle = px.line(df, x='date', y='delivery time', color='supplier',
                                          title="Customer Order Cycle Time by Supplier")
                st.plotly_chart(fig_order_cycle, use_container_width=True)

            # Cost Analysis
            st.header("Cost Analysis")
            col9, col10 = st.columns(2)
            
            with col9:
                # Total Supply Chain Cost
                df['total supply chain cost'] = (df['cogs (cost of goods sold)'] + df['shipping cost'])
                fig_cost = px.line(df.groupby('date')['total supply chain cost'].sum().reset_index(),
                                   x='date', y='total supply chain cost',
                                   title="Total Supply Chain Cost Over Time")
                st.plotly_chart(fig_cost, use_container_width=True)
            
            with col10:
                # Cost per Unit
                df['cost per unit'] = df['total supply chain cost'] / df['sales']
                fig_cost_unit = px.box(df, x='product category', y='cost per unit',
                                       title="Cost per Unit by Product Category")
                st.plotly_chart(fig_cost_unit, use_container_width=True)

            # Operational Efficiency
            st.header("Operational Efficiency")
            col11, col12 = st.columns(2)
            
            with col11:
                # Overall Equipment Effectiveness (OEE)
                df['oee'] = (df['quality rating'] * df['on-time delivery rate'])
                fig_oee = px.scatter(df, x='date', y='oee', color='product category',
                                     title="Overall Equipment Effectiveness (OEE) Over Time")
                st.plotly_chart(fig_oee, use_container_width=True)
            
            with col12:
                # Warehouse Utilization
                df['warehouse utilization'] = df['inventory level'] / df['warehouse/location'].nunique()
                fig_warehouse_util = px.bar(df.groupby('warehouse/location')['warehouse utilization'].mean().reset_index(),
                                            x='warehouse/location', y='warehouse utilization',
                                            title="Warehouse Utilization by Location")
                st.plotly_chart(fig_warehouse_util, use_container_width=True)

            # Sustainability Metrics
            st.header("Sustainability Metrics")
            col13, col14 = st.columns(2)
            
            with col13:
                # Carbon Footprint
                df['carbon footprint'] = df['shipping cost'] * 0.01  # Example calculation
                fig_carbon = px.line(df, x='date', y='carbon footprint', color='product category',
                                     title="Carbon Footprint Over Time")
                st.plotly_chart(fig_carbon, use_container_width=True)
            
            with col14:
                # Waste Reduction
                df['waste reduction'] = (df['inventory level'] - df['sales']) / df['inventory level']
                fig_waste = px.bar(df.groupby('product category')['waste reduction'].mean().reset_index(),
                                   x='product category', y='waste reduction',
                                   title="Waste Reduction by Product Category")
                st.plotly_chart(fig_waste, use_container_width=True)

            # Supplier Collaboration
            st.header("Supplier Collaboration")
            df['collaboration index'] = (df['on-time delivery rate'] * df['quality rating']) / df['lead time']
            fig_collab = px.scatter(df, x='supplier', y='collaboration index', color='product category',
                                    title="Supplier Collaboration Index")
            st.plotly_chart(fig_collab, use_container_width=True)

            # KPIs Overview
            st.header("Key Performance Indicators (KPIs) Overview")
            st.markdown("### Dashboard Overview")
            col15, col16 = st.columns(2)
            
            with col15:
                kpi1 = df['inventory level'].mean()
                kpi2 = df['lead time'].mean()
                kpi3 = df['total supply chain cost'].sum()
                
                fig_kpi1 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=kpi1,
                    title={'text': "Average Inventory Level"},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ))
                fig_kpi2 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=kpi2,
                    title={'text': "Average Lead Time"},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ))
                st.plotly_chart(fig_kpi1, use_container_width=True)
                st.plotly_chart(fig_kpi2, use_container_width=True)
            
            with col16:
                fig_kpi3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=kpi3,
                    title={'text': "Total Supply Chain Cost"},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ))
                st.plotly_chart(fig_kpi3, use_container_width=True)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
