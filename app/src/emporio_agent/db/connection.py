"""Abrir conexoes SQLite e aplicar o schema. Unico ponto que conhece o caminho do banco.

Pode importar de: config
Nao deve importar de: services, tools, agent, cli
Fase de implementacao: F1
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator

from emporio_agent.config import Settings

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(settings: Settings) -> sqlite3.Connection:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return connection


@contextmanager
def open_connection(settings: Settings) -> Iterator[sqlite3.Connection]:
    connection = connect(settings)
    try:
        yield connection
    finally:
        connection.close()
