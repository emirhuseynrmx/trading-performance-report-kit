from __future__ import annotations

from pathlib import Path
from typing import Annotated

import numpy as np
import pandas as pd
import typer

app = typer.Typer(help="Generate realistic sample trade logs.")


def generate_trade_log(rows: int = 120, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    symbols = rng.choice(["BTCUSDT", "ETHUSDT", "AAPL", "MSFT", "NVDA"], size=rows)
    sides = rng.choice(["long", "short"], size=rows, p=[0.62, 0.38])
    start = pd.Timestamp("2025-01-03")
    entry_times = [
        start + pd.Timedelta(days=int(index * 2 + rng.integers(0, 2)))
        for index in range(rows)
    ]
    holding_days = rng.integers(1, 8, size=rows)
    exit_times = [
        entry + pd.Timedelta(days=int(days))
        for entry, days in zip(entry_times, holding_days, strict=True)
    ]
    base_prices = {
        "BTCUSDT": 65_000,
        "ETHUSDT": 3_200,
        "AAPL": 190,
        "MSFT": 420,
        "NVDA": 850,
    }
    entry_prices = np.array([base_prices[symbol] for symbol in symbols]) * rng.normal(1, 0.04, rows)
    strategy_edge = rng.normal(0.003, 0.022, rows)
    direction = np.where(sides == "long", 1, -1)
    exit_prices = entry_prices * (1 + strategy_edge * direction)
    notional = rng.uniform(400, 1_800, rows)
    quantity = notional / entry_prices
    fees = np.maximum(notional * rng.uniform(0.0002, 0.0012, rows), 0.25)
    return pd.DataFrame(
        {
            "trade_id": [f"T-{index:04d}" for index in range(1, rows + 1)],
            "symbol": symbols,
            "side": sides,
            "entry_time": [timestamp.isoformat() for timestamp in entry_times],
            "exit_time": [timestamp.isoformat() for timestamp in exit_times],
            "entry_price": entry_prices.round(4),
            "exit_price": exit_prices.round(4),
            "quantity": quantity.round(4),
            "fees": fees.round(4),
        }
    )


@app.command()
def generate(
    out: Annotated[Path, typer.Option(help="Output CSV path.")] = Path("data/sample_trades.csv"),
    rows: Annotated[int, typer.Option(help="Number of trades.")] = 120,
    seed: Annotated[int, typer.Option(help="Random seed.")] = 42,
) -> None:
    frame = generate_trade_log(rows=rows, seed=seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False)
    typer.echo(f"Generated {len(frame)} trades at {out}")
