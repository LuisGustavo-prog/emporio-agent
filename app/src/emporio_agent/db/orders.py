"""Consultas parametrizadas de pedidos, itens e clientes.

Pode importar de: core, db.connection
Nao deve importar de: core.rules, services, tools, agent, cli
Fase de implementacao: F4
"""

import sqlite3
from datetime import date
from decimal import Decimal

from emporio_agent.core.enums import OrderStatus
from emporio_agent.core.models import Customer, Order, OrderItem


def get_order(conn: sqlite3.Connection, order_id: int) -> Order | None:
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if row is None:
        return None
    return Order(row["order_id"], row["customer_id"], date.fromisoformat(row["order_date"]),
                 OrderStatus(row["status"]), Decimal(row["total_brl"]), row["payment_method"],
                 row["tracking_code"], date.fromisoformat(row["estimated_delivery"]) if row["estimated_delivery"] else None,
                 row["notes"])


def get_order_customer(conn: sqlite3.Connection, order_id: int) -> Customer | None:
    row = conn.execute(
        "SELECT c.* FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE o.order_id = ?",
        (order_id,),
    ).fetchone()
    return Customer(row["customer_id"], row["name"], row["phone"], row["email"], row["city"]) if row else None


def get_order_items(conn: sqlite3.Connection, order_id: int) -> list[OrderItem]:
    return [OrderItem(row["order_id"], row["quantity"], row["product_id"])
            for row in conn.execute("SELECT order_id,quantity,product_id FROM order_items WHERE order_id = ?", (order_id,))]


def get_order_item_details(conn: sqlite3.Connection, order_id: int) -> list[dict]:
    return [dict(row) for row in conn.execute(
        "SELECT i.product_id, p.name, i.quantity FROM order_items i JOIN products p ON p.product_id = i.product_id WHERE i.order_id = ? ORDER BY p.name",
        (order_id,),
    )]
