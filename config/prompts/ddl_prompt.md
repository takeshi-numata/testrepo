# Role
You are an experienced data architect. Design the optimal data mart schema for KPI analysis.

# Input Information

## KPI Requirements
```
{kpi_requirement}
```

## Required Features (AI analyzed)
```json
{features}
```

## Related Central Warehouse Tables
```json
{related_metadata}
```

# Output Requirements

## 1. Data Mart Design Policy
- Adopt Star Schema or Snowflake Schema
- Fact Table: Numerical data for aggregation
- Dimension Tables: Analysis axes (time, customer, product, etc.)
- Appropriate index design

## 2. DDL Specifications
- Table name: `dm_` prefix
- Column name: snake_case
- Primary key: Required
- Foreign key: Ensure referential integrity
- NOT NULL constraint: Set appropriately
- Comment: Japanese description for all tables/columns

## 3. Output Format
```sql
-- ============================================
-- Data Mart: {data_mart_name}
-- Purpose: {purpose}
-- Created: {timestamp}
-- ============================================

-- Dimension Tables
CREATE TABLE dm_dim_xxx (
    ...
);

-- Fact Table
CREATE TABLE dm_fact_yyy (
    ...
);

-- Indexes
CREATE INDEX idx_xxx ON dm_fact_yyy(...);

-- Comments
COMMENT ON TABLE dm_fact_yyy IS '...';
COMMENT ON COLUMN dm_fact_yyy.column IS '...';
```

# Constraints
- Use PostgreSQL 16 syntax
- Select data types considering performance
- Consider future extensibility

# Important Notes
- Generate ONLY valid SQL DDL statements
- Do NOT include explanatory text or markdown formatting outside SQL comments
- Use Japanese for comments
- Ensure all foreign keys reference existing dimension tables
- Add appropriate indexes for query performance
