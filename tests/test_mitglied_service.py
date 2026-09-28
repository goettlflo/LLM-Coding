"""Issue 0004: Mitglied-Stammdaten und Einweisung (BR-AUS-04)."""
from __future__ import annotations

from app.container import Anwendungskontext


def test_einweisung_gilt_nur_fuer_ihre_kategorie(kontext: Anwendungskontext) -> None:
    mitglied = kontext.mitglied_service.mitglied_anlegen("Karim")
    kategorie_a = kontext.katalog_service.kategorie_anlegen("Kettensäge", 7, 10, True)
    kategorie_b = kontext.katalog_service.kategorie_anlegen("Zelt", 14, 20, False)

    assert not kontext.mitglied_service.ist_eingewiesen(mitglied.id, kategorie_a.id)

    kontext.mitglied_service.einweisung_erfassen(mitglied.id, kategorie_a.id)

    assert kontext.mitglied_service.ist_eingewiesen(mitglied.id, kategorie_a.id)
    assert not kontext.mitglied_service.ist_eingewiesen(mitglied.id, kategorie_b.id)
