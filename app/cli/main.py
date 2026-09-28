"""CLI für den Wart (ADR-0005: Typer). Fachbefehle (SUC-08, SUC-09) folgen in späteren Epics."""
from __future__ import annotations

import os

import typer

from app.container import erstellen
from app.db import get_connection, init_db
from app.errors import DomainError, NotFoundError

app = typer.Typer(help="Leihgut-Verwaltung: Kommandozeile für den Wart.")
pruefung_app = typer.Typer(help="Prüfprotokolle des Warts (SUC-07).")
app.add_typer(pruefung_app, name="pruefung")
wartung_app = typer.Typer(help="Wartung abschließen (SUC-08).")
app.add_typer(wartung_app, name="wartung")


def _kontext():
    db_path = os.environ.get("LEIHGUT_DB_PATH", "leihgut.db")
    conn = get_connection(db_path)
    init_db(conn)
    return erstellen(conn)


@app.callback()
def leihgut() -> None:
    """Leihgut-Verwaltung: Kommandozeile für den Wart."""


@app.command()
def health() -> None:
    """Prüft, ob das Datenbankschema aufgebaut werden kann (Grundgerüst, Issue 0002)."""
    _kontext()
    typer.echo("ok")


@pruefung_app.command("abschliessen")
def pruefung_abschliessen(
    gegenstand: str = typer.Option(..., "--gegenstand"),
    ergebnis: str = typer.Option(..., "--ergebnis"),
    abzug: int = typer.Option(0, "--abzug"),
    rolle: str = typer.Option(..., "--rolle"),
) -> None:
    """Schließt das Prüfprotokoll ab und entscheidet über die Kaution (SUC-07)."""
    kontext = _kontext()
    try:
        kontext.rueckgabe_service.pruefung_abschliessen(
            gegenstand, ergebnis, abzug=abzug, rolle=rolle
        )
    except NotFoundError as fehler:
        typer.echo(str(fehler), err=True)
        raise typer.Exit(code=2)
    except DomainError as fehler:
        typer.echo(str(fehler), err=True)
        raise typer.Exit(code=1)

    folgezustand = kontext.gegenstand_repository.finden(gegenstand).zustand
    typer.echo(f"Folgezustand: {folgezustand}")


@wartung_app.command("abschliessen")
def wartung_abschliessen(
    gegenstand: str = typer.Option(..., "--gegenstand"),
    rolle: str = typer.Option(..., "--rolle"),
) -> None:
    """Schließt die Wartung ab: Zustand verfügbar, Nutzungszähler auf null (SUC-08)."""
    kontext = _kontext()
    try:
        gegenstand_nachher = kontext.wartung_service.wartung_abschliessen(gegenstand, rolle=rolle)
    except NotFoundError as fehler:
        typer.echo(str(fehler), err=True)
        raise typer.Exit(code=2)
    except DomainError as fehler:
        typer.echo(str(fehler), err=True)
        raise typer.Exit(code=1)

    typer.echo(
        f"Zustand: {gegenstand_nachher.zustand}, Nutzungszähler: {gegenstand_nachher.nutzungszaehler}"
    )


@app.command("ausmustern")
def ausmustern(
    gegenstand: str = typer.Option(..., "--gegenstand"),
    rolle: str = typer.Option(..., "--rolle"),
) -> None:
    """Mustert einen Gegenstand endgültig aus, Vormerkungen bleiben unangetastet (SUC-09)."""
    kontext = _kontext()
    try:
        gegenstand_nachher = kontext.wartung_service.ausmustern(gegenstand, rolle=rolle)
    except NotFoundError as fehler:
        typer.echo(str(fehler), err=True)
        raise typer.Exit(code=2)
    except DomainError as fehler:
        typer.echo(str(fehler), err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Zustand: {gegenstand_nachher.zustand}")


if __name__ == "__main__":
    app()
