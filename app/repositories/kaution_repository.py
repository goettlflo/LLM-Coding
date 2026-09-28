"""Repository für Kaution (BR-AUS-05, BR-KAU-01)."""
from __future__ import annotations

import sqlite3
import uuid

from app.models import Kaution


class KautionRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def hinterlegen(self, ausleihe_id: str, betrag: int) -> Kaution:
        kaution_id = uuid.uuid4().hex
        self._conn.execute(
            "INSERT INTO kaution (id, ausleihe_id, betrag, status) VALUES (?, ?, ?, 'hinterlegt')",
            (kaution_id, ausleihe_id, betrag),
        )
        self._conn.commit()
        return Kaution(id=kaution_id, ausleihe_id=ausleihe_id, betrag=betrag, status="hinterlegt")

    def finden_fuer_ausleihe(self, ausleihe_id: str) -> Kaution | None:
        row = self._conn.execute(
            "SELECT * FROM kaution WHERE ausleihe_id = ?", (ausleihe_id,)
        ).fetchone()
        if row is None:
            return None
        return Kaution(
            id=row["id"], ausleihe_id=row["ausleihe_id"], betrag=row["betrag"], status=row["status"]
        )
