
WITH
orders AS (
    SELECT * FROM read_csv_auto('data/raw/orders.csv')
),
items AS (
    SELECT * FROM read_csv_auto('data/raw/order_items.csv')
),
products AS (
    SELECT * FROM read_csv_auto('data/raw/products.csv')
)

SELECT
    'Duplicate order IDs' AS check_name,
    COUNT(*) - COUNT(DISTINCT order_id) AS issue_count
FROM orders

UNION ALL

SELECT
    'Duplicate order item IDs',
    COUNT(*) - COUNT(DISTINCT order_item_id)
FROM items

UNION ALL

SELECT
    'Order items without matching order',
    COUNT(*)
FROM items i
LEFT JOIN orders o ON i.order_id = o.order_id
WHERE o.order_id IS NULL

UNION ALL

SELECT
    'Order items without matching product',
    COUNT(*)
FROM items i
LEFT JOIN products p ON i.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'Orders with missing order ID',
    COUNT(*)
FROM orders
WHERE order_id IS NULL

UNION ALL

SELECT
    'Order items with invalid quantity',
    COUNT(*)
FROM items
WHERE quantity IS NULL OR quantity <= 0

ORDER BY check_name;

-- 7. Invalid promotion types
SELECT
    'Invalid promotion type' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/promotions.csv')
WHERE discount_type IS NULL
   OR discount_type NOT IN ('Percentage', 'Fixed')

UNION ALL

-- 8. Invalid percentage discounts
SELECT
    'Invalid percentage discount' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/promotions.csv')
WHERE discount_type = 'Percentage'
  AND (
      discount_value IS NULL
      OR discount_value < 0
      OR discount_value > 100
  )

UNION ALL

-- 9. Invalid promotion date ranges
SELECT
    'Invalid promotion dates' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/promotions.csv')
WHERE TRY_CAST(start_date AS DATE) IS NULL
   OR TRY_CAST(end_date AS DATE) IS NULL
   OR TRY_CAST(start_date AS DATE) > TRY_CAST(end_date AS DATE)

UNION ALL

-- 10. Invalid VAT rates
SELECT
    'Invalid VAT rate' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/products.csv')
WHERE vat_rate IS NULL
   OR vat_rate < 0
   OR vat_rate > 1;


-- 11. Inconsistent totals for non-cancelled orders
SELECT
    'Inconsistent order totals' AS check_name,
    COUNT(*) AS issue_count
FROM read_csv_auto('data/raw/orders.csv')
WHERE order_status <> 'Cancelled'
  AND (
      subtotal IS NULL
      OR discount_total IS NULL
      OR vat_total IS NULL
      OR delivery_fee IS NULL
      OR total_amount IS NULL
      OR ABS(
          subtotal - discount_total
          + vat_total + delivery_fee
          - total_amount
      ) > 0.02
  );