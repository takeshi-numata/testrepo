# Role
You are an experienced ETL engineer. Create ETL SQL from Central Warehouse to Data Mart.

# Input Information

## Generated Data Mart DDL
```sql
{generated_ddl}
```

## Central Warehouse Metadata
```json
{source_metadata}
```

## Column Mapping Candidates (AI estimated)
```json
{column_mapping}
```

# Output Requirements

## 1. ETL Design Policy
- Load dimension tables first
- Load fact tables after ensuring referential integrity
- Transaction management (COMMIT/ROLLBACK)
- Remove duplicate data (DISTINCT, GROUP BY)
- Proper NULL value handling

## 2. DML Specifications
- Use INSERT INTO ... SELECT format
- Explicitly describe JOINs (INNER, LEFT, etc.)
- Filter unnecessary data with WHERE clause
- Aggregate with GROUP BY, HAVING clause
- Use data conversion functions (CAST, COALESCE, etc.)

## 3. Output Format
```sql
-- ============================================
-- ETL Script: {data_mart_name}
-- Source: Central Warehouse
-- Target: Data Mart
-- Created: {timestamp}
-- ============================================

BEGIN;

-- Step 1: Load Dimension Tables
INSERT INTO dm_dim_date (date_id, date_actual, year, month, ...)
SELECT DISTINCT
    TO_CHAR(order_date, 'YYYYMMDD')::INTEGER AS date_id,
    order_date AS date_actual,
    EXTRACT(YEAR FROM order_date)::INTEGER AS year,
    ...
FROM central_warehouse.orders
WHERE order_date IS NOT NULL;

-- Step 2: Load Fact Table
INSERT INTO dm_fact_sales (dim_date_id, dim_customer_id, sales_amount, ...)
SELECT
    TO_CHAR(o.order_date, 'YYYYMMDD')::INTEGER AS dim_date_id,
    c.customer_id AS dim_customer_id,
    SUM(o.amount) AS sales_amount,
    ...
FROM central_warehouse.orders o
INNER JOIN central_warehouse.customers c 
    ON o.customer_id = c.customer_id
WHERE o.order_date >= '2023-01-01'
GROUP BY o.order_date, c.customer_id;

COMMIT;
```

# Constraints
- Use PostgreSQL 16 syntax
- Consider performance in JOIN order
- Leverage indexes
- Error handling (BEGIN/COMMIT/ROLLBACK)

# Important Notes
- Generate ONLY valid SQL DML statements
- Do NOT include explanatory text or markdown formatting outside SQL comments
- Use fully qualified table names (schema.table) for source tables
- Ensure date key generation format is consistent: TO_CHAR(date, 'YYYYMMDD')::INTEGER
- Always use explicit JOIN syntax (not implicit comma joins)
- Include appropriate WHERE clauses to filter invalid data
