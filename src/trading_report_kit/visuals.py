from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def write_equity_curve(daily_equity: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(pd.to_datetime(daily_equity["exit_date"]), daily_equity["equity"], color="#0969da")
    ax.set_title("Equity Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def write_drawdown_chart(daily_equity: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.fill_between(
        pd.to_datetime(daily_equity["exit_date"]),
        daily_equity["drawdown_pct"] * 100,
        0,
        color="#d73a49",
        alpha=0.75,
    )
    ax.set_title("Drawdown")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown %")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def write_monthly_returns_chart(monthly_returns: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    colors = [
        "#2ea043" if value >= 0 else "#d73a49"
        for value in monthly_returns["monthly_return_pct"]
    ]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(monthly_returns["month"], monthly_returns["monthly_return_pct"] * 100, color=colors)
    ax.set_title("Monthly Returns")
    ax.set_xlabel("Month")
    ax.set_ylabel("Return %")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def write_trade_distribution_chart(ledger: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(ledger["net_pnl"], bins=16, color="#8250df", edgecolor="white", alpha=0.9)
    ax.axvline(0, color="#24292f", linewidth=1.5)
    ax.set_title("Trade PnL Distribution")
    ax.set_xlabel("Net PnL")
    ax.set_ylabel("Trades")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def write_dashboard_image(metrics: dict[str, float], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6.4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.axis("off")
    ax.text(
        0.04,
        0.92,
        "Trading Performance Evidence",
        color="#f0f6fc",
        fontsize=22,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.04,
        0.86,
        "Closed-trade ledger review with drawdown, expectancy, and sample-size checks.",
        color="#8b949e",
        fontsize=12,
        transform=ax.transAxes,
    )
    cards = [
        ("Net PnL", f"{metrics['net_pnl']:,.2f}", metrics["net_pnl"]),
        ("Return", f"{metrics['return_pct']:.2%}", metrics["return_pct"]),
        ("Win Rate", f"{metrics['win_rate']:.2%}", metrics["win_rate"] - 0.5),
        ("Max Drawdown", f"{metrics['max_drawdown_pct']:.2%}", metrics["max_drawdown_pct"]),
    ]
    positions = [(0.04, 0.58), (0.28, 0.58), (0.52, 0.58), (0.76, 0.58)]
    for (label, value, score), (x_pos, y_pos) in zip(cards, positions, strict=True):
        color = "#3fb950" if score >= 0 else "#f85149"
        card = FancyBboxPatch(
            (x_pos, y_pos),
            0.20,
            0.20,
            boxstyle="round,pad=0.016,rounding_size=0.018",
            linewidth=0.8,
            edgecolor="#30363d",
            facecolor="#161b22",
            transform=ax.transAxes,
        )
        ax.add_patch(card)
        ax.text(
            x_pos + 0.02,
            y_pos + 0.135,
            label.upper(),
            color="#8b949e",
            fontsize=9,
            fontweight="bold",
            transform=ax.transAxes,
        )
        ax.text(
            x_pos + 0.02,
            y_pos + 0.055,
            value,
            color=color,
            fontsize=21,
            fontweight="bold",
            transform=ax.transAxes,
        )

    checks = [
        ("Ledger integrity", "completed trades only"),
        ("Lookahead posture", "uses exit-time ordering"),
        ("Risk visibility", "drawdown and distribution included"),
        ("Claim boundary", "no profit forecast"),
    ]
    ax.text(
        0.04,
        0.43,
        "Evidence checks",
        color="#f0f6fc",
        fontsize=15,
        fontweight="bold",
        transform=ax.transAxes,
    )
    for index, (label, detail) in enumerate(checks):
        y_pos = 0.34 - index * 0.065
        ax.text(
            0.06,
            y_pos,
            label,
            color="#f0f6fc",
            fontsize=11,
            fontweight="bold",
            transform=ax.transAxes,
        )
        ax.text(0.28, y_pos, detail, color="#8b949e", fontsize=11, transform=ax.transAxes)
        ax.plot(
            [0.04, 0.94],
            [y_pos - 0.025, y_pos - 0.025],
            color="#21262d",
            linewidth=0.8,
            transform=ax.transAxes,
        )

    ax.text(
        0.04,
        0.05,
        "Interpretation: the report is an evidence layer, not a trading signal.",
        color="#d29922",
        fontsize=12,
        fontstyle="italic",
        transform=ax.transAxes,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path
