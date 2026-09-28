"""Issue 0002: REST-API Health-Check und Grundgerüst; Issue 0007/0008: SUC-01/SUC-02."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.app import create_app


@pytest.fixture
def client(tmp_path) -> TestClient:
    db_path = str(tmp_path / "leihgut.db")
    app = create_app(db_path)
    return TestClient(app)


def test_health_antwortet_200(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _kategorie_anlegen(client: TestClient, einweisungspflichtig=False) -> str:
    response = client.post(
        "/kategorien",
        json={
            "name": "Zelt",
            "leihdauerTage": 14,
            "wartungsintervall": 20,
            "einweisungspflichtig": einweisungspflichtig,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _gegenstand_anlegen(client: TestClient, kategorie_id: str, inventarnummer="INV-1") -> str:
    response = client.post(
        "/gegenstaende",
        json={
            "inventarnummer": inventarnummer,
            "kategorieId": kategorie_id,
            "wiederbeschaffungswert": 100,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _mitglied_anlegen(client: TestClient, name="Karim") -> str:
    response = client.post("/mitglieder", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def test_suc_01_ausgabe_erfolgreich(client: TestClient) -> None:
    kategorie_id = _kategorie_anlegen(client)
    gegenstand_id = _gegenstand_anlegen(client, kategorie_id)
    mitglied_id = _mitglied_anlegen(client)

    response = client.post(
        f"/gegenstaende/{gegenstand_id}/ausgabe",
        json={"mitgliedId": mitglied_id},
        headers={"X-Rolle": "thekendienst"},
    )

    assert response.status_code == 201
    assert response.json()["kaution"] == 20


def test_suc_01_ohne_passende_rolle_wird_abgelehnt_403(client: TestClient) -> None:
    kategorie_id = _kategorie_anlegen(client)
    gegenstand_id = _gegenstand_anlegen(client, kategorie_id)
    mitglied_id = _mitglied_anlegen(client)

    response = client.post(
        f"/gegenstaende/{gegenstand_id}/ausgabe",
        json={"mitgliedId": mitglied_id},
        headers={"X-Rolle": "mitglied"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_suc_01_unbekannter_gegenstand_404(client: TestClient) -> None:
    mitglied_id = _mitglied_anlegen(client)

    response = client.post(
        "/gegenstaende/unbekannt/ausgabe",
        json={"mitgliedId": mitglied_id},
        headers={"X-Rolle": "thekendienst"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_suc_02_verlaengerung_erfolgreich(client: TestClient) -> None:
    kategorie_id = _kategorie_anlegen(client)
    gegenstand_id = _gegenstand_anlegen(client, kategorie_id)
    mitglied_id = _mitglied_anlegen(client)
    ausgabe = client.post(
        f"/gegenstaende/{gegenstand_id}/ausgabe",
        json={"mitgliedId": mitglied_id},
        headers={"X-Rolle": "thekendienst"},
    )
    ausleihe_id = ausgabe.json()["id"]

    response = client.post(
        f"/ausleihen/{ausleihe_id}/verlaengerung", headers={"X-Rolle": "mitglied"}
    )

    assert response.status_code == 200
    assert response.json()["verlaengert"] is True


def test_suc_02_zweite_verlaengerung_409(client: TestClient) -> None:
    kategorie_id = _kategorie_anlegen(client)
    gegenstand_id = _gegenstand_anlegen(client, kategorie_id)
    mitglied_id = _mitglied_anlegen(client)
    ausgabe = client.post(
        f"/gegenstaende/{gegenstand_id}/ausgabe",
        json={"mitgliedId": mitglied_id},
        headers={"X-Rolle": "thekendienst"},
    )
    ausleihe_id = ausgabe.json()["id"]
    client.post(f"/ausleihen/{ausleihe_id}/verlaengerung", headers={"X-Rolle": "mitglied"})

    response = client.post(
        f"/ausleihen/{ausleihe_id}/verlaengerung", headers={"X-Rolle": "mitglied"}
    )

    assert response.status_code == 409
    assert response.json()["code"] == "EXTENSION_NOT_ALLOWED"


def test_suc_03_ruecknahme_erfolgreich(client: TestClient) -> None:
    kategorie_id = _kategorie_anlegen(client)
    gegenstand_id = _gegenstand_anlegen(client, kategorie_id)
    mitglied_id = _mitglied_anlegen(client)
    client.post(
        f"/gegenstaende/{gegenstand_id}/ausgabe",
        json={"mitgliedId": mitglied_id},
        headers={"X-Rolle": "thekendienst"},
    )

    response = client.post(
        f"/gegenstaende/{gegenstand_id}/ruecknahme",
        json={"auffaelligkeit": "Riss im Stoff"},
        headers={"X-Rolle": "thekendienst"},
    )

    assert response.status_code == 200
    assert response.json()["zustand"] == "in_pruefung"


def test_suc_03_unbekannter_gegenstand_404(client: TestClient) -> None:
    response = client.post(
        "/gegenstaende/unbekannt/ruecknahme",
        json={},
        headers={"X-Rolle": "thekendienst"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_suc_03_nicht_ausgeliehener_gegenstand_404(client: TestClient) -> None:
    kategorie_id = _kategorie_anlegen(client)
    gegenstand_id = _gegenstand_anlegen(client, kategorie_id)

    response = client.post(
        f"/gegenstaende/{gegenstand_id}/ruecknahme",
        json={},
        headers={"X-Rolle": "thekendienst"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
