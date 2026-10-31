"""Enumeracoes do negocio.

Responsabilidade: vocabulario fechado usado em todas as camadas.

Pode importar de: biblioteca padrao.
Nao deve importar de: nenhum outro modulo do projeto.
Fase de implementacao: F0 (pronto)
"""

from enum import Enum


class ProductStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    COMING_SOON = "coming_soon"


class StockAvailability(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    COMING_SOON = "coming_soon"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ReturnType(str, Enum):
    ARREPENDIMENTO = "arrependimento"
    DEFEITO = "defeito"
    PREFERENCIA = "preferencia"


class PaymentMethod(str, Enum):
    PIX = "pix"
    DEBIT = "debit"
    BOLETO = "boleto"
    CREDIT = "credit"
