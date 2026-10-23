
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
