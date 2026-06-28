from __future__ import annotations

import pandas as pd
from typer.testing import CliRunner

from trading_report_kit.cli import app
from trading_report_kit.kaggle_data import build_trade_ledger_from_ohlc


def test_cli_run_command(tmp_path) -> None:
    input_path = tmp_path / "trades.csv"
    build_trade_ledger_from_ohlc(ohlc_fixture(), max_trades=20).to_csv(input_path, index=False)

    result = CliRunner().invoke(
        app,
        [
            str(input_path),
            "--config",
            "examples/config.json",
            "--out",
            str(tmp_path / "report"),
        ],
    )

    assert result.exit_code == 0
    assert "Trading report complete" in result.output
    assert (tmp_path / "report" / "performance_report.pdf").exists()


def ohlc_fixture() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=140, freq="D")
    closes = [100 + index * 0.25 + ((index % 9) - 4) * 0.4 for index in range(140)]
    return pd.DataFrame(
        {
            "Date": dates.strftime("%m/%d/%Y"),
            "Open Price": closes,
            "High Price": [price * 1.01 for price in closes],
            "Low Price": [price * 0.99 for price in closes],
            "Close Price": closes,
            "Adj Close Price": closes,
            "Volume": [1_000_000 + index * 1000 for index in range(140)],
        }
    )
