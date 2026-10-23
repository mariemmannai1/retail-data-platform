
SELECT
    p.category,
    SUM(oi.quantity) AS units_sold,
    COUNT(DISTINCT o.order_id) AS number_of_orders,
    ROUND(SUM(oi.line_net_amount), 2) AS net_sales
FROM read_csv_auto('data/raw/orders.csv') AS o
JOIN read_csv_auto('data/raw/order_items.csv') AS oi
    ON o.order_id = oi.order_id
JOIN read_csv_auto('data/raw/products.csv') AS p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY net_sales DESC;
