"""Caso de uso de cotacao de frete, combinando catalogo e regra pura."""

from decimal import Decimal

from emporio_agent.config import Settings
from emporio_agent.core.errors import NotFoundError
from emporio_agent.core.rules.shipping import calculate_shipping
from emporio_agent.db.connection import open_connection
from emporio_agent.db.products import get_product, list_categories


def quote_shipping(settings: Settings, total_brl: Decimal, city: str,
                   product_ids: list[int] | None = None) -> dict:
    unique_ids = list(dict.fromkeys(product_ids or []))
    with open_connection(settings) as conn:
        products = tuple(get_product(conn, product_id) for product_id in unique_ids)
        if any(product is None for product in products):
            raise NotFoundError("Um ou mais produtos informados nao constam no sistema.")
        categories = tuple(list_categories(conn))
    quote = calculate_shipping(total_brl, city, products, categories)
    return {
        "fee_brl": str(quote.fee_brl) if quote.fee_brl is not None else None,
        "free_shipping": quote.free_shipping,
        "special_quote_required": quote.special_quote_required,
        "oversized_items": quote.oversized_items,
        "delivery_options_business_days": {name: list(days) for name, days in quote.delivery_options.items()},
        "fee_note": (
            "Cotacao individual necessaria para instrumento de grande porte."
            if quote.special_quote_required else
            "Valor calculado no checkout pelo CEP, peso e dimensoes."
            if quote.fee_brl is None else None
        ),
    }
