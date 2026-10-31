"""Tool consultar_politica.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F5
"""

from emporio_agent.services.policies import search_policy
from emporio_agent.tools.base import Tool, required_text

TOOL = Tool("consultar_politica", "Consulta o manual da loja e retorna trechos relevantes com pagina.", {
    "type": "object", "properties": {"pergunta": {"type": "string"}, "topico": {"type": "string"}},
    "required": ["pergunta"], "additionalProperties": False,
}, lambda settings, args: search_policy(required_text(args, "pergunta"),
    required_text(args, "topico", 100) if "topico" in args else None))
