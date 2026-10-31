"""Gerenciar o historico da sessao: janela das ultimas N mensagens e persistencia via db.conversations.

Pode importar de: db.conversations, config
Nao deve importar de: services, tools, cli
Fase de implementacao: F7
"""

from emporio_agent.config import Settings
from emporio_agent.db.connection import open_connection
from emporio_agent.db.conversations import add_message, create_session, get_messages


class ConversationMemory:
    def __init__(self, settings: Settings, session_id: str | None = None):
        self.settings = settings
        with open_connection(settings) as conn:
            self.session_id = create_session(conn, session_id)

    def history(self) -> list[dict]:
        with open_connection(self.settings) as conn:
            return get_messages(conn, self.session_id, self.settings.history_window)

    def append(self, message: dict) -> None:
        role = message.get("role")
        if role not in {"user", "assistant", "tool"}:
            raise ValueError("Papel de mensagem invalido.")
        with open_connection(self.settings) as conn:
            add_message(conn, self.session_id, role, message)
