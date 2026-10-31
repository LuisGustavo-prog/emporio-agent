"""Tool registrar_reclamacao.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F6
"""

from emporio_agent.services.complaints import register_complaint
from emporio_agent.tools.base import Tool, required_int, required_text

TOOL = Tool("registrar_reclamacao", "Registra uma reclamacao e retorna o protocolo.", {
    "type": "object", "properties": {
    "order_id": {"type": "integer", "minimum": 1},
    "nome": {"type": "string"}, "contato": {"type": "string"}, "descricao": {"type": "string"},
    }, "required": ["descricao"], "additionalProperties": False,
}, lambda settings, args: register_complaint(settings,
    required_text(args, "descricao", 3000),
    required_int(args, "order_id") if "order_id" in args else None,
    required_text(args, "nome", 160) if "nome" in args else None,
    required_text(args, "contato", 200) if "contato" in args else None))
