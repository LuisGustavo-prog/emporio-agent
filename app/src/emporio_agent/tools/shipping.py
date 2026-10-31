"""Tool para calcular frete local ou informar modalidades para outras cidades."""

from decimal import Decimal, InvalidOperation

from emporio_agent.services.shipping import quote_shipping
from emporio_agent.tools.base import Tool, required_text


def _quote(settings, args):
    try:
        total = Decimal(str(args["total_brl"]))
    except (KeyError, InvalidOperation) as exc:
        raise ValueError("'total_brl' deve ser numerico.") from exc
    if not total.is_finite() or total < 0:
        raise ValueError("'total_brl' deve ser um valor valido e nao negativo.")
    ids = args.get("product_ids", [])
    if not isinstance(ids, list) or any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in ids):
        raise ValueError("'product_ids' deve ser uma lista de ids inteiros positivos.")
    return quote_shipping(settings, total, required_text(args, "cidade", 100), ids)


TOOL = Tool("simular_frete", "Informa frete e prazo para Campo Grande ou modalidades para outras cidades.", {
    "type": "object", "properties": {
        "total_brl": {"type": "number", "minimum": 0},
        "cidade": {"type": "string"},
        "product_ids": {"type": "array", "items": {"type": "integer", "minimum": 1}},
    }, "required": ["total_brl", "cidade"], "additionalProperties": False,
}, _quote)
