"""WartungService — Wartung abschließen (Issue 0014) und Ausmustern (Issue 0015).

BR-WA-03, BR-WA-04, BR-VM-07 (ADR-0003: ein Service je fachlichem Vorgang).
"""
from __future__ import annotations

from app.errors import ConflictError, NotFoundError, ValidationError
from app.models import Gegenstand
from app.repositories.gegenstand_repository import GegenstandRepository


class WartungService:
    def __init__(self, gegenstand_repository: GegenstandRepository) -> None:
        self._gegenstand_repository = gegenstand_repository

    def wartung_abschliessen(self, gegenstand_id: str, rolle: str = "wart") -> Gegenstand:
        if rolle != "wart":  # BR-WA-04
            raise ValidationError("Nur der Wart schließt die Wartung ab", code="FORBIDDEN")

        gegenstand = self._gegenstand_repository.finden(gegenstand_id)
        if gegenstand is None:
            raise NotFoundError(f"Gegenstand {gegenstand_id} nicht gefunden")
        if gegenstand.zustand != "wartungsfaellig":
            raise ConflictError("Gegenstand ist nicht wartungsfällig")

        erfolgreich = self._gegenstand_repository.zustand_wechseln_atomar(
            gegenstand.id, "wartungsfaellig", "verfuegbar", gegenstand.version
        )
        if not erfolgreich:
            raise ConflictError("Gegenstand wurde inzwischen anderweitig verändert")

        self._gegenstand_repository.nutzungszaehler_zuruecksetzen(gegenstand.id)  # BR-WA-03
        return self._gegenstand_repository.finden(gegenstand.id)
