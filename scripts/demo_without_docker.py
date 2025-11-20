#!/usr/bin/env python3
"""
Demo script without Docker
Demonstrates the data mart generation workflow without actual database connections
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("=" * 80)
print("KPI要件からのデータマート自動生成システム - デモンストレーション")
print("=" * 80)
print()

# Sample KPI Requirement
kpi_requirement = """
月次の顧客セグメント別・商品カテゴリ別の売上金額と数量を分析したい。
前年同月比も算出すること。
地域別の売上推移も確認できるようにしたい。
"""

print("【KPI要件】")
print(kpi_requirement)
print()

# Step 1: Metadata Loading Simulation
print("=" * 80)
print("Step 1: メタデータ読込")
print("=" * 80)

from metadata_loader import MetadataLoader

config = {
    'databases': {},
    'vectorizer': {'model': 'paraphrase-multilingual-MiniLM-L12-v2', 'dimension': 384}
}

loader = MetadataLoader(config)
try:
    metadata = loader.load_from_excel("../data/input/metadata.xlsx")
    print(f"✅ メタデータ読込成功")
    print(f"   - テーブル数: {len(metadata['tables'])}")
    print(f"   - カラム総数: {len(metadata['columns'])}")
    print()
    print("【テーブル一覧】")
    for table in metadata['tables']:
        print(f"   - {table['table_name']}: {table.get('table_comment', '')}")
    print()
except Exception as e:
    print(f"❌ エラー: {e}")
    print()

# Step 2: Feature Extraction Simulation
print("=" * 80)
print("Step 2: KPI要件分析（特徴量抽出）")
print("=" * 80)

features = []
if any(word in kpi_requirement for word in ['月次', '月別']):
    features.append('時間')
if any(word in kpi_requirement for word in ['顧客', 'セグメント']):
    features.append('顧客')
if any(word in kpi_requirement for word in ['商品', 'カテゴリ']):
    features.append('商品')
if any(word in kpi_requirement for word in ['売上', '金額']):
    features.append('売上金額')
if any(word in kpi_requirement for word in ['数量']):
    features.append('数量')
if any(word in kpi_requirement for word in ['地域']):
    features.append('地域')

print(f"✅ 抽出された特徴量: {features}")
print()

# Step 3: Related Tables (Simulated)
print("=" * 80)
print("Step 3: 関連テーブル検索（ベクトル類似度）")
print("=" * 80)

# Simulate vector search results
related_tables = [
    {
        'table_name': 'orders',
        'table_comment': '受注トランザクション',
        'similarity': 0.92,
        'columns': [
            {'column_name': 'order_date', 'data_type': 'DATE'},
            {'column_name': 'customer_id', 'data_type': 'BIGINT'},
            {'column_name': 'total_amount', 'data_type': 'NUMERIC'}
        ]
    },
    {
        'table_name': 'order_details',
        'table_comment': '受注明細',
        'similarity': 0.88,
        'columns': [
            {'column_name': 'order_id', 'data_type': 'BIGINT'},
            {'column_name': 'product_id', 'data_type': 'BIGINT'},
            {'column_name': 'quantity', 'data_type': 'INTEGER'},
            {'column_name': 'amount', 'data_type': 'NUMERIC'}
        ]
    },
    {
        'table_name': 'customers',
        'table_comment': '顧客マスタ',
        'similarity': 0.85,
        'columns': [
            {'column_name': 'customer_id', 'data_type': 'BIGINT'},
            {'column_name': 'customer_name', 'data_type': 'VARCHAR'},
            {'column_name': 'segment', 'data_type': 'VARCHAR'},
            {'column_name': 'region', 'data_type': 'VARCHAR'}
        ]
    },
    {
        'table_name': 'products',
        'table_comment': '商品マスタ',
        'similarity': 0.83,
        'columns': [
            {'column_name': 'product_id', 'data_type': 'BIGINT'},
            {'column_name': 'product_name', 'data_type': 'VARCHAR'},
            {'column_name': 'category', 'data_type': 'VARCHAR'}
        ]
    }
]

print(f"✅ 関連テーブル検索完了")
for table in related_tables:
    print(f"   - {table['table_name']} (類似度: {table['similarity']:.2f})")
print()

# Step 4: DDL Generation (Simulated)
print("=" * 80)
print("Step 4: データマートDDL生成")
print("=" * 80)

sample_ddl = """-- ============================================
-- データマート: 月次売上分析
-- 目的: 顧客セグメント別・商品カテゴリ別・地域別売上KPI
-- 作成日: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
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
"""

print("✅ DDL生成完了（サンプル）")
print()
print("【生成されたDDL（抜粋）】")
print(sample_ddl[:800] + "...")
print()

# Save DDL
output_dir = Path("../data/output")
ddl_path = output_dir / "ddl" / f"datamart_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
ddl_path.parent.mkdir(parents=True, exist_ok=True)
ddl_path.write_text(sample_ddl, encoding='utf-8')
print(f"💾 DDL保存: {ddl_path}")
print()

# Step 5: DML Generation (Simulated)
print("=" * 80)
print("Step 5: ETL DML生成")
print("=" * 80)

sample_dml = """-- ============================================
-- ETLスクリプト: 月次売上分析
-- ソース: Central Warehouse
-- ターゲット: Data Mart
-- 作成日: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
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
"""

print("✅ DML生成完了（サンプル）")
print()
print("【生成されたDML（抜粋）】")
print(sample_dml[:800] + "...")
print()

# Save DML
dml_path = output_dir / "dml" / f"etl_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
dml_path.parent.mkdir(parents=True, exist_ok=True)
dml_path.write_text(sample_dml, encoding='utf-8')
print(f"💾 DML保存: {dml_path}")
print()

# Summary
print("=" * 80)
print("デモンストレーション完了")
print("=" * 80)
print()
print("【生成結果】")
print(f"✅ DDL: {ddl_path}")
print(f"✅ DML: {dml_path}")
print()
print("【スキーマ構成】")
print("   ディメンジョンテーブル:")
print("   - dm_dim_date (日付)")
print("   - dm_dim_customer (顧客)")
print("   - dm_dim_product (商品)")
print()
print("   ファクトテーブル:")
print("   - dm_fact_sales (売上)")
print()
print("【分析可能なKPI】")
print("   ✓ 月次売上分析")
print("   ✓ 顧客セグメント別売上")
print("   ✓ 商品カテゴリ別売上")
print("   ✓ 地域別売上")
print("   ✓ 前年同月比（年月ディメンジョンで可能）")
print()
print("【次のステップ】")
print("1. Docker環境がある場合:")
print("   cd docker && docker-compose up -d")
print("   docker exec ollama_llm ollama pull qwen2.5-coder:7b-instruct")
print("   cd ../src && python3 orchestrator.py")
print()
print("2. 生成されたSQL確認:")
print(f"   cat {ddl_path}")
print(f"   cat {dml_path}")
print()
print("3. PostgreSQLで実行:")
print("   psql -h localhost -p 5433 -U dm_user -d data_mart -f [DDL_PATH]")
print("   psql -h localhost -p 5433 -U dm_user -d data_mart -f [DML_PATH]")
print()
