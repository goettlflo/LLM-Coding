"""Domänen-Fehler mit Fehlercodes gemäß system-use-cases.adoc."""
from __future__ import annotations


class DomainError(Exception):
    """Basisklasse für fachliche Fehler; `code` entspricht dem REST-Fehlercode."""

    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ConflictError(DomainError):
    """Fachlicher Konflikt (REST 409), z. B. Gegenstand nicht verfügbar oder Wettlauf verloren (BR-NL-01)."""

    code = "ITEM_NOT_AVAILABLE"


class ValidationError(DomainError):
    """Verletzte Geschäftsregel (REST 422), z. B. Limit, Sperre, fehlende Einweisung."""

    code = "VALIDATION_ERROR"
