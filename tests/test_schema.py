"""Issue 0002: schema.sql läuft fehlerfrei gegen eine leere SQLite-Datei."""
from __future__ import annotations

import sqlite3

from app.db import init_db


def test_schema_laeuft_gegen_leere_datenbank(tmp_path) -> None:
    db_path = tmp_path / "leihgut.db"
    conn = sqlite3.connect(str(db_path))
    init_db(conn)

    tabellen = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }
    conn.close()

    erwartet = {
        "kategorie",
        "gegenstand",
        "mitglied",
        "einweisung",
        "ausleihe",
        "kaution",
        "vormerkung",
        "audit_log",
    }
    assert erwartet <= tabellen
