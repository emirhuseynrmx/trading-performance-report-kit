from __future__ import annotations

from trading_report_kit.sample_data import generate_trade_log


def test_generate_trade_log_is_reproducible() -> None:
    first = generate_trade_log(rows=20, seed=3)
    second = generate_trade_log(rows=20, seed=3)

    assert first.equals(second)
    assert set(first["side"].unique()) <= {"long", "short"}
