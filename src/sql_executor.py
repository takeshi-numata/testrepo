"""
SQL Executor
Execute DDL/DML on PostgreSQL databases
"""

import psycopg2
from typing import Dict
from loguru import logger


class SQLExecutor:
    """Execute SQL on PostgreSQL databases"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def _get_connection(self, database: str):
        """
        Get database connection
        
        Args:
            database: Database name (central_warehouse, data_mart, vector_db)
            
        Returns:
            Database connection
        """
        db_config = self.config['databases'][database]
        return psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
    
    def execute_ddl(self, ddl: str, database: str = 'data_mart') -> Dict:
        """
        Execute DDL SQL
        
        Args:
            ddl: DDL SQL text
            database: Target database
            
        Returns:
            Execution result
        """
        logger.info(f"Executing DDL on {database}...")
        
        conn = self._get_connection(database)
        cur = conn.cursor()
        
        try:
            # Execute DDL
            cur.execute(ddl)
            conn.commit()
            
            logger.info("DDL execution successful")
            return {
                'success': True,
                'message': 'DDL executed successfully'
            }
            
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"DDL execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            cur.close()
            conn.close()
    
    def execute_dml(
        self,
        dml: str,
        source_db: str = 'central_warehouse',
        target_db: str = 'data_mart'
    ) -> Dict:
        """
        Execute DML SQL (ETL)
        
        Args:
            dml: DML SQL text
            source_db: Source database
            target_db: Target database
            
        Returns:
            Execution result
        """
        logger.info(f"Executing DML (ETL from {source_db} to {target_db})...")
        
        # For ETL, we need to use dblink or execute from target with schema qualification
        # Simplified: assume source tables are accessible via schema or dblink
        conn = self._get_connection(target_db)
        cur = conn.cursor()
        
        try:
            # Replace source table references if needed
            # In real implementation, use dblink or foreign data wrapper
            # For this PoC, assuming tables are in same PostgreSQL instance
            modified_dml = dml.replace(
                'central_warehouse.',
                'public.'  # Assuming source is on same instance
            )
            
            # Execute DML
            cur.execute(modified_dml)
            
            # Get row count
            row_count = cur.rowcount if cur.rowcount > 0 else 0
            
            conn.commit()
            
            logger.info(f"DML execution successful: {row_count} rows affected")
            return {
                'success': True,
                'rows_inserted': row_count,
                'message': f'ETL completed: {row_count} rows processed'
            }
            
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"DML execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'rows_inserted': 0
            }
        finally:
            cur.close()
            conn.close()
    
    def validate_syntax(self, sql: str, database: str = 'data_mart') -> Dict:
        """
        Validate SQL syntax without execution
        
        Args:
            sql: SQL text
            database: Target database
            
        Returns:
            Validation result
        """
        conn = self._get_connection(database)
        cur = conn.cursor()
        
        try:
            # Use EXPLAIN to validate syntax without execution
            cur.execute(f"EXPLAIN {sql}")
            conn.rollback()  # Don't commit
            
            return {
                'valid': True,
                'message': 'SQL syntax is valid'
            }
            
        except psycopg2.Error as e:
            conn.rollback()
            return {
                'valid': False,
                'error': str(e)
            }
        finally:
            cur.close()
            conn.close()
    
    def check_table_exists(self, table_name: str, database: str = 'data_mart') -> bool:
        """
        Check if table exists
        
        Args:
            table_name: Table name to check
            database: Target database
            
        Returns:
            True if table exists
        """
        conn = self._get_connection(database)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            
            exists = cur.fetchone()[0]
            return exists
            
        except psycopg2.Error as e:
            logger.error(f"Error checking table: {e}")
            return False
        finally:
            cur.close()
            conn.close()
