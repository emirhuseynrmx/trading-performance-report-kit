from __future__ import annotations

from typer.testing import CliRunner

from trading_report_kit.cli import app
from trading_report_kit.sample_data import generate_trade_log


def test_cli_run_command(tmp_path) -> None:
    input_path = tmp_path / "trades.csv"
    generate_trade_log(rows=30, seed=11).to_csv(input_path, index=False)

    result = CliRunner().invoke(
        app,
        [
            str(input_path),
            "--config",
            "examples/config.json",
            "--out",
            str(tmp_path / "report"),
        ],
    )

    assert result.exit_code == 0
    assert "Trading report complete" in result.output
    assert (tmp_path / "report" / "performance_report.pdf").exists()
