"""Repository für Vormerkung — minimale Grundlage für BR-AUS-07.

Vollständige Vormerkungs-Verwaltung (Anlegen über REST/CLI, Warteschlange) folgt in Epic 0016.
"""
from __future__ import annotations

import sqlite3
import uuid


class VormerkungRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def anlegen(self, kategorie_id: str, mitglied_id: str, eingangszeit: str) -> str:
        vormerkung_id = uuid.uuid4().hex
        self._conn.execute(
            "INSERT INTO vormerkung (id, kategorie_id, mitglied_id, eingangszeit) VALUES (?, ?, ?, ?)",
            (vormerkung_id, kategorie_id, mitglied_id, eingangszeit),
        )
        self._conn.commit()
        return vormerkung_id

    def hat_offene_vormerkung(self, kategorie_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM vormerkung WHERE kategorie_id = ?", (kategorie_id,)
        ).fetchone()
        return row is not None
