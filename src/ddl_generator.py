"""
DDL Generator
Generate data mart DDL using Ollama AI
"""

import requests
import json
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from loguru import logger


class DDLGenerator:
    """Generate data mart DDL using AI"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.ollama_config = config['ollama']
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load DDL prompt template"""
        template_path = Path(self.config['prompts']['ddl_template'])
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        else:
            # Fallback to basic template
            return """Generate PostgreSQL DDL for data mart based on:
KPI Requirement: {kpi_requirement}
Features: {features}
Related Tables: {related_metadata}

Generate star schema with dimension and fact tables.
Use dm_ prefix for table names.
Include appropriate indexes and foreign keys.
Add Japanese comments."""
    
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
        
        logger.info(f"Calling Ollama API: {self.ollama_config['model']}")
        
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
        kpi_requirement: str,
        features: List[str],
        related_metadata: List[Dict]
    ) -> str:
        """
        Generate data mart DDL
        
        Args:
            kpi_requirement: KPI requirement text
            features: Extracted features
            related_metadata: Related table metadata
            
        Returns:
            Generated DDL SQL
        """
        logger.info("Generating DDL...")
        
        # Prepare prompt
        prompt = self.prompt_template.format(
            kpi_requirement=kpi_requirement,
            features=json.dumps(features, ensure_ascii=False, indent=2),
            related_metadata=json.dumps(related_metadata, ensure_ascii=False, indent=2),
            data_mart_name='sales_analysis',
            purpose='KPI分析用データマート',
            timestamp=datetime.now().isoformat()
        )
        
        # Call AI
        ddl = self._call_ollama(prompt)
        
        # Post-process: Extract SQL from response
        ddl = self._extract_sql(ddl)
        
        logger.info("DDL generation completed")
        return ddl
    
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
    
    def validate_ddl(self, ddl: str) -> Dict:
        """
        Validate generated DDL
        
        Args:
            ddl: DDL SQL text
            
        Returns:
            Validation result
        """
        issues = []
        
        # Basic validation
        if not ddl or len(ddl.strip()) == 0:
            issues.append("DDL is empty")
        
        if 'CREATE TABLE' not in ddl.upper():
            issues.append("No CREATE TABLE statement found")
        
        # Check for required elements
        required_elements = ['PRIMARY KEY', 'COMMENT ON']
        for element in required_elements:
            if element not in ddl.upper():
                issues.append(f"Missing: {element}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
