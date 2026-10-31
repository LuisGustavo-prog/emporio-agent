"""Regras de frete: regiao metropolitana de Campo Grande, outras cidades, itens grandes.

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F2
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from dataclasses import dataclass
from decimal import Decimal
import unicodedata

from emporio_agent.core.constants import (
    FREE_SHIPPING_MIN_BRL,
    LOCAL_SHIPPING_FEE_BRL,
    METROPOLITAN_CITIES,
    OUT_OF_TOWN_SHIPPING_OPTIONS,
    OVERSIZED_NAME_TERMS,
)
from emporio_agent.core.models import Category, Product


@dataclass(frozen=True, slots=True)
class ShippingQuote:
    fee_brl: Decimal | None
    free_shipping: bool
    oversized_items: int
    special_quote_required: bool
    delivery_options: dict[str, tuple[int, int]]


def calculate_shipping(
    total_brl: Decimal,
    city: str,
    products: tuple[Product, ...] = (),
    categories: tuple[Category, ...] = (),
) -> ShippingQuote:
    """Calcula o frete com base no valor, localidade e itens grandes."""
    if not total_brl.is_finite() or total_brl < 0:
        raise ValueError("O total nao pode ser negativo.")
    def normalize(value: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c))
    city_normalized = normalize(city.strip())
    local_cities = {normalize(name) for name in METROPOLITAN_CITIES}
    local = city_normalized in local_cities
    category_names = {c.category_id: normalize(c.name) for c in categories}
    oversized_terms = tuple(normalize(term) for term in OVERSIZED_NAME_TERMS)
    oversized = sum(
        1 for product in products
        if any(term in normalize(product.name) for term in oversized_terms)
        or any(term in category_names.get(product.category_id, "") for term in oversized_terms)
    )
    special_quote = oversized > 0
    free = local and total_brl > Decimal(FREE_SHIPPING_MIN_BRL) and not special_quote
    fee = None if not local or special_quote else (Decimal("0") if free else Decimal(LOCAL_SHIPPING_FEE_BRL))
    options = {"Motoboy": (1, 3)} if local else dict(OUT_OF_TOWN_SHIPPING_OPTIONS)
    return ShippingQuote(fee, free, oversized, special_quote, options)
