"""Issue 0010 (Gegenstand zurücknehmen): BR-RP-01, BR-RP-02."""
from __future__ import annotations

import pytest

from app.container import Anwendungskontext
from app.errors import NotFoundError


def _kategorie(kontext: Anwendungskontext, *, leihdauer_tage=14, einweisungspflichtig=False):
    return kontext.katalog_service.kategorie_anlegen(
        "Zelt", leihdauer_tage, 20, einweisungspflichtig
    )


def _gegenstand(kontext: Anwendungskontext, kategorie_id: str, inventarnummer="INV-100"):
    return kontext.katalog_service.gegenstand_anlegen(inventarnummer, kategorie_id, 100)


def _mitglied(kontext: Anwendungskontext, name="Karim"):
    return kontext.mitglied_service.mitglied_anlegen(name)


def test_rueckgabe_versetzt_gegenstand_in_pruefung_ausleihe_bleibt_aktiv_br_rp_01(
    kontext: Anwendungskontext,
) -> None:
    kategorie = _kategorie(kontext)
    gegenstand = _gegenstand(kontext, kategorie.id)
    mitglied = _mitglied(kontext)
    ausleihe = kontext.ausleihe_service.ausgeben(gegenstand.id, mitglied.id)

    zurueckgenommen = kontext.rueckgabe_service.zuruecknehmen(gegenstand.id)

    assert zurueckgenommen.zustand == "in_pruefung"
    aktive_ausleihe = kontext.ausleihe_repository.finden(ausleihe.id)
    assert aktive_ausleihe.status == "aktiv"


def test_kaution_bleibt_nach_rueckgabe_mit_auffaelligkeit_unveraendert_br_rp_02(
    kontext: Anwendungskontext,
) -> None:
    kategorie = _kategorie(kontext)
    gegenstand = _gegenstand(kontext, kategorie.id)
    mitglied = _mitglied(kontext)
    ausleihe = kontext.ausleihe_service.ausgeben(gegenstand.id, mitglied.id)
    kaution_vorher = kontext.kaution_repository.finden_fuer_ausleihe(ausleihe.id)

    kontext.rueckgabe_service.zuruecknehmen(gegenstand.id, auffaelligkeit="Riss im Stoff")

    kaution_nachher = kontext.kaution_repository.finden_fuer_ausleihe(ausleihe.id)
    assert kaution_nachher.betrag == kaution_vorher.betrag
    assert kaution_nachher.status == kaution_vorher.status


def test_rueckgabe_nicht_ausgeliehener_gegenstand_wird_abgelehnt(
    kontext: Anwendungskontext,
) -> None:
    kategorie = _kategorie(kontext)
    gegenstand = _gegenstand(kontext, kategorie.id)

    with pytest.raises(NotFoundError):
        kontext.rueckgabe_service.zuruecknehmen(gegenstand.id)


def test_rueckgabe_unbekannter_gegenstand_wird_abgelehnt(kontext: Anwendungskontext) -> None:
    with pytest.raises(NotFoundError):
        kontext.rueckgabe_service.zuruecknehmen("unbekannt")
