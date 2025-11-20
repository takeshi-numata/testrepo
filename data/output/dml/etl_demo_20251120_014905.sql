-- ============================================
-- ETLスクリプト: 月次売上分析
-- ソース: Central Warehouse
-- ターゲット: Data Mart
-- 作成日: 2025-11-20 01:49:05
-- ============================================

BEGIN;

-- Step 1: 日付ディメンジョン投入
INSERT INTO dm_dim_date (date_id, date_actual, year, month, quarter, year_month)
SELECT DISTINCT
    TO_CHAR(order_date, 'YYYYMMDD')::INTEGER AS date_id,
    order_date AS date_actual,
    EXTRACT(YEAR FROM order_date)::INTEGER AS year,
    EXTRACT(MONTH FROM order_date)::INTEGER AS month,
    EXTRACT(QUARTER FROM order_date)::INTEGER AS quarter,
    TO_CHAR(order_date, 'YYYY-MM') AS year_month
FROM public.orders
WHERE order_date IS NOT NULL
ON CONFLICT (date_actual) DO NOTHING;

-- Step 2: 顧客ディメンジョン投入
INSERT INTO dm_dim_customer (source_customer_id, customer_name, segment, region)
SELECT DISTINCT
    customer_id AS source_customer_id,
    customer_name,
    segment,
    region
FROM public.customers
WHERE customer_id IS NOT NULL
ON CONFLICT (source_customer_id) DO NOTHING;

-- Step 3: 商品ディメンジョン投入
INSERT INTO dm_dim_product (source_product_id, product_name, category)
SELECT DISTINCT
    product_id AS source_product_id,
    product_name,
    category
FROM public.products
WHERE product_id IS NOT NULL
ON CONFLICT (source_product_id) DO NOTHING;

-- Step 4: 売上ファクトテーブル投入
INSERT INTO dm_fact_sales (
    dim_date_id,
    dim_customer_id,
    dim_product_id,
    sales_amount,
    quantity,
    created_at
)
SELECT
    TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER AS dim_date_id,
    dc.customer_id AS dim_customer_id,
    dp.product_id AS dim_product_id,
    SUM(od.amount) AS sales_amount,
    SUM(od.quantity) AS quantity,
    CURRENT_TIMESTAMP AS created_at
FROM public.orders o
INNER JOIN public.order_details od 
    ON o.order_id = od.order_id
INNER JOIN dm_dim_customer dc 
    ON o.customer_id = dc.source_customer_id
INNER JOIN dm_dim_product dp 
    ON od.product_id = dp.source_product_id
WHERE o.order_date IS NOT NULL
  AND o.status = '完了'
GROUP BY TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER, dc.customer_id, dp.product_id;

-- 統計情報更新
ANALYZE dm_dim_date;
ANALYZE dm_dim_customer;
ANALYZE dm_dim_product;
ANALYZE dm_fact_sales;

COMMIT;
