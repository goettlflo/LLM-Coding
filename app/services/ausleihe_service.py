"""AusleiheService — Ausgabe (Issue 0007) und Verlängerung (Issue 0008).

BR-AUS-01..07, BR-NL-01 (ADR-0006: optimistisches Locking über Gegenstand.version).
"""
from __future__ import annotations

from datetime import date, timedelta

from app.errors import ConflictError, NotFoundError, ValidationError
from app.models import Ausleihe
from app.repositories.ausleihe_repository import AusleiheRepository
from app.repositories.gegenstand_repository import GegenstandRepository
from app.repositories.kategorie_repository import KategorieRepository
from app.repositories.kaution_repository import KautionRepository
from app.repositories.mitglied_repository import MitgliedRepository
from app.repositories.vormerkung_repository import VormerkungRepository
from app.services.audit_service import AuditService
from app.services.mitglied_service import MitgliedService

AUSLEIHLIMIT = 3


class AusleiheService:
    def __init__(
        self,
        gegenstand_repository: GegenstandRepository,
        kategorie_repository: KategorieRepository,
        mitglied_repository: MitgliedRepository,
        ausleihe_repository: AusleiheRepository,
        kaution_repository: KautionRepository,
        vormerkung_repository: VormerkungRepository,
        mitglied_service: MitgliedService,
        audit_service: AuditService,
    ) -> None:
        self._gegenstand_repository = gegenstand_repository
        self._kategorie_repository = kategorie_repository
        self._mitglied_repository = mitglied_repository
        self._ausleihe_repository = ausleihe_repository
        self._kaution_repository = kaution_repository
        self._vormerkung_repository = vormerkung_repository
        self._mitglied_service = mitglied_service
        self._audit_service = audit_service

    def ausgeben(self, gegenstand_id: str, mitglied_id: str) -> Ausleihe:
        gegenstand = self._gegenstand_repository.finden(gegenstand_id)
        if gegenstand is None:
            raise NotFoundError(f"Gegenstand {gegenstand_id} nicht gefunden")
        mitglied = self._mitglied_repository.finden(mitglied_id)
        if mitglied is None:
            raise NotFoundError(f"Mitglied {mitglied_id} nicht gefunden")

        if self._mitglied_service.ist_gesperrt(mitglied_id):  # BR-AUS-03 (abgeleitet, BR-SP-01)
            raise ValidationError("Mitglied ist gesperrt", code="MEMBER_LOCKED")

        if self._ausleihe_repository.anzahl_aktiver_ausleihen(mitglied_id) >= AUSLEIHLIMIT:  # BR-AUS-02
            raise ValidationError("Ausleihlimit erreicht", code="MEMBER_LIMIT_REACHED")

        kategorie = self._kategorie_repository.finden(gegenstand.kategorie_id)
        if kategorie.einweisungspflichtig and not self._mitglied_service.ist_eingewiesen(
            mitglied_id, kategorie.id
        ):  # BR-AUS-04
            raise ValidationError("Einweisung für diese Kategorie fehlt", code="INSTRUCTION_REQUIRED")

        if gegenstand.zustand != "verfuegbar":  # BR-AUS-01
            raise ConflictError("Gegenstand ist nicht verfügbar")

        # BR-NL-01: atomarer Zustandswechsel, verliert den Wettlauf bei gleichzeitigem Zugriff
        erfolgreich = self._gegenstand_repository.zustand_wechseln_atomar(
            gegenstand.id, "verfuegbar", "ausgeliehen", gegenstand.version
        )
        if not erfolgreich:
            raise ConflictError("Gegenstand wurde inzwischen anderweitig ausgegeben")

        ausgabedatum = date.today()
        rueckgabefrist = ausgabedatum + timedelta(days=kategorie.leihdauer_tage)
        ausleihe = self._ausleihe_repository.anlegen(
            gegenstand.id, mitglied.id, ausgabedatum.isoformat(), rueckgabefrist.isoformat()
        )
        self._kaution_repository.hinterlegen(ausleihe.id, gegenstand.kaution)  # BR-AUS-05

        self._audit_service.protokollieren(
            "gegenstand_zustand", "ausgeliehen", f"mitglied:{mitglied.id}", gegenstand.id
        )
        self._audit_service.protokollieren(
            "kaution_hinterlegung", str(gegenstand.kaution), f"ausleihe:{ausleihe.id}", ausleihe.id
        )
        return ausleihe

    def verlaengern(self, ausleihe_id: str) -> Ausleihe:
        ausleihe = self._ausleihe_repository.finden(ausleihe_id)
        if ausleihe is None:
            raise NotFoundError(f"Ausleihe {ausleihe_id} nicht gefunden")

        if ausleihe.verlaengert:  # BR-AUS-06
            raise ConflictError("Ausleihe wurde bereits verlängert", code="EXTENSION_NOT_ALLOWED")

        if date.fromisoformat(ausleihe.rueckgabefrist) < date.today():  # BR-AUS-07 (überfällig)
            raise ConflictError("Ausleihe ist bereits überfällig", code="EXTENSION_NOT_ALLOWED")

        gegenstand = self._gegenstand_repository.finden(ausleihe.gegenstand_id)
        if self._vormerkung_repository.hat_offene_vormerkung(gegenstand.kategorie_id):  # BR-AUS-07
            raise ConflictError("Für die Kategorie liegt eine Vormerkung vor", code="EXTENSION_NOT_ALLOWED")

        kategorie = self._kategorie_repository.finden(gegenstand.kategorie_id)
        neue_rueckgabefrist = date.fromisoformat(ausleihe.rueckgabefrist) + timedelta(
            days=kategorie.leihdauer_tage
        )
        self._ausleihe_repository.verlaengern(ausleihe.id, neue_rueckgabefrist.isoformat())
        return self._ausleihe_repository.finden(ausleihe.id)
