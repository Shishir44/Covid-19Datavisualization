import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide"
)

# Add title and description
st.title("🦠 COVID-19 Global Dashboard")
st.markdown("""
This dashboard visualizes COVID-19 data across different countries and regions.
Data is updated regularly from reliable sources.
""")

# Function to load data
@st.cache_data
def load_data():
    # Replace this with your actual data loading logic
    # For example, you could load from a CSV file or API
    df = pd.read_csv('//data//covid-19.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Load the data
try:
    df = load_data()
except:
    st.error("Please ensure your COVID-19 data file is in the correct location!")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

# Country selection
countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(df['Country'].unique()),
    default=['Global']
)

# Date range selection
min_date = df['Date'].min()
max_date = df['Date'].max()

start_date = st.sidebar.date_input(
    "Start Date",
    min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date",
    max_date,
    min_value=min_date,
    max_value=max_date
)

# Filter data based on selection
mask = (
    df['Country'].isin(countries) &
    (df['Date'].dt.date >= start_date) &
    (df['Date'].dt.date <= end_date)
)
filtered_df = df.loc[mask]

# Create main dashboard layout
col1, col2, col3, col4 = st.columns(4)

# Key metrics
with col1:
    st.metric(
        "Total Cases",
        f"{filtered_df['Total Cases'].sum():,.0f}",
        f"{filtered_df['New Cases'].sum():+,.0f}"
    )

with col2:
    st.metric(
        "Total Deaths",
        f"{filtered_df['Total Deaths'].sum():,.0f}",
        f"{filtered_df['New Deaths'].sum():+,.0f}"
    )

with col3:
    recovery_rate = (filtered_df['Recovered'].sum() / filtered_df['Total Cases'].sum() * 100)
    st.metric(
        "Recovery Rate",
        f"{recovery_rate:.1f}%"
    )

with col4:
    vaccination_rate = (filtered_df['Total Vaccinations'].sum() / filtered_df['Population'].sum() * 100)
    st.metric(
        "Vaccination Rate",
        f"{vaccination_rate:.1f}%"
    )

# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🗺️ Geographic", "📊 Comparisons"])

with tab1:
    # Time series of cases
    st.subheader("Cases Over Time")
    fig_cases = px.line(
        filtered_df,
        x='Date',
        y='Total Cases',
        color='Country',
        title='Total COVID-19 Cases'
    )
    st.plotly_chart(fig_cases, use_container_width=True)

    # Vaccination progress
    st.subheader("Vaccination Progress")
    fig_vac = px.line(
        filtered_df,
        x='Date',
        y='Vaccination Rate',
        color='Country',
        title='Vaccination Rate Progress'
    )
    st.plotly_chart(fig_vac, use_container_width=True)

with tab2:
    # World map of cases
    st.subheader("Global Distribution")
    fig_map = px.choropleth(
        filtered_df,
        locations='Country',
        locationmode='country names',
        color='Total Cases',
        hover_name='Country',
        color_continuous_scale='Reds',
        title='Total Cases by Country'
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    # Bar chart comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Country")
        fig_bar = px.bar(
            filtered_df.groupby('Country')['Total Cases'].max().reset_index(),
            x='Country',
            y='Total Cases',
            title='Total Cases by Country'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("Deaths by Country")
        fig_bar2 = px.bar(
            filtered_df.groupby('Country')['Total Deaths'].max().reset_index(),
            x='Country',
            y='Total Deaths',
            title='Total Deaths by Country'
        )
        st.plotly_chart(fig_bar2, use_container_width=True)

# Add data source and update time
st.sidebar.markdown("---")
st.sidebar.caption("Data last updated: " + str(max_date.date()))
st.sidebar.caption("Source: [Dataset Source]")

# Add download button for the data
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="Download Data",
    data=filtered_df.to_csv().encode('utf-8'),
    file_name='covid_data.csv',
    mime='text/csv'
)