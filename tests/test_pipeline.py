from __future__ import annotations

from pathlib import Path

from trading_report_kit.config import ReportConfig
from trading_report_kit.pipeline import run_report_pipeline
from trading_report_kit.sample_data import generate_trade_log


def test_run_report_pipeline_writes_outputs(tmp_path: Path) -> None:
    input_path = tmp_path / "trades.csv"
    generate_trade_log(rows=40, seed=7).to_csv(input_path, index=False)

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
