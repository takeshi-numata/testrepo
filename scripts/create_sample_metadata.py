#!/usr/bin/env python3
"""
Create sample metadata Excel file from Central Warehouse schema
"""

import pandas as pd
from pathlib import Path

def create_metadata_excel(output_path: str):
    """Create metadata Excel file with table and column information"""
    
    # Table Metadata
    table_data = [
        {
            'schema_name': 'public',
            'table_name': 'customers',
            'table_comment': '顧客マスタ。企業顧客と個人顧客の基本情報を管理'
        },
        {
            'schema_name': 'public',
            'table_name': 'products',
            'table_comment': '商品マスタ。販売している商品の情報と価格を管理'
        },
        {
            'schema_name': 'public',
            'table_name': 'orders',
            'table_comment': '受注トランザクション。顧客からの注文情報を記録'
        },
        {
            'schema_name': 'public',
            'table_name': 'order_details',
            'table_comment': '受注明細トランザクション。注文の商品明細と金額を記録'
        }
    ]
    
    # Column Metadata
    column_data = [
        # customers table
        {'schema_name': 'public', 'table_name': 'customers', 'column_name': 'customer_id', 
         'data_type': 'BIGINT', 'column_comment': '顧客ID（内部キー）。システム内で顧客を一意に識別する番号'},
        {'schema_name': 'public', 'table_name': 'customers', 'column_name': 'customer_code', 
         'data_type': 'VARCHAR(20)', 'column_comment': '顧客コード（業務キー）。業務で使用する顧客番号'},
        {'schema_name': 'public', 'table_name': 'customers', 'column_name': 'customer_name', 
         'data_type': 'VARCHAR(255)', 'column_comment': '顧客名。企業名または個人名'},
        {'schema_name': 'public', 'table_name': 'customers', 'column_name': 'segment', 
         'data_type': 'VARCHAR(50)', 'column_comment': '顧客セグメント。企業/個人の区分'},
        {'schema_name': 'public', 'table_name': 'customers', 'column_name': 'region', 
         'data_type': 'VARCHAR(50)', 'column_comment': '地域。顧客の所在地域'},
        {'schema_name': 'public', 'table_name': 'customers', 'column_name': 'created_at', 
         'data_type': 'TIMESTAMPTZ', 'column_comment': 'レコード作成日時'},
        
        # products table
        {'schema_name': 'public', 'table_name': 'products', 'column_name': 'product_id', 
         'data_type': 'BIGINT', 'column_comment': '商品ID（内部キー）。システム内で商品を一意に識別する番号'},
        {'schema_name': 'public', 'table_name': 'products', 'column_name': 'product_code', 
         'data_type': 'VARCHAR(20)', 'column_comment': '商品コード（業務キー）。業務で使用する商品番号'},
        {'schema_name': 'public', 'table_name': 'products', 'column_name': 'product_name', 
         'data_type': 'VARCHAR(255)', 'column_comment': '商品名。商品の正式名称'},
        {'schema_name': 'public', 'table_name': 'products', 'column_name': 'category', 
         'data_type': 'VARCHAR(100)', 'column_comment': '商品カテゴリ。電子機器/周辺機器等の分類'},
        {'schema_name': 'public', 'table_name': 'products', 'column_name': 'unit_price', 
         'data_type': 'NUMERIC(18,2)', 'column_comment': '単価。商品の標準販売価格'},
        {'schema_name': 'public', 'table_name': 'products', 'column_name': 'created_at', 
         'data_type': 'TIMESTAMPTZ', 'column_comment': 'レコード作成日時'},
        
        # orders table
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'order_id', 
         'data_type': 'BIGINT', 'column_comment': '受注ID（内部キー）。システム内で受注を一意に識別する番号'},
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'order_code', 
         'data_type': 'VARCHAR(20)', 'column_comment': '受注番号（業務キー）。業務で使用する注文番号'},
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'customer_id', 
         'data_type': 'BIGINT', 'column_comment': '顧客ID。注文した顧客を示す外部キー'},
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'order_date', 
         'data_type': 'DATE', 'column_comment': '受注日。注文を受けた日付'},
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'total_amount', 
         'data_type': 'NUMERIC(18,2)', 'column_comment': '合計金額。注文の総額'},
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'status', 
         'data_type': 'VARCHAR(20)', 'column_comment': 'ステータス。完了/処理中等の状態'},
        {'schema_name': 'public', 'table_name': 'orders', 'column_name': 'created_at', 
         'data_type': 'TIMESTAMPTZ', 'column_comment': 'レコード作成日時'},
        
        # order_details table
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'detail_id', 
         'data_type': 'BIGINT', 'column_comment': '明細ID（内部キー）。システム内で明細を一意に識別する番号'},
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'order_id', 
         'data_type': 'BIGINT', 'column_comment': '受注ID。どの注文の明細かを示す外部キー'},
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'product_id', 
         'data_type': 'BIGINT', 'column_comment': '商品ID。注文された商品を示す外部キー'},
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'quantity', 
         'data_type': 'INTEGER', 'column_comment': '数量。注文された商品の個数'},
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'unit_price', 
         'data_type': 'NUMERIC(18,2)', 'column_comment': '単価。注文時点での商品価格'},
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'amount', 
         'data_type': 'NUMERIC(18,2)', 'column_comment': '金額。数量×単価の明細金額'},
        {'schema_name': 'public', 'table_name': 'order_details', 'column_name': 'created_at', 
         'data_type': 'TIMESTAMPTZ', 'column_comment': 'レコード作成日時'}
    ]
    
    # Create DataFrames
    df_tables = pd.DataFrame(table_data)
    df_columns = pd.DataFrame(column_data)
    
    # Write to Excel with multiple sheets
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_tables.to_excel(writer, sheet_name='テーブル一覧', index=False)
        df_columns.to_excel(writer, sheet_name='カラム一覧', index=False)
    
    print(f"✅ Metadata Excel created: {output_file}")
    print(f"   - Tables: {len(df_tables)} records")
    print(f"   - Columns: {len(df_columns)} records")

if __name__ == "__main__":
    create_metadata_excel("../data/input/metadata.xlsx")
