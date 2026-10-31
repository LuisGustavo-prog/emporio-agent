"""Consultas parametrizadas de produtos, categorias e promocoes. Retorna objetos de core.models, sem regra de negocio.

Pode importar de: core, db.connection
Nao deve importar de: core.rules, services, tools, agent, cli
Fase de implementacao: F3
"""

import json
import re
import sqlite3
from difflib import get_close_matches
from datetime import date
from decimal import Decimal
import unicodedata

from emporio_agent.core.enums import ProductStatus
from emporio_agent.core.models import Category, Product, Promotion


def _normalize_category(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    unaccented = "".join(char for char in decomposed if not unicodedata.combining(char))
    tokens = re.findall(r"[a-z0-9]+", unaccented)
    normalized = []
    for token in tokens:
        if token.endswith("oes") and len(token) > 3:
            token = token[:-3] + "ao"
        elif token.endswith("aes") and len(token) > 3:
            token = token[:-3] + "ao"
        elif token.endswith("s") and len(token) > 3:
            token = token[:-1]
        normalized.append(token)
    return " ".join(normalized)


def _product(row: sqlite3.Row) -> Product:
    return Product(int(row["product_id"]), Decimal(row["price_brl"]), row["name"],
                   int(row["category_id"]), row["description"], int(row["stock_quantity"]),
                   ProductStatus(row["status"]), json.loads(row["specs"]), date.fromisoformat(row["created_at"]))


def get_product(conn: sqlite3.Connection, product_id: int) -> Product | None:
    row = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    return _product(row) if row else None


def search_products(conn: sqlite3.Connection, query: str = "", category: str | None = None,
                    brand: str | None = None, only_available: bool = False,
                    limit: int = 10) -> list[Product]:
    query = query.strip()
    if not 1 <= limit <= 50:
        raise ValueError("O limite de resultados deve estar entre 1 e 50.")
    query_like = f"%{query.casefold()}%" if query else "%"
    brand_like = f"{brand.casefold()}%" if brand else "%"
    available_clause = " AND p.status = 'active' AND p.stock_quantity > 0" if only_available else ""
    category_clause = ""
    params: list[object] = [query_like, query_like]
    if category:
        category_key = _normalize_category(category)
        category_rows = conn.execute("SELECT category_id,name FROM categories").fetchall()
        matches = [row for row in category_rows
                   if category_key in _normalize_category(row["name"])
                   or _normalize_category(row["name"]) in category_key]
        if not matches:
            normalized_names = {_normalize_category(row["name"]): row for row in category_rows}
            close = get_close_matches(category_key, list(normalized_names), n=1, cutoff=0.65)
            matches = [normalized_names[close[0]]] if close else []
        if not matches:
            return []
        category_clause = f" AND p.category_id IN ({','.join('?' for _ in matches)})"
        params.extend(row["category_id"] for row in matches)
    params.append(brand_like)
    params.append(limit)
    rows = conn.execute(
        "SELECT p.* FROM products p JOIN categories c ON c.category_id=p.category_id "
        "WHERE (lower(p.name) LIKE ? OR lower(p.description) LIKE ?) "
        + category_clause + " AND lower(p.name) LIKE ?" + available_clause +
        " ORDER BY p.name LIMIT ?",
        params,
    ).fetchall()
    return [_product(row) for row in rows]


def list_categories(conn: sqlite3.Connection) -> list[Category]:
    return [Category(row["category_id"], row["name"], row["description"])
            for row in conn.execute("SELECT * FROM categories ORDER BY name")]


def get_active_promotion(conn: sqlite3.Connection, product_id: int) -> Promotion | None:
    row = conn.execute(
        "SELECT * FROM promotions WHERE product_id = ? AND is_active = 1 ORDER BY CAST(discount_percent AS REAL) DESC LIMIT 1",
        (product_id,),
    ).fetchone()
    if not row:
        return None
    return Promotion(row["promotion_id"], row["product_id"], Decimal(row["discount_percent"]),
                     row["description"], bool(row["is_active"]))


def get_product_by_name(conn: sqlite3.Connection, name: str) -> Product | None:
    row = conn.execute("SELECT * FROM products WHERE lower(name) = ? ORDER BY product_id LIMIT 1",
                       (name.strip().casefold(),)).fetchone()
    if row is None:
        row = conn.execute("SELECT * FROM products WHERE lower(name) LIKE ? ORDER BY name LIMIT 1",
                           (f"%{name.strip().casefold()}%",)).fetchone()
    if row is None:
        candidates = conn.execute("SELECT name FROM products ORDER BY name").fetchall()
        matches = get_close_matches(name.strip().casefold(),
                                    [item["name"].casefold() for item in candidates], n=1, cutoff=0.55)
        if matches:
            row = conn.execute("SELECT * FROM products WHERE lower(name) = ? LIMIT 1", (matches[0],)).fetchone()
    return _product(row) if row else None
