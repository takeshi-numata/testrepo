# KPI要件からのデータマート自動生成システム

生成AIを活用して、KPI要件文章からデータマートDDL/DMLを自動生成するPoCシステムです。

## システム概要

### 主要機能
1. **メタデータベクトル化**: セントラルウェアハウスのメタデータをpgvectorでベクトル化
2. **関連テーブル検索**: KPI要件から関連するテーブルを自動検索
3. **DDL自動生成**: Ollama AIでデータマートDDLを生成
4. **DML自動生成**: ETL SQLを自動生成
5. **SQL実行**: 生成したDDL/DMLを実行してデータマート構築

### アーキテクチャ
- **PostgreSQL (Central Warehouse)**: 既存データウェアハウス
- **PostgreSQL (Data Mart)**: 生成されるデータマート
- **pgvector**: メタデータベクトルDB
- **Ollama (qwen2.5-coder)**: SQL生成AI
- **Python**: オーケストレーション

## セットアップ手順

### 1. Docker環境起動

```bash
cd docker
docker-compose up -d

# ヘルスチェック
docker ps
```

### 2. Ollamaモデルプル

```bash
docker exec ollama_llm ollama pull qwen2.5-coder:7b-instruct
```

### 3. Python環境構築

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 使用方法

### オプション1: Pythonスクリプト直接実行

```bash
cd src
python3 orchestrator.py
```

### オプション2: インタラクティブ実行

```python
from orchestrator import DataMartOrchestrator

orchestrator = DataMartOrchestrator()

kpi_req = """
月次の顧客セグメント別・商品カテゴリ別の売上金額と数量を分析したい。
前年同月比も算出すること。
"""

result = orchestrator.generate_datamart(
    kpi_requirement=kpi_req,
    metadata_excel_path="../data/input/metadata.xlsx",
    execute_sql=True  # SQL実行する場合はTrue
)

print(f"Status: {result['status']}")
print(f"DDL Path: {result['ddl_path']}")
print(f"DML Path: {result['dml_path']}")
```

## ディレクトリ構成

```
datamart-generator/
├── docker/                 # Docker構成
│   ├── docker-compose.yml
│   ├── postgres-cwh/       # Central Warehouse
│   │   └── init.sql
│   ├── postgres-dm/        # Data Mart
│   │   └── init.sql
│   └── pgvector/           # Vector DB
│       └── init.sql
├── src/                    # ソースコード
│   ├── orchestrator.py     # メインオーケストレーター
│   ├── metadata_loader.py  # メタデータ読込
│   ├── vectorizer.py       # ベクトル化処理
│   ├── ddl_generator.py    # DDL生成
│   ├── dml_generator.py    # DML生成
│   └── sql_executor.py     # SQL実行
├── config/                 # 設定ファイル
│   ├── config.yaml
│   └── prompts/
│       ├── ddl_prompt.md
│       └── dml_prompt.md
├── data/                   # データディレクトリ
│   ├── input/
│   │   ├── metadata.xlsx   # メタデータExcel
│   │   └── kpi_requirements.txt
│   └── output/
│       ├── ddl/            # 生成DDL
│       ├── dml/            # 生成DML
│       └── logs/           # 実行ログ
├── scripts/                # ユーティリティスクリプト
│   └── create_sample_metadata.py
└── requirements.txt
```

## 生成されるファイル

### DDL (data/output/ddl/)
- データマートのテーブル定義SQL
- スタースキーマ設計（ディメンジョン + ファクト）
- インデックス定義
- コメント（日本語）

### DML (data/output/dml/)
- ETL SQL (INSERT INTO ... SELECT)
- トランザクション制御
- データ品質チェック

## データベース接続情報

### Central Warehouse
- Host: localhost
- Port: 5432
- Database: central_warehouse
- User: cwh_user
- Password: cwh_pass

### Data Mart
- Host: localhost
- Port: 5433
- Database: data_mart
- User: dm_user
- Password: dm_pass

### Vector DB
- Host: localhost
- Port: 5434
- Database: metadata_db
- User: vector_user
- Password: vector_pass

### Ollama
- URL: http://localhost:11434
- Model: qwen2.5-coder:7b-instruct

## トラブルシューティング

### Ollama接続エラー
```bash
# モデルが未プルの場合
docker exec ollama_llm ollama pull qwen2.5-coder:7b-instruct

# コンテナ再起動
docker restart ollama_llm
```

### PostgreSQL接続エラー
```bash
# コンテナ状態確認
docker ps
docker logs central_warehouse
docker logs data_mart
docker logs metadata_vector_db

# 再起動
docker-compose restart
```

### pgvector拡張エラー
```bash
# pgvector拡張を手動で有効化
docker exec -it metadata_vector_db psql -U vector_user -d metadata_db
# psql> CREATE EXTENSION IF NOT EXISTS vector;
```

## テストデータ

サンプルデータは以下を含みます：
- 顧客マスタ: 10件（企業/個人）
- 商品マスタ: 10件（電子機器/周辺機器）
- 受注データ: 50件（2023-2024）
- 受注明細: 100+件

## 参考情報

### KPI要件例

```
月次の売上分析
→ 時間ディメンジョン（月別）+ 売上ファクト

顧客セグメント別・商品カテゴリ別売上
→ 顧客ディメンジョン + 商品ディメンジョン + 売上ファクト

地域別売上推移
→ 地域ディメンジョン + 時間ディメンジョン + 売上ファクト
```

### 生成されるスキーマ例

```sql
-- ディメンジョンテーブル
CREATE TABLE dm_dim_date (...);
CREATE TABLE dm_dim_customer (...);
CREATE TABLE dm_dim_product (...);

-- ファクトテーブル
CREATE TABLE dm_fact_sales (
    dim_date_id INTEGER,
    dim_customer_id BIGINT,
    dim_product_id BIGINT,
    sales_amount NUMERIC(18,2),
    quantity INTEGER,
    ...
);
```

## ライセンス

This is a PoC (Proof of Concept) system for research purposes.

## 作成者

AI-Generated Data Mart System PoC
