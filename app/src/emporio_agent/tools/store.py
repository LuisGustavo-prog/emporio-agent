"""Tool horario_atual_loja.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F5
"""

from emporio_agent.services.store import current_store_status
from emporio_agent.tools.base import Tool

TOOL = Tool("horario_atual_loja", "Informa horario, proxima abertura, endereco e contatos oficiais da loja.", {
    "type": "object", "properties": {}, "additionalProperties": False,
}, lambda settings, args: current_store_status())
