from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence


def fetch_one(connection: sqlite3.Connection, query: str, parameters: Sequence[object] = ()) -> sqlite3.Row | None:
    return connection.execute(query, parameters).fetchone()


def fetch_all(connection: sqlite3.Connection, query: str, parameters: Sequence[object] = ()) -> list[sqlite3.Row]:
    return connection.execute(query, parameters).fetchall()


def execute_write(connection: sqlite3.Connection, query: str, parameters: Sequence[object] = ()) -> int:
    cursor = connection.execute(query, parameters)
    connection.commit()
    return cursor.lastrowid
