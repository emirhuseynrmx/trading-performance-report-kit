from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from trading_report_kit.metrics import PerformanceMetrics


def write_pdf_report(
    *,
    output_path: Path,
    metrics: PerformanceMetrics,
    monthly_returns: pd.DataFrame,
    symbol_breakdown: pd.DataFrame,
    dashboard_path: Path,
    equity_curve_path: Path,
    drawdown_chart_path: Path,
    monthly_returns_chart_path: Path,
    trade_distribution_path: Path,
    currency: str = "USD",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    compact = ParagraphStyle(
        "Compact",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    )
    story = [
        Paragraph("Trading Performance Report", styles["Title"]),
        Paragraph(
            "Executive summary: this report turns a provided closed-trade ledger into "
            "a structured performance review. It is not a trading signal, not financial "
            "advice, and it does not use future data to make a prediction.",
            styles["BodyText"],
        ),
        Spacer(1, 0.15 * inch),
        Image(str(dashboard_path), width=6.5 * inch, height=4.0 * inch),
        Spacer(1, 0.18 * inch),
        Paragraph("Core Metrics", styles["Heading2"]),
        _dataframe_table(_format_metrics(metrics, currency)),
        Spacer(1, 0.18 * inch),
        Paragraph("Evidence Checklist", styles["Heading2"]),
        _dataframe_table(_evidence_checklist(metrics), font_size=8, wrap_text=True),
        Spacer(1, 0.18 * inch),
        Paragraph("Symbol Breakdown", styles["Heading2"]),
        _dataframe_table(symbol_breakdown.head(10)),
        Spacer(1, 0.18 * inch),
        Paragraph("Monthly Returns", styles["Heading2"]),
        _dataframe_table(monthly_returns.tail(12)),
        Spacer(1, 0.18 * inch),
        Paragraph("Equity Curve", styles["Heading2"]),
        Image(str(equity_curve_path), width=6.5 * inch, height=3.5 * inch),
        Spacer(1, 0.1 * inch),
        Paragraph("Drawdown", styles["Heading2"]),
        Image(str(drawdown_chart_path), width=6.5 * inch, height=3.0 * inch),
        Spacer(1, 0.1 * inch),
        Paragraph("Monthly Return Chart", styles["Heading2"]),
        Image(str(monthly_returns_chart_path), width=6.5 * inch, height=3.5 * inch),
        Spacer(1, 0.1 * inch),
        Paragraph("Trade Distribution", styles["Heading2"]),
        Image(str(trade_distribution_path), width=6.0 * inch, height=3.2 * inch),
        Spacer(1, 0.18 * inch),
        Paragraph("Limitations", styles["Heading2"]),
        Paragraph(
            "Backtest and trade-log performance can be affected by fees, slippage, "
            "survivorship bias, missing trades, overfitting, and market regime changes. "
            "A strong report should make those risks visible instead of hiding them. "
            "No result in this report guarantees future profit.",
            styles["BodyText"],
        ),
        Spacer(1, 0.08 * inch),
        Paragraph(
            "Recommended next review: verify fees/slippage assumptions, inspect the "
            "largest winners and losers, compare walk-forward periods, and review "
            "whether performance is concentrated in one symbol or market regime.",
            compact,
        ),
    ]
    doc.build(story)
    return output_path


def _dataframe_table(
    frame: pd.DataFrame,
    *,
    font_size: int = 7,
    wrap_text: bool = False,
) -> Table:
    display = frame.copy()
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(lambda value: f"{value:.4f}")
    if wrap_text:
        styles = getSampleStyleSheet()
        rows = [
            [Paragraph(str(column), styles["BodyText"]) for column in display.columns.tolist()]
        ]
        rows.extend(
            [Paragraph(str(value), styles["BodyText"]) for value in row]
            for row in display.astype(str).values.tolist()
        )
    else:
        rows = [display.columns.tolist()]
        rows.extend(display.astype(str).values.tolist())
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0969da")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7de")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f6f8fa")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


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
        ("Max drawdown %", f"{metrics.max_drawdown_pct:.2%}"),
        ("Sharpe ratio", f"{metrics.sharpe_ratio:.2f}"),
        ("Best trade", f"{currency} {metrics.best_trade:,.2f}"),
        ("Worst trade", f"{currency} {metrics.worst_trade:,.2f}"),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def _evidence_checklist(metrics: PerformanceMetrics) -> pd.DataFrame:
    status = "Review" if metrics.total_trades < 30 else "Pass"
    return pd.DataFrame(
        [
            {
                "Check": "Closed-trade ledger",
                "Status": "Pass",
                "Note": "Report summarizes completed trades only.",
            },
            {
                "Check": "Minimum sample size",
                "Status": status,
                "Note": "Small trade counts can overstate strategy quality.",
            },
            {
                "Check": "Drawdown visibility",
                "Status": "Pass",
                "Note": "Equity and drawdown charts are included.",
            },
            {
                "Check": "Forward-looking claims",
                "Status": "Pass",
                "Note": "The report does not forecast future profit.",
            },
        ]
    )
