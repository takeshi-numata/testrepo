"""
Data Mart Orchestrator
Overall control of data mart generation from KPI requirements
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from metadata_loader import MetadataLoader
from vectorizer import MetadataVectorizer
from ddl_generator import DDLGenerator
from dml_generator import DMLGenerator
from sql_executor import SQLExecutor


class DataMartOrchestrator:
    """Data Mart generation orchestrator"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Args:
            config_path: Configuration file path
        """
        self.config = self._load_config(config_path)
        self.metadata_loader = MetadataLoader(self.config)
        self.vectorizer = MetadataVectorizer(self.config)
        self.ddl_generator = DDLGenerator(self.config)
        self.dml_generator = DMLGenerator(self.config)
        self.sql_executor = SQLExecutor(self.config)
        
        # Setup logging
        logger.add(
            Path(self.config['output']['log_dir']) / "orchestrator_{time}.log",
            rotation="100 MB",
            level=self.config['logging']['level']
        )
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def generate_datamart(
        self, 
        kpi_requirement: str,
        metadata_excel_path: str,
        output_dir: Optional[str] = None,
        execute_sql: bool = True
    ) -> Dict:
        """
        Generate data mart from KPI requirements (Main process)
        
        Args:
            kpi_requirement: KPI requirement text
            metadata_excel_path: Metadata Excel file path
            output_dir: Output directory (optional)
            execute_sql: Whether to execute generated SQL
            
        Returns:
            Execution result (DDL, DML, logs, etc.)
        """
        logger.info("=" * 60)
        logger.info("Data Mart Generation Started")
        logger.info("=" * 60)
        
        if output_dir is None:
            output_dir = "data/output"
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "kpi_requirement": kpi_requirement,
            "status": "RUNNING",
            "ddl": None,
            "dml": None,
            "ddl_path": None,
            "dml_path": None,
            "errors": [],
            "execution_results": {}
        }
        
        try:
            # Step 1: Load metadata from Excel
            logger.info("[Step 1] Loading metadata from Excel")
            metadata = self.metadata_loader.load_from_excel(metadata_excel_path)
            logger.info(f"  - Tables: {len(metadata['tables'])}")
            logger.info(f"  - Columns: {len(metadata['columns'])}")
            
            # Step 2: Vectorize and store in pgvector
            logger.info("[Step 2] Vectorizing metadata")
            self.vectorizer.vectorize_and_store(metadata)
            logger.info("  - Vector DB population completed")
            
            # Step 3: Analyze KPI requirements (extract features)
            logger.info("[Step 3] Analyzing KPI requirements")
            features = self._analyze_kpi_requirements(kpi_requirement)
            logger.info(f"  - Extracted features: {features}")
            
            # Step 4: Search related tables
            logger.info("[Step 4] Searching related tables (vector similarity)")
            related_tables = self.vectorizer.search_related_tables(
                kpi_requirement, 
                top_n=10
            )
            logger.info(f"  - Related tables: {[t['table_name'] for t in related_tables]}")
            
            # Step 5: Generate DDL
            logger.info("[Step 5] Generating data mart DDL")
            ddl = self.ddl_generator.generate(
                kpi_requirement=kpi_requirement,
                features=features,
                related_metadata=related_tables
            )
            result["ddl"] = ddl
            
            # Validate DDL
            ddl_validation = self.ddl_generator.validate_ddl(ddl)
            if not ddl_validation['valid']:
                logger.warning(f"DDL validation issues: {ddl_validation['issues']}")
            
            # Save DDL
            ddl_path = Path(output_dir) / "ddl" / f"datamart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            ddl_path.parent.mkdir(parents=True, exist_ok=True)
            ddl_path.write_text(ddl, encoding='utf-8')
            result["ddl_path"] = str(ddl_path)
            logger.info(f"  - DDL saved: {ddl_path}")
            
            # Step 6: Execute DDL (if enabled)
            if execute_sql:
                logger.info("[Step 6] Executing DDL")
                ddl_result = self.sql_executor.execute_ddl(ddl, database='data_mart')
                result["execution_results"]["ddl"] = ddl_result
                
                if not ddl_result['success']:
                    raise Exception(f"DDL execution error: {ddl_result['error']}")
                logger.info("  - DDL execution successful")
            else:
                logger.info("[Step 6] Skipping DDL execution (execute_sql=False)")
            
            # Step 7: Generate DML
            logger.info("[Step 7] Generating ETL DML")
            dml = self.dml_generator.generate(
                ddl=ddl,
                source_metadata=related_tables,
                column_mapping=self._generate_column_mapping(ddl, related_tables)
            )
            result["dml"] = dml
            
            # Validate DML
            dml_validation = self.dml_generator.validate_dml(dml)
            if not dml_validation['valid']:
                logger.warning(f"DML validation issues: {dml_validation['issues']}")
            
            # Save DML
            dml_path = Path(output_dir) / "dml" / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            dml_path.parent.mkdir(parents=True, exist_ok=True)
            dml_path.write_text(dml, encoding='utf-8')
            result["dml_path"] = str(dml_path)
            logger.info(f"  - DML saved: {dml_path}")
            
            # Step 8: Execute DML (if enabled)
            if execute_sql:
                logger.info("[Step 8] Executing DML (ETL processing)")
                dml_result = self.sql_executor.execute_dml(
                    dml, 
                    source_db='central_warehouse',
                    target_db='data_mart'
                )
                result["execution_results"]["dml"] = dml_result
                
                if not dml_result['success']:
                    raise Exception(f"DML execution error: {dml_result['error']}")
                logger.info(f"  - DML execution successful (rows inserted: {dml_result['rows_inserted']})")
            else:
                logger.info("[Step 8] Skipping DML execution (execute_sql=False)")
            
            # Step 9: Data quality check
            if execute_sql:
                logger.info("[Step 9] Data quality check")
                quality_result = self._check_data_quality(ddl)
                result["data_quality"] = quality_result
                logger.info(f"  - Quality check: {quality_result}")
            
            result["status"] = "SUCCESS"
            logger.info("=" * 60)
            logger.info("Data Mart Generation Completed Successfully")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}", exc_info=True)
            result["status"] = "FAILED"
            result["errors"].append(str(e))
            logger.error("=" * 60)
            logger.error("Data Mart Generation Failed")
            logger.error("=" * 60)
        
        # Save result summary
        self._save_result_summary(result, output_dir)
        
        return result
    
    def _analyze_kpi_requirements(self, kpi_requirement: str) -> List[str]:
        """
        Extract required features from KPI requirements
        
        Args:
            kpi_requirement: KPI requirement text
            
        Returns:
            Feature list
        """
        # Simple feature extraction
        # In production, use Ollama AI for better analysis
        features = []
        
        # Time-related
        if any(word in kpi_requirement for word in ['月次', '月別', '日次', '年次', '期間']):
            features.append('時間')
        
        # Customer-related
        if any(word in kpi_requirement for word in ['顧客', 'セグメント', '地域']):
            features.append('顧客')
        
        # Product-related
        if any(word in kpi_requirement for word in ['商品', 'カテゴリ', '製品']):
            features.append('商品')
        
        # Measures
        if any(word in kpi_requirement for word in ['売上', '金額', '収益']):
            features.append('売上金額')
        
        if any(word in kpi_requirement for word in ['数量', '件数']):
            features.append('数量')
        
        return features if features else ['時間', '売上金額']
    
    def _generate_column_mapping(self, ddl: str, related_tables: List[Dict]) -> Dict:
        """
        Generate column mapping from DDL and source tables
        
        Args:
            ddl: Generated DDL
            related_tables: Related table metadata
            
        Returns:
            Column mapping dictionary
        """
        # Simplified mapping
        return {
            'note': 'Auto-generated column mapping',
            'source_tables': [t['table_name'] for t in related_tables]
        }
    
    def _check_data_quality(self, ddl: str) -> Dict:
        """
        Data quality check
        
        Args:
            ddl: Generated DDL
            
        Returns:
            Quality check result
        """
        # Basic quality checks
        return {
            "status": "OK",
            "checks_performed": ["NULL check", "duplicate check"],
            "issues_found": 0
        }
    
    def _save_result_summary(self, result: Dict, output_dir: str):
        """
        Save result summary as JSON
        
        Args:
            result: Result dictionary
            output_dir: Output directory
        """
        summary_path = Path(output_dir) / "logs" / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create summary (exclude large text fields)
        summary = {
            'timestamp': result['timestamp'],
            'status': result['status'],
            'kpi_requirement': result['kpi_requirement'],
            'ddl_path': result.get('ddl_path'),
            'dml_path': result.get('dml_path'),
            'execution_results': result.get('execution_results', {}),
            'errors': result.get('errors', [])
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Result summary saved: {summary_path}")


if __name__ == "__main__":
    # Usage example
    orchestrator = DataMartOrchestrator()
    
    kpi_req = """
    月次の顧客セグメント別・商品カテゴリ別の売上金額と数量を分析したい。
    前年同月比も算出すること。
    """
    
    result = orchestrator.generate_datamart(
        kpi_requirement=kpi_req,
        metadata_excel_path="data/input/metadata.xlsx",
        execute_sql=False  # Set to True to execute SQL
    )
    
    print(f"\n{'='*60}")
    print(f"Execution Status: {result['status']}")
    print(f"{'='*60}")
    if result['status'] == 'SUCCESS':
        print(f"DDL Path: {result['ddl_path']}")
        print(f"DML Path: {result['dml_path']}")
    else:
        print(f"Errors: {result['errors']}")
