from pathlib import Path

from typer.testing import CliRunner

from chromeguard import cli

runner = CliRunner()


def test_whitelist_add(tmp_path: Path, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("CHROMEGUARD_DATA", str(data_dir))
    result = runner.invoke(cli.app, ["whitelist", "add", "abcd"])
    assert result.exit_code == 0
    assert "Added" in result.stdout


def test_update_command() -> None:
    result = runner.invoke(cli.app, ["update"])
    assert result.exit_code == 0

