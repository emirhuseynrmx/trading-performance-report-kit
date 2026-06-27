from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReportConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    initial_capital: float = Field(default=10_000, gt=0)
    currency: str = "USD"
    trade_id_column: str = "trade_id"
    symbol_column: str = "symbol"
    side_column: str = "side"
    entry_time_column: str = "entry_time"
    exit_time_column: str = "exit_time"
    entry_price_column: str = "entry_price"
    exit_price_column: str = "exit_price"
    quantity_column: str = "quantity"
    fees_column: str = "fees"
    long_label: str = "long"
    short_label: str = "short"
    annualization_days: int = Field(default=252, ge=1)
    risk_free_rate: float = 0.0
    max_table_rows: int = Field(default=12, ge=3, le=50)
    report_title: str = "Trading Performance Report"
    mode: Literal["trades"] = "trades"

    @classmethod
    def load(cls, path: Path | None) -> ReportConfig:
        if path is None:
            return cls()
        return cls.model_validate_json(path.read_text(encoding="utf-8"))
