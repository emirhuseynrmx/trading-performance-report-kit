from __future__ import annotations

import pandas as pd
import pandera.pandas as pa


def validate_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    schema = pa.DataFrameSchema(
        {
            "metric": pa.Column(str, nullable=False),
            "value": pa.Column(float, nullable=False),
        },
        coerce=True,
        strict=True,
    )
    return schema.validate(frame, lazy=True)


def validate_ledger(frame: pd.DataFrame) -> pd.DataFrame:
    required_columns = {
        "gross_pnl": pa.Column(float, nullable=False),
        "net_pnl": pa.Column(float, nullable=False),
        "return_pct": pa.Column(float, nullable=False),
        "equity": pa.Column(float, checks=pa.Check.gt(0)),
        "drawdown": pa.Column(float, nullable=False),
        "drawdown_pct": pa.Column(float, checks=pa.Check.le(0)),
    }
    return pa.DataFrameSchema(required_columns, coerce=True, strict=False).validate(
        frame,
        lazy=True,
    )


def validate_monthly_returns(frame: pd.DataFrame) -> pd.DataFrame:
    schema = pa.DataFrameSchema(
        {
            "month": pa.Column(str, nullable=False),
            "start_equity": pa.Column(float, checks=pa.Check.gt(0)),
            "end_equity": pa.Column(float, checks=pa.Check.gt(0)),
            "monthly_return_pct": pa.Column(float, nullable=False),
        },
        coerce=True,
        strict=True,
    )
    return schema.validate(frame, lazy=True)


def validate_evidence_checks(frame: pd.DataFrame) -> pd.DataFrame:
    schema = pa.DataFrameSchema(
        {
            "check": pa.Column(str, nullable=False),
            "status": pa.Column(str, checks=pa.Check.isin(["pass", "review", "fail"])),
            "evidence": pa.Column(str, nullable=False),
        },
        coerce=True,
        strict=True,
    )
    return schema.validate(frame, lazy=True)
