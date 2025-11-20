-- ============================================
-- pgvector Metadata DB Initialization
-- ============================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table Metadata
CREATE TABLE table_metadata (
    table_id SERIAL PRIMARY KEY,
    schema_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    table_comment TEXT,
    embedding vector(384),  -- sentence-transformers dimension
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(schema_name, table_name)
);

COMMENT ON TABLE table_metadata IS 'テーブルメタデータとベクトル';
COMMENT ON COLUMN table_metadata.table_id IS 'テーブルID';
COMMENT ON COLUMN table_metadata.schema_name IS 'スキーマ名';
COMMENT ON COLUMN table_metadata.table_name IS 'テーブル名';
COMMENT ON COLUMN table_metadata.table_comment IS 'テーブル説明';
COMMENT ON COLUMN table_metadata.embedding IS 'テーブル説明文のベクトル表現';

-- Column Metadata
CREATE TABLE column_metadata (
    column_id SERIAL PRIMARY KEY,
    table_id INTEGER NOT NULL REFERENCES table_metadata(table_id),
    column_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50),
    column_comment TEXT,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_id, column_name)
);

COMMENT ON TABLE column_metadata IS 'カラムメタデータとベクトル';
COMMENT ON COLUMN column_metadata.column_id IS 'カラムID';
COMMENT ON COLUMN column_metadata.table_id IS 'テーブルID';
COMMENT ON COLUMN column_metadata.column_name IS 'カラム名';
COMMENT ON COLUMN column_metadata.data_type IS 'データ型';
COMMENT ON COLUMN column_metadata.column_comment IS 'カラム説明';
COMMENT ON COLUMN column_metadata.embedding IS 'カラム説明文のベクトル表現';

-- Vector search indexes (HNSW: High-performance approximate nearest neighbor search)
CREATE INDEX idx_table_embedding ON table_metadata 
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_column_embedding ON column_metadata 
    USING hnsw (embedding vector_cosine_ops);

-- Search function (get top N similar tables)
CREATE OR REPLACE FUNCTION search_similar_tables(
    query_embedding vector(384),
    top_n INTEGER DEFAULT 5
)
RETURNS TABLE (
    table_id INTEGER,
    schema_name VARCHAR,
    table_name VARCHAR,
    table_comment TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_id,
        t.schema_name,
        t.table_name,
        t.table_comment,
        1 - (t.embedding <=> query_embedding) AS similarity
    FROM table_metadata t
    WHERE t.embedding IS NOT NULL
    ORDER BY t.embedding <=> query_embedding
    LIMIT top_n;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_similar_tables IS 'ベクトル類似度でテーブルを検索';

-- Column search function
CREATE OR REPLACE FUNCTION search_similar_columns(
    query_embedding vector(384),
    top_n INTEGER DEFAULT 10
)
RETURNS TABLE (
    column_id INTEGER,
    table_name VARCHAR,
    column_name VARCHAR,
    data_type VARCHAR,
    column_comment TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.column_id,
        t.table_name,
        c.column_name,
        c.data_type,
        c.column_comment,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM column_metadata c
    INNER JOIN table_metadata t ON c.table_id = t.table_id
    WHERE c.embedding IS NOT NULL
    ORDER BY c.embedding <=> query_embedding
    LIMIT top_n;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION search_similar_columns IS 'ベクトル類似度でカラムを検索';
