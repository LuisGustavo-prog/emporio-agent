"""Regras de disponibilidade por status e estoque (ativo, esgotado, descontinuado, em breve).

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F2
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from emporio_agent.core.enums import ProductStatus, StockAvailability
from emporio_agent.core.models import Product


def check_stock(product: Product, quantity: int = 1) -> StockAvailability:
    """Determina a disponibilidade; status tem precedencia sobre a quantidade."""
    if quantity < 1:
        raise ValueError("A quantidade solicitada deve ser maior que zero.")

    if product.status is ProductStatus.DISCONTINUED:
        return StockAvailability.DISCONTINUED
    if product.status is ProductStatus.COMING_SOON:
        return StockAvailability.COMING_SOON
    if product.stock_quantity < quantity:
        return StockAvailability.OUT_OF_STOCK
    return StockAvailability.AVAILABLE
