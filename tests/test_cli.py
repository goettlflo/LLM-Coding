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


def _in_pruefung(tmp_path, monkeypatch) -> str:
    monkeypatch.setenv("LEIHGUT_DB_PATH", str(tmp_path / "leihgut.db"))
    from app.container import erstellen
    from app.db import get_connection, init_db

    conn = get_connection(str(tmp_path / "leihgut.db"))
    init_db(conn)
    kontext = erstellen(conn)
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    gegenstand = kontext.katalog_service.gegenstand_anlegen("INV-CLI-1", kategorie.id, 100)
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")
    kontext.ausleihe_service.ausgeben(gegenstand.id, mitglied.id)
    kontext.rueckgabe_service.zuruecknehmen(gegenstand.id)
    conn.close()
    return gegenstand.id


def test_cli_pruefung_abschliessen_erfolgreich(tmp_path, monkeypatch) -> None:
    gegenstand_id = _in_pruefung(tmp_path, monkeypatch)

    result = runner.invoke(
        app,
        [
            "pruefung",
            "abschliessen",
            "--gegenstand",
            gegenstand_id,
            "--ergebnis",
            "unauffaellig",
            "--rolle",
            "wart",
        ],
    )

    assert result.exit_code == 0
    assert "Folgezustand: verfuegbar" in result.stdout


def test_cli_pruefung_abschliessen_falsche_rolle_exit_1(tmp_path, monkeypatch) -> None:
    gegenstand_id = _in_pruefung(tmp_path, monkeypatch)

    result = runner.invoke(
        app,
        [
            "pruefung",
            "abschliessen",
            "--gegenstand",
            gegenstand_id,
            "--ergebnis",
            "unauffaellig",
            "--rolle",
            "thekendienst",
        ],
    )

    assert result.exit_code == 1


def test_cli_pruefung_abschliessen_unbekannter_gegenstand_exit_2(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LEIHGUT_DB_PATH", str(tmp_path / "leihgut.db"))

    result = runner.invoke(
        app,
        [
            "pruefung",
            "abschliessen",
            "--gegenstand",
            "unbekannt",
            "--ergebnis",
            "unauffaellig",
            "--rolle",
            "wart",
        ],
    )

    assert result.exit_code == 2


def _wartungsfaellig(tmp_path, monkeypatch) -> str:
    monkeypatch.setenv("LEIHGUT_DB_PATH", str(tmp_path / "leihgut.db"))
    from app.container import erstellen
    from app.db import get_connection, init_db

    conn = get_connection(str(tmp_path / "leihgut.db"))
    init_db(conn)
    kontext = erstellen(conn)
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    gegenstand = kontext.katalog_service.gegenstand_anlegen("INV-CLI-2", kategorie.id, 100)
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")
    kontext.ausleihe_service.ausgeben(gegenstand.id, mitglied.id)
    kontext.rueckgabe_service.zuruecknehmen(gegenstand.id)
    kontext.rueckgabe_service.pruefung_abschliessen(gegenstand.id, "wartungsfaellig")
    conn.close()
    return gegenstand.id


def test_cli_wartung_abschliessen_erfolgreich(tmp_path, monkeypatch) -> None:
    gegenstand_id = _wartungsfaellig(tmp_path, monkeypatch)

    result = runner.invoke(
        app,
        ["wartung", "abschliessen", "--gegenstand", gegenstand_id, "--rolle", "wart"],
    )

    assert result.exit_code == 0
    assert "Zustand: verfuegbar" in result.stdout
    assert "Nutzungszähler: 0" in result.stdout


def test_cli_wartung_abschliessen_falsche_rolle_exit_1(tmp_path, monkeypatch) -> None:
    gegenstand_id = _wartungsfaellig(tmp_path, monkeypatch)

    result = runner.invoke(
        app,
        ["wartung", "abschliessen", "--gegenstand", gegenstand_id, "--rolle", "thekendienst"],
    )

    assert result.exit_code == 1


def test_cli_wartung_abschliessen_unbekannter_gegenstand_exit_2(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LEIHGUT_DB_PATH", str(tmp_path / "leihgut.db"))

    result = runner.invoke(
        app,
        ["wartung", "abschliessen", "--gegenstand", "unbekannt", "--rolle", "wart"],
    )

    assert result.exit_code == 2
