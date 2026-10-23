SELECT
    MIN(CAST(order_datetime AS TIMESTAMP)) AS first_order,
    MAX(CAST(order_datetime AS TIMESTAMP)) AS last_order
FROM read_csv_auto('data/raw/orders.csv');