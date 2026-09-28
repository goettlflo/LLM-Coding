"""AuditService — wiederverwendbarer, append-only Audit-Trail (Issue 0005, BR-KAU-04, arc42 8.2/8.4)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, audit_repository: AuditRepository) -> None:
        self._audit_repository = audit_repository

    def protokollieren(
        self, ereignis_typ: str, betrag_oder_zustand: str, ausloeser: str, referenz_id: str
    ) -> None:
        """Erzeugt einen unveränderlichen Eintrag mit Zeitstempel, Betrag/Zustand und Auslöser."""
        zeitstempel = datetime.now(timezone.utc).isoformat()
        self._audit_repository.eintragen(
            zeitstempel=zeitstempel,
            ereignis_typ=ereignis_typ,
            betrag_oder_zustand=betrag_oder_zustand,
            ausloeser=ausloeser,
            referenz_id=referenz_id,
        )
