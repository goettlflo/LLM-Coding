"""Issue 0014 (Wartung abschließen): BR-WA-03, BR-WA-04.
Issue 0015 (Gegenstand ausmustern): BR-VM-07.
"""
from __future__ import annotations

import pytest

from app.container import Anwendungskontext
from app.errors import ConflictError, NotFoundError, ValidationError


def _kategorie(kontext: Anwendungskontext, *, leihdauer_tage=14, einweisungspflichtig=False):
    return kontext.katalog_service.kategorie_anlegen(
        "Zelt", leihdauer_tage, 20, einweisungspflichtig
    )


def _gegenstand(kontext: Anwendungskontext, kategorie_id: str, inventarnummer="INV-100"):
    return kontext.katalog_service.gegenstand_anlegen(inventarnummer, kategorie_id, 100)


def _mitglied(kontext: Anwendungskontext, name="Karim"):
    return kontext.mitglied_service.mitglied_anlegen(name)


def _wartungsfaellig(kontext: Anwendungskontext, inventarnummer="INV-100"):
    kategorie = _kategorie(kontext)
    gegenstand = _gegenstand(kontext, kategorie.id, inventarnummer=inventarnummer)
    mitglied = _mitglied(kontext)
    kontext.ausleihe_service.ausgeben(gegenstand.id, mitglied.id)
    kontext.rueckgabe_service.zuruecknehmen(gegenstand.id)
    kontext.rueckgabe_service.pruefung_abschliessen(gegenstand.id, "wartungsfaellig")
    return kontext.gegenstand_repository.finden(gegenstand.id)


def test_wartung_abschliessen_setzt_zustand_und_zaehler_zurueck_br_wa_03(
    kontext: Anwendungskontext,
) -> None:
    gegenstand = _wartungsfaellig(kontext)

    ergebnis = kontext.wartung_service.wartung_abschliessen(gegenstand.id)

    assert ergebnis.zustand == "verfuegbar"
    assert ergebnis.nutzungszaehler == 0


def test_wartung_abschliessen_durch_falsche_rolle_wird_abgelehnt_br_wa_04(
    kontext: Anwendungskontext,
) -> None:
    gegenstand = _wartungsfaellig(kontext)

    with pytest.raises(ValidationError):
        kontext.wartung_service.wartung_abschliessen(gegenstand.id, rolle="thekendienst")


def test_wartung_abschliessen_nicht_wartungsfaelliger_gegenstand_wird_abgelehnt(
    kontext: Anwendungskontext,
) -> None:
    kategorie = _kategorie(kontext)
    gegenstand = _gegenstand(kontext, kategorie.id)

    with pytest.raises(ConflictError):
        kontext.wartung_service.wartung_abschliessen(gegenstand.id)


def test_wartung_abschliessen_unbekannter_gegenstand_wird_abgelehnt(
    kontext: Anwendungskontext,
) -> None:
    with pytest.raises(NotFoundError):
        kontext.wartung_service.wartung_abschliessen("unbekannt")
