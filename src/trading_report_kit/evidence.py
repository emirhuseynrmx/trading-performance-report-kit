from __future__ import annotations

import pandas as pd

from trading_report_kit.config import ReportConfig


def build_evidence_checks(
    ledger: pd.DataFrame,
    symbol_breakdown: pd.DataFrame,
    config: ReportConfig,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            _closed_trade_check(ledger, config),
            _sample_size_check(ledger, config),
            _fee_coverage_check(ledger, config),
            _symbol_concentration_check(symbol_breakdown, config),
            _timestamp_order_check(ledger, config),
            _lookahead_boundary_check(config),
            _survivorship_bias_check(symbol_breakdown, config),
            _multiple_testing_check(),
        ]
    )


def _closed_trade_check(ledger: pd.DataFrame, config: ReportConfig) -> dict[str, str]:
    entry_times = pd.to_datetime(ledger[config.entry_time_column])
    exit_times = pd.to_datetime(ledger[config.exit_time_column])
    passed = bool((exit_times >= entry_times).all())
    return {
        "check": "closed_trade_timestamps",
        "status": "pass" if passed else "fail",
        "evidence": "All exit timestamps are on or after entry timestamps."
        if passed
        else "At least one trade exits before it enters.",
    }


def _sample_size_check(ledger: pd.DataFrame, config: ReportConfig) -> dict[str, str]:
    trade_count = len(ledger)
    passed = trade_count >= config.minimum_trade_count
    return {
        "check": "minimum_trade_count",
        "status": "pass" if passed else "review",
        "evidence": f"{trade_count} trades; configured minimum is {config.minimum_trade_count}.",
    }


def _fee_coverage_check(ledger: pd.DataFrame, config: ReportConfig) -> dict[str, str]:
    coverage = float((ledger[config.fees_column] > 0).mean())
    passed = coverage >= config.minimum_fee_coverage
    return {
        "check": "fee_coverage",
        "status": "pass" if passed else "review",
        "evidence": f"{coverage:.1%} of trades include non-zero fees.",
    }


def _symbol_concentration_check(
    symbol_breakdown: pd.DataFrame,
    config: ReportConfig,
) -> dict[str, str]:
    total_trades = int(symbol_breakdown["trades"].sum())
    top_row = symbol_breakdown.sort_values("trades", ascending=False).iloc[0]
    share = float(top_row["trades"] / total_trades)
    passed = share <= config.max_symbol_trade_concentration
    return {
        "check": "symbol_concentration",
        "status": "pass" if passed else "review",
        "evidence": (
            f"Top symbol {top_row[config.symbol_column]} is {share:.1%} of trades; "
            f"limit is {config.max_symbol_trade_concentration:.1%}."
        ),
    }


def _timestamp_order_check(ledger: pd.DataFrame, config: ReportConfig) -> dict[str, str]:
    exit_times = pd.to_datetime(ledger[config.exit_time_column])
    passed = bool(exit_times.is_monotonic_increasing)
    return {
        "check": "exit_time_order",
        "status": "pass" if passed else "review",
        "evidence": "Ledger is sorted by exit timestamp."
        if passed
        else "Ledger was not sorted by exit timestamp before processing.",
    }


def _lookahead_boundary_check(config: ReportConfig) -> dict[str, str]:
    return {
        "check": "lookahead_boundary",
        "status": "pass",
        "evidence": (
            "The report summarizes closed trades only and does not train a predictive "
            f"model; use at least {config.embargo_days} day(s) of embargo for any "
            "future walk-forward feature study."
        ),
    }


def _survivorship_bias_check(
    symbol_breakdown: pd.DataFrame,
    config: ReportConfig,
) -> dict[str, str]:
    symbol_count = int(symbol_breakdown[config.symbol_column].nunique())
    status = "review" if symbol_count <= 1 else "pass"
    return {
        "check": "survivorship_bias",
        "status": status,
        "evidence": (
            f"{symbol_count} symbol(s) present. Confirm the source universe includes "
            "delisted or failed names when evaluating broad strategies."
        ),
    }


def _multiple_testing_check() -> dict[str, str]:
    return {
        "check": "multiple_testing",
        "status": "review",
        "evidence": (
            "If this strategy was selected after many variants, report candidate count "
            "and walk-forward results before treating the performance as evidence."
        ),
    }
