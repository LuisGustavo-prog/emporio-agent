"""Modelos imutaveis usados pelas regras e camadas de dados do negocio.

Responsabilidade: representar produtos, promocoes, clientes, pedidos e itens.
Pode importar de: biblioteca padrao, core.enums.
Nao deve importar de: db, rag, services, tools, agent, cli.
Fase de implementacao: F1.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Mapping

from emporio_agent.core.enums import OrderStatus, ProductStatus


@dataclass(frozen=True, slots=True)
class Category:
    category_id: int
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class Product:
    product_id: int
    price_brl: Decimal
    name: str
    category_id: int
    description: str
    stock_quantity: int
    status: ProductStatus
    specs: Mapping[str, str]
    created_at: date


@dataclass(frozen=True, slots=True)
class Promotion:
    promotion_id: int
    product_id: int
    discount_percent: Decimal
    description: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class Customer:
    customer_id: int
    name: str
    phone: str
    email: str
    city: str


@dataclass(frozen=True, slots=True)
class Order:
    order_id: int
    customer_id: int
    order_date: date
    status: OrderStatus
    total_brl: Decimal
    payment_method: str
    tracking_code: str | None
    estimated_delivery: date | None
    notes: str | None


@dataclass(frozen=True, slots=True)
class OrderItem:
    order_id: int
    quantity: int
    product_id: int


@dataclass(frozen=True, slots=True)
class Complaint:
    protocol: str
    order_id: int | None
    customer_name: str | None
    contact: str | None
    description: str
    created_at: str


@dataclass(frozen=True, slots=True)
class PolicyChunk:
    text: str
    page: int
    section: str | None = None
