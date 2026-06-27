from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

from trading_report_kit.config import ReportConfig


def validate_trades(frame: pd.DataFrame, config: ReportConfig) -> pd.DataFrame:
    required = {
        config.trade_id_column: pa.Column(str, nullable=False),
        config.symbol_column: pa.Column(str, nullable=False),
        config.side_column: pa.Column(
            str,
            checks=pa.Check.isin([config.long_label, config.short_label]),
            nullable=False,
        ),
        config.entry_time_column: pa.Column(str, nullable=False),
        config.exit_time_column: pa.Column(str, nullable=False),
        config.entry_price_column: pa.Column(float, checks=pa.Check.gt(0), nullable=False),
        config.exit_price_column: pa.Column(float, checks=pa.Check.gt(0), nullable=False),
        config.quantity_column: pa.Column(float, checks=pa.Check.gt(0), nullable=False),
        config.fees_column: pa.Column(float, checks=pa.Check.ge(0), nullable=False),
    }
    validated = pa.DataFrameSchema(required, coerce=True, strict=False).validate(
        frame,
        lazy=True,
    )
    if len(validated) < 5:
        raise ValueError("Performance reporting needs at least 5 trades.")
    duplicate_ids = int(validated[config.trade_id_column].duplicated().sum())
    if duplicate_ids:
        raise ValueError("Duplicate trade IDs found. Please deduplicate the trade log.")
    entry_times = pd.to_datetime(validated[config.entry_time_column], errors="raise")
    exit_times = pd.to_datetime(validated[config.exit_time_column], errors="raise")
    if (exit_times < entry_times).any():
        raise ValueError("Each exit_time must be greater than or equal to entry_time.")
    return validated
