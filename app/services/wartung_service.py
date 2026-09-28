"""WartungService — Wartung abschließen (Issue 0014) und Ausmustern (Issue 0015).

BR-WA-03, BR-WA-04, BR-VM-07 (ADR-0003: ein Service je fachlichem Vorgang).
"""
from __future__ import annotations

from app.errors import ConflictError, NotFoundError, ValidationError
from app.models import Gegenstand
from app.repositories.gegenstand_repository import GegenstandRepository
from app.services.vormerkung_service import VormerkungService


class WartungService:
    def __init__(
        self, gegenstand_repository: GegenstandRepository, vormerkung_service: VormerkungService
    ) -> None:
        self._gegenstand_repository = gegenstand_repository
        self._vormerkung_service = vormerkung_service

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
        self._vormerkung_service.zuteilen(gegenstand.id, gegenstand.kategorie_id)  # BR-VM-03
        return self._gegenstand_repository.finden(gegenstand.id)

    def ausmustern(self, gegenstand_id: str, rolle: str = "wart") -> Gegenstand:
        if rolle != "wart":
            raise ValidationError("Nur der Wart mustert Gegenstände aus", code="FORBIDDEN")

        gegenstand = self._gegenstand_repository.finden(gegenstand_id)
        if gegenstand is None:
            raise NotFoundError(f"Gegenstand {gegenstand_id} nicht gefunden")

        # BR-VM-07: Vormerkungs-Warteschlange bleibt unangetastet
        erfolgreich = self._gegenstand_repository.zustand_setzen(
            gegenstand.id, "ausgemustert", gegenstand.version
        )
        if not erfolgreich:
            raise ConflictError("Gegenstand wurde inzwischen anderweitig verändert")

        return self._gegenstand_repository.finden(gegenstand.id)
