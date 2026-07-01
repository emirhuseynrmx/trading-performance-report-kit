# ruff: noqa: E501
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from shutil import which

import pandas as pd

from trading_report_kit.metrics import PerformanceMetrics


def write_pdf_report(
    *,
    output_path: Path,
    metrics: PerformanceMetrics,
    monthly_returns: pd.DataFrame,
    symbol_breakdown: pd.DataFrame,
    evidence_checks: pd.DataFrame,
    dashboard_path: Path,
    equity_curve_path: Path,
    drawdown_chart_path: Path,
    monthly_returns_chart_path: Path,
    trade_distribution_path: Path,
    currency: str = "USD",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_path = output_path.with_suffix(".typ")
    source_path.write_text(
        _build_typst_source(
            metrics=metrics,
            monthly_returns=monthly_returns,
            symbol_breakdown=symbol_breakdown,
            evidence_checks=evidence_checks,
            dashboard_path=dashboard_path,
            equity_curve_path=equity_curve_path,
            drawdown_chart_path=drawdown_chart_path,
            monthly_returns_chart_path=monthly_returns_chart_path,
            trade_distribution_path=trade_distribution_path,
            currency=currency,
        ),
        encoding="utf-8",
    )
    _compile_typst(source_path, output_path)
    return output_path


def _build_typst_source(
    *,
    metrics: PerformanceMetrics,
    monthly_returns: pd.DataFrame,
    symbol_breakdown: pd.DataFrame,
    evidence_checks: pd.DataFrame,
    dashboard_path: Path,
    equity_curve_path: Path,
    drawdown_chart_path: Path,
    monthly_returns_chart_path: Path,
    trade_distribution_path: Path,
    currency: str,
) -> str:
    cards = "\n".join(
        [
            f'  metric("Trades", "{metrics.total_trades:,}", "Closed ledger rows", color: blue),',
            f'  metric("Net PnL", "{currency} {metrics.net_pnl:,.2f}", "After costs in ledger", color: green),',
            f'  metric("Max DD", "{currency} {metrics.max_drawdown:,.2f}", "Worst equity decline", color: red),',
            f'  metric("Sharpe", "{metrics.sharpe_ratio:.2f}", "Risk-adjusted return", color: amber),',
        ]
    )
    metrics_table = _frame_table(_format_metrics(metrics, currency), max_rows=14)
    clean_evidence = evidence_checks.copy()
    if "evidence" in clean_evidence.columns:
        clean_evidence["evidence"] = clean_evidence["evidence"].map(_shorten)
    return f'''#set page(paper: "us-letter", margin: (x: 0.62in, y: 0.58in))
#set text(size: 9pt, fill: rgb("#152033"))
#set par(leading: 0.62em, spacing: 0.5em)

#let navy = rgb("#102033")
#let blue = rgb("#2563eb")
#let green = rgb("#059669")
#let amber = rgb("#d97706")
#let red = rgb("#dc2626")
#let border = rgb("#d8dee8")
#let soft = rgb("#f6f8fb")
#let muted = rgb("#64748b")

#let metric(label, value, note, color: blue) = block(fill: soft, stroke: 0.6pt + border, radius: 7pt, inset: 10pt, width: 100%)[
  #text(size: 7.5pt, fill: muted, weight: "bold", label)
  #v(3pt)
  #text(size: 17pt, fill: color, weight: "bold", value)
  #v(2pt)
  #text(size: 7.4pt, fill: muted, note)
]

#let section(title) = [
  #v(8pt)
  #text(size: 13.3pt, weight: "bold", fill: navy, title)
  #v(4pt)
  #line(length: 100%, stroke: 0.7pt + border)
  #v(6pt)
]

#let cell(body, header: false) = table.cell(
  fill: if header {{ navy }} else {{ none }},
  inset: 5pt,
)[#text(size: if header {{ 7.2pt }} else {{ 6.9pt }}, fill: if header {{ white }} else {{ rgb("#152033") }}, weight: if header {{ "bold" }} else {{ "regular" }}, body)]

#align(center)[
  #text(size: 20pt, weight: "bold", fill: navy, "Trading Performance Evidence Report")
  #v(3pt)
  #text(size: 8.6pt, fill: muted, "Closed-trade ledger review with drawdown, concentration, and risk checks")
]

#v(9pt)
#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 8pt,
{cards}
)

#section("Executive Read")
#grid(columns: (1.05fr, 0.95fr), gutter: 12pt,
[
  This report reviews a closed-trade ledger. It is evidence, not a trading signal. The goal is to make performance, concentration, drawdown, and data-quality risks visible before a strategy is marketed or scaled.

  No result here guarantees future profit. The report is designed to surface overfitting, missing costs, and symbol concentration instead of hiding them behind a single equity curve.
],
[
  #image({_q(_image_ref(dashboard_path))}, width: 100%)
])

#section("Core Metrics")
{metrics_table}

#section("Evidence Checklist")
{_frame_table(clean_evidence, max_rows=12)}

#pagebreak()

#section("Charts")
#grid(columns: (1fr, 1fr), gutter: 12pt,
[
  #image({_q(_image_ref(equity_curve_path))}, width: 100%)
  #v(8pt)
  #image({_q(_image_ref(monthly_returns_chart_path))}, width: 100%)
],
[
  #image({_q(_image_ref(drawdown_chart_path))}, width: 100%)
  #v(8pt)
  #image({_q(_image_ref(trade_distribution_path))}, width: 100%)
])

#section("Breakdowns")
#grid(columns: (1fr, 1fr), gutter: 12pt,
[
  #text(weight: "bold", "Symbol Breakdown")
  #v(5pt)
{_frame_table(symbol_breakdown.head(8), max_rows=8)}
],
[
  #text(weight: "bold", "Recent Monthly Returns")
  #v(5pt)
{_frame_table(monthly_returns.tail(10), max_rows=10)}
])

#section("Limitations")
Backtest and trade-log performance can be affected by fees, slippage, survivorship bias, missing trades, overfitting, and market regime changes. A strong report should make those risks visible instead of hiding them.
'''


def _frame_table(frame: pd.DataFrame, *, max_rows: int) -> str:
    display = frame.head(max_rows).copy()
    display.columns = [_short_column_name(column) for column in display.columns]
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(lambda value: f"{value:.4f}")
    headers = ", ".join(f"cell({_q(column)}, header: true)" for column in display.columns)
    cells = ",\n  ".join(
        f"cell({_q(value)})"
        for row in display.astype(str).itertuples(index=False)
        for value in row
    )
    column_spec = ", ".join(["1fr"] * len(display.columns))
    return f'''#table(
  columns: ({column_spec}),
  stroke: 0.45pt + border,
  table.header({headers}),
  {cells}
)'''


def _format_metrics(metrics: PerformanceMetrics, currency: str) -> pd.DataFrame:
    rows = [
        ("Total trades", f"{metrics.total_trades:,}"),
        ("Net PnL", f"{currency} {metrics.net_pnl:,.2f}"),
        ("Return", f"{metrics.return_pct:.2%}"),
        ("Win rate", f"{metrics.win_rate:.2%}"),
        ("Profit factor", f"{metrics.profit_factor:.2f}"),
        ("Expectancy", f"{currency} {metrics.expectancy:,.2f}"),
        ("Average win", f"{currency} {metrics.average_win:,.2f}"),
        ("Average loss", f"{currency} {metrics.average_loss:,.2f}"),
        ("Payoff ratio", f"{metrics.payoff_ratio:.2f}"),
        ("Max drawdown", f"{currency} {metrics.max_drawdown:,.2f}"),
        ("Max drawdown pct", f"{metrics.max_drawdown_pct:.2%}"),
        ("Sharpe ratio", f"{metrics.sharpe_ratio:.2f}"),
        ("Best trade", f"{currency} {metrics.best_trade:,.2f}"),
        ("Worst trade", f"{currency} {metrics.worst_trade:,.2f}"),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def _shorten(value: object) -> str:
    text = str(value)
    return text if len(text) <= 130 else f"{text[:127]}..."


def _image_ref(path: Path) -> str:
    return path.name


def _q(value: object) -> str:
    return json.dumps(str(value))



def _short_column_name(column: object) -> str:
    names = {
        "avg_churn_probability": "avg_prob",
        "cumulative_churners": "cum_churners",
        "cumulative_churn_capture_rate": "cum_capture",
        "mean_predicted_probability": "mean_pred",
        "observed_churn_rate": "observed_rate",
        "absolute_gap": "gap",
        "bootstrap_samples": "samples",
        "monthly_return_pct": "monthly_return",
        "average_trade": "avg_trade",
        "retention_priority": "priority",
        "churn_probability": "risk",
        "risk_segment": "segment",
        "likely_drivers": "drivers",
    }
    return names.get(str(column), str(column))


def _compile_typst(source_path: Path, output_path: Path) -> None:
    if which("typst") is None:
        raise RuntimeError("Typst CLI is required to build the PDF report.")
    subprocess.run(
        ["typst", "compile", source_path.name, output_path.name],
        cwd=source_path.parent,
        check=True,
        capture_output=True,
        text=True,
    )
