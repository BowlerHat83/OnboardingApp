import pandas as pd
import io
import json
from typing import Dict, Any, List

def parse_waikay_export(file_bytes: bytes, filename: str = "") -> List[Dict[str, Any]]:
    """
    Parses a Waikay export file (CSV or JSON).
    Standardizes header fields across Waikay visibility reports.
    """
    # 1. Try parsing JSON export
    if filename.endswith(".json") or file_bytes.strip().startswith(b"{"):
        try:
            data = json.loads(file_bytes.decode("utf-8"))
            if isinstance(data, dict) and "rankings" in data.get("data", {}):
                return _normalize_waikay_api_json(data["data"]["rankings"])
            elif isinstance(data, list):
                return _normalize_df(pd.DataFrame(data))
        except Exception:
            pass

    # 2. Try parsing CSV export
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        return _normalize_df(df)
    except Exception as e:
        raise ValueError(f"Unable to parse Waikay file as CSV or JSON: {str(e)}")


def _normalize_df(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Flexibly maps Waikay column headers."""
    df.columns = [str(col).strip() for col in df.columns]
    column_mapping = {}

    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['prompt', 'keyword', 'prompt_text', 'query', 'prompt name']:
            column_mapping[col] = 'keyword'
        elif col_lower in ['ai_triggered', 'ai triggered', 'triggered', 'visibility', 'is_triggered']:
            column_mapping[col] = 'ai_triggered'
        elif col_lower in ['brand_mentioned', 'brand mentioned', 'mentioned', 'brand_occurrences']:
            column_mapping[col] = 'brand_mentioned'
        elif any(k in col_lower for k in ['chatgpt', 'gpt', 'model_3']):
            column_mapping[col] = 'chatgpt'
        elif any(k in col_lower for k in ['claude', 'model_5']):
            column_mapping[col] = 'claude'
        elif any(k in col_lower for k in ['sonar', 'perplexity', 'model_1']):
            column_mapping[col] = 'sonar'
        elif any(k in col_lower for k in ['gemini', 'model_100']):
            column_mapping[col] = 'gemini'
        elif col_lower in ['top_competitor', 'competitor', 'top competitor cited', 'competitor_cited']:
            column_mapping[col] = 'top_competitor'

    df = df.rename(columns=column_mapping)

    # Ensure required standard columns exist
    target_cols = ['keyword', 'ai_triggered', 'brand_mentioned', 'chatgpt', 'claude', 'sonar', 'gemini', 'top_competitor']
    for col in target_cols:
        if col not in df.columns:
            df[col] = False if col not in ['keyword', 'top_competitor'] else ''

    return df[target_cols].to_dict(orient="records")


def _normalize_waikay_api_json(rankings_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalizes native Waikay API JSON structure."""
    records = []
    for item in rankings_list:
        records.append({
            "keyword": item.get("prompt_name") or item.get("prompt") or "Unknown Prompt",
            "ai_triggered": bool(item.get("ai_triggered", True)),
            "brand_mentioned": bool(item.get("brand_mentioned") or item.get("occurrences", 0) > 0),
            "chatgpt": bool(item.get("models", {}).get("chatgpt", False)),
            "claude": bool(item.get("models", {}).get("claude", False)),
            "sonar": bool(item.get("models", {}).get("sonar", False)),
            "gemini": bool(item.get("models", {}).get("gemini", False)),
            "top_competitor": str(item.get("top_competitor", ""))
        })
    return records