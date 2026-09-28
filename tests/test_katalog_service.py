"""Issue 0003: Gegenstand/Kategorie anlegen und abfragen (BR-KAT-01..04)."""
from __future__ import annotations

import pytest

from app.container import Anwendungskontext
from app.errors import NotFoundError, ValidationError
from app.services.katalog_service import kaution_berechnen


@pytest.mark.parametrize(
    ("wert", "erwartete_kaution"),
    [
        (10, 5),  # 20% = 2 -> unter Mindestbetrag, gedeckelt auf 5
        (100, 20),
        (600, 100),  # 20% = 120 -> gedeckelt auf 100
        (12.5, 5),  # 20% = 2.5, kaufmännisch auf 3 -> unter Mindestbetrag, gedeckelt auf 5
        (37.5, 8),  # 20% = 7.5, kaufmännisch gerundet auf 8
    ],
)
def test_kaution_berechnung_br_kat_04(wert: float, erwartete_kaution: int) -> None:
    assert kaution_berechnen(wert) == erwartete_kaution


def test_inventarnummer_ist_eindeutig_br_kat_01(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    kontext.katalog_service.gegenstand_anlegen("INV-001", kategorie.id, 100)

    with pytest.raises(ValidationError):
        kontext.katalog_service.gegenstand_anlegen("INV-001", kategorie.id, 50)


def test_gegenstand_referenziert_existierende_kategorie(kontext: Anwendungskontext) -> None:
    with pytest.raises(NotFoundError):
        kontext.katalog_service.gegenstand_anlegen("INV-002", "unbekannt", 100)


def test_gegenstand_anlegen_und_abfragen(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    angelegt = kontext.katalog_service.gegenstand_anlegen("INV-003", kategorie.id, 100)

    gelesen = kontext.katalog_service.gegenstand_lesen(angelegt.id)

    assert gelesen.inventarnummer == "INV-003"
    assert gelesen.kaution == 20
    assert gelesen.zustand == "verfuegbar"


def test_verfuegbarkeit_zaehlt_nur_verfuegbare_gegenstaende_suc_05(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    kontext.katalog_service.gegenstand_anlegen("INV-010", kategorie.id, 100)
    ausgeliehen = kontext.katalog_service.gegenstand_anlegen("INV-011", kategorie.id, 100)
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")
    kontext.ausleihe_service.ausgeben(ausgeliehen.id, mitglied.id)

    verfuegbarkeit = kontext.katalog_service.verfuegbarkeit(kategorie.id)

    assert verfuegbarkeit.anzahl_verfuegbar == 1
    assert verfuegbarkeit.warteschlangenlaenge == 0


def test_verfuegbarkeit_liefert_warteschlangenlaenge_suc_05(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")
    kontext.vormerkung_service.vormerken(kategorie.id, mitglied.id)

    verfuegbarkeit = kontext.katalog_service.verfuegbarkeit(kategorie.id)

    assert verfuegbarkeit.warteschlangenlaenge == 1


def test_verfuegbarkeit_mit_unbekannter_kategorie_wirft_not_found(kontext: Anwendungskontext) -> None:
    with pytest.raises(NotFoundError):
        kontext.katalog_service.verfuegbarkeit("unbekannt")
