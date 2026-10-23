-- 1. Orders with missing customers
SELECT
    'Orders with unknown customers' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/orders.csv') o
LEFT JOIN read_csv_auto('data/raw/customers.csv') c
    ON o.customer_id = c.customer_id
WHERE o.customer_id IS NOT NULL
  AND c.customer_id IS NULL

UNION ALL

-- 2. Orders with missing stores
SELECT
    'Orders with unknown stores' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/orders.csv') o
LEFT JOIN read_csv_auto('data/raw/stores.csv') s
    ON o.store_id = s.store_id
WHERE o.store_id IS NOT NULL
  AND s.store_id IS NULL

UNION ALL

-- 3. Products with missing suppliers
SELECT
    'Products with unknown suppliers' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/products.csv') p
LEFT JOIN read_csv_auto('data/raw/suppliers.csv') s
    ON p.supplier_id = s.supplier_id
WHERE p.supplier_id IS NOT NULL
  AND s.supplier_id IS NULL;