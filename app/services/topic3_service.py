import pandas as pd
import numpy as np
from typing import Dict, Any, List


class Topic3Service:
    """
    Service for processing Keyword, Traffic, and Search Visibility Data.
    Calculates summary metrics, distributions, and top keyword rankings.
    """

    def __init__(self, raw_data: List[Dict[str, Any]]):
        self.df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

    def process_intelligence(self) -> Dict[str, Any]:
        if self.df.empty:
            return {
                "status": "warning",
                "message": "No keyword data available to analyze.",
                "summary": {},
                "top_keywords": [],
            }

        # 1. Sanitize numeric columns
        for col in ["position", "search_volume", "keyword_difficulty"]:
            if col in self.df.columns:
                self.df[col] = (
                    pd.to_numeric(self.df[col], errors="coerce").fillna(0)
                )
            else:
                self.df[col] = 0

        self.df["url"] = self.df["url"].fillna("").astype(str)

        # 2. Filter active rankings (position > 0) for position calculations
        active_rankings = self.df[self.df["position"] > 0]

        # 3. Calculate Summary Metrics
        total_keywords = int(len(self.df))
        total_volume = int(self.df["search_volume"].sum())
        avg_position = (
            float(active_rankings["position"].mean())
            if not active_rankings.empty
            else 0.0
        )
        avg_kd = (
            float(
                self.df[self.df["keyword_difficulty"] > 0][
                    "keyword_difficulty"
                ].mean()
            )
            if (self.df["keyword_difficulty"] > 0).any()
            else 0.0
        )

        pos = active_rankings["position"]
        ranking_brackets = {
            "top_3": int((pos.between(1, 3)).sum()),
            "positions_4_10": int((pos.between(4, 10)).sum()),
            "page_2": int((pos.between(11, 20)).sum()),
            "beyond_page_2": int((pos > 20).sum()),
        }

        # 4. Extract Top 10 Keywords by Search Volume
        top_keywords = (
            self.df.sort_values(by=["search_volume"], ascending=False)
            .head(10)
            .to_dict(orient="records")
        )

        clean_top_keywords = self._sanitize_records(top_keywords)

        return {
            "status": "success",
            "summary": {
                "total_keywords": total_keywords,
                "total_search_volume": total_volume,
                "average_position": round(avg_position, 1),
                "average_difficulty": round(avg_kd, 1),
                "rankings_distribution": ranking_brackets,
            },
            "top_keywords": clean_top_keywords,
        }

    def _sanitize_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensures all values are native Python types for JSON serialization."""
        clean_list = []
        for row in records:
            clean_row = {}
            for k, v in row.items():
                if k == "position":
                    clean_row[k] = int(v)
                elif isinstance(v, (np.integer, int)):
                    clean_row[k] = int(v)
                elif isinstance(v, (np.floating, float)):
                    clean_row[k] = float(v) if not np.isnan(v) else 0.0
                else:
                    clean_row[k] = str(v) if pd.notna(v) else ""
            clean_list.append(clean_row)
        return clean_list