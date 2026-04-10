"""
Chart annotation helpers.

Primary responsibility:
- add summary annotations and key thesis markers to figures
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.explain.risk_builder import RiskFramework


def add_thesis_annotations(
    fig: go.Figure,
    df: pd.DataFrame,
    risk: RiskFramework,
    trend_label: str,
    posture: str,
) -> go.Figure:
    """
    Add a few lightweight annotations to the main chart.
    """
    out = go.Figure(fig)
    latest = df.iloc[-1]
    x_last = df.index[-1]
    close = float(latest["Close"])

    out.add_annotation(
        x=x_last,
        y=close,
        text=f"Trend: {trend_label}",
        showarrow=True,
        arrowhead=1,
        yshift=35,
    )

    out.add_annotation(
        xref="paper",
        yref="paper",
        x=0.01,
        y=0.98,
        text=f"Posture: {posture}",
        showarrow=False,
        borderpad=4,
        bgcolor="rgba(30,30,30,0.55)",
    )

    if "Rolling_Support_20" in df.columns and pd.notna(latest.get("Rolling_Support_20")):
        support = float(latest["Rolling_Support_20"])
        out.add_annotation(
            x=x_last,
            y=support,
            text="Support watch",
            showarrow=True,
            arrowhead=1,
            yshift=-28,
        )

    if "Rolling_Resistance_20" in df.columns and pd.notna(latest.get("Rolling_Resistance_20")):
        resistance = float(latest["Rolling_Resistance_20"])
        out.add_annotation(
            x=x_last,
            y=resistance,
            text="Resistance watch",
            showarrow=True,
            arrowhead=1,
            yshift=28,
        )

    out.update_layout(
        annotations=list(out.layout.annotations),
        title=f"{out.layout.title.text} | Thesis map",
    )

    return out
