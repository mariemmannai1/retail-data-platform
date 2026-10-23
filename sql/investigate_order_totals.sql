SELECT
    order_status,
    COUNT(*) AS total_orders,
    SUM(
        CASE
            WHEN subtotal IS NULL
              OR discount_total IS NULL
              OR vat_total IS NULL
              OR delivery_fee IS NULL
              OR total_amount IS NULL
              OR ABS(
                  subtotal - discount_total
                  + vat_total + delivery_fee
                  - total_amount
              ) > 0.02
            THEN 1
            ELSE 0
        END
    ) AS inconsistent_orders
FROM read_csv_auto('data/raw/orders.csv')
GROUP BY order_status
ORDER BY order_status;