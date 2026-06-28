from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from trading_report_kit.config import ReportConfig
from trading_report_kit.contracts import (
    validate_evidence_checks,
    validate_ledger,
    validate_metrics,
    validate_monthly_returns,
)
from trading_report_kit.evidence import build_evidence_checks
from trading_report_kit.metrics import PerformanceMetrics, calculate_metrics
from trading_report_kit.outputs import write_csv, write_manifest, write_metrics_report
from trading_report_kit.pdf_report import write_pdf_report
from trading_report_kit.schema import validate_trades
from trading_report_kit.trades import build_daily_equity, build_monthly_returns, build_trade_ledger
from trading_report_kit.visuals import (
    write_dashboard_image,
    write_drawdown_chart,
    write_equity_curve,
    write_monthly_returns_chart,
    write_trade_distribution_chart,
)


@dataclass(frozen=True)
class PipelineResult:
    output_dir: Path
    metrics: PerformanceMetrics
    metrics_path: Path
    ledger_path: Path
    daily_equity_path: Path
    monthly_returns_path: Path
    symbol_breakdown_path: Path
    evidence_checks_path: Path
    metrics_report_path: Path
    pdf_report_path: Path
    dashboard_path: Path
    equity_curve_path: Path
    drawdown_chart_path: Path
    monthly_returns_chart_path: Path
    trade_distribution_path: Path
    manifest_path: Path


def run_report_pipeline(input_path: Path, output_dir: Path, config: ReportConfig) -> PipelineResult:
    trades = validate_trades(pd.read_csv(input_path), config)
    ledger = validate_ledger(build_trade_ledger(trades, config))
    daily_equity = build_daily_equity(ledger, config)
    monthly_returns = validate_monthly_returns(build_monthly_returns(daily_equity, config))
    metrics = calculate_metrics(ledger, daily_equity, config)
    metrics_frame = validate_metrics(metrics.to_frame())
    symbol_breakdown = _build_symbol_breakdown(ledger, config)
    evidence_checks = validate_evidence_checks(
        build_evidence_checks(ledger, symbol_breakdown, config)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = write_csv(metrics_frame, output_dir / "performance_metrics.csv")
    ledger_path = write_csv(ledger, output_dir / "trade_ledger.csv")
    daily_equity_path = write_csv(daily_equity, output_dir / "daily_equity.csv")
    monthly_returns_path = write_csv(monthly_returns, output_dir / "monthly_returns.csv")
    symbol_breakdown_path = write_csv(symbol_breakdown, output_dir / "symbol_breakdown.csv")
    evidence_checks_path = write_csv(evidence_checks, output_dir / "evidence_checks.csv")

    dashboard_path = write_dashboard_image(metrics.model_dump(), output_dir / "dashboard.png")
    equity_curve_path = write_equity_curve(daily_equity, output_dir / "equity_curve.png")
    drawdown_chart_path = write_drawdown_chart(daily_equity, output_dir / "drawdown.png")
    monthly_returns_chart_path = write_monthly_returns_chart(
        monthly_returns,
        output_dir / "monthly_returns.png",
    )
    trade_distribution_path = write_trade_distribution_chart(
        ledger,
        output_dir / "trade_distribution.png",
    )
    best_symbol = str(symbol_breakdown.iloc[0][config.symbol_column])
    worst_symbol = str(symbol_breakdown.iloc[-1][config.symbol_column])
    metrics_report_path = write_metrics_report(
        metrics=metrics,
        output_path=output_dir / "metrics_report.md",
        best_symbol=best_symbol,
        worst_symbol=worst_symbol,
        evidence_checks=evidence_checks,
    )
    pdf_report_path = write_pdf_report(
        output_path=output_dir / "performance_report.pdf",
        metrics=metrics,
        monthly_returns=monthly_returns,
        symbol_breakdown=symbol_breakdown,
        evidence_checks=evidence_checks,
        dashboard_path=dashboard_path,
        equity_curve_path=equity_curve_path,
        drawdown_chart_path=drawdown_chart_path,
        monthly_returns_chart_path=monthly_returns_chart_path,
        trade_distribution_path=trade_distribution_path,
        currency=config.currency,
    )
    manifest_path = write_manifest(
        {
            "performance_metrics": metrics_path,
            "trade_ledger": ledger_path,
            "daily_equity": daily_equity_path,
            "monthly_returns": monthly_returns_path,
            "symbol_breakdown": symbol_breakdown_path,
            "evidence_checks": evidence_checks_path,
            "metrics_report": metrics_report_path,
            "pdf_report": pdf_report_path,
            "dashboard": dashboard_path,
            "equity_curve": equity_curve_path,
            "drawdown_chart": drawdown_chart_path,
            "monthly_returns_chart": monthly_returns_chart_path,
            "trade_distribution": trade_distribution_path,
        },
        output_dir / "manifest.json",
    )
    return PipelineResult(
        output_dir=output_dir,
        metrics=metrics,
        metrics_path=metrics_path,
        ledger_path=ledger_path,
        daily_equity_path=daily_equity_path,
        monthly_returns_path=monthly_returns_path,
        symbol_breakdown_path=symbol_breakdown_path,
        evidence_checks_path=evidence_checks_path,
        metrics_report_path=metrics_report_path,
        pdf_report_path=pdf_report_path,
        dashboard_path=dashboard_path,
        equity_curve_path=equity_curve_path,
        drawdown_chart_path=drawdown_chart_path,
        monthly_returns_chart_path=monthly_returns_chart_path,
        trade_distribution_path=trade_distribution_path,
        manifest_path=manifest_path,
    )


def _build_symbol_breakdown(ledger: pd.DataFrame, config: ReportConfig) -> pd.DataFrame:
    return (
        ledger.groupby(config.symbol_column, as_index=False)
        .agg(
            trades=(config.trade_id_column, "size"),
            net_pnl=("net_pnl", "sum"),
            win_rate=("net_pnl", lambda values: float((values > 0).mean())),
            average_trade=("net_pnl", "mean"),
        )
        .sort_values("net_pnl", ascending=False)
    )
