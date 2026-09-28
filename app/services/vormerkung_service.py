"""VormerkungService — Kategorie vormerken (Issue 0017, BR-VM-01, BR-VM-02, BR-VM-08)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.errors import NotFoundError
from app.models import Vormerkung
from app.repositories.kategorie_repository import KategorieRepository
from app.repositories.mitglied_repository import MitgliedRepository
from app.repositories.vormerkung_repository import VormerkungRepository


class VormerkungService:
    def __init__(
        self,
        kategorie_repository: KategorieRepository,
        mitglied_repository: MitgliedRepository,
        vormerkung_repository: VormerkungRepository,
    ) -> None:
        self._kategorie_repository = kategorie_repository
        self._mitglied_repository = mitglied_repository
        self._vormerkung_repository = vormerkung_repository

    def vormerken(self, kategorie_id: str, mitglied_id: str) -> tuple[Vormerkung, int]:
        if self._kategorie_repository.finden(kategorie_id) is None:  # BR-VM-01
            raise NotFoundError(f"Kategorie {kategorie_id} nicht gefunden")
        if self._mitglied_repository.finden(mitglied_id) is None:  # BR-VM-01
            raise NotFoundError(f"Mitglied {mitglied_id} nicht gefunden")

        # BR-VM-08: keine Sperrprüfung — gesperrtes Mitglied darf vormerken
        eingangszeit = datetime.now(timezone.utc).isoformat()
        vormerkung = self._vormerkung_repository.anlegen(kategorie_id, mitglied_id, eingangszeit)

        warteschlange = self._vormerkung_repository.warteschlange(kategorie_id)  # BR-VM-02
        position = next(
            index + 1 for index, eintrag in enumerate(warteschlange) if eintrag.id == vormerkung.id
        )
        return vormerkung, position
