"""Ler os CSVs de data/raw, normalizar campos (e-mail, telefone, specs em JSON) e carregar no SQLite. Executavel com python -m emporio_agent.db.loader.

Pode importar de: config, core, db.connection, db.validators
Nao deve importar de: services, tools, agent, cli
Fase de implementacao: F1
"""

import csv
import json
from pathlib import Path

from emporio_agent.config import RAW_DATA_DIR, SAMPLE_DATA_DIR, Settings
from emporio_agent.db.connection import connect
from emporio_agent.db.validators import format_report, validate_records

CSV_FILES = ("categories", "products", "promotions", "customers", "orders", "order_items")


def read_csv_tables(data_dir: Path | None = None) -> dict[str, list[dict[str, str]]]:
    use_sample_fallback = data_dir is None
    data_dir = data_dir or RAW_DATA_DIR
    tables: dict[str, list[dict[str, str]]] = {}
    for table in CSV_FILES:
        path = data_dir / f"{table}.csv"
        if not path.is_file() and use_sample_fallback and table in {"customers", "orders", "order_items"}:
            path = SAMPLE_DATA_DIR / f"{table}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"CSV obrigatorio nao encontrado: {path}")
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            tables[table] = list(csv.DictReader(handle))
    for row in tables["customers"]:
        row["email"] = row["email"].strip().casefold()
        row["phone"] = "".join(character for character in row["phone"] if character.isdigit())
    for row in tables["products"]:
        specs = json.loads(row.get("specs") or "{}")
        if not isinstance(specs, dict):
            raise ValueError(f"Specs do produto {row['product_id']} devem ser um objeto JSON.")
        row["specs"] = json.dumps(specs, ensure_ascii=False, sort_keys=True)
    return tables


def load_database(settings: Settings, data_dir: Path | None = None) -> str:
    tables = read_csv_tables(data_dir)
    issues = validate_records(tables)
    report = format_report(issues)
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        raise ValueError(report)

    conn = connect(settings)
    try:
        with conn:
            conn.execute("DELETE FROM order_items")
            conn.execute("DELETE FROM orders")
            conn.execute("DELETE FROM promotions")
            conn.execute("DELETE FROM products")
            conn.execute("DELETE FROM categories")
            conn.execute("DELETE FROM customers")
            conn.executemany("INSERT INTO categories VALUES (:category_id,:name,:description)", tables["categories"])
            conn.executemany("INSERT INTO products VALUES (:product_id,:price_brl,:name,:category_id,:description,:stock_quantity,:status,:specs,:created_at)", tables["products"])
            conn.executemany("INSERT INTO promotions VALUES (:promotion_id,:product_id,:discount_percent,:description,:is_active)", tables["promotions"])
            conn.executemany("INSERT INTO customers VALUES (:customer_id,:name,:phone,:email,:city)", tables["customers"])
            conn.executemany("INSERT INTO orders VALUES (:order_id,:customer_id,:order_date,:status,:total_brl,:payment_method,:tracking_code,:estimated_delivery,:notes)", tables["orders"])
            conn.executemany("INSERT INTO order_items VALUES (:order_id,:quantity,:product_id)", tables["order_items"])
    finally:
        conn.close()
    counts = ", ".join(f"{name}={len(rows)}" for name, rows in tables.items())
    return f"{report}\nCarga concluida: {counts}."


def main() -> None:
    print(load_database(Settings.load()))


if __name__ == "__main__":
    main()
