"""Öffnungstage — Hilfsfunktionen für Reservierungsverfall (Issue 0018, BR-VM-04)."""
from __future__ import annotations

from datetime import date, timedelta

OEFFNUNGSTAGE = {1, 5}  # Dienstag, Samstag


def naechster_oeffnungstag(datum: date) -> date:
    kandidat = datum
    for _ in range(7):
        if kandidat.weekday() in OEFFNUNGSTAGE:
            return kandidat
        kandidat = kandidat + timedelta(days=1)
    return kandidat


def verfallszeit_berechnen(entstehungsdatum: date) -> date:
    return naechster_oeffnungstag(entstehungsdatum) + timedelta(days=3)
