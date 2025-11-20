"""
Metadata Vectorizer
Vectorize metadata and store in pgvector database
"""

import psycopg2
from sentence_transformers import SentenceTransformer
from typing import Dict, List
import numpy as np
from loguru import logger


class MetadataVectorizer:
    """Vectorize metadata and manage pgvector operations"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model = None
        self.db_config = config['databases']['vector_db']
    
    def _load_model(self):
        """Load sentence transformer model"""
        if self.model is None:
            model_name = self.config['vectorizer']['model']
            logger.info(f"Loading vectorizer model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Model loaded successfully")
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            database=self.db_config['database'],
            user=self.db_config['user'],
            password=self.db_config['password']
        )
    
    def vectorize_text(self, text: str) -> List[float]:
        """
        Vectorize text
        
        Args:
            text: Input text
            
        Returns:
            Vector embedding
        """
        self._load_model()
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def vectorize_and_store(self, metadata: Dict) -> None:
        """
        Vectorize metadata and store in pgvector database
        
        Args:
            metadata: Metadata dictionary with tables and columns
        """
        self._load_model()
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # Clear existing data
            cur.execute("TRUNCATE TABLE table_metadata CASCADE")
            logger.info("Cleared existing metadata")
            
            # Insert table metadata
            for table in metadata['tables']:
                # Combine table information for vectorization
                text_for_embedding = f"{table['table_name']} {table.get('table_comment', '')}"
                embedding = self.vectorize_text(text_for_embedding)
                
                cur.execute("""
                    INSERT INTO table_metadata (schema_name, table_name, table_comment, embedding)
                    VALUES (%s, %s, %s, %s)
                    RETURNING table_id
                """, (
                    table['schema_name'],
                    table['table_name'],
                    table.get('table_comment', ''),
                    embedding
                ))
                
                table_id = cur.fetchone()[0]
                
                # Insert column metadata
                table_columns = [
                    c for c in metadata['columns']
                    if c['table_name'] == table['table_name']
                ]
                
                for column in table_columns:
                    # Combine column information for vectorization
                    col_text = f"{column['column_name']} {column.get('data_type', '')} {column.get('column_comment', '')}"
                    col_embedding = self.vectorize_text(col_text)
                    
                    cur.execute("""
                        INSERT INTO column_metadata (table_id, column_name, data_type, column_comment, embedding)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        table_id,
                        column['column_name'],
                        column.get('data_type', ''),
                        column.get('column_comment', ''),
                        col_embedding
                    ))
            
            conn.commit()
            logger.info(f"Vectorized and stored {len(metadata['tables'])} tables and {len(metadata['columns'])} columns")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error vectorizing metadata: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def search_related_tables(self, query_text: str, top_n: int = 5) -> List[Dict]:
        """
        Search related tables by vector similarity
        
        Args:
            query_text: Query text (KPI requirement or features)
            top_n: Number of results to return
            
        Returns:
            List of related table metadata
        """
        self._load_model()
        
        # Vectorize query
        query_embedding = self.vectorize_text(query_text)
        
        # Search in pgvector
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT * FROM search_similar_tables(%s::vector, %s)
            """, (query_embedding, top_n))
            
            results = []
            for row in cur.fetchall():
                table_id, schema_name, table_name, table_comment, similarity = row
                
                # Get columns for this table
                cur.execute("""
                    SELECT column_name, data_type, column_comment
                    FROM column_metadata
                    WHERE table_id = %s
                """, (table_id,))
                
                columns = [
                    {
                        'column_name': col[0],
                        'data_type': col[1],
                        'column_comment': col[2]
                    }
                    for col in cur.fetchall()
                ]
                
                results.append({
                    'table_id': table_id,
                    'schema_name': schema_name,
                    'table_name': table_name,
                    'table_comment': table_comment,
                    'similarity': float(similarity),
                    'columns': columns
                })
            
            logger.info(f"Found {len(results)} related tables for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching tables: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def search_related_columns(self, query_text: str, top_n: int = 10) -> List[Dict]:
        """
        Search related columns by vector similarity
        
        Args:
            query_text: Query text
            top_n: Number of results to return
            
        Returns:
            List of related column metadata
        """
        self._load_model()
        
        query_embedding = self.vectorize_text(query_text)
        
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT * FROM search_similar_columns(%s::vector, %s)
            """, (query_embedding, top_n))
            
            results = [
                {
                    'column_id': row[0],
                    'table_name': row[1],
                    'column_name': row[2],
                    'data_type': row[3],
                    'column_comment': row[4],
                    'similarity': float(row[5])
                }
                for row in cur.fetchall()
            ]
            
            logger.info(f"Found {len(results)} related columns")
            return results
            
        except Exception as e:
            logger.error(f"Error searching columns: {e}")
            raise
        finally:
            cur.close()
            conn.close()
