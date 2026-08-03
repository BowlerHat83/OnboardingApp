import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def parse_screaming_frog_csv(csv_path: str) -> Dict[str, Any]:
    """
    Parses a Screaming Frog 'Internal:All' CSV export file.
    Cleans column headers, extracts aggregate health metrics, 
    and handles NaN/Inf values for clean JSON output.
    """
    try:
        # Read CSV with flexible encoding handling
        try:
            df = pd.read_csv(csv_path, low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="latin1", low_memory=False)

        if df.empty:
            logger.warning(f"[Screaming Frog Parser] File {csv_path} is empty.")
            return {"summary": {}, "rows_count": 0, "sample_data": []}

        # Normalize column headers (lowercase, underscores, strip special chars)
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("-", "_", regex=False)
            .str.replace("/", "_", regex=False)
        )

        total_rows = len(df)

        # Helper getters to accommodate slight header variations across SF versions
        def get_col(candidates):
            for col in candidates:
                if col in df.columns:
                    return df[col]
            return pd.Series(dtype=object)

        status_codes = get_col(["status_code"])
        indexability = get_col(["indexability"])
        titles = get_col(["title_1", "title"])
        meta_desc = get_col(["meta_description_1", "meta_description"])
        h1s = get_col(["h1_1", "h1"])
        canonical_link = get_col(["canonical_link_element_1", "canonical"])

        # Calculate high-level audit aggregates
        summary = {
            "total_urls_crawled": total_rows,
            "status_code_breakdown": (
                status_codes.value_counts().dropna().to_dict()
                if not status_codes.empty else {}
            ),
            "indexability_breakdown": (
                indexability.value_counts().dropna().to_dict()
                if not indexability.empty else {}
            ),
            "issues_summary": {
                "missing_title": int(titles.isna().sum()) if not titles.empty else 0,
                "missing_meta_description": int(meta_desc.isna().sum()) if not meta_desc.empty else 0,
                "missing_h1": int(h1s.isna().sum()) if not h1s.empty else 0,
                "missing_canonical": int(canonical_link.isna().sum()) if not canonical_link.empty else 0,
                "non_200_status": int((status_codes != 200).sum()) if not status_codes.empty else 0,
            }
        }

        # Replace NaN/Inf values with None for JSON serialization safety
        df_cleaned = df.replace({np.nan: None, np.inf: None, -np.inf: None})

        return {
            "summary": summary,
            "rows_count": total_rows,
            "records": df_cleaned.to_dict(orient="records")
        }

    except Exception as e:
        logger.error(f"[Screaming Frog Parser] Error processing {csv_path}: {str(e)}")
        return {
            "error": f"Failed to parse Screaming Frog CSV: {str(e)}",
            "summary": {},
            "records": []
        }