# Leihgut-Verwaltung

Verwaltung für den Verleih von Gegenständen (Werkzeug, Geräte) an Vereinsmitglieder — Katalog, Ausleihe, Rückgabe/Prüfung, Kaution, Wartung, Vormerkung/Reservierung und Sperre bei Überfälligkeit.

Die vollständige Spezifikation (PRD, Use Cases, Geschäftsregeln, arc42-Architektur, Issues) liegt unter [src/docs](src/docs).

## Voraussetzungen

- Python ≥ 3.11

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tests

```bash
source .venv/bin/activate
python -m pytest
```

## REST-API starten

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Standardmäßig läuft die API auf Port 8000. Ein anderer Port lässt sich mit `--port` wählen, z. B. `uvicorn app.main:app --reload --port 8080`.

Die Datenbankdatei liegt standardmäßig unter `leihgut.db` im Arbeitsverzeichnis; über die Umgebungsvariable `LEIHGUT_DB_PATH` lässt sich ein anderer Pfad setzen.

### API-Dokumentation

FastAPI generiert die Doku automatisch aus den Endpunkten und Pydantic-Schemas — es gibt kein separat gepflegtes API-Dokument:

- **Swagger UI**: <http://localhost:8000/docs> — interaktiv, alle Endpunkte inkl. Request-/Response-Schemas, direkt im Browser testbar.
- **ReDoc**: <http://localhost:8000/redoc> — reine Referenzdarstellung.
- **OpenAPI-JSON**: <http://localhost:8000/openapi.json> — maschinenlesbar.

Die fachliche Spezifikation der Schnittstellen (Validierung, Statuscodes, Fehlercodes, EARS-Anforderungen) steht in [src/docs/specs/system-use-cases.adoc](src/docs/specs/system-use-cases.adoc).

Wichtige Endpunkte (Rolle per Header `X-Rolle`, sofern erforderlich):

| Methode | Pfad | Rolle | Zweck |
|---|---|---|---|
| GET | `/health` | – | Health-Check |
| POST | `/kategorien` | – | Kategorie anlegen |
| GET | `/kategorien/{id}` | – | Kategorie lesen |
| GET | `/kategorien/{id}/verfuegbarkeit` | – | Anzahl verfügbarer Gegenstände, Warteschlangenlänge |
| POST | `/kategorien/{id}/vormerkungen` | `mitglied`, `thekendienst` | Kategorie vormerken |
| POST | `/gegenstaende` | – | Gegenstand anlegen |
| GET | `/gegenstaende/{id}` | – | Gegenstand lesen (inkl. Rückgabefrist bzw. Reservierungsinhaber) |
| POST | `/gegenstaende/{id}/ausgabe` | `thekendienst` | Ausgabe an ein Mitglied |
| POST | `/gegenstaende/{id}/ruecknahme` | `thekendienst` | Rücknahme (Zustand „in Prüfung“) |
| POST | `/ausleihen/{id}/verlaengerung` | `thekendienst`, `mitglied` | Ausleihe verlängern |
| POST | `/mitglieder` | – | Mitglied anlegen |
| GET | `/mitglieder/{id}` | – | Mitglied lesen (inkl. abgeleitetem Sperrstatus) |
| POST | `/mitglieder/{id}/einweisungen` | – | Einweisung erfassen |

## CLI (Rolle: Wart)

```bash
leihgut --help
leihgut health
leihgut pruefung abschliessen --gegenstand <id> --ergebnis <unauffaellig|wartungsfaellig|verloren> [--abzug <euro>] --rolle wart
leihgut wartung abschliessen --gegenstand <id> --rolle wart
leihgut ausmustern --gegenstand <id> --rolle wart
```

Exit-Codes: `0` Erfolg, `1` Geschäftsregel verletzt, `2` unbekannte Gegenstand-ID.

## Projektstruktur

```
app/            Anwendungscode (Repositories, Services, REST-API, CLI)
tests/          pytest-Tests
src/docs/       Spezifikation: PRD, Use Cases, Geschäftsregeln, arc42-Architektur, Issues
```

Architekturentscheidungen stehen als ADRs unter [src/docs/arc42/adr](src/docs/arc42/adr), offene Vorhaben als Issue-Dateien unter [src/docs/issues](src/docs/issues) (Archiv abgeschlossener Issues: [src/docs/issues/closed](src/docs/issues/closed)).