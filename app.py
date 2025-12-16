import streamlit as st
import pandas as pd
import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from run_pipeline import run
from src.indicators import add_indicators

st.set_page_config(
    page_title="Market Intelligence System",
    layout="wide"
)

st.title("📈 Market Intelligence & Trading Signals")

# -----------------------------
# User Input
# -----------------------------
symbol = st.text_input(
    "Enter NSE Stock Symbol (e.g. TCS.NS, INFY.NS)",
    value="TCS.NS"
)

# -----------------------------
# Run Pipeline
# -----------------------------
if st.button("Run Analysis"):
    with st.spinner("Running market analysis..."):
        result = run(symbol)

    st.success("Analysis completed")

    # Result is a dict
    st.subheader("📌 Latest Signal")
    st.metric("Stock", result["symbol"])
    st.metric("Signal", result["signal"])
    st.metric("Trend", result["trend"])

# -----------------------------
# Load Price Data
# -----------------------------
price_file = f"data/prices_{symbol}.csv"

if os.path.exists(price_file):
    price_df = pd.read_csv(price_file)

    # Ensure numeric
    price_df["Close"] = pd.to_numeric(price_df["Close"], errors="coerce")
    price_df["Date"] = pd.to_datetime(price_df["Date"])
    price_df = price_df.dropna()

    # Add indicators
    price_df = add_indicators(price_df)

    # -----------------------------
    # Plotly Chart
    # -----------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            f"{symbol} Price Chart with SMA",
            "RSI Indicator"
        )
    )

    # Price
    fig.add_trace(
        go.Scatter(
            x=price_df["Date"],
            y=price_df["Close"],
            name="Close Price",
            line=dict(color="royalblue")
        ),
        row=1,
        col=1
    )

    # SMA
    fig.add_trace(
        go.Scatter(
            x=price_df["Date"],
            y=price_df["SMA_20"],
            name="SMA 20",
            line=dict(color="orange", dash="dash")
        ),
        row=1,
        col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(
            x=price_df["Date"],
            y=price_df["RSI"],
            name="RSI",
            line=dict(color="purple")
        ),
        row=2,
        col=1
    )

    # RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(
        height=700,
        showlegend=True,
        title_text=f"📊 Technical Analysis for {symbol}"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Signal History
# -----------------------------
if os.path.exists("data/signals.csv"):
    st.subheader("📜 Signal History")
    signals_df = pd.read_csv("data/signals.csv")
    st.dataframe(signals_df.tail(10))
