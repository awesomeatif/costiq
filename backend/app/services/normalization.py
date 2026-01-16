"""
Data Normalization Service

Single responsibility: Column name mapping + data type casting.
Accepts parsed CSV rows, normalizes column names, casts data types,
returns structured dicts ready for database storage.
"""

import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import re


# Column name mappings: standard_name -> [possible input variations]
COLUMN_MAPPINGS = {
    # Procurement columns
    "vendor_name": ["vendor_name", "vendor", "supplier", "supplier_name"],
    "item_sku": ["item_sku", "sku", "product_code", "item_code"],
    "item_description": ["item_description", "description", "item_name"],
    "unit_price": ["unit_price", "price", "cost", "unit_cost"],
    "quantity": ["quantity", "qty", "amount"],
    "po_number": ["po_number", "po", "purchase_order", "order_number"],
    "po_date": ["po_date", "order_date", "date"],
    "department": ["department", "dept", "cost_center"],
    
    # Inventory columns
    "sku": ["sku", "item_sku", "product_code"],
    "location": ["location", "storage_location", "warehouse"],
    "quantity_on_hand": ["quantity_on_hand", "qty_on_hand", "on_hand", "quantity"],
    "expiry_date": ["expiry_date", "exp_date", "expiration_date"],
    "unit_cost": ["unit_cost", "cost", "price"],
    
    # Labor columns
    "staff_id": ["staff_id", "employee_id", "emp_id"],
    "shift_date": ["shift_date", "date", "work_date"],
    "hours_worked": ["hours_worked", "hours", "total_hours"],
    "overtime_hours": ["overtime_hours", "ot_hours", "overtime"],
}


def normalize_column_name(col: str) -> str:
    """Normalize column name for matching (lowercase, no spaces/underscores)."""
    return re.sub(r'[\s_-]', '', col.lower())


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map input column names to standard column names.
    
    Args:
        df: DataFrame with original column names
        
    Returns:
        DataFrame with standardized column names
    """
    # Build reverse lookup: normalized_input -> standard_name
    rename_map = {}
    
    for col in df.columns:
        normalized = normalize_column_name(col)
        
        # Find matching standard name
        for standard_name, variations in COLUMN_MAPPINGS.items():
            for variation in variations:
                if normalize_column_name(variation) == normalized:
                    rename_map[col] = standard_name
                    break
    
    return df.rename(columns=rename_map)


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast columns to appropriate data types.
    
    Args:
        df: DataFrame with standardized column names
        
    Returns:
        DataFrame with correct data types
    """
    # Numeric columns
    numeric_cols = ["unit_price", "quantity", "quantity_on_hand", "unit_cost", 
                    "hours_worked", "overtime_hours"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Date columns
    date_cols = ["po_date", "expiry_date", "shift_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    
    # String columns - strip whitespace
    string_cols = ["vendor_name", "item_sku", "item_description", "department", 
                   "sku", "location", "staff_id"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace("nan", "")
    
    return df


def normalize(df: pd.DataFrame, file_type: str) -> Tuple[List[Dict], List[str]]:
    """
    Main normalization function.
    
    1. Map column names to standard names
    2. Cast data types appropriately
    3. Return list of dicts ready for database
    
    Args:
        df: Raw DataFrame from CSV
        file_type: Type of file (po, invoice, inventory, labor, equipment)
        
    Returns:
        Tuple of (list of normalized row dicts, list of warnings)
    """
    warnings = []
    
    # Step 1: Map column names
    df = map_columns(df)
    
    # Step 2: Cast data types
    df = cast_types(df)
    
    # Step 3: Check for required columns based on file type
    if file_type in ["po", "invoice"]:
        required = ["vendor_name", "item_sku", "unit_price"]
    elif file_type == "inventory":
        required = ["sku", "quantity_on_hand"]
    elif file_type == "labor":
        required = ["department", "hours_worked"]
    else:
        required = []
    
    missing = [col for col in required if col not in df.columns]
    if missing:
        warnings.append(f"Missing columns: {', '.join(missing)}")
    
    # Step 4: Convert to list of dicts
    records = df.to_dict(orient="records")
    
    return records, warnings
