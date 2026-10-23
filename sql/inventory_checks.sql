-- 1. Negative stock quantities
SELECT
    'Negative stock quantities' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/inventory.csv')
WHERE stock_on_hand < 0
   OR stock_on_order < 0

UNION ALL

-- 2. Inventory with unknown products
SELECT
    'Inventory with unknown products' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/inventory.csv') i
LEFT JOIN read_csv_auto('data/raw/products.csv') p
    ON i.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

-- 3. Inventory with unknown stores
SELECT
    'Inventory with unknown stores' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/inventory.csv') i
LEFT JOIN read_csv_auto('data/raw/stores.csv') s
    ON i.store_id = s.store_id
WHERE s.store_id IS NULL;