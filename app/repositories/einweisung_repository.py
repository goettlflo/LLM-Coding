"""Repository für Einweisung (BR-AUS-04)."""
from __future__ import annotations

import sqlite3
import uuid

from app.models import Einweisung


class EinweisungRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def anlegen(self, mitglied_id: str, kategorie_id: str, datum: str) -> Einweisung:
        einweisung_id = uuid.uuid4().hex
        self._conn.execute(
            "INSERT INTO einweisung (id, mitglied_id, kategorie_id, datum) VALUES (?, ?, ?, ?)",
            (einweisung_id, mitglied_id, kategorie_id, datum),
        )
        self._conn.commit()
        return Einweisung(einweisung_id, mitglied_id, kategorie_id, datum)

    def existiert(self, mitglied_id: str, kategorie_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM einweisung WHERE mitglied_id = ? AND kategorie_id = ?",
            (mitglied_id, kategorie_id),
        ).fetchone()
        return row is not None
