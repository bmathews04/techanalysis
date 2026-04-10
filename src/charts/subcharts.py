"""
Supporting indicator chart builders.

Primary responsibility:
- build RSI, MACD, volume, and ATR charts
- keep each chart separate and readable
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def build_rsi_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    if "RSI_14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["RSI_14"],
                mode="lines",
                name="RSI 14",
            )
        )

    fig.add_hline(y=70, line_dash="dash", annotation_text="70")
    fig.add_hline(y=50, line_dash="dot", annotation_text="50")
    fig.add_hline(y=30, line_dash="dash", annotation_text="30")

    fig.update_layout(
        title="RSI",
        xaxis_title="Date",
        yaxis_title="RSI",
        height=260,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        hovermode="x unified",
        showlegend=False,
    )
    return fig


def build_macd_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    if "MACD_line" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MACD_line"],
                mode="lines",
                name="MACD",
            )
        )

    if "MACD_signal" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MACD_signal"],
                mode="lines",
                name="Signal",
            )
        )

    if "MACD_hist" in df.columns:
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["MACD_hist"],
                name="Histogram",
            )
        )

    fig.add_hline(y=0, line_dash="dot")

    fig.update_layout(
        title="MACD",
        xaxis_title="Date",
        yaxis_title="Value",
        height=300,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        hovermode="x unified",
    )
    return fig


def build_volume_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
        )
    )

    if "Volume_MA_20" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Volume_MA_20"],
                mode="lines",
                name="Volume MA 20",
            )
        )

    fig.update_layout(
        title="Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=280,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        hovermode="x unified",
    )
    return fig


def build_atr_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    if "ATR_14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["ATR_14"],
                mode="lines",
                name="ATR 14",
            )
        )

    fig.update_layout(
        title="ATR",
        xaxis_title="Date",
        yaxis_title="ATR",
        height=260,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        hovermode="x unified",
        showlegend=False,
    )
    return fig
