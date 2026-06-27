from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from trading_report_kit.config import ReportConfig
from trading_report_kit.pipeline import run_report_pipeline

app = typer.Typer(help="Generate trading performance reports from a trade CSV.")
console = Console()


@app.command()
def run(
    input_path: Annotated[Path, typer.Argument(help="Trade CSV path.")],
    config: Annotated[Path | None, typer.Option(help="Config JSON path.")] = None,
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("outputs/report"),
) -> None:
    report_config = ReportConfig.load(config)
    result = run_report_pipeline(input_path, out, report_config)
    console.print("[green]Trading report complete[/green]")
    console.print(f"Metrics: {result.metrics_path}")
    console.print(f"PDF report: {result.pdf_report_path}")
    console.print(f"Dashboard: {result.dashboard_path}")
