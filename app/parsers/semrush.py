import pandas as pd
import io
from typing import Dict, Any, List

def parse_semrush_excel(file_bytes: bytes) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parses an Excel (.xlsx / .xls) or CSV file containing SEO keyword data.
    Standardizes column headers and strips unneeded metadata.
    """
    results = {}
    
    # Try reading as Excel first
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            df = _clean_and_normalize_df(df)
            results[sheet_name] = df.to_dict(orient="records")
        return results
    except Exception:
        pass

    # Fallback to CSV
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        df = _clean_and_normalize_df(df)
        results["default"] = df.to_dict(orient="records")
        return results
    except Exception as e:
        raise ValueError(f"Unable to parse file as Excel or CSV: {str(e)}")


def _clean_and_normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Flexible column mapper for Ahrefs, Semrush, and GSC exports."""
    column_mapping = {}
    
    for col in df.columns:
        col_clean = str(col).strip()
        col_lower = col_clean.lower()

        if col_lower in ['keyword', 'query', 'search term']:
            column_mapping[col] = 'keyword'
        elif col_lower in ['current position', 'position', 'rank', 'google position', 'pos']:
            column_mapping[col] = 'position'
        elif col_lower in ['search volume', 'volume', 'global volume', 'vol']:
            column_mapping[col] = 'search_volume'
        elif col_lower in ['keyword difficulty', 'kd', 'difficulty', 'keyword difficulty index']:
            column_mapping[col] = 'keyword_difficulty'
        elif col_lower in ['current url', 'url', 'landing page', 'page']:
            column_mapping[col] = 'url'

    df = df.rename(columns=column_mapping)

    # Retain ONLY target columns
    target_cols = ['keyword', 'position', 'search_volume', 'keyword_difficulty', 'url']
    for col in target_cols:
        if col not in df.columns:
            df[col] = 0 if col != 'url' else ''

    return df[target_cols]