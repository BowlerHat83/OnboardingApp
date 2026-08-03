import io
import json
import re
import pandas as pd
from typing import Dict, Any, List


def parse_spyfu_export(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Parses SpyFu PPC/Domain exports (CSV, XLSX, or JSON).
    Cleans raw strings (e.g. '$12.50', '85%') and standardizes headers.
    """
    file_lower = filename.lower()
    df = pd.DataFrame()

    # 1. Try JSON
    if file_lower.endswith(".json") or file_bytes.strip().startswith(b"{"):
        try:
            data = json.loads(file_bytes.decode("utf-8"))
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                records = (
                    data.get("results")
                    or data.get("keywords")
                    or data.get("most_successful_keywords")
                    or [data]
                )
                df = pd.DataFrame(records)
        except Exception:
            pass

    # 2. Try Excel
    if df.empty and (file_lower.endswith(".xlsx") or file_lower.endswith(".xls")):
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
        except Exception:
            pass

    # 3. Fallback to CSV
    if df.empty:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Unable to parse SpyFu file as CSV, XLSX, or JSON: {str(e)}")

    return _normalize_and_clean_df(df)


def _clean_numeric(val: Any) -> float:
    """Helper to convert '$1,250.50' or '15.5%' into float."""
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).strip()
    # Strip currency symbols, commas, percentages, and trailing units
    cleaned = re.sub(r"[^\d.-]", "", val_str)
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def _normalize_and_clean_df(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Maps SpyFu column headers to standard schema and cleans row data."""
    df.columns = [str(col).strip().lower() for col in df.columns]
    column_mapping = {}

    for col in df.columns:
        # Keyword mapping
        if col in ['keyword', 'ppc keyword', 'term', 'search term', 'paid keyword']:
            column_mapping[col] = 'keyword'
        # Search Volume
        elif col in ['search volume', 'monthly searches', 'volume', 'searchvolume', 'exact local monthly searches']:
            column_mapping[col] = 'search_volume'
        # Cost Per Click
        elif col in ['cpc', 'cost per click', 'avg cpc', 'broadcostperclick', 'cost_per_click', 'average cpc']:
            column_mapping[col] = 'cpc'
        # Monthly Spend
        elif col in ['monthly cost', 'est monthly spend', 'ad spend', 'monthly_spend', 'estimated monthly cost']:
            column_mapping[col] = 'monthly_spend'
        # Top Competitors
        elif col in ['paid competitor', 'competitor', 'top paid competitor', 'top_competitor', 'domain']:
            column_mapping[col] = 'top_competitor'
        # Impression / Market Share
        elif col in ['impression share', 'ppc impression share', 'share of voice', 'market share']:
            column_mapping[col] = 'impression_share'

    df = df.rename(columns=column_mapping)

    # Ensure essential columns exist
    for required_col in ['keyword', 'search_volume', 'cpc', 'monthly_spend', 'top_competitor', 'impression_share']:
        if required_col not in df.columns:
            df[required_col] = 0.0 if required_col in ['search_volume', 'cpc', 'monthly_spend', 'impression_share'] else ''

    # Clean numeric columns
    for num_col in ['search_volume', 'cpc', 'monthly_spend', 'impression_share']:
        df[num_col] = df[num_col].apply(_clean_numeric)

    df['keyword'] = df['keyword'].fillna('').astype(str).str.strip()
    df['top_competitor'] = df['top_competitor'].fillna('').astype(str).str.strip()

    return df[['keyword', 'search_volume', 'cpc', 'monthly_spend', 'top_competitor', 'impression_share']].to_dict(orient="records")