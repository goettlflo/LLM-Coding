-- Schema: Leihgut-Verwaltung (Epic 0001 Katalog-Grundlage, Epic 0006 Ausleihe-Prozess)
-- ADR-0002 (SQLite-Datei), ADR-0004 (raw sqlite3, versioniertes Schema-Skript), ADR-0006 (Versions-Spalte)

CREATE TABLE IF NOT EXISTS kategorie (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    leihdauer_tage INTEGER NOT NULL,
    wartungsintervall INTEGER NOT NULL,
    einweisungspflichtig INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS gegenstand (
    id TEXT PRIMARY KEY,
    inventarnummer TEXT NOT NULL UNIQUE,
    kategorie_id TEXT NOT NULL REFERENCES kategorie(id),
    wiederbeschaffungswert REAL NOT NULL,
    kaution INTEGER NOT NULL,
    nutzungszaehler INTEGER NOT NULL DEFAULT 0,
    zustand TEXT NOT NULL DEFAULT 'verfuegbar',
    version INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mitglied (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gesperrt INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS einweisung (
    id TEXT PRIMARY KEY,
    mitglied_id TEXT NOT NULL REFERENCES mitglied(id),
    kategorie_id TEXT NOT NULL REFERENCES kategorie(id),
    datum TEXT NOT NULL,
    UNIQUE (mitglied_id, kategorie_id)
);

CREATE TABLE IF NOT EXISTS ausleihe (
    id TEXT PRIMARY KEY,
    gegenstand_id TEXT NOT NULL REFERENCES gegenstand(id),
    mitglied_id TEXT NOT NULL REFERENCES mitglied(id),
    ausgabedatum TEXT NOT NULL,
    rueckgabefrist TEXT NOT NULL,
    verlaengert INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'aktiv'
);

CREATE TABLE IF NOT EXISTS kaution (
    id TEXT PRIMARY KEY,
    ausleihe_id TEXT NOT NULL UNIQUE REFERENCES ausleihe(id),
    betrag INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'hinterlegt'
);

-- Minimale Grundlage fuer BR-AUS-07 (Verlaengerungssperre bei offener Vormerkung);
-- vollstaendige Vormerkungs-Verwaltung folgt in Epic 0016.
CREATE TABLE IF NOT EXISTS vormerkung (
    id TEXT PRIMARY KEY,
    kategorie_id TEXT NOT NULL REFERENCES kategorie(id),
    mitglied_id TEXT NOT NULL REFERENCES mitglied(id),
    eingangszeit TEXT NOT NULL
);

-- Issue 0005: append-only Audit-Log fuer Zustands- und Kautionsaenderungen (BR-KAU-04, arc42 Kapitel 8.4)
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    zeitstempel TEXT NOT NULL,
    ereignis_typ TEXT NOT NULL,
    betrag_oder_zustand TEXT NOT NULL,
    ausloeser TEXT NOT NULL,
    referenz_id TEXT NOT NULL
);

-- Issue 0018: Reservierung nach automatischer Zuteilung (BR-VM-03, BR-VM-04)
CREATE TABLE IF NOT EXISTS reservierung (
    id TEXT PRIMARY KEY,
    gegenstand_id TEXT NOT NULL REFERENCES gegenstand(id),
    mitglied_id TEXT NOT NULL REFERENCES mitglied(id),
    status TEXT NOT NULL DEFAULT 'aktiv',
    erstellt_am TEXT NOT NULL,
    verfallszeit TEXT NOT NULL
);

-- Issue 0011: Pruefprotokoll des Warts mit Kautionsentscheidung (BR-RP-05)
CREATE TABLE IF NOT EXISTS pruefprotokoll (
    id TEXT PRIMARY KEY,
    gegenstand_id TEXT NOT NULL REFERENCES gegenstand(id),
    ausleihe_id TEXT NOT NULL REFERENCES ausleihe(id),
    ergebnis TEXT NOT NULL,
    abzug INTEGER NOT NULL DEFAULT 0,
    schaden_vermerkt INTEGER NOT NULL DEFAULT 0,
    erstellt_am TEXT NOT NULL
);
