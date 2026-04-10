from __future__ import annotations

import streamlit as st

from src.config.settings import (
    DEFAULT_INTERVAL,
    DEFAULT_PERIOD,
    DEFAULT_TICKER,
    SUPPORTED_INTERVALS,
    SUPPORTED_PERIODS,
)
from src.charts.main_chart import build_main_price_chart
from src.charts.subcharts import (
    build_atr_chart,
    build_macd_chart,
    build_rsi_chart,
    build_volume_chart,
)
from src.pipeline.build_analysis import build_full_analysis


st.set_page_config(
    page_title="Analyze Ticker",
    page_icon="📊",
    layout="wide",
)

st.title("Analyze Ticker")
st.caption("Single-ticker technical analysis with educational interpretation.")

with st.sidebar:
    st.header("Inputs")

    ticker = st.text_input(
        "Ticker",
        value=st.session_state.get("ticker", DEFAULT_TICKER),
        help="Enter a single stock or ETF ticker.",
    )

    period = st.selectbox(
        "Period",
        options=SUPPORTED_PERIODS,
        index=SUPPORTED_PERIODS.index(
            st.session_state.get("period", DEFAULT_PERIOD)
            if st.session_state.get("period", DEFAULT_PERIOD) in SUPPORTED_PERIODS
            else DEFAULT_PERIOD
        ),
    )

    interval = st.selectbox(
        "Interval",
        options=SUPPORTED_INTERVALS,
        index=SUPPORTED_INTERVALS.index(
            st.session_state.get("interval", DEFAULT_INTERVAL)
            if st.session_state.get("interval", DEFAULT_INTERVAL) in SUPPORTED_INTERVALS
            else DEFAULT_INTERVAL
        ),
    )

    st.subheader("Chart overlays")
    show_bollinger = st.checkbox("Show Bollinger Bands", value=True)
    show_sma = st.checkbox("Show SMAs", value=True)
    show_ema = st.checkbox("Show EMAs", value=False)

    run_analysis = st.button("Run analysis", type="primary", use_container_width=True)

if run_analysis:
    st.session_state["ticker"] = ticker
    st.session_state["period"] = period
    st.session_state["interval"] = interval

if "analysis_ran" not in st.session_state:
    st.session_state["analysis_ran"] = False

if run_analysis:
    st.session_state["analysis_ran"] = True

if not st.session_state["analysis_ran"]:
    st.info("Enter a ticker in the sidebar and click **Run analysis** to begin.")
    st.stop()

try:
    with st.spinner("Running technical analysis..."):
        result = build_full_analysis(
            ticker=st.session_state["ticker"],
            period=st.session_state["period"],
            interval=st.session_state["interval"],
        )
except Exception as exc:
    st.error(f"Analysis failed: {exc}")
    st.stop()

# Header summary
top1, top2, top3, top4, top5, top6 = st.columns(6)

with top1:
    st.metric("Ticker", result.ticker)
with top2:
    st.metric("Market state", result.trend.label)
with top3:
    st.metric("Trend strength", f"{result.scores.trend}/100")
with top4:
    st.metric("Signal agreement", result.agreement.label)
with top5:
    st.metric("Participation fit", result.guidance.posture)
with top6:
    st.metric("Guidance confidence", f"{result.guidance.confidence:.1f}/10")

st.divider()

summary_left, summary_right = st.columns([1.7, 1])

with summary_left:
    st.subheader("Executive summary")
    st.write(result.summary_text)

    st.subheader("Why the app thinks that")
    st.markdown(f"**Trend reason:** {result.trend.reason}")
    st.markdown(f"**Agreement:** {result.agreement.reason}")
    st.markdown(f"**Participation framing:** {result.guidance.summary}")

with summary_right:
    st.subheader("Primary considerations")
    for item in result.guidance.considerations:
        st.markdown(f"- {item}")

    st.subheader("Caution flags")
    if result.guidance.caution_flags or result.evidence.risk_flags:
        merged_flags = list(dict.fromkeys(result.guidance.caution_flags + result.evidence.risk_flags))
        for flag in merged_flags:
            st.markdown(f"- {flag}")
    else:
        st.markdown("- No major caution flags identified by the current rules.")

st.divider()

# Main chart
st.subheader("Price chart")
main_fig = build_main_price_chart(
    result.data,
    ticker=result.ticker,
    show_bollinger=show_bollinger,
    show_sma=show_sma,
    show_ema=show_ema,
)
st.plotly_chart(main_fig, use_container_width=True)

st.divider()

# Scorecards
st.subheader("Technical scorecard")
s1, s2, s3, s4, s5 = st.columns(5)
with s1:
    st.metric("Trend", result.scores.trend)
with s2:
    st.metric("Momentum", result.scores.momentum)
with s3:
    st.metric("Volatility", result.scores.volatility)
with s4:
    st.metric("Volume", result.scores.volume)
with s5:
    st.metric("Structure", result.scores.structure)

st.divider()

# Evidence tabs
tabs = st.tabs(
    [
        "Trend",
        "Momentum",
        "Volatility",
        "Volume",
        "Structure",
        "Scenarios",
        "Recent changes",
        "Data snapshot",
    ]
)

with tabs[0]:
    st.subheader("Trend evidence")
    for item in result.evidence.trend:
        st.markdown(f"- {item}")

with tabs[1]:
    st.subheader("Momentum evidence")
    for item in result.evidence.momentum:
        st.markdown(f"- {item}")
    st.plotly_chart(build_rsi_chart(result.data), use_container_width=True)
    st.plotly_chart(build_macd_chart(result.data), use_container_width=True)

with tabs[2]:
    st.subheader("Volatility evidence")
    for item in result.evidence.volatility:
        st.markdown(f"- {item}")
    st.plotly_chart(build_atr_chart(result.data), use_container_width=True)

with tabs[3]:
    st.subheader("Volume evidence")
    for item in result.evidence.volume:
        st.markdown(f"- {item}")
    st.plotly_chart(build_volume_chart(result.data), use_container_width=True)

with tabs[4]:
    st.subheader("Structure evidence")
    for item in result.evidence.structure:
        st.markdown(f"- {item}")

with tabs[5]:
    st.subheader("Bull / Base / Bear scenarios")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"### {result.scenarios.bull.title}")
        st.markdown(f"**Trigger:** {result.scenarios.bull.trigger}")
        st.markdown(f"**Implication:** {result.scenarios.bull.implication}")
        st.markdown("**Watch items:**")
        for item in result.scenarios.bull.watch_items:
            st.markdown(f"- {item}")

    with c2:
        st.markdown(f"### {result.scenarios.base.title}")
        st.markdown(f"**Trigger:** {result.scenarios.base.trigger}")
        st.markdown(f"**Implication:** {result.scenarios.base.implication}")
        st.markdown("**Watch items:**")
        for item in result.scenarios.base.watch_items:
            st.markdown(f"- {item}")

    with c3:
        st.markdown(f"### {result.scenarios.bear.title}")
        st.markdown(f"**Trigger:** {result.scenarios.bear.trigger}")
        st.markdown(f"**Implication:** {result.scenarios.bear.implication}")
        st.markdown("**Watch items:**")
        for item in result.scenarios.bear.watch_items:
            st.markdown(f"- {item}")

with tabs[6]:
    st.subheader("Recent technical changes")
    if result.recent_changes:
        for item in result.recent_changes:
            st.markdown(f"- {item}")
    else:
        st.markdown("No notable recent technical changes were detected by the current rules.")

with tabs[7]:
    st.subheader("Latest data snapshot")
    preview_cols = [
        col
        for col in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "SMA_20",
            "SMA_50",
            "SMA_200",
            "RSI_14",
            "MACD_line",
            "MACD_signal",
            "MACD_hist",
            "ATR_14",
            "BB_upper",
            "BB_mid",
            "BB_lower",
            "Relative_Volume_20",
            "Rolling_Resistance_20",
            "Rolling_Support_20",
        ]
        if col in result.data.columns
    ]
    st.dataframe(result.data[preview_cols].tail(20), use_container_width=True)

st.divider()

with st.expander("Methodology notes"):
    st.markdown(
        """
This page uses a rule-based educational framework built from:
- trend indicators,
- momentum indicators,
- volatility measures,
- volume confirmation,
- and price structure context.

The goal is not to predict the future with certainty. The goal is to translate the current technical condition into a readable framework for understanding what the chart is doing now.
"""
    )

st.caption(
    "Educational use only. This tool does not provide financial, investment, legal, or tax advice."
)
