# Bugreport: Manuelle Tests der Ausleihen-REST-API

**Datum:** 2026-09-28
**Getestete Endpunkte:** `POST /gegenstaende/{id}/ausgabe`, `POST /ausleihen/{id}/verlaengerung`, unterstützend: `POST /mitglieder/{id}/einweisungen`, `POST /gegenstaende`, `POST /mitglieder`, `POST /kategorien`
**Testmethode:** Manuelle Tests via `curl` gegen lokal gestarteten `uvicorn`-Server (SQLite-Testdatenbank), auf Basis von [system-use-cases.adoc](src/docs/specs/system-use-cases.adoc) und [geschaeftsregeln.adoc](src/docs/specs/geschaeftsregeln.adoc)

## Zusammenfassung

| # | Bug | Schweregrad | Endpunkt |
|---|-----|-------------|----------|
| 1 | 500 Internal Server Error bei Einweisung mit unbekannter `kategorieId` | Hoch | `POST /mitglieder/{id}/einweisungen` |
| 2 | Verlängerung ohne Prüfung der Mitglieds-Identität (Broken Object Level Authorization) | Hoch | `POST /ausleihen/{id}/verlaengerung` |
| 3 | `mitgliedId` akzeptiert leeren String, liefert irreführenden 404 statt 422 | Mittel | `POST /gegenstaende/{id}/ausgabe` |
| 4 | Leere Namen werden bei Mitglied/Kategorie ohne Validierung akzeptiert | Niedrig | `POST /mitglieder`, `POST /kategorien` |
| 5 | Fehlermeldung zeigt Python-Literal `'None'` statt sprechendem Text bei fehlendem `X-Rolle`-Header | Niedrig | `POST /gegenstaende/{id}/ausgabe`, `POST /ausleihen/{id}/verlaengerung` |

Alle Kernregeln BR-AUS-01, BR-AUS-02, BR-AUS-05, BR-AUS-06, BR-KAT-04 sowie das nebenläufige Ausgabe-Szenario (BR-NL-01, Race-Condition-Test mit parallelen Requests) wurden **korrekt** umgesetzt vorgefunden.

---

## Bug 1: 500 Internal Server Error bei Einweisung mit unbekannter `kategorieId`

**Schweregrad:** Hoch

**Request:**
```
POST /mitglieder/{mitglied_id}/einweisungen
Content-Type: application/json

{ "kategorieId": "nicht-existent" }
```

**Erwartet:** `404 NOT_FOUND` (analog zur Prüfung in `KatalogService.gegenstand_anlegen`, die eine unbekannte `kategorieId` bereits sauber abfängt).

**Tatsächlich:** `500 Internal Server Error` (kein JSON-Fehlerbody, unbehandelte Exception).

**Ursache:** [`MitgliedService.einweisung_erfassen`](app/services/mitglied_service.py) prüft nur, ob das Mitglied existiert, nicht ob die Kategorie existiert. Das `INSERT` in [`EinweisungRepository.anlegen`](app/repositories/einweisung_repository.py) verletzt daraufhin den FOREIGN KEY-Constraint auf `einweisung.kategorie_id`, und `sqlite3.IntegrityError` wird von keinem Exception-Handler in [`app/api/app.py`](app/api/app.py) abgefangen.

**Server-Log:**
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
  File "app/repositories/einweisung_repository.py", line 16, in anlegen
  File "app/services/mitglied_service.py", line 33, in einweisung_erfassen
  File "app/api/app.py", line 117, in einweisung_anlegen
```

**Auswirkung:** Interne Implementierungsdetails (Stacktrace potenziell in Logs, generische 500-Antwort ohne Fehlercode) werden nach außen sichtbar; Clients können keinen fachlichen Fehlercode auswerten. Verstößt gegen das in der API durchgängig verwendete Fehlerformat `{"code": ..., "message": ...}`.

---

## Bug 2: Verlängerung ohne Prüfung der Mitglieds-Identität (Broken Object Level Authorization)

**Schweregrad:** Hoch

**Request:**
```
POST /ausleihen/{beliebige_ausleihe_id}/verlaengerung
X-Rolle: mitglied
```

**Beobachtung:** Der Endpunkt akzeptiert jede syntaktisch gültige `ausleihe_id` und verlängert sie, sofern nur der Header `X-Rolle: mitglied` gesetzt ist — unabhängig davon, welchem Mitglied die Ausleihe tatsächlich gehört. Es wird **keine Mitglieds-ID** im Request mitgegeben oder geprüft.

**Erwartet (fachlich sinnvoll):** Ein Mitglied sollte nur seine **eigenen** Ausleihen verlängern können. `UC-02` beschreibt zwar "Ein Mitglied möchte die Rückgabefrist ... verschieben", aber weder [`system-use-cases.adoc`](src/docs/specs/system-use-cases.adoc) SUC-02 noch die Implementierung sehen eine Zuordnungsprüfung vor.

**Auswirkung:** Da `X-Rolle` clientseitig frei wählbar ist (dokumentiertes Risiko R-01, keine echte Authentifizierung in Release 1), kann jeder Aufrufer mit dem Header `X-Rolle: mitglied` beliebige fremde Ausleihen anderer Mitglieder verlängern (z. B. um eine drohende Rückgabefrist zu verschieben, ohne Berechtigung dazu zu haben). Dies ist ein klassischer Fall von *Broken Object Level Authorization* (OWASP API Security Top 10, API1:2023) und geht über das bereits dokumentierte Risiko R-01 (gefälschte Rolle) hinaus, da selbst bei korrekter Rollenzuordnung keine Objektzugehörigkeit geprüft wird.

---

## Bug 3: `mitgliedId` akzeptiert leeren String, liefert irreführenden 404 statt 422

**Schweregrad:** Mittel

**Request:**
```
POST /gegenstaende/{gegenstand_id}/ausgabe
X-Rolle: thekendienst

{ "mitgliedId": "" }
```

**Erwartet:** `422 VALIDATION_ERROR` mit klarer Meldung, dass `mitgliedId` nicht leer sein darf.

**Tatsächlich:** `404 NOT_FOUND` mit Meldung `"Mitglied  nicht gefunden"` (doppeltes Leerzeichen, da die leere ID in die Nachricht interpoliert wird).

**Ursache:** [`AusgabeRequest`](app/api/schemas.py) definiert `mitgliedId: str` ohne `min_length=1`; die Prüfung an der REST-Grenze (laut ADR-0001 vorgesehen) fehlt für dieses Feld.

---

## Bug 4: Leere Namen werden ohne Validierung akzeptiert

**Schweregrad:** Niedrig

**Requests:**
```
POST /mitglieder            { "name": "" }   → 201 Created
POST /kategorien             { "name": "" }   → 201 Created
```

**Erwartet:** `422`, da ein leerer Name fachlich sinnlos ist.

**Ursache:** `MitgliedAnlegenRequest.name` und `KategorieAnlegenRequest.name` sind als `str` ohne `min_length` deklariert.

---

## Bug 5: Fehlermeldung zeigt Python-Literal `'None'` bei fehlendem Rollen-Header

**Schweregrad:** Niedrig

**Request:**
```
POST /gegenstaende/{id}/ausgabe   (ohne Header X-Rolle)
```

**Tatsächlich:** `403 FORBIDDEN`, `{"message": "Rolle 'None' ist für diese Aktion nicht erlaubt"}`

**Erwartet:** Eine sprechende Meldung wie `"Es wurde keine Rolle angegeben"`, statt der Python-`None`-Repräsentation, die ein internes Implementierungsdetail preisgibt.

**Ursache:** [`rolle_pruefen`](app/api/app.py) formatiert den rohen Header-Wert (`None` bei Fehlen) direkt in die Fehlermeldung.

---

## Positiv verifiziert (keine Bugs gefunden)

- BR-AUS-01: Doppelte Ausgabe eines bereits ausgeliehenen Gegenstands → korrekt `409 ITEM_NOT_AVAILABLE`.
- BR-NL-01: Zwei parallele Ausgabe-Requests für denselben Gegenstand → korrekt genau ein `201`, ein `409` (optimistisches Locking funktioniert).
- BR-AUS-02: Vierte gleichzeitige Ausleihe eines Mitglieds → korrekt `422 MEMBER_LIMIT_REACHED`.
- BR-AUS-04: Einweisungspflichtiger Gegenstand ohne Einweisung → korrekt `422 INSTRUCTION_REQUIRED`; nach Einweisung erfolgreich.
- BR-AUS-05 / BR-KAT-04: Kautionsberechnung inkl. kaufmännischer Rundung und Deckelung (5–100 €) korrekt (getestet u. a. mit 37,50 € → 8 €).
- BR-AUS-06: Zweite Verlängerung derselben Ausleihe → korrekt `409 EXTENSION_NOT_ALLOWED`.
- Duplikat-Inventarnummer → korrekt `422 DUPLICATE_INVENTARNUMMER`.
- Fehlerhaftes JSON im Body → korrekt `422` mit FastAPI-Standardfehler.
- Rollenprüfung (403) bei falscher/fehlender Rolle für Ausgabe und Verlängerung greift grundsätzlich.
