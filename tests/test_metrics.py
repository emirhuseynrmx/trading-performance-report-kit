from __future__ import annotations

import pandas as pd

from trading_report_kit.config import ReportConfig
from trading_report_kit.metrics import calculate_metrics
from trading_report_kit.trades import build_daily_equity, build_trade_ledger


def test_calculate_metrics_reports_core_values() -> None:
    config = ReportConfig(initial_capital=1000)
    frame = pd.DataFrame(
        {
            "trade_id": ["A", "B", "C", "D", "E"],
            "symbol": ["AAPL"] * 5,
            "side": ["long"] * 5,
            "entry_time": pd.date_range("2025-01-01", periods=5).astype(str),
            "exit_time": pd.date_range("2025-01-02", periods=5).astype(str),
            "entry_price": [100, 100, 100, 100, 100],
            "exit_price": [110, 90, 105, 95, 108],
            "quantity": [1, 1, 1, 1, 1],
            "fees": [0, 0, 0, 0, 0],
        }
    )

    ledger = build_trade_ledger(frame, config)
    daily = build_daily_equity(ledger, config)
    metrics = calculate_metrics(ledger, daily, config)

    assert metrics.total_trades == 5
    assert metrics.win_rate == 0.6
    assert metrics.net_pnl == 8
