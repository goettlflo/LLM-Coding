from __future__ import annotations

import sqlite3

import pytest

from app.container import Anwendungskontext, erstellen
from app.db import init_db


@pytest.fixture
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    init_db(connection)
    yield connection
    connection.close()


@pytest.fixture
def kontext(conn: sqlite3.Connection) -> Anwendungskontext:
    return erstellen(conn)
