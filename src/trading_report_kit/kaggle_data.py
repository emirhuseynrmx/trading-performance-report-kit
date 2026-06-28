from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

DATASET_SLUG = "serkanp/algorithmic-trading-strategy"
RAW_FILENAME = "AAPL.csv"

app = typer.Typer(help="Download and prepare Kaggle market data into a closed-trade ledger.")


def download_market_dataset(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "kaggle",
            "datasets",
            "download",
            "-d",
            DATASET_SLUG,
            "-p",
            str(data_dir),
            "--unzip",
        ],
        check=True,
    )
    raw_path = data_dir / RAW_FILENAME
    if not raw_path.exists():
        raise FileNotFoundError(f"Kaggle download completed but {RAW_FILENAME} was not found.")
    return raw_path


def build_trade_ledger_from_ohlc(raw: pd.DataFrame, max_trades: int = 180) -> pd.DataFrame:
    prices = raw.copy()
    prices["Date"] = pd.to_datetime(prices["Date"])
    prices = prices.sort_values("Date").reset_index(drop=True)
    prices["fast_ma"] = prices["Close Price"].rolling(8).mean()
    prices["slow_ma"] = prices["Close Price"].rolling(21).mean()

    trades: list[dict[str, object]] = []
    for idx in range(25, len(prices) - 6, 5):
        row = prices.iloc[idx]
        exit_row = prices.iloc[idx + 5]
        side = "long" if row["fast_ma"] >= row["slow_ma"] else "short"
        entry_price = float(row["Close Price"])
        exit_price = float(exit_row["Close Price"])
        quantity = round(1_000 / entry_price, 6)
        trades.append(
            {
                "trade_id": f"AAPL-{idx:04d}",
                "symbol": "AAPL",
                "side": side,
                "entry_time": row["Date"].isoformat(),
                "exit_time": exit_row["Date"].isoformat(),
                "entry_price": round(entry_price, 4),
                "exit_price": round(exit_price, 4),
                "quantity": quantity,
                "fees": round(max(1_000 * 0.0005, 0.25), 4),
            }
        )
        if len(trades) >= max_trades:
            break
    return pd.DataFrame(trades)


def prepare_market_trades(raw_path: Path, output_path: Path) -> Path:
    trades = build_trade_ledger_from_ohlc(pd.read_csv(raw_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(output_path, index=False, float_format="%.5f")
    return output_path


@app.command()
def prepare(
    data_dir: Annotated[Path, typer.Option(help="Directory for the Kaggle download.")] = Path(
        "data/raw/kaggle/aapl"
    ),
    out: Annotated[Path, typer.Option(help="Prepared trade CSV path.")] = Path(
        "data/aapl_strategy_trades.csv"
    ),
    skip_download: Annotated[
        bool,
        typer.Option(help="Use an existing raw Kaggle CSV in data_dir."),
    ] = False,
) -> None:
    raw_path = data_dir / RAW_FILENAME if skip_download else download_market_dataset(data_dir)
    prepared = prepare_market_trades(raw_path, out)
    typer.echo(f"Prepared Kaggle market trade ledger at {prepared}")
