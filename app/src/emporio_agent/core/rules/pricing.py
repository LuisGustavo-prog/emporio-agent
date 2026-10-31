"""Regras de preco: promocao ativa, preco final, desconto de PIX sem acumular com promocao.

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F2
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from decimal import Decimal, ROUND_HALF_UP

from emporio_agent.core.constants import PIX_DISCOUNT_PERCENT
from emporio_agent.core.models import Product, Promotion

CENT = Decimal("0.01")


def calculate_price(
    product: Product,
    promotion: Promotion | None = None,
    payment_method: str | None = None,
) -> Decimal:
    """Calcula o preco final; promocao ativa nao acumula com desconto de PIX."""
    if product.price_brl < 0:
        raise ValueError("O preco do produto nao pode ser negativo.")

    has_promotion = (
        promotion is not None
        and promotion.is_active
        and promotion.product_id == product.product_id
    )

    if has_promotion:
        assert promotion is not None
        if not Decimal("0") <= promotion.discount_percent <= Decimal("100"):
            raise ValueError("O percentual da promocao deve estar entre 0 e 100.")
        discount = promotion.discount_percent / Decimal("100")
        price = product.price_brl * (Decimal("1") - discount)
    elif payment_method is not None and payment_method.strip().lower() == "pix":
        discount = Decimal(PIX_DISCOUNT_PERCENT) / Decimal("100")
        price = product.price_brl * (Decimal("1") - discount)
    else:
        price = product.price_brl

    return price.quantize(CENT, rounding=ROUND_HALF_UP)
