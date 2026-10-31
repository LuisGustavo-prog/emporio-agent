"""Tools buscar_produtos e obter_produto. Camada fina: valida argumentos, chama services.catalog e devolve JSON.

Pode importar de: services, tools.base
Nao deve importar de: db, core.rules, agent, cli
Fase de implementacao: F3
"""

from decimal import Decimal, InvalidOperation

from emporio_agent.services.catalog import get_catalog_product, search_catalog
from emporio_agent.tools.base import Tool, required_int, required_text


def _search(settings, args):
    query = args.get("termo", "")
    category = args.get("categoria")
    brand = args.get("marca")
    for name, value in (("termo", query), ("categoria", category), ("marca", brand)):
        if value is not None and not isinstance(value, str):
            raise ValueError(f"'{name}' deve ser texto.")
    def price(name):
        value = args.get(name)
        if value is None:
            return None
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"'{name}' deve ser numerico.") from exc
        if not amount.is_finite() or amount < 0:
            raise ValueError(f"'{name}' deve ser um valor positivo valido.")
        return amount
    only_available = args.get("apenas_disponiveis", True)
    if not isinstance(only_available, bool):
        raise ValueError("'apenas_disponiveis' deve ser booleano.")
    limit = required_int(args, "limite", 1, 20) if "limite" in args else 12
    return search_catalog(settings, query, category, brand, price("preco_min"), price("preco_max"), only_available, limit)


def _detail(settings, args):
    value = args.get("nome_ou_id")
    if isinstance(value, int) and not isinstance(value, bool):
        product_key = value
    elif isinstance(value, str) and value.strip():
        product_key = int(value.strip()) if value.strip().isdigit() else required_text(args, "nome_ou_id", 200)
    else:
        raise ValueError("'nome_ou_id' deve conter o nome ou id do produto.")
    return get_catalog_product(settings, product_key)

SEARCH = Tool("buscar_produtos", "Busca e filtra produtos por termo, categoria, marca, preco e disponibilidade.", {
    "type": "object", "properties": {
        "termo": {"type": "string"}, "categoria": {"type": "string"}, "marca": {"type": "string"},
        "preco_min": {"type": "number", "minimum": 0}, "preco_max": {"type": "number", "minimum": 0},
        "apenas_disponiveis": {"type": "boolean"}, "limite": {"type": "integer", "minimum": 1, "maximum": 20},
    }, "additionalProperties": False,
}, _search)

DETAIL = Tool("obter_produto", "Obtem ficha, preco de tabela, promocao, PIX, parcelas e disponibilidade.", {
    "type": "object", "properties": {"nome_ou_id": {"type": "string", "minLength": 1}},
    "required": ["nome_ou_id"], "additionalProperties": False,
}, _detail)

TOOLS = (SEARCH, DETAIL)
