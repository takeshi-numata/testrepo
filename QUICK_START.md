# Quick Start Guide - KPI要件からのデータマート自動生成システム

## 🚀 PCローカルでのテスト実行（Docker環境あり）

### 前提条件
- Docker & Docker Compose インストール済み
- Python 3.11+ インストール済み

### ステップ1: プロジェクトのセットアップ

```bash
cd /path/to/datamart-generator

# Python環境構築
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### ステップ2: Docker環境起動

```bash
cd docker
docker-compose up -d

# コンテナ起動確認
docker ps

# 以下の4つのコンテナが起動していることを確認:
# - central_warehouse (PostgreSQL - Port 5432)
# - data_mart (PostgreSQL - Port 5433)
# - metadata_vector_db (pgvector - Port 5434)
# - ollama_llm (Ollama - Port 11434)
```

### ステップ3: Ollamaモデルのダウンロード

```bash
# qwen2.5-coder:7b-instructモデルをプル（初回のみ、約4GB）
docker exec ollama_llm ollama pull qwen2.5-coder:7b-instruct

# モデル確認
docker exec ollama_llm ollama list
```

### ステップ4: データマート生成実行

```bash
cd ../src

# Pythonスクリプト実行
python3 orchestrator.py
```

### ステップ5: 結果確認

```bash
# 生成されたDDL確認
ls -la ../data/output/ddl/

# 生成されたDML確認
ls -la ../data/output/dml/

# SQLファイル内容確認
cat ../data/output/ddl/datamart_YYYYMMDD_HHMMSS.sql
cat ../data/output/dml/etl_YYYYMMDD_HHMMSS.sql
```

---

## 🎯 Docker環境なしでのデモ実行

Docker環境が利用できない場合でも、システムの動作を確認できます。

```bash
cd scripts
python3 demo_without_docker.py
```

このデモでは以下が実行されます：
1. ✅ メタデータExcelの読込
2. ✅ KPI要件の分析
3. ✅ 関連テーブルの検索（シミュレーション）
4. ✅ DDL生成（サンプル）
5. ✅ DML生成（サンプル）

生成されたSQLファイル：
- `data/output/ddl/datamart_demo_*.sql`
- `data/output/dml/etl_demo_*.sql`

---

## 📊 KPI要件のカスタマイズ

### 方法1: テキストファイル編集

```bash
# KPI要件ファイル編集
nano data/input/kpi_requirements.txt

# 例:
# 月次の顧客セグメント別・商品カテゴリ別の売上金額と数量を分析したい。
# 前年同月比も算出すること。
```

### 方法2: Pythonコードで直接指定

```python
from orchestrator import DataMartOrchestrator

orchestrator = DataMartOrchestrator()

# カスタムKPI要件
kpi_req = """
週次の地域別売上分析を行いたい。
新規顧客と既存顧客を区別して集計すること。
商品カテゴリ別の売上構成比も確認したい。
"""

result = orchestrator.generate_datamart(
    kpi_requirement=kpi_req,
    metadata_excel_path="data/input/metadata.xlsx",
    execute_sql=True
)
```

---

## 🔍 生成されたデータマートの確認

### PostgreSQLに接続

```bash
# Data Martに接続
psql -h localhost -p 5433 -U dm_user -d data_mart
# Password: dm_pass

# テーブル確認
\dt datamart.*

# データ確認（ETL実行後）
SELECT * FROM dm_dim_date LIMIT 10;
SELECT * FROM dm_dim_customer LIMIT 10;
SELECT * FROM dm_fact_sales LIMIT 10;

# KPI分析例: 月次売上集計
SELECT 
    d.year_month,
    c.segment,
    p.category,
    SUM(f.sales_amount) as total_sales,
    SUM(f.quantity) as total_quantity
FROM dm_fact_sales f
JOIN dm_dim_date d ON f.dim_date_id = d.date_id
JOIN dm_dim_customer c ON f.dim_customer_id = c.customer_id
JOIN dm_dim_product p ON f.dim_product_id = p.product_id
GROUP BY d.year_month, c.segment, p.category
ORDER BY d.year_month, total_sales DESC;
```

---

## 📁 プロジェクト構成の理解

```
datamart-generator/
├── docker/               # Docker構成ファイル
│   ├── docker-compose.yml
│   ├── postgres-cwh/     # Central Warehouse初期化SQL
│   ├── postgres-dm/      # Data Mart初期化SQL
│   └── pgvector/         # Vector DB初期化SQL
│
├── src/                  # Pythonソースコード
│   ├── orchestrator.py   # ⭐ メインエントリーポイント
│   ├── metadata_loader.py
│   ├── vectorizer.py
│   ├── ddl_generator.py
│   ├── dml_generator.py
│   └── sql_executor.py
│
├── config/               # 設定ファイル
│   ├── config.yaml       # データベース接続情報等
│   └── prompts/          # AIプロンプトテンプレート
│
├── data/
│   ├── input/
│   │   ├── metadata.xlsx      # ⭐ メタデータExcel
│   │   └── kpi_requirements.txt
│   └── output/
│       ├── ddl/          # 生成されたDDL
│       ├── dml/          # 生成されたDML
│       └── logs/         # 実行ログ
│
└── scripts/              # ユーティリティスクリプト
    ├── create_sample_metadata.py
    └── demo_without_docker.py
```

---

## 🛠️ トラブルシューティング

### Ollama接続エラー

```bash
# Ollamaコンテナの状態確認
docker logs ollama_llm

# Ollamaサービス再起動
docker restart ollama_llm

# モデル再ダウンロード
docker exec ollama_llm ollama pull qwen2.5-coder:7b-instruct
```

### PostgreSQL接続エラー

```bash
# コンテナログ確認
docker logs central_warehouse
docker logs data_mart
docker logs metadata_vector_db

# コンテナ再起動
docker-compose restart
```

### pgvector拡張エラー

```bash
# pgvector拡張を手動で有効化
docker exec -it metadata_vector_db psql -U vector_user -d metadata_db
```

```sql
-- psqlプロンプトで実行
CREATE EXTENSION IF NOT EXISTS vector;
\dx  -- 拡張機能確認
```

### Python依存関係エラー

```bash
# 依存パッケージ再インストール
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 🎓 システムの動作理解

### 処理フロー

1. **メタデータ読込**: ExcelからCentral Warehouseのテーブル・カラム情報を読込
2. **ベクトル化**: sentence-transformersでメタデータをベクトル化してpgvectorに保存
3. **関連テーブル検索**: KPI要件をベクトル化し、コサイン類似度で関連テーブルを検索
4. **DDL生成**: Ollama AIでデータマートのスキーマ（スタースキーマ）を生成
5. **DML生成**: ETL SQL（INSERT INTO ... SELECT）を生成
6. **SQL実行**: DDL/DMLを実行してデータマート構築

### 生成されるスキーマ設計

- **ディメンジョンテーブル**: 分析軸（日付、顧客、商品等）
- **ファクトテーブル**: 集計対象の数値データ（売上金額、数量等）
- **スタースキーマ**: ディメンジョン + ファクトの標準的なDWH設計
- **インデックス**: クエリパフォーマンス最適化

---

## 📚 次のステップ

### 1. メタデータのカスタマイズ

実際のCentral Warehouseのメタデータに合わせてExcelを更新：

```bash
# メタデータExcel編集
libreoffice data/input/metadata.xlsx
# または
python3 scripts/create_sample_metadata.py  # サンプル再生成
```

### 2. プロンプトのチューニング

AIの生成品質を向上させるためにプロンプトを調整：

```bash
nano config/prompts/ddl_prompt.md
nano config/prompts/dml_prompt.md
```

### 3. 実データでのテスト

Central Warehouseに実データを投入してテスト：

```bash
psql -h localhost -p 5432 -U cwh_user -d central_warehouse -f your_data.sql
```

### 4. BIツールとの連携

生成したデータマートをTableau、Power BI等のBIツールで可視化

---

## ⚙️ 設定のカスタマイズ

### config/config.yaml

```yaml
# データベース接続情報変更
databases:
  central_warehouse:
    host: your-db-host
    port: 5432
    database: your_db
    user: your_user
    password: your_password

# Ollamaモデル変更
ollama:
  model: qwen2.5-coder:7b-instruct  # または他のモデル
  options:
    temperature: 0.1  # 生成のランダム性（0-1）
```

---

## 📞 サポート

質問や問題が発生した場合：

1. **README.md**: 詳細なドキュメント
2. **ログ確認**: `data/output/logs/`
3. **GitHub Issues**: プロジェクトのIssueを作成

---

## ✅ チェックリスト

完全な動作確認のためのチェックリスト：

- [ ] Dockerコンテナが4つすべて起動している
- [ ] Ollamaモデル（qwen2.5-coder:7b-instruct）がダウンロード済み
- [ ] Python依存パッケージがインストール済み
- [ ] メタデータExcelが存在する
- [ ] DDL/DMLが正常に生成される
- [ ] PostgreSQLでDDL/DMLが実行できる
- [ ] データマートにデータが投入される

すべてチェックが完了すれば、本番環境への適用準備完了です！
