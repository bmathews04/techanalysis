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
from src.screener.screener import (
    get_sp500_tickers,
    parse_tickers,
    run_market_screen,
    slice_ticker_batch,
)

st.set_page_config(
    page_title="Market Screener",
    page_icon="🧭",
    layout="wide",
)

st.title("Market Screener")
st.caption("Screen a custom list of tickers for strong bullish and strong bearish setups.")


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def load_sp500_tickers() -> list[str]:
    return get_sp500_tickers(use_live_fetch=False)


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


def get_preset_text(preset_name: str) -> str:
    if preset_name == "S&P 500":
        return "\n".join(load_sp500_tickers())

    if preset_name == "Mega Cap Tech":
        return "\n".join(
            [
                "AAPL",
                "MSFT",
                "NVDA",
                "AMZN",
                "META",
                "GOOGL",
                "TSLA",
                "AMD",
                "NFLX",
                "AVGO",
                "ORCL",
                "CRM",
                "ADBE",
                "INTC",
                "CSCO",
                "QCOM",
            ]
        )

    if preset_name == "Index ETFs":
        return "\n".join(
            [
                "SPY",
                "QQQ",
                "IWM",
                "DIA",
                "XLF",
                "XLK",
                "XLE",
                "XLV",
                "XLI",
                "XLP",
                "XLY",
                "XLU",
                "XLB",
                "XLRE",
                "XLC",
            ]
        )

    return DEFAULT_WATCHLIST


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


with st.sidebar:
    st.header("Screening inputs")

    preset = st.selectbox(
        "Universe preset",
        options=[
            "Custom",
            "S&P 500",
            "Mega Cap Tech",
            "Index ETFs",
        ],
        index=0,
    )

    default_text = get_preset_text(preset)

    with st.form("screener_form"):
        tickers_raw = st.text_area(
            "Ticker list",
            value=default_text,
            height=320,
            help="Enter tickers separated by commas, spaces, semicolons, or new lines.",
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

        batch_size = st.selectbox(
            "Batch size",
            options=[25, 50, 75, 100],
            index=3,
            help="Smaller batches are slower overall but more reliable against Yahoo rate limits.",
        )

        batch_number = st.number_input(
            "Batch number",
            min_value=1,
            value=1,
            step=1,
            help="Batch 1 screens the first chunk, batch 2 the next chunk, and so on.",
        )

        per_ticker_pause_seconds = st.selectbox(
            "Pause per ticker (seconds)",
            options=[0.25, 0.5, 0.75, 1.0],
            index=1,
            help="Higher pause reduces the chance of Yahoo rate limiting.",
        )
        
        submitted = st.form_submit_button(
            "Run screen",
            type="primary",
            width="stretch",
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
    st.info("Choose a preset or enter your own ticker list, then click **Run screen**.")
    st.stop()

tickers = parse_tickers(tickers_raw)

if not tickers:
    st.warning("No valid tickers were provided.")
    st.stop()

batch_tickers, start_idx, end_idx, total_tickers = slice_ticker_batch(
    tickers=tickers,
    batch_size=batch_size,
    batch_number=int(batch_number),
)

if not batch_tickers:
    st.warning(
        f"Batch {int(batch_number)} is out of range. "
        f"You only have {total_tickers} tickers with batch size {batch_size}."
    )
    st.stop()

total_batches = (total_tickers + batch_size - 1) // batch_size

if total_tickers > batch_size:
    st.info(
        f"Screening batch {int(batch_number)} of {total_batches}: "
        f"tickers {start_idx + 1} to {end_idx} out of {total_tickers} total."
    )

tickers = batch_tickers

with st.spinner(
    f"Screening {len(tickers)} tickers... this can take a while and may hit Yahoo rate limits."
):
    screen_result = run_market_screen(
        tickers=tickers,
        period=period,
        interval=interval,
        benchmark=benchmark,
        per_ticker_pause_seconds=float(per_ticker_pause_seconds),
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

if total_tickers > batch_size:
    prev_col, mid_col, next_col = st.columns(3)

    with prev_col:
        if int(batch_number) > 1:
            st.caption(f"Previous batch: {int(batch_number) - 1}")

    with mid_col:
        st.caption(f"Current batch: {int(batch_number)} of {total_batches}")

    with next_col:
        if int(batch_number) < total_batches:
            st.caption(f"Next batch: {int(batch_number) + 1}")

st.divider()

bull_tab, bear_tab, all_tab, skipped_tab = st.tabs(
    ["Strong Bullish", "Strong Bearish", "All Results", "Skipped"]
)

with bull_tab:
    st.subheader("Strong bullish")
    strong_bullish_df = to_dataframe(screen_result.strong_bullish)
    if strong_bullish_df.empty:
        st.info("No strong bullish tickers found in this run.")
    else:
        st.dataframe(strong_bullish_df, width="stretch")

    st.subheader("Bullish")
    bullish_df = to_dataframe(screen_result.bullish)
    if bullish_df.empty:
        st.info("No additional bullish tickers found in this run.")
    else:
        st.dataframe(bullish_df, width="stretch")

with bear_tab:
    st.subheader("Strong bearish")
    strong_bearish_df = to_dataframe(screen_result.strong_bearish)
    if strong_bearish_df.empty:
        st.info("No strong bearish tickers found in this run.")
    else:
        st.dataframe(strong_bearish_df, width="stretch")

    st.subheader("Bearish")
    bearish_df = to_dataframe(screen_result.bearish)
    if bearish_df.empty:
        st.info("No additional bearish tickers found in this run.")
    else:
        st.dataframe(bearish_df, width="stretch")

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
        st.dataframe(all_df, width="stretch")

with skipped_tab:
    st.subheader("Skipped tickers")
    if not screen_result.skipped:
        st.success("No tickers were skipped.")
    else:
        skipped_df = pd.DataFrame(
            screen_result.skipped,
            columns=["Ticker", "Reason"],
        )
        st.dataframe(skipped_df, width="stretch")
