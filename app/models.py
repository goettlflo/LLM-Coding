"""Domänen-Objekte (Dataclasses) gemäß supplementary.adoc Entitätsmodell.

ADR-0004: Repository-Methoden geben Domänen-Objekte zurück, kein automatisches Mapping.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Kategorie:
    id: str
    name: str
    leihdauer_tage: int
    wartungsintervall: int
    einweisungspflichtig: bool


@dataclass(frozen=True)
class Gegenstand:
    id: str
    inventarnummer: str
    kategorie_id: str
    wiederbeschaffungswert: float
    kaution: int
    nutzungszaehler: int
    zustand: str
    version: int


@dataclass(frozen=True)
class Mitglied:
    id: str
    name: str
    gesperrt: bool


@dataclass(frozen=True)
class Einweisung:
    id: str
    mitglied_id: str
    kategorie_id: str
    datum: str


@dataclass(frozen=True)
class Ausleihe:
    id: str
    gegenstand_id: str
    mitglied_id: str
    ausgabedatum: str
    rueckgabefrist: str
    verlaengert: bool
    status: str


@dataclass(frozen=True)
class Kaution:
    id: str
    ausleihe_id: str
    betrag: int
    status: str


@dataclass(frozen=True)
class Pruefprotokoll:
    id: str
    gegenstand_id: str
    ausleihe_id: str
    ergebnis: str
    abzug: int
    schaden_vermerkt: bool
    erstellt_am: str


@dataclass(frozen=True)
class Vormerkung:
    id: str
    kategorie_id: str
    mitglied_id: str
    eingangszeit: str


@dataclass(frozen=True)
class Reservierung:
    id: str
    gegenstand_id: str
    mitglied_id: str
    status: str
    erstellt_am: str
    verfallszeit: str
