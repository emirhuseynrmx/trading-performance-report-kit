from __future__ import annotations

import pandas as pd

from trading_report_kit.kaggle_data import build_trade_ledger_from_ohlc


def test_build_trade_ledger_from_ohlc_uses_market_prices() -> None:
    dates = pd.date_range("2024-01-01", periods=40, freq="D")
    raw = pd.DataFrame(
        {
            "Date": dates.strftime("%m/%d/%Y"),
            "Open Price": [100 + i for i in range(40)],
            "High Price": [101 + i for i in range(40)],
            "Low Price": [99 + i for i in range(40)],
            "Close Price": [100 + i for i in range(40)],
            "Adj Close Price": [100 + i for i in range(40)],
            "Volume": [1_000_000 + i for i in range(40)],
        }
    )

    trades = build_trade_ledger_from_ohlc(raw, max_trades=2)

    assert len(trades) == 2
    assert set(trades["symbol"]) == {"AAPL"}
    assert set(trades["side"]) <= {"long", "short"}
