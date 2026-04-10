from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.explain.glossary import GLOSSARY

st.set_page_config(
    page_title="Methodology",
    page_icon="📘",
    layout="wide",
)

st.title("Methodology")
st.caption("How the technical education assistant thinks about charts.")

st.markdown(
    """
This project uses a **rule-based technical framework** to describe a ticker's current chart condition.

The goal is not to make absolute predictions.  
The goal is to answer five core questions clearly:

1. What trend is the ticker in?
2. How healthy is that trend?
3. Are momentum, volatility, volume, and structure aligned?
4. What are the most reasonable near-term scenarios?
5. What type of participation posture best fits the current chart environment?
"""
)

st.divider()

st.subheader("How the engine is structured")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
### Data layer
- Fetches OHLCV market data
- Normalizes column names and index format
- Validates that the dataset is usable

### Indicator layer
- Trend: moving averages, EMA alignment, slope, distance from averages
- Momentum: RSI, MACD
- Volatility: ATR, Bollinger Bands
- Volume: relative volume, OBV
- Structure: support, resistance, breakout/breakdown context
"""
    )

with col2:
    st.markdown(
        """
### Analysis layer
- Classifies the overall trend regime
- Scores trend, momentum, volatility, volume, and structure
- Assesses signal agreement or disagreement
- Builds participation guidance
- Generates bull/base/bear scenarios
- Detects recent technical changes

### Explanation layer
- Produces plain-English summary text
- Builds grouped evidence for each category
- Surfaces risk and caution flags
"""
    )

st.divider()

st.subheader("How to interpret the outputs")

st.markdown(
    """
### Trend regime
The trend regime is a plain-English label such as:
- Strong uptrend
- Healthy uptrend
- Breakout / continuation attempt
- Range-bound / consolidation
- Bullish reversal attempt
- Healthy downtrend
- Breakdown / continuation attempt
- Mixed / transition

### Technical scores
Scores range from 0 to 100 and summarize how constructive or weak each category appears.

### Signal agreement
This shows whether the technical categories are telling a similar story or producing conflict.

### Participation posture
This is an educational framing of the chart environment, such as:
- Trend-friendly / accumulation-friendly
- Pullback-friendly / avoid chasing extension
- Breakout-watch / confirmation-focused
- Defensive / caution zone
- Patience / no clear edge
"""
)

st.divider()

st.subheader("Glossary")

for term, definition in GLOSSARY.items():
    with st.expander(term):
        st.write(definition)

st.divider()

st.subheader("Important limitations")

st.markdown(
    """
- This framework is **rule-based**, not omniscient.
- Indicators can conflict, lag, or behave differently in different volatility environments.
- A technically constructive chart can still fail.
- A technically weak chart can still bounce.
- No technical framework should be treated as certainty.

This tool is designed to improve interpretation and decision quality, not eliminate uncertainty.
"""
)

st.info(
    "This project is for educational and informational purposes only. "
    "It is not financial or investment advice."
)
