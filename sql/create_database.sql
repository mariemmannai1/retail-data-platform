
-- Create a reusable database table for daily sales
CREATE OR REPLACE TABLE daily_sales AS
SELECT
    CAST(order_datetime AS DATE) AS order_date,
    order_channel,
    COUNT(*) AS number_of_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM read_csv_auto('data/raw/orders.csv')
WHERE order_status = 'Completed'
GROUP BY
    CAST(order_datetime AS DATE),
    order_channel;
