import sqlite3

from emporio_agent.db.products import search_products


def test_category_filter_matches_singular_query_and_excludes_unavailable():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE categories (category_id INTEGER PRIMARY KEY, name TEXT, description TEXT);
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY, price_brl TEXT, name TEXT, category_id INTEGER,
            description TEXT, stock_quantity INTEGER, status TEXT, specs TEXT, created_at TEXT
        );
        INSERT INTO categories VALUES (5, 'Violões', '');
        INSERT INTO products VALUES
            (1, '599.90', 'Yamaha C40', 5, 'Violão clássico', 12, 'active', '{}', '2021-03-15'),
            (2, '799.90', 'Giannini GF-3D', 5, 'Violão clássico', 0, 'active', '{}', '2021-03-15');
        """
    )

    results = search_products(connection, category="Violão", only_available=True)

    assert [product.product_id for product in results] == [1]
    connection.close()
