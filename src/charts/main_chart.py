"""
Main price chart builder.

Primary responsibility:
- build the primary candlestick chart
- add core overlays such as moving averages and Bollinger Bands
- annotate support, resistance, and key thesis levels
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def build_main_price_chart(
    df: pd.DataFrame,
    ticker: str,
    show_bollinger: bool = True,
    show_sma: bool = True,
    show_ema: bool = False,
) -> go.Figure:
    """
    Build the main candlestick chart with optional overlays.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        )
    )

    if show_sma:
        for col, label in [
            ("SMA_20", "SMA 20"),
            ("SMA_50", "SMA 50"),
            ("SMA_200", "SMA 200"),
        ]:
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[col],
                        mode="lines",
                        name=label,
                        line={"width": 1.8},
                    )
                )

    if show_ema:
        for col, label in [
            ("EMA_20", "EMA 20"),
            ("EMA_50", "EMA 50"),
            ("EMA_200", "EMA 200"),
        ]:
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[col],
                        mode="lines",
                        name=label,
                        line={"dash": "dot", "width": 1.2},
                    )
                )

    if show_bollinger:
        for col, label in [
            ("BB_upper", "BB Upper"),
            ("BB_mid", "BB Mid"),
            ("BB_lower", "BB Lower"),
        ]:
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[col],
                        mode="lines",
                        name=label,
                        line={"width": 1.0, "dash": "dash"},
                        opacity=0.7,
                    )
                )

    latest = df.iloc[-1]

    if "Rolling_Resistance_20" in df.columns and pd.notna(latest.get("Rolling_Resistance_20")):
        resistance = float(latest["Rolling_Resistance_20"])
        fig.add_hline(
            y=resistance,
            line_dash="dot",
            annotation_text=f"Resistance {resistance:.2f}",
            annotation_position="top left",
        )

    if "Rolling_Support_20" in df.columns and pd.notna(latest.get("Rolling_Support_20")):
        support = float(latest["Rolling_Support_20"])
        fig.add_hline(
            y=support,
            line_dash="dot",
            annotation_text=f"Support {support:.2f}",
            annotation_position="bottom left",
        )

    if "SMA_50" in df.columns and pd.notna(latest.get("SMA_50")):
        sma50 = float(latest["SMA_50"])
        fig.add_hline(
            y=sma50,
            line_dash="dash",
            annotation_text=f"SMA 50 {sma50:.2f}",
            annotation_position="right",
            opacity=0.45,
        )

    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        legend_title="Overlays",
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        height=700,
        hovermode="x unified",
    )

    return fig
