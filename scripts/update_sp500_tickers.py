from __future__ import annotations

from pathlib import Path

import pandas as pd


WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def fetch_sp500_tickers() -> list[str]:
    tables = pd.read_html(WIKI_URL)
    if not tables:
        raise RuntimeError("No tables found on Wikipedia S&P 500 page.")

    companies = tables[0]
    if "Symbol" not in companies.columns:
        raise RuntimeError("Wikipedia S&P 500 table missing 'Symbol' column.")

    tickers = (
        companies["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "-", regex=False)  # Yahoo-style symbols
        .tolist()
    )

    cleaned: list[str] = []
    seen: set[str] = set()

    for ticker in tickers:
        if ticker and ticker not in seen:
            seen.add(ticker)
            cleaned.append(ticker)

    return cleaned


def write_python_file(tickers: list[str], output_path: Path) -> None:
    lines = [
        "from __future__ import annotations",
        "",
        "# Auto-generated from Wikipedia S&P 500 constituents",
        f"# Total tickers: {len(tickers)}",
        "",
        "SP500_TICKERS = [",
    ]

    for ticker in tickers:
        lines.append(f'    "{ticker}",')

    lines.append("]")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    tickers = fetch_sp500_tickers()

    if len(tickers) < 500:
        raise RuntimeError(
            f"Expected about 500+ ticker entries, got {len(tickers)}. Aborting."
        )

    output_path = Path("src/data/sp500_tickers.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_python_file(tickers, output_path)

    print(f"Wrote {len(tickers)} tickers to {output_path}")


if __name__ == "__main__":
    main()
