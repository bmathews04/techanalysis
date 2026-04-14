from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import (
    DEFAULT_INTERVAL,
    DEFAULT_PERIOD,
    SUPPORTED_INTERVALS,
    SUPPORTED_PERIODS,
)
from src.screener.screener import parse_tickers, run_market_screen


st.set_page_config(
    page_title="Market Screener",
    page_icon="🧭",
    layout="wide",
)

st.title("Market Screener")
st.caption("Screen a custom list of tickers for strong bullish and strong bearish setups.")

DEFAULT_WATCHLIST = """AAPL
MSFT
NVDA
AMZN
META
GOOGL
TSLA
AMD
NFLX
SPY
QQQ
IWM
"""

with st.sidebar:
    st.header("Screening inputs")

    with st.form("screener_form"):
        tickers_raw = st.text_area(
            "Ticker list",
            value=DEFAULT_WATCHLIST,
            height=260,
            help="Enter tickers separated by commas, spaces, or new lines.",
        )

        period = st.selectbox(
            "Period",
            options=SUPPORTED_PERIODS,
            index=SUPPORTED_PERIODS.index(DEFAULT_PERIOD),
        )

        interval = st.selectbox(
            "Interval",
            options=SUPPORTED_INTERVALS,
            index=SUPPORTED_INTERVALS.index(DEFAULT_INTERVAL),
        )

        benchmark = st.text_input(
            "Benchmark",
            value="SPY",
            help="Used for relative strength comparison.",
        )

        submitted = st.form_submit_button(
            "Run screen",
            type="primary",
            use_container_width=True,
        )

st.markdown(
    """
This page runs the existing single-ticker analysis pipeline across a list of tickers and groups them into:

- **Strong bullish**
- **Bullish**
- **Strong bearish**
- **Bearish**
- **Mixed**
"""
)

if not submitted:
    st.info("Enter a ticker list in the sidebar and click **Run screen**.")
    st.stop()

tickers = parse_tickers(tickers_raw)

if not tickers:
    st.warning("No valid tickers were provided.")
    st.stop()

with st.spinner(f"Screening {len(tickers)} tickers..."):
    screen_result = run_market_screen(
        tickers=tickers,
        period=period,
        interval=interval,
        benchmark=benchmark,
    )


def to_dataframe(items: list) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(
            columns=[
                "Ticker",
                "Classification",
                "Trend",
                "Agreement",
                "Trend Score",
                "Momentum",
                "Volatility",
                "Volume",
                "Structure",
                "Summary",
            ]
        )

    return pd.DataFrame(
        [
            {
                "Ticker": item.ticker,
                "Classification": item.classification,
                "Trend": item.trend_label,
                "Agreement": item.agreement_label,
                "Trend Score": item.trend_score,
                "Momentum": item.momentum_score,
                "Volatility": item.volatility_score,
                "Volume": item.volume_score,
                "Structure": item.structure_score,
                "Summary": item.summary_text,
            }
            for item in items
        ]
    )


top1, top2, top3, top4, top5 = st.columns(5)
with top1:
    st.metric("Input tickers", len(tickers))
with top2:
    st.metric("Strong bullish", len(screen_result.strong_bullish))
with top3:
    st.metric("Bullish", len(screen_result.bullish))
with top4:
    st.metric("Strong bearish", len(screen_result.strong_bearish))
with top5:
    st.metric("Bearish", len(screen_result.bearish))

st.divider()

bull_tab, bear_tab, all_tab, skipped_tab = st.tabs(
    ["Strong Bullish", "Strong Bearish", "All Results", "Skipped"]
)

with bull_tab:
    st.subheader("Strong bullish")
    bullish_df = to_dataframe(screen_result.strong_bullish)
    if bullish_df.empty:
        st.info("No strong bullish tickers found in this run.")
    else:
        st.dataframe(bullish_df, use_container_width=True)

    st.subheader("Bullish")
    bullish_df_2 = to_dataframe(screen_result.bullish)
    if bullish_df_2.empty:
        st.info("No additional bullish tickers found in this run.")
    else:
        st.dataframe(bullish_df_2, use_container_width=True)

with bear_tab:
    st.subheader("Strong bearish")
    bearish_df = to_dataframe(screen_result.strong_bearish)
    if bearish_df.empty:
        st.info("No strong bearish tickers found in this run.")
    else:
        st.dataframe(bearish_df, use_container_width=True)

    st.subheader("Bearish")
    bearish_df_2 = to_dataframe(screen_result.bearish)
    if bearish_df_2.empty:
        st.info("No additional bearish tickers found in this run.")
    else:
        st.dataframe(bearish_df_2, use_container_width=True)

with all_tab:
    combined = (
        screen_result.strong_bullish
        + screen_result.bullish
        + screen_result.mixed
        + screen_result.bearish
        + screen_result.strong_bearish
    )
    all_df = to_dataframe(combined)
    if all_df.empty:
        st.info("No completed ticker analyses were returned.")
    else:
        st.dataframe(all_df, use_container_width=True)

with skipped_tab:
    st.subheader("Skipped tickers")
    if not screen_result.skipped:
        st.success("No tickers were skipped.")
    else:
        skipped_df = pd.DataFrame(
            screen_result.skipped,
            columns=["Ticker", "Reason"],
        )
        st.dataframe(skipped_df, use_container_width=True)
