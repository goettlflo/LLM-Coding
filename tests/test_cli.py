"""Issue 0002: die CLI zeigt ihre Hilfe (`--help`) an."""
from __future__ import annotations

from typer.testing import CliRunner

from app.cli.main import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Leihgut-Verwaltung" in result.stdout


def test_cli_health(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LEIHGUT_DB_PATH", str(tmp_path / "leihgut.db"))

    result = runner.invoke(app, ["health"])

    assert result.exit_code == 0
    assert "ok" in result.stdout
