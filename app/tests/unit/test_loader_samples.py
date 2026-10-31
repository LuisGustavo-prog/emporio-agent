import shutil
from pathlib import Path

from emporio_agent.db import loader


def test_loader_falls_back_to_synthetic_private_data(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    for filename in ("categories.csv", "products.csv", "promotions.csv"):
        shutil.copyfile(source_dir / filename, raw_dir / filename)

    monkeypatch.setattr(loader, "RAW_DATA_DIR", raw_dir)
    tables = loader.read_csv_tables()

    assert tables["customers"] == [{
        "customer_id": "1",
        "name": "Cliente Demonstracao",
        "phone": "0000000001",
        "email": "demo@example.invalid",
        "city": "Campo Grande",
    }]
    assert tables["orders"][0]["order_id"] == "900001"
    assert tables["order_items"] == [{
        "order_id": "900001",
        "quantity": "1",
        "product_id": "81",
    }]
