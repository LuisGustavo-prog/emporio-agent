"""Persistir e recuperar sessoes e mensagens do historico.

Pode importar de: core, db.connection
Nao deve importar de: core.rules, services, tools, agent, cli
Fase de implementacao: F7
"""

import json
from datetime import datetime, timezone
from uuid import uuid4


def create_session(conn, session_id: str | None = None) -> str:
    session_id = session_id or uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    with conn:
        conn.execute("INSERT OR IGNORE INTO conversations VALUES(?,?,?)", (session_id, now, now))
    return session_id


def add_message(conn, session_id: str, role: str, content: str | dict) -> None:
    if role not in {"user", "assistant", "tool"}:
        raise ValueError("Papel de mensagem invalido.")
    if isinstance(content, dict):
        content = json.dumps(content, ensure_ascii=False)
    now = datetime.now(timezone.utc).isoformat()
    with conn:
        conn.execute("INSERT INTO conversations VALUES(?,?,?) ON CONFLICT(session_id) DO NOTHING", (session_id, now, now))
        conn.execute("INSERT INTO messages(session_id,role,content,created_at) VALUES(?,?,?,?)", (session_id, role, content, now))
        conn.execute("UPDATE conversations SET updated_at = ? WHERE session_id = ?", (now, session_id))


def get_messages(conn, session_id: str, limit: int = 20) -> list[dict[str, str]]:
    rows = conn.execute(
        "SELECT role,content FROM (SELECT message_id,role,content FROM messages WHERE session_id = ? ORDER BY message_id DESC LIMIT ?) ORDER BY message_id",
        (session_id, limit),
    ).fetchall()
    rows = list(rows)
    first_user = next((index for index, row in enumerate(rows) if row["role"] == "user"), len(rows))
    rows = rows[first_user:]
    result = []
    for row in rows:
        try:
            message = json.loads(row["content"])
            if isinstance(message, dict) and message.get("role") == row["role"]:
                result.append(message)
                continue
        except (TypeError, json.JSONDecodeError):
            pass
        result.append({"role": row["role"], "content": row["content"]})
    return result


def delete_session(conn, session_id: str) -> None:
    with conn:
        conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
