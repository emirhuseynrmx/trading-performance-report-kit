from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from trading_report_kit.metrics import PerformanceMetrics


def write_csv(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.4f")
    return path


def write_metrics_report(
    *,
    metrics: PerformanceMetrics,
    output_path: Path,
    best_symbol: str,
    worst_symbol: str,
) -> Path:
    data = metrics.model_dump()
    lines = [
        "# Trading Performance Metrics Report",
        "",
        f"- Total trades: `{data['total_trades']}`",
        f"- Net PnL: `{data['net_pnl']:.2f}`",
        f"- Return: `{data['return_pct']:.2%}`",
        f"- Win rate: `{data['win_rate']:.2%}`",
        f"- Profit factor: `{data['profit_factor']:.2f}`",
        f"- Max drawdown: `{data['max_drawdown_pct']:.2%}`",
        f"- Sharpe ratio: `{data['sharpe_ratio']:.2f}`",
        "",
        "## Business Read",
        "",
        "Use the equity curve and drawdown chart together. A strategy can show positive "
        "return while still having unacceptable drawdown.",
        "",
        f"- Best symbol by net PnL: `{best_symbol}`",
        f"- Worst symbol by net PnL: `{worst_symbol}`",
        "",
        "No metric in this report guarantees future performance.",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def write_manifest(files: dict[str, Path], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"files": {key: str(value) for key, value in files.items()}}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
