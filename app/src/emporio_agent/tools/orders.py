"""Tool consultar_pedido.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F4
"""

from emporio_agent.services.orders import consult_order
from emporio_agent.tools.base import Tool, required_int, required_text


def _consult(settings, args):
    contact = required_text(args, "email_ou_telefone", 200)
    email = contact if "@" in contact else None
    phone = None if email else contact
    return consult_order(settings, required_int(args, "order_id"), email, phone)


TOOL = Tool("consultar_pedido", "Consulta pedido apos validar o e-mail e/ou telefone do titular.", {
    "type": "object", "properties": {
        "order_id": {"type": "integer", "minimum": 1}, "email_ou_telefone": {"type": "string"},
    }, "required": ["order_id", "email_ou_telefone"], "additionalProperties": False,
}, _consult)
