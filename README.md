# Technical Education Assistant

A Streamlit-based single-ticker technical analysis education assistant.

The goal of this project is to help users make smarter, more informed market participation decisions by translating raw technical analysis into clear, structured, plain-English insight.

This app is **not** intended to provide financial advice or guaranteed predictions.  
It is designed to act as an educational decision assistant by analyzing one ticker at a time and explaining:

- the current trend
- the strength and health of that trend
- momentum, volatility, volume, and market structure
- likely near-term scenarios
- participation styles that may fit the current setup
- risk and invalidation levels

## Product vision

A user should be able to:

1. open the Streamlit app
2. enter a ticker
3. run a full technical analysis
4. view a clean, highly informative UI
5. understand what the chart is doing, why it matters, and what to watch next

The app is designed to feel like a smart technical chart coach rather than a raw indicator dashboard.

## Planned core outputs

For each ticker, the app will provide:

- market regime classification
- trend score
- momentum score
- volatility score
- volume confirmation score
- structure score
- signal agreement / disagreement
- plain-English summary
- bull / base / bear scenarios
- participation guidance
- risk and invalidation framework
- annotated charts and supporting indicator panels

## Repo structure

```text
technical-education-assistant/
├─ .streamlit/
│  └─ config.toml
│
├─ app/
│  ├─ Home.py
│  └─ pages/
│     ├─ 1_Analyze_Ticker.py
│     └─ 2_Methodology.py
│
├─ src/
│  ├─ config/
│  │  └─ settings.py
│  ├─ data/
│  │  ├─ fetch.py
│  │  ├─ normalize.py
│  │  └─ validate.py
│  ├─ indicators/
│  │  ├─ trend.py
│  │  ├─ momentum.py
│  │  ├─ volatility.py
│  │  ├─ volume.py
│  │  └─ structure.py
│  ├─ analysis/
│  │  ├─ trend_classifier.py
│  │  ├─ signal_scores.py
│  │  ├─ signal_agreement.py
│  │  ├─ scenario_engine.py
│  │  ├─ participation_guidance.py
│  │  └─ recent_changes.py
│  ├─ charts/
│  │  ├─ main_chart.py
│  │  ├─ subcharts.py
│  │  └─ annotations.py
│  ├─ explain/
│  │  ├─ summary_text.py
│  │  ├─ evidence_builder.py
│  │  └─ glossary.py
│  ├─ pipeline/
│  │  └─ build_analysis.py
│  └─ utils/
│     ├─ formatting.py
│     ├─ dates.py
│     └─ math_helpers.py
│
├─ tests/
│  ├─ test_indicators.py
│  ├─ test_classifier.py
│  └─ test_pipeline.py
│
├─ requirements.txt
├─ README.md
├─ .gitignore
└─ LICENSE
