import pandas as pd
from typing import Dict, Any

class ScreamingFrogParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> Dict[str, Any]:
        """Parses Screaming Frog crawl export CSV and extracts technical SEO metrics."""
        try:
            df = pd.read_csv(self.file_path)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to read Screaming Frog CSV: {str(e)}",
                "metrics": {
                    "total_issues": 0,
                    "broken_links_404": 0,
                    "high_priority_errors": 0,
                    "non_indexable_url_count": 0,
                    "missing_titles": 0,
                    "missing_h1s": 0,
                }
            }

        # Normalize column headers
        df.columns = [c.strip() for c in df.columns]
        total_urls = len(df)

        # 1. File Type Breakdown
        file_type_breakdown = {
            "HTML": 0, "JavaScript": 0, "CSS": 0, 
            "Images": 0, "PDF": 0, "Flash": 0, "Other": 0
        }

        content_type_col = next((c for c in ['Content Type', 'Content', 'Type'] if c in df.columns), None)
        if content_type_col:
            for val in df[content_type_col].dropna().astype(str):
                val_lower = val.lower()
                if 'html' in val_lower:
                    file_type_breakdown["HTML"] += 1
                elif 'javascript' in val_lower or 'js' in val_lower:
                    file_type_breakdown["JavaScript"] += 1
                elif 'css' in val_lower:
                    file_type_breakdown["CSS"] += 1
                elif any(ext in val_lower for ext in ['image', 'png', 'jpeg', 'jpg', 'webp', 'gif']):
                    file_type_breakdown["Images"] += 1
                elif 'pdf' in val_lower:
                    file_type_breakdown["PDF"] += 1
                elif 'flash' in val_lower or 'swf' in val_lower:
                    file_type_breakdown["Flash"] += 1
                else:
                    file_type_breakdown["Other"] += 1

        # 2. Status Codes & 4xx Broken Links
        status_4xx, status_5xx = 0, 0
        if 'Status Code' in df.columns:
            status_codes = pd.to_numeric(df['Status Code'], errors='coerce')
            status_4xx = int(((status_codes >= 400) & (status_codes < 500)).sum())
            status_5xx = int(((status_codes >= 500) & (status_codes < 600)).sum())

        # 3. Non-Indexable URLs
        non_indexable = 0
        if 'Indexability' in df.columns:
            non_indexable = int((df['Indexability'].astype(str).str.lower() == 'non-indexable').sum())

        # 4. Missing Title Tags
        missing_titles = 0
        title_col = next((c for c in ['Title 1', 'Title', 'Page Title'] if c in df.columns), None)
        if title_col:
            missing_titles = int(df[title_col].isna().sum() + (df[title_col].astype(str).str.strip() == '').sum())

        # 5. Missing H1 Headers
        missing_h1s = 0
        h1_col = next((c for c in ['H1-1', 'H1 1', 'H1'] if c in df.columns), None)
        if h1_col:
            missing_h1s = int(df[h1_col].isna().sum() + (df[h1_col].astype(str).str.strip() == '').sum())

        # 6. Meta Descriptions
        missing_meta = 0
        meta_col = next((c for c in ['Meta Description 1', 'Meta Description', 'Description'] if c in df.columns), None)
        if meta_col:
            missing_meta = int(df[meta_col].isna().sum() + (df[meta_col].astype(str).str.strip() == '').sum())

        # Calculate high-priority issues count for normalizer
        total_issues = status_4xx + status_5xx + missing_titles + missing_h1s

        return {
            "status": "success",
            "metrics": {
                "total_urls": total_urls,
                "file_type_breakdown": file_type_breakdown,
                "total_issues": total_issues,
                "broken_links_404": status_4xx,
                "high_priority_errors": status_5xx,
                "non_indexable_url_count": non_indexable,
                "missing_titles": missing_titles,
                "missing_h1s": missing_h1s,
                "missing_meta_descriptions": missing_meta
            }
        }
