"""Issue 0017: Kategorie vormerken (BR-VM-01, BR-VM-02, BR-VM-08)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.container import Anwendungskontext
from app.errors import NotFoundError


def test_zweite_vormerkung_landet_an_position_zwei_br_vm_01_02(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    mitglied_a = kontext.mitglied_service.mitglied_anlegen("Karim")
    mitglied_b = kontext.mitglied_service.mitglied_anlegen("Lena")

    _, position_a = kontext.vormerkung_service.vormerken(kategorie.id, mitglied_a.id)
    vormerkung_b, position_b = kontext.vormerkung_service.vormerken(kategorie.id, mitglied_b.id)

    assert position_a == 1
    assert position_b == 2
    assert vormerkung_b.kategorie_id == kategorie.id
    assert vormerkung_b.mitglied_id == mitglied_b.id


def test_gesperrtes_mitglied_darf_vormerken_br_vm_08(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)
    gegenstand = kontext.katalog_service.gegenstand_anlegen("INV-100", kategorie.id, 100)
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")
    ausleihe = kontext.ausleihe_service.ausgeben(gegenstand.id, mitglied.id)
    kontext.ausleihe_repository.rueckgabefrist_setzen(
        ausleihe.id, (date.today() - timedelta(days=1)).isoformat()
    )
    assert kontext.mitglied_service.ist_gesperrt(mitglied.id)

    vormerkung, position = kontext.vormerkung_service.vormerken(kategorie.id, mitglied.id)

    assert position == 1
    assert vormerkung.mitglied_id == mitglied.id


def test_vormerken_mit_unbekannter_kategorie_wirft_not_found(kontext: Anwendungskontext) -> None:
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")

    with pytest.raises(NotFoundError):
        kontext.vormerkung_service.vormerken("unbekannt", mitglied.id)


def test_vormerken_mit_unbekanntem_mitglied_wirft_not_found(kontext: Anwendungskontext) -> None:
    kategorie = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)

    with pytest.raises(NotFoundError):
        kontext.vormerkung_service.vormerken(kategorie.id, "unbekannt")
