"""Uvicorn-Einstiegspunkt: `uvicorn app.main:app`."""
from __future__ import annotations

import os

from app.api.app import create_app

DB_PATH = os.environ.get("LEIHGUT_DB_PATH", "leihgut.db")

app = create_app(DB_PATH)
