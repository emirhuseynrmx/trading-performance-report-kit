from __future__ import annotations

import pandas as pd
import pytest

from trading_report_kit.config import ReportConfig
from trading_report_kit.schema import validate_trades


def _valid_trades() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "trade_id": [f"T-{index}" for index in range(5)],
            "symbol": ["AAPL"] * 5,
            "side": ["long", "short", "long", "long", "short"],
            "entry_time": pd.date_range("2025-01-01", periods=5).astype(str),
            "exit_time": pd.date_range("2025-01-02", periods=5).astype(str),
            "entry_price": [100, 101, 102, 103, 104],
            "exit_price": [101, 100, 103, 104, 103],
            "quantity": [1, 1, 1, 1, 1],
            "fees": [0.1, 0.1, 0.1, 0.1, 0.1],
        }
    )


def test_validate_trades_accepts_valid_log() -> None:
    validated = validate_trades(_valid_trades(), ReportConfig())

    assert len(validated) == 5


def test_validate_trades_rejects_duplicate_ids() -> None:
    frame = _valid_trades()
    frame.loc[1, "trade_id"] = "T-0"

    with pytest.raises(ValueError, match="Duplicate trade IDs"):
        validate_trades(frame, ReportConfig())
