from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt


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
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.2))
    fig.suptitle("Trading Performance Snapshot", fontsize=18, fontweight="bold")
    cards = [
        ("Net PnL", f"{metrics['net_pnl']:.2f}"),
        ("Return", f"{metrics['return_pct']:.2%}"),
        ("Win Rate", f"{metrics['win_rate']:.2%}"),
        ("Max Drawdown", f"{metrics['max_drawdown_pct']:.2%}"),
    ]
    for ax, (label, value) in zip(axes.flatten(), cards, strict=True):
        ax.axis("off")
        ax.text(0.05, 0.62, label, fontsize=13, color="#57606a")
        ax.text(0.05, 0.32, value, fontsize=30, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path
