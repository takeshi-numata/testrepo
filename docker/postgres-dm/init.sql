-- ============================================
-- Data Mart DB Initialization
-- ============================================

-- Schema creation
CREATE SCHEMA IF NOT EXISTS datamart;

-- ETL execution log
CREATE TABLE datamart.etl_execution_log (
    log_id BIGSERIAL PRIMARY KEY,
    datamart_name VARCHAR(100) NOT NULL,
    execution_start TIMESTAMPTZ,
    execution_end TIMESTAMPTZ,
    status VARCHAR(20), -- SUCCESS, FAILED, RUNNING
    records_inserted INTEGER,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE datamart.etl_execution_log IS 'ETL実行ログ';

-- ETL error log
CREATE TABLE datamart.etl_error_log (
    error_id BIGSERIAL PRIMARY KEY,
    etl_name VARCHAR(100),
    phase VARCHAR(50),
    error_type VARCHAR(100),
    error_message TEXT,
    record_count INTEGER,
    occurred_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE datamart.etl_error_log IS 'ETLエラーログ';

-- SQL generation history
CREATE TABLE datamart.sql_generation_history (
    history_id BIGSERIAL PRIMARY KEY,
    kpi_requirement TEXT NOT NULL,
    generated_ddl TEXT,
    generated_dml TEXT,
    ai_model VARCHAR(50),
    generation_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    execution_status VARCHAR(20)
);

COMMENT ON TABLE datamart.sql_generation_history IS 'AI生成SQL履歴';
