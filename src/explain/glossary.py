"""
Glossary content for methodology and UI help text.
"""

from __future__ import annotations

GLOSSARY: dict[str, str] = {
    "Trend regime": (
        "A plain-English label that describes the current chart environment, such as strong uptrend, "
        "healthy uptrend, range-bound consolidation, or downtrend."
    ),
    "RSI": (
        "Relative Strength Index. A momentum indicator that measures the speed and persistence of price moves. "
        "Higher readings generally reflect stronger momentum, while lower readings reflect weaker momentum."
    ),
    "MACD": (
        "Moving Average Convergence Divergence. A momentum and trend-following indicator built from moving averages. "
        "It can help show whether momentum is strengthening or fading."
    ),
    "ATR": (
        "Average True Range. A volatility measure that estimates how much price typically moves over a given period. "
        "It helps frame how calm or aggressive the current environment is."
    ),
    "Bollinger Bands": (
        "Bands plotted around a moving average using standard deviation. They help show whether price is relatively "
        "stretched, compressed, or trading near the center of its recent range."
    ),
    "OBV": (
        "On-Balance Volume. A cumulative volume measure that attempts to show whether buying or selling pressure is "
        "confirming price movement."
    ),
    "Support": (
        "An area where price has recently found buyers or stopped falling. A clean break below support can weaken the chart."
    ),
    "Resistance": (
        "An area where price has recently struggled to move higher. A clean break above resistance can strengthen the chart."
    ),
    "Breakout": (
        "A move above a recent resistance area. Stronger breakouts are usually supported by follow-through and healthy volume."
    ),
    "Breakdown": (
        "A move below a recent support area. Stronger breakdowns are often accompanied by weakness in trend and momentum."
    ),
    "EMA stack": (
        "The ordering of exponential moving averages. A bullish stack usually means shorter-term averages are above longer-term "
        "averages, which is often a sign of healthy trend alignment."
    ),
    "Signal agreement": (
        "A summary of whether trend, momentum, volatility, volume, and structure are telling the same story or giving mixed messages."
    ),
    "Participation posture": (
        "An educational framing of how favorable or unfavorable the chart may be for different styles of market participation, "
        "such as accumulation-friendly, pullback-friendly, patience zone, or caution zone."
    ),
    "Invaldation level": (
        "A key price area that would materially weaken the current technical thesis if lost. This helps frame risk and scenario planning."
    ),
    "Extension": (
        "A condition where price has moved far enough from its trend support or average behavior that chasing can become less attractive."
    ),
    "Compression": (
        "A period of reduced volatility or narrowing range. Compression can sometimes precede a larger move, but it does not guarantee direction."
    ),
}
