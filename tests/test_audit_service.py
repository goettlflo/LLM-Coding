"""Issue 0005: Audit-Log-Infrastruktur (BR-KAU-04, arc42 Kapitel 8.4)."""
from __future__ import annotations

from app.container import Anwendungskontext


def test_ereignis_wird_unveraenderlich_protokolliert(kontext: Anwendungskontext) -> None:
    kontext.audit_service.protokollieren(
        ereignis_typ="kaution_hinterlegung",
        betrag_oder_zustand="20",
        ausloeser="mitglied:m1",
        referenz_id="ausleihe:a1",
    )

    eintraege = kontext.audit_repository.alle_fuer("ausleihe:a1")

    assert len(eintraege) == 1
    eintrag = eintraege[0]
    assert eintrag["ereignis_typ"] == "kaution_hinterlegung"
    assert eintrag["betrag_oder_zustand"] == "20"
    assert eintrag["ausloeser"] == "mitglied:m1"
    assert eintrag["zeitstempel"]


def test_mehrere_ereignisse_bleiben_alle_erhalten(kontext: Anwendungskontext) -> None:
    kontext.audit_service.protokollieren("zustand", "ausgeliehen", "thekendienst", "gegenstand:g1")
    kontext.audit_service.protokollieren("zustand", "in_pruefung", "thekendienst", "gegenstand:g1")

    eintraege = kontext.audit_repository.alle_fuer("gegenstand:g1")

    assert len(eintraege) == 2
