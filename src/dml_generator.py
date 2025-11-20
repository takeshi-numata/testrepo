"""
DML Generator
Generate ETL DML using Ollama AI
"""

import requests
import json
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from loguru import logger
import re


class DMLGenerator:
    """Generate ETL DML using AI"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.ollama_config = config['ollama']
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load DML prompt template"""
        template_path = Path(self.config['prompts']['dml_template'])
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        else:
            # Fallback to basic template
            return """Generate PostgreSQL ETL DML based on:
DDL: {generated_ddl}
Source Metadata: {source_metadata}
Column Mapping: {column_mapping}

Generate INSERT INTO ... SELECT statements.
Load dimension tables first, then fact tables.
Use BEGIN/COMMIT for transaction.
Include data quality checks."""
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API
        
        Args:
            prompt: Input prompt
            
        Returns:
            AI response
        """
        url = f"{self.ollama_config['base_url']}/api/generate"
        
        payload = {
            'model': self.ollama_config['model'],
            'prompt': prompt,
            'stream': False,
            'options': self.ollama_config['options']
        }
        
        logger.info(f"Calling Ollama API for DML generation: {self.ollama_config['model']}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.ollama_config['timeout']
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def generate(
        self,
        ddl: str,
        source_metadata: List[Dict],
        column_mapping: Dict = None
    ) -> str:
        """
        Generate ETL DML
        
        Args:
            ddl: Generated DDL
            source_metadata: Source table metadata
            column_mapping: Column mapping dictionary (optional)
            
        Returns:
            Generated DML SQL
        """
        logger.info("Generating DML...")
        
        if column_mapping is None:
            column_mapping = self._auto_generate_mapping(ddl, source_metadata)
        
        # Prepare prompt
        prompt = self.prompt_template.format(
            generated_ddl=ddl,
            source_metadata=json.dumps(source_metadata, ensure_ascii=False, indent=2),
            column_mapping=json.dumps(column_mapping, ensure_ascii=False, indent=2),
            data_mart_name='sales_analysis',
            timestamp=datetime.now().isoformat()
        )
        
        # Call AI
        dml = self._call_ollama(prompt)
        
        # Post-process: Extract SQL from response
        dml = self._extract_sql(dml)
        
        logger.info("DML generation completed")
        return dml
    
    def _extract_sql(self, text: str) -> str:
        """
        Extract SQL from AI response
        
        Args:
            text: AI response text
            
        Returns:
            Cleaned SQL
        """
        # Remove markdown code blocks
        if '```sql' in text:
            parts = text.split('```sql')
            if len(parts) > 1:
                sql_part = parts[1].split('```')[0]
                return sql_part.strip()
        
        if '```' in text:
            parts = text.split('```')
            if len(parts) >= 3:
                return parts[1].strip()
        
        # Return as-is if no code blocks found
        return text.strip()
    
    def _auto_generate_mapping(self, ddl: str, source_metadata: List[Dict]) -> Dict:
        """
        Auto-generate column mapping from DDL and source metadata
        
        Args:
            ddl: Generated DDL
            source_metadata: Source table metadata
            
        Returns:
            Column mapping dictionary
        """
        # Extract table names from DDL
        table_pattern = r'CREATE TABLE (\w+)'
        tables = re.findall(table_pattern, ddl, re.IGNORECASE)
        
        mapping = {}
        for table in tables:
            mapping[table] = {
                'source_tables': [m['table_name'] for m in source_metadata],
                'note': 'Auto-generated mapping'
            }
        
        return mapping
    
    def validate_dml(self, dml: str) -> Dict:
        """
        Validate generated DML
        
        Args:
            dml: DML SQL text
            
        Returns:
            Validation result
        """
        issues = []
        
        # Basic validation
        if not dml or len(dml.strip()) == 0:
            issues.append("DML is empty")
        
        if 'INSERT INTO' not in dml.upper():
            issues.append("No INSERT INTO statement found")
        
        if 'SELECT' not in dml.upper():
            issues.append("No SELECT statement found")
        
        # Check for transaction
        has_begin = 'BEGIN' in dml.upper()
        has_commit = 'COMMIT' in dml.upper()
        
        if not (has_begin and has_commit):
            issues.append("Missing transaction control (BEGIN/COMMIT)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
