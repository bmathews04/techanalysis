from __future__ import annotations

from src.screener.screener import parse_tickers


def test_parse_tickers_deduplicates_and_uppercases() -> None:
    raw = "aapl, msft\nnvda AAPL\nspy"
    parsed = parse_tickers(raw)
    assert parsed == ["AAPL", "MSFT", "NVDA", "SPY"]
