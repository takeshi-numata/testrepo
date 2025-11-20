-- ============================================
-- データマート: 月次売上分析
-- 目的: 顧客セグメント別・商品カテゴリ別・地域別売上KPI
-- 作成日: 2025-11-20 01:49:05
-- ============================================

-- 日付ディメンジョン
CREATE TABLE dm_dim_date (
    date_id INTEGER PRIMARY KEY,
    date_actual DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    CONSTRAINT uk_dim_date_actual UNIQUE (date_actual)
);

COMMENT ON TABLE dm_dim_date IS '日付ディメンジョン';
COMMENT ON COLUMN dm_dim_date.date_id IS '日付ID (YYYYMMDD形式)';
COMMENT ON COLUMN dm_dim_date.year_month IS '年月 (YYYY-MM形式)';

-- 顧客ディメンジョン
CREATE TABLE dm_dim_customer (
    customer_id BIGSERIAL PRIMARY KEY,
    source_customer_id BIGINT NOT NULL,
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    region VARCHAR(50),
    CONSTRAINT uk_dim_customer_source UNIQUE (source_customer_id)
);

COMMENT ON TABLE dm_dim_customer IS '顧客ディメンジョン';
COMMENT ON COLUMN dm_dim_customer.segment IS '顧客セグメント（企業/個人）';
COMMENT ON COLUMN dm_dim_customer.region IS '地域';

-- 商品ディメンジョン
CREATE TABLE dm_dim_product (
    product_id BIGSERIAL PRIMARY KEY,
    source_product_id BIGINT NOT NULL,
    product_name VARCHAR(255),
    category VARCHAR(100),
    CONSTRAINT uk_dim_product_source UNIQUE (source_product_id)
);

COMMENT ON TABLE dm_dim_product IS '商品ディメンジョン';
COMMENT ON COLUMN dm_dim_product.category IS '商品カテゴリ';

-- 売上ファクトテーブル
CREATE TABLE dm_fact_sales (
    fact_id BIGSERIAL PRIMARY KEY,
    dim_date_id INTEGER NOT NULL,
    dim_customer_id BIGINT NOT NULL,
    dim_product_id BIGINT NOT NULL,
    sales_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_dim_date FOREIGN KEY (dim_date_id) 
        REFERENCES dm_dim_date(date_id),
    CONSTRAINT fk_dim_customer FOREIGN KEY (dim_customer_id) 
        REFERENCES dm_dim_customer(customer_id),
    CONSTRAINT fk_dim_product FOREIGN KEY (dim_product_id) 
        REFERENCES dm_dim_product(product_id)
);

COMMENT ON TABLE dm_fact_sales IS '売上ファクトテーブル';
COMMENT ON COLUMN dm_fact_sales.sales_amount IS '売上金額';
COMMENT ON COLUMN dm_fact_sales.quantity IS '数量';

-- インデックス作成
CREATE INDEX idx_fact_sales_date ON dm_fact_sales(dim_date_id);
CREATE INDEX idx_fact_sales_customer ON dm_fact_sales(dim_customer_id);
CREATE INDEX idx_fact_sales_product ON dm_fact_sales(dim_product_id);
CREATE INDEX idx_fact_sales_date_customer ON dm_fact_sales(dim_date_id, dim_customer_id);
CREATE INDEX idx_fact_sales_date_product ON dm_fact_sales(dim_date_id, dim_product_id);
