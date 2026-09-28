"""RueckgabeService — Rücknahme an der Theke (Issue 0010).

BR-RP-01, BR-RP-02 (ADR-0003: ein Service je fachlichem Vorgang).
"""
from __future__ import annotations

from app.errors import ConflictError, NotFoundError
from app.models import Gegenstand
from app.repositories.gegenstand_repository import GegenstandRepository


class RueckgabeService:
    def __init__(self, gegenstand_repository: GegenstandRepository) -> None:
        self._gegenstand_repository = gegenstand_repository

    def zuruecknehmen(self, gegenstand_id: str, auffaelligkeit: str | None = None) -> Gegenstand:
        gegenstand = self._gegenstand_repository.finden(gegenstand_id)
        if gegenstand is None or gegenstand.zustand != "ausgeliehen":  # SUC-03
            raise NotFoundError(f"Gegenstand {gegenstand_id} ist nicht ausgeliehen")

        # BR-RP-01: Ausleihe bleibt offen, BR-RP-02: Kaution bleibt unverändert
        erfolgreich = self._gegenstand_repository.zustand_wechseln_atomar(
            gegenstand.id, "ausgeliehen", "in_pruefung", gegenstand.version
        )
        if not erfolgreich:
            raise ConflictError("Gegenstand wurde inzwischen anderweitig verändert")

        return self._gegenstand_repository.finden(gegenstand.id)
