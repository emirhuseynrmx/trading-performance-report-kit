from __future__ import annotations

import numpy as np
import pandas as pd

from trading_report_kit.config import ReportConfig


def build_trade_ledger(frame: pd.DataFrame, config: ReportConfig) -> pd.DataFrame:
    ledger = frame.copy()
    side_multiplier = np.where(ledger[config.side_column] == config.long_label, 1.0, -1.0)
    gross_pnl = (
        (ledger[config.exit_price_column] - ledger[config.entry_price_column])
        * ledger[config.quantity_column]
        * side_multiplier
    )
    ledger["gross_pnl"] = gross_pnl
    ledger["net_pnl"] = gross_pnl - ledger[config.fees_column]
    ledger["return_pct"] = ledger["net_pnl"] / config.initial_capital
    ledger["exit_date"] = pd.to_datetime(ledger[config.exit_time_column]).dt.date
    ledger = ledger.sort_values(config.exit_time_column).reset_index(drop=True)
    ledger["cumulative_pnl"] = ledger["net_pnl"].cumsum()
    ledger["equity"] = config.initial_capital + ledger["cumulative_pnl"]
    ledger["peak_equity"] = ledger["equity"].cummax()
    ledger["drawdown"] = ledger["equity"] - ledger["peak_equity"]
    ledger["drawdown_pct"] = ledger["drawdown"] / ledger["peak_equity"]
    return ledger


def build_daily_equity(ledger: pd.DataFrame, config: ReportConfig) -> pd.DataFrame:
    daily = (
        ledger.groupby("exit_date", as_index=False)
        .agg(net_pnl=("net_pnl", "sum"))
        .sort_values("exit_date")
    )
    daily["equity"] = config.initial_capital + daily["net_pnl"].cumsum()
    daily["daily_return"] = daily["equity"].pct_change().fillna(
        daily["net_pnl"] / config.initial_capital
    )
    daily["peak_equity"] = daily["equity"].cummax()
    daily["drawdown"] = daily["equity"] - daily["peak_equity"]
    daily["drawdown_pct"] = daily["drawdown"] / daily["peak_equity"]
    return daily


def build_monthly_returns(daily_equity: pd.DataFrame, config: ReportConfig) -> pd.DataFrame:
    monthly = daily_equity.copy()
    monthly["month"] = pd.to_datetime(monthly["exit_date"]).dt.to_period("M").astype(str)
    output = (
        monthly.groupby("month", as_index=False)
        .agg(start_equity=("equity", "first"), end_equity=("equity", "last"))
        .sort_values("month")
    )
    output["monthly_return_pct"] = (
        output["end_equity"] - output["start_equity"]
    ) / config.initial_capital
    return output
