import streamlit as st
import pandas as pd

# Set page config for a professional look
st.set_page_config(page_title="Ali Informatics | Econ-Tracker", layout="wide")

st.title("📈 Global Economic Data Pipeline")
st.markdown("Automated historical analysis and currency tracking.")

# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('data/economy_data.csv')
    # Ensure Date is actually a datetime object for better sorting
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # 2. Sidebar Navigation
    st.sidebar.header("Dashboard Controls")
    selection = st.sidebar.radio("Select Data Stream:", ["Forex", "Macro"])

    # 3. Filtering Logic
    filtered_df = df[df['Type'] == selection].sort_values('Date', ascending=False)

    # 4. Display Content based on Selection
    if selection == "Forex":
        st.subheader("💱 EUR/USD Exchange Rate (Last 14 Days)")

        # The scraper writes forex as one row per day with the EUR/USD close in 'Value'.
        # Build the EUR_USD and USD_EUR columns here so the chart and table stay unchanged.
        forex_df = filtered_df[['Date', 'Value']].copy()
        forex_df['EUR_USD'] = forex_df['Value']
        forex_df['USD_EUR'] = (1 / forex_df['Value']).round(4)

        # Display the Graph
        st.line_chart(forex_df, x='Date', y='EUR_USD')

        # Display CLEAN Table (Only Currency Columns)
        st.write("### Raw Exchange Data")
        st.dataframe(forex_df[['Date', 'EUR_USD', 'USD_EUR']], use_container_width=True)

    else:
        st.subheader("🌎 Macroeconomic Indicators (5 Decades)")
        
        # 1. Metric Selection (Keep as single choice so we compare same units)
        metric = st.selectbox("Choose Metric:", filtered_df['Metric'].unique())
        
        # 2. THE FIX: Multi-select for Countries
        selected_countries = st.multiselect(
            "Choose Countries to Compare:", 
            options=filtered_df['Country'].unique(),
            default=filtered_df['Country'].unique()[:1] # Defaults to the first country
        )
        
        if selected_countries:
            # Filter data for selected metric and countries
            plot_df = filtered_df[
                (filtered_df['Metric'] == metric) & 
                (filtered_df['Country'].isin(selected_countries))
            ]
            
            # Pivot the data so each country has its own column for the chart
            chart_data = plot_df.pivot(index='Date', columns='Country', values='Value')
            
            # Display the Multi-Line Graph
            st.line_chart(chart_data)
            
            # Display the Table
            st.write(f"### Raw {metric} Data")
            st.dataframe(plot_df[['Date', 'Country', 'Metric', 'Value']], use_container_width=True)
        else:
            st.warning("Please select at least one country to view the graph.")

except Exception as e:
    st.error(f"Waiting for data pipeline to complete... Error: {e}")
    st.info("If you just pushed the code, wait 1 minute for the GitHub Action to generate the CSV.")

st.sidebar.markdown("---")
st.sidebar.info("Data automatically updated via GitHub Actions.")