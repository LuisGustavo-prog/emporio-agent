"""Validar a consistencia dos dados na carga (total do pedido x itens, chaves estrangeiras, status validos) e gerar relatorio, sem corrigir em silencio.

Pode importar de: core
Nao deve importar de: services, tools, agent, cli
Fase de implementacao: F1
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    record_id: str | None = None


def validate_records(tables: Mapping[str, list[dict[str, str]]]) -> list[ValidationIssue]:
    """Valida relacionamentos e anomalias sem alterar os registros."""
    indexed = {
        name: {row[key]: row for row in tables.get(name, [])}
        for name, key in (("categories", "category_id"), ("products", "product_id"),
                          ("customers", "customer_id"), ("orders", "order_id"))
    }
    categories, products, customers, orders = (indexed[k] for k in ("categories", "products", "customers", "orders"))
    issues: list[ValidationIssue] = []
    for row in tables.get("products", []):
        if row["category_id"] not in categories:
            issues.append(ValidationIssue("error", "missing_category", "Produto referencia categoria inexistente.", row["product_id"]))
        if row["status"] not in {"active", "discontinued", "coming_soon"}:
            issues.append(ValidationIssue("error", "invalid_product_status", "Status de produto desconhecido.", row["product_id"]))
        if row["status"] in {"discontinued", "coming_soon"} and int(row["stock_quantity"]) > 0:
            issues.append(ValidationIssue("warning", "stock_for_unavailable_product", "Status prevalece sobre quantidade positiva em estoque.", row["product_id"]))
    for row in tables.get("orders", []):
        if row["customer_id"] not in customers:
            issues.append(ValidationIssue("error", "missing_customer", "Pedido referencia cliente inexistente.", row["order_id"]))
        if row["status"] not in {"pending", "confirmed", "shipped", "delivered", "cancelled"}:
            issues.append(ValidationIssue("error", "invalid_order_status", "Status de pedido desconhecido.", row["order_id"]))
    for row in tables.get("promotions", []):
        if row["product_id"] not in products:
            issues.append(ValidationIssue("error", "missing_promotion_product", "Promocao referencia produto inexistente.", row["promotion_id"]))
        try:
            discount = Decimal(row["discount_percent"])
            if not Decimal(0) <= discount <= Decimal(100):
                raise ValueError
        except (ValueError, ArithmeticError):
            issues.append(ValidationIssue("error", "invalid_promotion_discount", "Desconto deve estar entre 0 e 100.", row["promotion_id"]))
    for item in tables.get("order_items", []):
        if item["order_id"] not in orders or item["product_id"] not in products:
            issues.append(ValidationIssue("error", "invalid_order_item_reference", "Item referencia pedido ou produto inexistente.", item["order_id"]))
    email_owners: dict[str, list[str]] = {}
    for row in tables.get("customers", []):
        email_owners.setdefault(row["email"].strip().casefold(), []).append(row["customer_id"])
    for email, ids in email_owners.items():
        if email and len(ids) > 1:
            issues.append(ValidationIssue("warning", "duplicate_customer_email", f"E-mail compartilhado por clientes {', '.join(ids)}."))
    used_categories = {row["category_id"] for row in tables.get("products", [])}
    for category in tables.get("categories", []):
        if category["category_id"] not in used_categories:
            issues.append(ValidationIssue("warning", "empty_category", "Categoria sem produtos.", category["category_id"]))
    item_totals: dict[str, Decimal] = {}
    for item in tables.get("order_items", []):
        product = products.get(item["product_id"])
        if product:
            order_id = item["order_id"]
            item_totals[order_id] = item_totals.get(order_id, Decimal(0)) + Decimal(product["price_brl"]) * int(item["quantity"])
    for order_id, calculated in item_totals.items():
        if order_id in orders and calculated != Decimal(orders[order_id]["total_brl"]):
            issues.append(ValidationIssue("warning", "order_total_mismatch", "Total diverge da soma dos itens; o total registrado sera preservado.", order_id))
    return issues


def format_report(issues: Iterable[ValidationIssue]) -> str:
    issues = list(issues)
    errors = sum(issue.severity == "error" for issue in issues)
    warnings = sum(issue.severity == "warning" for issue in issues)
    lines = [f"Validacao: {errors} erro(s), {warnings} aviso(s)."]
    lines.extend(f"[{item.severity.upper()}] {item.code}: {item.message}" + (f" (registro {item.record_id})" if item.record_id else "") for item in issues)
    return "\n".join(lines)
