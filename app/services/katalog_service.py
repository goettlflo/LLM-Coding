"""KatalogService — Kategorien und Gegenstände anlegen/abfragen (Issue 0003, BR-KAT-01..04)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.errors import NotFoundError, ValidationError
from app.models import Gegenstand, Kategorie, Verfuegbarkeit
from app.repositories.gegenstand_repository import GegenstandRepository
from app.repositories.kategorie_repository import KategorieRepository
from app.repositories.vormerkung_repository import VormerkungRepository

KAUTION_SATZ = Decimal("0.2")
KAUTION_MIN = 5
KAUTION_MAX = 100


def kaution_berechnen(wiederbeschaffungswert: float) -> int:
    """BR-KAT-04: 20 % des Wiederbeschaffungswerts, kaufmännisch gerundet, gedeckelt auf [5, 100]."""
    roh = Decimal(str(wiederbeschaffungswert)) * KAUTION_SATZ
    gerundet = int(roh.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return max(KAUTION_MIN, min(KAUTION_MAX, gerundet))


class KatalogService:
    def __init__(
        self,
        kategorie_repository: KategorieRepository,
        gegenstand_repository: GegenstandRepository,
        vormerkung_repository: VormerkungRepository,
    ) -> None:
        self._kategorie_repository = kategorie_repository
        self._gegenstand_repository = gegenstand_repository
        self._vormerkung_repository = vormerkung_repository

    def kategorie_anlegen(
        self,
        name: str,
        leihdauer_tage: int,
        wartungsintervall: int,
        einweisungspflichtig: bool,
    ) -> Kategorie:
        return self._kategorie_repository.anlegen(
            name, leihdauer_tage, wartungsintervall, einweisungspflichtig
        )

    def kategorie_lesen(self, kategorie_id: str) -> Kategorie:
        kategorie = self._kategorie_repository.finden(kategorie_id)
        if kategorie is None:
            raise NotFoundError(f"Kategorie {kategorie_id} nicht gefunden")
        return kategorie

    def gegenstand_anlegen(
        self, inventarnummer: str, kategorie_id: str, wiederbeschaffungswert: float
    ) -> Gegenstand:
        # BR-KAT-01: eindeutige Inventarnummer, Kategorie muss existieren
        if self._gegenstand_repository.inventarnummer_existiert(inventarnummer):
            raise ValidationError(
                f"Inventarnummer {inventarnummer} ist bereits vergeben", code="DUPLICATE_INVENTARNUMMER"
            )
        if self._kategorie_repository.finden(kategorie_id) is None:
            raise NotFoundError(f"Kategorie {kategorie_id} nicht gefunden")
        # BR-KAT-03
        if wiederbeschaffungswert <= 0:
            raise ValidationError(
                "Wiederbeschaffungswert muss größer als 0 Euro sein", code="INVALID_WIEDERBESCHAFFUNGSWERT"
            )
        kaution = kaution_berechnen(wiederbeschaffungswert)
        return self._gegenstand_repository.anlegen(
            inventarnummer, kategorie_id, wiederbeschaffungswert, kaution
        )

    def gegenstand_lesen(self, gegenstand_id: str) -> Gegenstand:
        gegenstand = self._gegenstand_repository.finden(gegenstand_id)
        if gegenstand is None:
            raise NotFoundError(f"Gegenstand {gegenstand_id} nicht gefunden")
        return gegenstand

    def verfuegbarkeit(self, kategorie_id: str) -> Verfuegbarkeit:  # SUC-05
        if self._kategorie_repository.finden(kategorie_id) is None:
            raise NotFoundError(f"Kategorie {kategorie_id} nicht gefunden")
        return Verfuegbarkeit(
            anzahl_verfuegbar=self._gegenstand_repository.anzahl_verfuegbar_fuer_kategorie(kategorie_id),
            warteschlangenlaenge=self._vormerkung_repository.warteschlangenlaenge(kategorie_id),
        )
