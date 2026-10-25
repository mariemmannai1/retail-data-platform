
-- 1. Dimension produits
CREATE OR REPLACE TABLE dim_products AS
SELECT
    product_id,
    product_name,
    category,
    brand,
    supplier_id,
    unit_cost,
    unit_price,
    vat_rate,
    reorder_level,
    active
FROM read_csv_auto('data/raw/products.csv');

-- 2. Dimension magasins
CREATE OR REPLACE TABLE dim_stores AS
SELECT
    store_id,
    store_name,
    city,
    region,
    postcode,
    store_format,
    opening_date,
    staff_count
FROM read_csv_auto('data/raw/stores.csv');

-- 3. Dimension clients
CREATE OR REPLACE TABLE dim_customers AS
SELECT
    customer_id,
    city,
    postcode_area,
    signup_date,
    loyalty_tier,
    customer_segment,
    marketing_opt_in
FROM read_csv_auto('data/raw/customers.csv');

-- 4. Table de faits des ventes
CREATE OR REPLACE TABLE fact_sales AS
SELECT
    i.order_item_id,
    o.order_id,
    CAST(o.order_datetime AS DATE) AS order_date,
    o.order_datetime,
    o.store_id,
    o.customer_id,
    i.product_id,
    i.promotion_id,
    o.order_channel,
    o.payment_method,
    o.order_status,
    i.quantity,
    i.unit_price,
    i.discount_amount,
    i.line_net_amount,
    i.line_vat_amount,
    o.total_amount AS order_total_amount
FROM read_csv_auto('data/raw/order_items.csv') i
JOIN read_csv_auto('data/raw/orders.csv') o
    ON i.order_id = o.order_id;


-- 5. Faits de stock
CREATE OR REPLACE TABLE fact_inventory AS
SELECT
    store_id,
    product_id,
    stock_on_hand,
    stock_on_order,
    last_restock_date,
    aisle_location
FROM read_csv_auto('data/raw/inventory.csv');
-- 6. Dimension date : une ligne par jour, de la première à la dernière date de vente
CREATE OR REPLACE TABLE dim_date AS
WITH bounds AS (
    SELECT MIN(order_date) AS first_date, MAX(order_date) AS last_date
    FROM fact_sales
),
calendar AS (
    SELECT CAST(d AS DATE) AS date_key
    FROM bounds, generate_series(first_date, last_date, INTERVAL 1 DAY) AS t(d)
)
SELECT
    date_key,
    year(date_key) AS year,
    quarter(date_key) AS quarter,
    month(date_key) AS month,
    strftime(date_key, '%Y-%m') AS year_month,
    monthname(date_key) AS month_name,
    day(date_key) AS day_of_month,
    isodow(date_key) AS day_of_week,
    dayname(date_key) AS day_name,
    weekofyear(date_key) AS iso_week,
    isodow(date_key) >= 6 AS is_weekend
FROM calendar;


-- 7. Table de faits des commandes : une ligne par commande
CREATE OR REPLACE TABLE fact_orders AS
SELECT
    o.order_id,
    CAST(o.order_datetime AS DATE) AS order_date,
    o.order_datetime,
    o.store_id,
    o.customer_id,
    o.order_channel,
    o.payment_method,
    o.order_status,
    o.subtotal,
    o.discount_total,
    o.vat_total,
    o.delivery_fee,
    o.total_amount,
    COUNT(i.order_item_id) AS line_count,
    COALESCE(SUM(i.quantity), 0) AS units,
    COALESCE(ROUND(SUM(i.line_net_amount), 2), 0) AS net_sales
FROM read_csv_auto('data/raw/orders.csv') o
LEFT JOIN read_csv_auto('data/raw/order_items.csv') i
    ON o.order_id = i.order_id
GROUP BY ALL;
-- 8. Ventes quotidiennes par canal : commandes Completed, montant TTC au niveau commande
CREATE OR REPLACE TABLE daily_sales AS
SELECT
    order_date,
    order_channel,
    COUNT(*) AS number_of_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(
    SUM(CAST(total_amount AS DECIMAL(18, 2)))
    / NULLIF(COUNT(*), 0),
    2
) AS average_order_value
FROM fact_orders
WHERE order_status = 'Completed'
GROUP BY order_date, order_channel;
