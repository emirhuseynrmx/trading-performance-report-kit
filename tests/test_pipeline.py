from __future__ import annotations

from pathlib import Path

import pandas as pd

from trading_report_kit.config import ReportConfig
from trading_report_kit.kaggle_data import build_trade_ledger_from_ohlc
from trading_report_kit.pipeline import run_report_pipeline


def test_run_report_pipeline_writes_outputs(tmp_path: Path) -> None:
    input_path = tmp_path / "trades.csv"
    build_trade_ledger_from_ohlc(ohlc_fixture(), max_trades=20).to_csv(input_path, index=False)

    result = run_report_pipeline(input_path, tmp_path / "out", ReportConfig())

    assert result.metrics_path.exists()
    assert result.ledger_path.exists()
    assert result.daily_equity_path.exists()
    assert result.monthly_returns_path.exists()
    assert result.symbol_breakdown_path.exists()
    assert result.pdf_report_path.exists()
    assert result.dashboard_path.exists()
    assert result.equity_curve_path.exists()
    assert result.drawdown_chart_path.exists()
    assert result.monthly_returns_chart_path.exists()
    assert result.trade_distribution_path.exists()
    assert result.manifest_path.exists()


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
