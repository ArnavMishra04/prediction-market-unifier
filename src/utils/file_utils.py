# src/utils/file_utils.py
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
from src.utils.logging_config import setup_logger

logger = setup_logger(__name__)

def read_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of dictionaries containing the JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        raise

def write_json_file(data: Any, file_path: Path, indent: int = 2) -> None:
    """
    Write data to a JSON file.
    
    Args:
        data: Data to write (must be JSON serializable)
        file_path: Path to the output file
        indent: JSON indentation level
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, default=str)
        logger.info(f"Successfully wrote JSON data to {file_path}")
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        raise

def write_csv_file(data: List[Dict[str, Any]], file_path: Path) -> None:
    """
    Write data to a CSV file.
    
    Args:
        data: List of dictionaries to write as CSV
        file_path: Path to the output file
    """
    try:
        if not data:
            logger.warning("No data to write to CSV")
            return
            
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, encoding='utf-8')
        logger.info(f"Successfully wrote CSV data to {file_path}")
    except Exception as e:
        logger.error(f"Error writing CSV file {file_path}: {e}")
        raise 
