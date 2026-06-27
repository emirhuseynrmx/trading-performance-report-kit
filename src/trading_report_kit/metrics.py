from __future__ import annotations

import math

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from trading_report_kit.config import ReportConfig


class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_trades: int
    net_pnl: float
    return_pct: float
    win_rate: float
    profit_factor: float
    expectancy: float
    average_win: float
    average_loss: float
    payoff_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    best_trade: float
    worst_trade: float

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"metric": key, "value": value} for key, value in self.model_dump().items()]
        )


def calculate_metrics(
    ledger: pd.DataFrame,
    daily_equity: pd.DataFrame,
    config: ReportConfig,
) -> PerformanceMetrics:
    wins = ledger.loc[ledger["net_pnl"] > 0, "net_pnl"]
    losses = ledger.loc[ledger["net_pnl"] < 0, "net_pnl"]
    gross_profit = float(wins.sum())
    gross_loss = abs(float(losses.sum()))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else math.inf
    average_win = float(wins.mean()) if len(wins) else 0.0
    average_loss = float(losses.mean()) if len(losses) else 0.0
    payoff_ratio = average_win / abs(average_loss) if average_loss else math.inf
    daily_risk_free_rate = config.risk_free_rate / config.annualization_days
    daily_excess = daily_equity["daily_return"] - daily_risk_free_rate
    sharpe = _safe_sharpe(daily_excess, config)
    return PerformanceMetrics(
        total_trades=len(ledger),
        net_pnl=round(float(ledger["net_pnl"].sum()), 4),
        return_pct=round(float(ledger["net_pnl"].sum() / config.initial_capital), 4),
        win_rate=round(float((ledger["net_pnl"] > 0).mean()), 4),
        profit_factor=round(float(profit_factor), 4) if math.isfinite(profit_factor) else 999.0,
        expectancy=round(float(ledger["net_pnl"].mean()), 4),
        average_win=round(average_win, 4),
        average_loss=round(average_loss, 4),
        payoff_ratio=round(float(payoff_ratio), 4) if math.isfinite(payoff_ratio) else 999.0,
        max_drawdown=round(float(daily_equity["drawdown"].min()), 4),
        max_drawdown_pct=round(float(daily_equity["drawdown_pct"].min()), 4),
        sharpe_ratio=round(sharpe, 4),
        best_trade=round(float(ledger["net_pnl"].max()), 4),
        worst_trade=round(float(ledger["net_pnl"].min()), 4),
    )


def _safe_sharpe(daily_excess: pd.Series, config: ReportConfig) -> float:
    standard_deviation = float(daily_excess.std(ddof=1))
    if np.isnan(standard_deviation) or standard_deviation == 0:
        return 0.0
    return float(daily_excess.mean() / standard_deviation * np.sqrt(config.annualization_days))
