"""Tool avaliar_devolucao.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F4
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from emporio_agent.config import Settings
from emporio_agent.core.constants import STORE_TIMEZONE
from emporio_agent.services.returns import evaluate_order_return
from emporio_agent.tools.base import Tool, required_int, required_text


def _evaluate(settings: Settings, args):
    contact = required_text(args, "email_ou_telefone", 200)
    email, phone = (contact, None) if "@" in contact else (None, contact)
    received_date = None
    if "data_recebimento" in args:
        try:
            received_date = date.fromisoformat(required_text(args, "data_recebimento", 10))
        except ValueError as exc:
            raise ValueError("'data_recebimento' deve estar no formato AAAA-MM-DD.") from exc
    online = args.get("compra_online", True)
    if not isinstance(online, bool):
        raise ValueError("'compra_online' deve ser booleano.")
    return evaluate_order_return(settings, required_int(args, "order_id"),
        required_text(args, "tipo", 40), settings.reference_date or datetime.now(ZoneInfo(STORE_TIMEZONE)).date(),
        email, phone, received_date, online)


TOOL = Tool("avaliar_devolucao", "Avalia prazo de devolucao ou troca por defeito apos verificar o titular.", {
    "type": "object", "properties": {
        "order_id": {"type": "integer", "minimum": 1},
        "tipo": {"type": "string", "enum": ["arrependimento", "defeito", "preferencia"]},
        "email_ou_telefone": {"type": "string"},
        "data_recebimento": {"type": "string", "format": "date"}, "compra_online": {"type": "boolean"},
    }, "required": ["order_id", "tipo", "email_ou_telefone"], "additionalProperties": False,
}, _evaluate)
