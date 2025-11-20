"""
Metadata Loader
Load metadata from Excel file
"""

import pandas as pd
from typing import Dict, List
from pathlib import Path


class MetadataLoader:
    """Load metadata from Excel file"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def load_from_excel(self, excel_path: str) -> Dict[str, List[Dict]]:
        """
        Load metadata from Excel file
        
        Args:
            excel_path: Path to metadata Excel file
            
        Returns:
            Dictionary containing tables and columns metadata
        """
        excel_file = Path(excel_path)
        if not excel_file.exists():
            raise FileNotFoundError(f"Metadata Excel file not found: {excel_path}")
        
        # Read tables sheet
        df_tables = pd.read_excel(excel_path, sheet_name='テーブル一覧')
        tables = df_tables.to_dict('records')
        
        # Read columns sheet
        df_columns = pd.read_excel(excel_path, sheet_name='カラム一覧')
        columns = df_columns.to_dict('records')
        
        return {
            'tables': tables,
            'columns': columns
        }
    
    def get_table_metadata(self, metadata: Dict, table_name: str) -> Dict:
        """
        Get specific table metadata
        
        Args:
            metadata: Full metadata dictionary
            table_name: Target table name
            
        Returns:
            Table metadata with columns
        """
        # Find table
        table_info = next(
            (t for t in metadata['tables'] if t['table_name'] == table_name),
            None
        )
        
        if not table_info:
            return None
        
        # Get columns for this table
        table_columns = [
            c for c in metadata['columns'] 
            if c['table_name'] == table_name
        ]
        
        return {
            **table_info,
            'columns': table_columns
        }
