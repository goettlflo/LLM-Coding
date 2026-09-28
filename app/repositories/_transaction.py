from __future__ import annotations

from contextlib import contextmanager
import sqlite3

_TRANSACTION_DEPTH: dict[int, int] = {}


def commit_when_unmanaged(conn: sqlite3.Connection) -> None:
    if _TRANSACTION_DEPTH.get(id(conn), 0) == 0:
        conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection, *, immediate: bool = False):
    key = id(conn)
    depth = _TRANSACTION_DEPTH.get(key, 0)
    if depth == 0:
        conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
    _TRANSACTION_DEPTH[key] = depth + 1
    try:
        yield
    except Exception:
        if _TRANSACTION_DEPTH.get(key, 0) == 1:
            conn.rollback()
        raise
    else:
        if _TRANSACTION_DEPTH.get(key, 0) == 1:
            conn.commit()
    finally:
        new_depth = _TRANSACTION_DEPTH[key] - 1
        if new_depth == 0:
            _TRANSACTION_DEPTH.pop(key, None)
        else:
            _TRANSACTION_DEPTH[key] = new_depth
