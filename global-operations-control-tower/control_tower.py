# control_tower.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load Data ---
user_reports = pd.read_csv('user_reports.csv', parse_dates=['date'])
response_times = pd.read_csv('response_times.csv', parse_dates=['date'])
policy_compliance = pd.read_csv('policy_compliance.csv', parse_dates=['date'])

# --- Streamlit Page Config ---
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
# Group by date
reports_trend = reports_filtered.groupby('date').size().reset_index(name='report_count')
response_trend = response_filtered.groupby('date')['resolution_time'].mean().reset_index()
compliance_trend = compliance_filtered.groupby('date')['compliance_score'].mean().reset_index()

# Plotting
fig1 = px.line(reports_trend, x='date', y='report_count', title="Daily User Reports")
fig2 = px.line(response_trend, x='date', y='resolution_time', title="Daily Avg Resolution Time")
fig3 = px.line(compliance_trend, x='date', y='compliance_score', title="Daily Avg Compliance Score")

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)

# --- Anomaly Detection (Simple) ---
st.header("⚠️ Anomaly Detection")
z_score_threshold = 3
reports_trend['z_score'] = (reports_trend['report_count'] - reports_trend['report_count'].mean()) / reports_trend['report_count'].std()
anomalies = reports_trend[reports_trend['z_score'].abs() > z_score_threshold]

st.write("High Severity Report Spikes:")
st.dataframe(anomalies[['date', 'report_count', 'z_score']])