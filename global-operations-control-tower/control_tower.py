# control_tower_enhanced.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Load Data ---
user_reports = pd.read_csv('user_reports.csv', parse_dates=['date'])
response_times = pd.read_csv('response_times.csv', parse_dates=['date'])
policy_compliance = pd.read_csv('policy_compliance.csv', parse_dates=['date'])

# --- Map synthetic regions to example countries ---
region_to_country = {
    "North America": "United States",
    "Europe": "Germany",
    "Asia": "India",
    "South America": "Brazil",
    "Africa": "South Africa"
}

user_reports['country'] = user_reports['region'].map(region_to_country)
response_times['country'] = response_times['region'].map(region_to_country)
policy_compliance['country'] = policy_compliance['region'].map(region_to_country)

# --- Streamlit Config ---
st.set_page_config(page_title="Global Operations Control Tower", layout="wide")
st.title("🌐 Global Operations Control Tower")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
selected_region = st.sidebar.multiselect("Select Region", options=user_reports['region'].unique(), default=user_reports['region'].unique())
selected_app = st.sidebar.multiselect("Select App", options=user_reports['app'].unique(), default=user_reports['app'].unique())

# Filter datasets
reports_filtered = user_reports[(user_reports['region'].isin(selected_region)) & (user_reports['app'].isin(selected_app))]
response_filtered = response_times[(response_times['region'].isin(selected_region)) & (response_times['app'].isin(selected_app))]
compliance_filtered = policy_compliance[(policy_compliance['region'].isin(selected_region)) & (policy_compliance['app'].isin(selected_app))]

# --- KPI Metrics ---
st.header("📊 Key Metrics")
col1, col2, col3 = st.columns(3)

avg_resolution = response_filtered['resolution_time'].mean()
high_severity_count = reports_filtered[reports_filtered['severity']=='high'].shape[0]
avg_compliance = compliance_filtered['compliance_score'].mean()

col1.metric("Avg. Resolution Time (hrs)", f"{avg_resolution:.2f}")
col2.metric("High Severity Reports", high_severity_count)
col3.metric("Avg. Compliance Score", f"{avg_compliance:.2f}")

# --- Time Series Trends ---
st.header("📈 Trends Over Time")
reports_trend = reports_filtered.groupby('date').size().reset_index(name='report_count')
response_trend = response_filtered.groupby('date')['resolution_time'].mean().reset_index()
compliance_trend = compliance_filtered.groupby('date')['compliance_score'].mean().reset_index()

fig1 = px.line(reports_trend, x='date', y='report_count', title="Daily User Reports")
fig2 = px.line(response_trend, x='date', y='resolution_time', title="Daily Avg Resolution Time")
fig3 = px.line(compliance_trend, x='date', y='compliance_score', title="Daily Avg Compliance Score")

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)

# --- High-Level Metrics by Region / App ---
st.header("📊 High-Level Metrics by Region / App")

# Aggregations
region_severity = reports_filtered[reports_filtered['severity']=='high'].groupby('country').size().reset_index(name='high_severity_count')
app_severity = reports_filtered[reports_filtered['app']=='Facebook'].groupby('app').size().reset_index(name='high_severity_count')  # example

region_resolution = response_filtered.groupby('country')['resolution_time'].mean().reset_index()
app_resolution = response_filtered.groupby('app')['resolution_time'].mean().reset_index()

region_compliance = compliance_filtered.groupby('country')['compliance_score'].mean().reset_index()
app_compliance = compliance_filtered.groupby('app')['compliance_score'].mean().reset_index()

# --- Bar Charts by Region ---
st.subheader("Metrics by Region")
fig_bar_severity = px.bar(region_severity, x='country', y='high_severity_count', color='high_severity_count', title='High Severity Reports by Country')
fig_bar_resolution = px.bar(region_resolution, x='country', y='resolution_time', color='resolution_time', title='Average Resolution Time by Country')
fig_bar_compliance = px.bar(region_compliance, x='country', y='compliance_score', color='compliance_score', title='Average Compliance Score by Country')

st.plotly_chart(fig_bar_severity, use_container_width=True)
st.plotly_chart(fig_bar_resolution, use_container_width=True)
st.plotly_chart(fig_bar_compliance, use_container_width=True)

# --- Choropleth Maps ---
st.header("🌍 Regional KPIs Heatmap")

# High severity
fig_heatmap_severity = px.choropleth(
    region_severity,
    locations='country',
    locationmode='country names',
    color='high_severity_count',
    color_continuous_scale='Reds',
    title='High Severity Reports by Country'
)
st.plotly_chart(fig_heatmap_severity, use_container_width=True)

# Resolution time
fig_heatmap_resolution = px.choropleth(
    region_resolution,
    locations='country',
    locationmode='country names',
    color='resolution_time',
    color_continuous_scale='Blues',
    title='Average Resolution Time by Country'
)
st.plotly_chart(fig_heatmap_resolution, use_container_width=True)

# Compliance score
fig_heatmap_compliance = px.choropleth(
    region_compliance,
    locations='country',
    locationmode='country names',
    color='compliance_score',
    color_continuous_scale='Greens',
    title='Average Compliance Score by Country'
)
st.plotly_chart(fig_heatmap_compliance, use_container_width=True)

# --- Alerts ---
st.header("⚠️ Alerts")
alert_threshold_resolution = 6
alert_threshold_compliance = 75
alert_threshold_reports = 50

alerts = []

# Resolution time alerts
for idx, row in region_resolution.iterrows():
    if row['resolution_time'] > alert_threshold_resolution:
        alerts.append(f"⚠️ {row['country']} has high average resolution time: {row['resolution_time']:.2f} hrs")

# Compliance alerts
for idx, row in region_compliance.iterrows():
    if row['compliance_score'] < alert_threshold_compliance:
        alerts.append(f"⚠️ {row['country']} has low compliance score: {row['compliance_score']:.2f}")

# High severity alerts
for idx, row in region_severity.iterrows():
    if row['high_severity_count'] > alert_threshold_reports:
        alerts.append(f"⚠️ {row['country']} has high number of severe reports: {row['high_severity_count']}")

if alerts:
    st.write("\n".join(alerts))
else:
    st.success("No alerts! All countries within thresholds ✅")
