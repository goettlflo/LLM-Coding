"""Repository für Mitglied."""
from __future__ import annotations

import sqlite3
import uuid

from app.models import Mitglied


class MitgliedRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def anlegen(self, name: str) -> Mitglied:
        mitglied_id = uuid.uuid4().hex
        self._conn.execute(
            "INSERT INTO mitglied (id, name, gesperrt) VALUES (?, ?, 0)",
            (mitglied_id, name),
        )
        self._conn.commit()
        return Mitglied(id=mitglied_id, name=name, gesperrt=False)

    def finden(self, mitglied_id: str) -> Mitglied | None:
        row = self._conn.execute(
            "SELECT * FROM mitglied WHERE id = ?", (mitglied_id,)
        ).fetchone()
        if row is None:
            return None
        return Mitglied(id=row["id"], name=row["name"], gesperrt=bool(row["gesperrt"]))

    def sperre_setzen(self, mitglied_id: str, gesperrt: bool) -> None:
        """Test-/Grundlagen-Hilfsmethode; volle Sperr-Logik folgt in Epic 0019."""
        self._conn.execute(
            "UPDATE mitglied SET gesperrt = ? WHERE id = ?", (int(gesperrt), mitglied_id)
        )
        self._conn.commit()
