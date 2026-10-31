"""Interface de linha de comando.

Responsabilidade: ler a entrada do usuario, chamar o agente e exibir a resposta.
Nenhuma regra de negocio fica aqui.

Pode importar de: agent, config.
Nao deve importar de: core.rules, db, services, tools.
Fase de implementacao: F0 (hello), F7 (CLI completa)
"""

from __future__ import annotations

import argparse
import logging

from emporio_agent.agent.orchestrator import Agent
from emporio_agent.config import Settings
from emporio_agent.db.connection import open_connection
from emporio_agent.db.loader import load_database
from emporio_agent.log import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente de atendimento da Emporio da Musica")
    parser.add_argument("--load-data", action="store_true", help="valida e carrega os CSVs no SQLite")
    parser.add_argument("--session-id", help="retoma uma sessao existente")
    args = parser.parse_args()
    settings = Settings.load()
    configure_logging(settings.log_level)
    if args.load_data:
        print(load_database(settings))
        return
    with open_connection(settings) as conn:
        has_data = conn.execute("SELECT EXISTS(SELECT 1 FROM products)").fetchone()[0]
    if not has_data:
        print(load_database(settings))
    try:
        agent = Agent(settings, args.session_id)
    except RuntimeError as exc:
        parser.error(str(exc))
    print(f"Sessao: {agent.memory.session_id}")
    print("Tom: Oi! Sou o Tom, da Emporio da Musica. Como posso te chamar? Como posso ajudar? (digite 'sair' para encerrar)")
    try:
        while True:
            user_text = input("Voce: ").strip()
            if user_text.casefold() in {"sair", "exit", "quit"}:
                print("Tom: Ate mais! Se precisar, estou por aqui.")
                break
            try:
                print(f"Tom: {agent.respond(user_text)}")
            except RuntimeError:
                logger.exception("Falha ao processar a mensagem")
                print("Tom: Tive um problema temporario para responder. Tente novamente em instantes.")
    except (EOFError, KeyboardInterrupt):
        print("\nTom: Ate mais!")


if __name__ == "__main__":
    main()
