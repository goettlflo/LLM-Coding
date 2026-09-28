"""CLI für den Wart (ADR-0005: Typer). Fachbefehle (SUC-07..09) folgen in späteren Epics."""
from __future__ import annotations

import os

import typer

from app.container import erstellen
from app.db import get_connection, init_db

app = typer.Typer(help="Leihgut-Verwaltung: Kommandozeile für den Wart.")


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


if __name__ == "__main__":
    app()
