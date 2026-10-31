"""Casos de uso de catalogo: buscar produtos e obter produto, aplicando regras de preco e disponibilidade.

Pode importar de: core, db
Nao deve importar de: tools, agent, cli
Fase de implementacao: F3
"""

from decimal import Decimal

from emporio_agent.config import Settings
from emporio_agent.core.rules.payments import allowed_installments
from emporio_agent.core.rules.pricing import calculate_price
from emporio_agent.core.rules.stock import check_stock
from emporio_agent.db.connection import open_connection
from emporio_agent.db.products import get_active_promotion, get_product, get_product_by_name, list_categories, search_products


def _product_result(conn, product):
    promotion = get_active_promotion(conn, product.product_id)
    final_price = calculate_price(product, promotion)
    return {
        "product_id": product.product_id,
        "name": product.name,
        "description": product.description,
        "price_list_brl": str(product.price_brl),
        "promotion_discount_percent": str(promotion.discount_percent) if promotion else None,
        "promotion_description": promotion.description if promotion else None,
        "price_final_brl": str(final_price),
        "price_pix_brl": str(calculate_price(product, promotion, "pix")),
        "pix_discount_applied": not bool(promotion),
        "availability": check_stock(product).value,
        "stock_quantity": product.stock_quantity,
    }


def search_catalog(settings: Settings, query: str = "", category: str | None = None,
                   brand: str | None = None, min_price: Decimal | None = None,
                   max_price: Decimal | None = None, only_available: bool = True,
                   limit: int = 12) -> list[dict]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ValueError("preco_min nao pode ser maior que preco_max.")
    with open_connection(settings) as conn:
        products = search_products(conn, query, category, brand, only_available, min(limit * 5, 50) if min_price is not None or max_price is not None else limit)
        results = []
        for product in products:
            result = _product_result(conn, product)
            final_price = Decimal(result["price_final_brl"])
            if min_price is not None and final_price < min_price:
                continue
            if max_price is not None and final_price > max_price:
                continue
            results.append(result)
            if len(results) == limit:
                break
        return results


def get_catalog_product(settings: Settings, product_id: int | str) -> dict | None:
    with open_connection(settings) as conn:
        if isinstance(product_id, str):
            product = get_product_by_name(conn, product_id)
        else:
            product = get_product(conn, product_id)
        if product is None:
            return None
        result = _product_result(conn, product)
        result.update({"category_id": product.category_id, "specs": dict(product.specs), "created_at": product.created_at.isoformat(),
                       "available_installments": list(allowed_installments(Decimal(result["price_final_brl"]))),
                       "product_status": product.status.value})
        if result["availability"] != "available":
            category = next((item for item in list_categories(conn) if item.category_id == product.category_id), None)
            alternatives = search_products(conn, category=category.name if category else None,
                                           only_available=True, limit=4) if category else []
            result["alternatives"] = [_product_result(conn, item) for item in alternatives
                                       if item.product_id != product.product_id][:3]
        return result
