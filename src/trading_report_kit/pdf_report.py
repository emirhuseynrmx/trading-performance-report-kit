from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
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
    story = [
        Paragraph("Trading Performance Report", styles["Title"]),
        Paragraph(
            "This report summarizes a provided trade log. It is a performance review, "
            "not a trading signal and not financial advice.",
            styles["BodyText"],
        ),
        Spacer(1, 0.15 * inch),
        Image(str(dashboard_path), width=6.5 * inch, height=4.0 * inch),
        Spacer(1, 0.18 * inch),
        Paragraph("Core Metrics", styles["Heading2"]),
        _dataframe_table(metrics.to_frame()),
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
            "No result in this report guarantees future profit.",
            styles["BodyText"],
        ),
    ]
    doc.build(story)
    return output_path


def _dataframe_table(frame: pd.DataFrame) -> Table:
    display = frame.copy()
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(lambda value: f"{value:.4f}")
    rows = [display.columns.tolist()]
    rows.extend(display.astype(str).values.tolist())
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0969da")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7de")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f6f8fa")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table
