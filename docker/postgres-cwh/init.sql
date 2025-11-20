-- ============================================
-- Central Warehouse Sample Data
-- ============================================

-- Customer Master
CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    segment VARCHAR(50),
    region VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE customers IS '顧客マスタ';
COMMENT ON COLUMN customers.customer_id IS '顧客ID（内部キー）';
COMMENT ON COLUMN customers.customer_code IS '顧客コード（業務キー）';
COMMENT ON COLUMN customers.customer_name IS '顧客名';
COMMENT ON COLUMN customers.segment IS '顧客セグメント（企業/個人等）';
COMMENT ON COLUMN customers.region IS '地域';

-- Product Master
CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    product_code VARCHAR(20) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit_price NUMERIC(18,2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE products IS '商品マスタ';
COMMENT ON COLUMN products.product_id IS '商品ID';
COMMENT ON COLUMN products.product_code IS '商品コード';
COMMENT ON COLUMN products.product_name IS '商品名';
COMMENT ON COLUMN products.category IS '商品カテゴリ';
COMMENT ON COLUMN products.unit_price IS '単価';

-- Order Transaction
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    order_code VARCHAR(20) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    total_amount NUMERIC(18,2) NOT NULL,
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE orders IS '受注トランザクション';
COMMENT ON COLUMN orders.order_id IS '受注ID';
COMMENT ON COLUMN orders.order_code IS '受注番号';
COMMENT ON COLUMN orders.customer_id IS '顧客ID';
COMMENT ON COLUMN orders.order_date IS '受注日';
COMMENT ON COLUMN orders.total_amount IS '合計金額';
COMMENT ON COLUMN orders.status IS 'ステータス';

-- Order Details
CREATE TABLE order_details (
    detail_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(18,2) NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE order_details IS '受注明細トランザクション';
COMMENT ON COLUMN order_details.detail_id IS '明細ID';
COMMENT ON COLUMN order_details.order_id IS '受注ID';
COMMENT ON COLUMN order_details.product_id IS '商品ID';
COMMENT ON COLUMN order_details.quantity IS '数量';
COMMENT ON COLUMN order_details.unit_price IS '単価';
COMMENT ON COLUMN order_details.amount IS '金額';

-- Sample Data
INSERT INTO customers (customer_code, customer_name, segment, region) VALUES
    ('C001', '株式会社A商事', '企業', '東京'),
    ('C002', '山田太郎', '個人', '大阪'),
    ('C003', '株式会社Bシステム', '企業', '名古屋'),
    ('C004', '佐藤花子', '個人', '東京'),
    ('C005', '株式会社C物産', '企業', '福岡'),
    ('C006', '鈴木一郎', '個人', '札幌'),
    ('C007', '株式会社D商店', '企業', '大阪'),
    ('C008', '田中美咲', '個人', '横浜'),
    ('C009', '株式会社Eトレード', '企業', '名古屋'),
    ('C010', '高橋健太', '個人', '仙台');

INSERT INTO products (product_code, product_name, category, unit_price) VALUES
    ('P001', 'ノートPC', '電子機器', 150000.00),
    ('P002', 'マウス', '周辺機器', 2000.00),
    ('P003', 'キーボード', '周辺機器', 5000.00),
    ('P004', 'モニター', '電子機器', 35000.00),
    ('P005', 'プリンター', '電子機器', 25000.00),
    ('P006', 'USBケーブル', '周辺機器', 800.00),
    ('P007', 'HDMIケーブル', '周辺機器', 1200.00),
    ('P008', 'Webカメラ', '電子機器', 8000.00),
    ('P009', 'ヘッドセット', '周辺機器', 6000.00),
    ('P010', 'スピーカー', '電子機器', 12000.00);

-- Insert 50 orders across 2023-2024
INSERT INTO orders (order_code, customer_id, order_date, total_amount, status) VALUES
    ('O001', 1, '2023-01-15', 152000.00, '完了'),
    ('O002', 2, '2023-01-20', 7000.00, '完了'),
    ('O003', 3, '2023-02-01', 300000.00, '完了'),
    ('O004', 4, '2023-02-14', 37000.00, '完了'),
    ('O005', 5, '2023-03-05', 180000.00, '完了'),
    ('O006', 6, '2023-03-22', 14000.00, '完了'),
    ('O007', 7, '2023-04-10', 62000.00, '完了'),
    ('O008', 8, '2023-04-25', 156000.00, '完了'),
    ('O009', 9, '2023-05-08', 225000.00, '完了'),
    ('O010', 10, '2023-05-19', 43000.00, '完了'),
    ('O011', 1, '2023-06-02', 95000.00, '完了'),
    ('O012', 2, '2023-06-18', 19000.00, '完了'),
    ('O013', 3, '2023-07-07', 280000.00, '完了'),
    ('O014', 4, '2023-07-23', 52000.00, '完了'),
    ('O015', 5, '2023-08-11', 195000.00, '完了'),
    ('O016', 6, '2023-08-28', 28000.00, '完了'),
    ('O017', 7, '2023-09-14', 73000.00, '完了'),
    ('O018', 8, '2023-09-29', 167000.00, '完了'),
    ('O019', 9, '2023-10-05', 240000.00, '完了'),
    ('O020', 10, '2023-10-22', 38000.00, '完了'),
    ('O021', 1, '2023-11-06', 88000.00, '完了'),
    ('O022', 2, '2023-11-19', 16000.00, '完了'),
    ('O023', 3, '2023-12-03', 315000.00, '完了'),
    ('O024', 4, '2023-12-18', 49000.00, '完了'),
    ('O025', 5, '2023-12-27', 205000.00, '完了'),
    -- 2024 data
    ('O026', 6, '2024-01-10', 31000.00, '完了'),
    ('O027', 7, '2024-01-24', 78000.00, '完了'),
    ('O028', 8, '2024-02-08', 172000.00, '完了'),
    ('O029', 9, '2024-02-21', 255000.00, '完了'),
    ('O030', 10, '2024-03-05', 42000.00, '完了'),
    ('O031', 1, '2024-03-18', 97000.00, '完了'),
    ('O032', 2, '2024-04-02', 21000.00, '完了'),
    ('O033', 3, '2024-04-16', 295000.00, '完了'),
    ('O034', 4, '2024-05-01', 56000.00, '完了'),
    ('O035', 5, '2024-05-15', 210000.00, '完了'),
    ('O036', 6, '2024-06-03', 34000.00, '完了'),
    ('O037', 7, '2024-06-17', 81000.00, '完了'),
    ('O038', 8, '2024-07-01', 178000.00, '完了'),
    ('O039', 9, '2024-07-14', 265000.00, '完了'),
    ('O040', 10, '2024-08-02', 45000.00, '完了'),
    ('O041', 1, '2024-08-19', 102000.00, '完了'),
    ('O042', 2, '2024-09-05', 23000.00, '完了'),
    ('O043', 3, '2024-09-18', 305000.00, '完了'),
    ('O044', 4, '2024-10-02', 59000.00, '完了'),
    ('O045', 5, '2024-10-16', 220000.00, '完了'),
    ('O046', 6, '2024-11-01', 37000.00, '完了'),
    ('O047', 7, '2024-11-14', 84000.00, '完了'),
    ('O048', 8, '2024-12-03', 185000.00, '完了'),
    ('O049', 9, '2024-12-17', 275000.00, '完了'),
    ('O050', 10, '2024-12-28', 48000.00, '完了');

-- Insert order details (100+ records)
INSERT INTO order_details (order_id, product_id, quantity, unit_price, amount) VALUES
    -- Order 1
    (1, 1, 1, 150000.00, 150000.00),
    (1, 2, 1, 2000.00, 2000.00),
    -- Order 2
    (2, 2, 2, 2000.00, 4000.00),
    (2, 3, 1, 3000.00, 3000.00),
    -- Order 3
    (3, 1, 2, 150000.00, 300000.00),
    -- Order 4
    (4, 4, 1, 35000.00, 35000.00),
    (4, 2, 1, 2000.00, 2000.00),
    -- Order 5
    (5, 1, 1, 150000.00, 150000.00),
    (5, 5, 1, 25000.00, 25000.00),
    (5, 3, 1, 5000.00, 5000.00),
    -- Continue pattern for remaining orders (simplified)
    (6, 8, 1, 8000.00, 8000.00),
    (6, 9, 1, 6000.00, 6000.00),
    (7, 4, 1, 35000.00, 35000.00),
    (7, 5, 1, 25000.00, 25000.00),
    (7, 2, 1, 2000.00, 2000.00),
    (8, 1, 1, 150000.00, 150000.00),
    (8, 9, 1, 6000.00, 6000.00),
    (9, 1, 1, 150000.00, 150000.00),
    (9, 4, 2, 35000.00, 70000.00),
    (9, 3, 1, 5000.00, 5000.00),
    (10, 4, 1, 35000.00, 35000.00),
    (10, 8, 1, 8000.00, 8000.00);

-- Add more order details for comprehensive testing
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 11..50 LOOP
        INSERT INTO order_details (order_id, product_id, quantity, unit_price, amount)
        VALUES 
            (i, ((i % 10) + 1), ((i % 3) + 1), 
             (SELECT unit_price FROM products WHERE product_id = ((i % 10) + 1)),
             ((i % 3) + 1) * (SELECT unit_price FROM products WHERE product_id = ((i % 10) + 1)));
    END LOOP;
END $$;

-- Indexes
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_details_order ON order_details(order_id);
CREATE INDEX idx_order_details_product ON order_details(product_id);

-- Analyze tables
ANALYZE customers;
ANALYZE products;
ANALYZE orders;
ANALYZE order_details;
