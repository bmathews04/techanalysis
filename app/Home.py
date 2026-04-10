from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Technical Education Assistant",
    page_icon="📈",
    layout="wide",
)

st.title("Technical Education Assistant")
st.caption("Single-ticker technical analysis explained in plain English.")

st.markdown(
    """
This app is designed to function like a **technical chart coach**.

Instead of dumping a pile of raw indicators onto the page, the goal is to help the user understand:

- what trend the ticker is in right now,
- how healthy that trend appears,
- whether momentum, volume, volatility, and structure agree,
- what the likely near-term scenarios look like,
- what type of participation posture may fit the setup,
- and what would weaken the current technical thesis.
"""
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Workflow", "1 ticker", "Educational analysis")
with col2:
    st.metric("Focus", "Technical state", "Trend + momentum + structure")
with col3:
    st.metric("Output style", "Plain English", "Scenario-based")

st.divider()

left, right = st.columns([1.4, 1])

with left:
    st.subheader("What the app will provide")
    st.markdown(
        """
When you analyze a ticker, the app is built to return:

- a **trend regime classification**
- **technical category scores** for trend, momentum, volatility, volume, and structure
- a **signal agreement** read to show whether the chart is aligned or conflicted
- **participation guidance** like accumulation-friendly, pullback-friendly, patience zone, or caution zone
- **bull, base, and bear scenarios**
- **recent technical changes**
- a **plain-English summary**
- supporting evidence to explain the read
"""
    )

    st.subheader("Design principles")
    st.markdown(
        """
- The app is meant to be **educational**, not predictive.
- “**No action**” is a valid outcome when the chart is unclear.
- The goal is **clarity**, not indicator overload.
- The analysis should translate technical inputs into **useful decision context**.
"""
    )

with right:
    st.subheader("How to use it")
    st.markdown(
        """
1. Open the **Analyze Ticker** page  
2. Enter a ticker symbol  
3. Choose a timeframe  
4. Run the analysis  
5. Review the summary, chart context, scenarios, and risks
"""
    )

    st.info(
        "This project is for educational and informational use only. "
        "It does not provide financial or investment advice."
    )

st.divider()

st.subheader("What is under the hood")
st.markdown(
    """
The current architecture is structured so the Streamlit UI stays thin while analysis logic lives in reusable Python modules.

The engine is designed to combine:
- market data normalization and validation,
- indicator calculations,
- trend and structure classification,
- rule-based scoring,
- scenario generation,
- and explanation building.
"""
)

with st.expander("See the product philosophy"):
    st.markdown(
        """
A lot of technical tools show you everything and explain nothing.

This project is trying to do the opposite:
- show the important technical evidence,
- explain what it means,
- and help the user think more clearly about market participation.

The product should feel less like a scanner and more like a disciplined technical reasoning assistant.
"""
    )

st.page_link("pages/1_Analyze_Ticker.py", label="Go to Analyze Ticker", icon="📊")
st.page_link("pages/2_Methodology.py", label="Go to Methodology", icon="📘")
