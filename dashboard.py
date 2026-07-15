"""
dashboard.py
Streamlit dashboard for the Trade Settlement Anomaly Detection tool.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from detect_anomalies import run_detection

st.set_page_config(page_title="Trade Anomaly Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("trades.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    scored = run_detection(df)
    return scored

df = load_data()

st.title("📊 Trade Settlement Anomaly Detection & Automation Dashboard")
st.caption("Simulated trading ops dashboard — flags high-risk trades and automates review queues.")

# --- KPI Row ---
col1, col2, col3, col4 = st.columns(4)
total_trades = len(df)
failed_rate = (df["status"] == "FAILED").mean() * 100
flagged_rate = df["flagged"].mean() * 100
total_volume = df["amount_usd"].sum()

col1.metric("Total Trades", f"{total_trades:,}")
col2.metric("Failed Settlement Rate", f"{failed_rate:.1f}%")
col3.metric("Flagged for Review", f"{flagged_rate:.1f}%")
col4.metric("Total Volume (USD)", f"${total_volume/1e6:.1f}M")

st.divider()

# --- Trend chart ---
st.subheader("Daily Trade Volume & Flagged Trades")
df["date"] = df["timestamp"].dt.date
daily = df.groupby("date").agg(
    total_trades=("trade_id", "count"),
    flagged_trades=("flagged", "sum")
).reset_index()

fig = px.line(daily, x="date", y=["total_trades", "flagged_trades"],
              labels={"value": "Count", "date": "Date"},
              title=None)
st.plotly_chart(fig, use_container_width=True)

# --- Breakdown charts ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Trades by Status")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig2 = px.pie(status_counts, names="status", values="count")
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    st.subheader("Trades by Instrument")
    inst_counts = df["instrument"].value_counts().reset_index()
    inst_counts.columns = ["instrument", "count"]
    fig3 = px.bar(inst_counts, x="instrument", y="count")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- Flagged trades table ---
st.subheader("🚩 Flagged Trades — Needs Manual Review")
flagged_df = df[df["flagged"]].sort_values("risk_score", ascending=False)
st.dataframe(
    flagged_df[["trade_id", "timestamp", "counterparty", "instrument",
                "amount_usd", "status", "risk_score"]],
    use_container_width=True,
    height=400
)

st.caption(f"Showing {len(flagged_df)} of {total_trades} trades flagged by IsolationForest + rule-based checks.")
