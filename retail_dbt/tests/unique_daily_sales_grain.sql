SELECT
    order_date,
    order_channel,
    COUNT(*) AS row_count
FROM {{ ref('mart_daily_sales') }}
GROUP BY order_date, order_channel
HAVING COUNT(*) > 1