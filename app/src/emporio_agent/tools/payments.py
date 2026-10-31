"""Tool simular_pagamento.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F3
"""

from decimal import Decimal, InvalidOperation

from emporio_agent.services.payments import payment_options, quote_payment
from emporio_agent.tools.base import Tool, required_int


def _quote(settings, args):
    try:
        amount = Decimal(str(args["total_brl"]))
    except (KeyError, InvalidOperation) as exc:
        raise ValueError("'total_brl' deve ser um valor numerico.") from exc
    promotion_active = args.get("promocao_ativa", False)
    if not isinstance(promotion_active, bool):
        raise ValueError("'promocao_ativa' deve ser booleano.")
    method = args.get("forma")
    if method is None:
        return payment_options(amount, promotion_active)
    if not isinstance(method, str):
        raise ValueError("'forma' deve ser texto.")
    return quote_payment(amount, method, required_int(args, "parcelas", 1, 12) if "parcelas" in args else 1,
                         promotion_active)


TOOL = Tool("simular_pagamento", "Informa opcoes de PIX, debito, boleto, parcelamento e pagamento combinado.", {
    "type": "object", "properties": {
        "total_brl": {"type": "number", "exclusiveMinimum": 0},
        "forma": {"type": "string", "enum": ["pix", "debit", "boleto", "credit"]},
        "parcelas": {"type": "integer", "minimum": 1, "maximum": 12},
        "promocao_ativa": {"type": "boolean"},
    }, "required": ["total_brl"], "additionalProperties": False,
}, _quote)
