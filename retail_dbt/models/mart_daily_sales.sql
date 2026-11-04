SELECT
    CAST(order_date AS DATE) AS order_date,
    order_channel,
    number_of_orders,
    total_revenue,
    average_order_value
FROM main.daily_sales
WHERE total_revenue > 0
