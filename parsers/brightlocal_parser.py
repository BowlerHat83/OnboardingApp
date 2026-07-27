from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class BrightLocalParser(BaseCSVParser):
    """Parses BrightLocal Roll-Up CSV exports for Local SEO, Map Pack, and Citation data."""

    def parse(self) -> Dict[str, Any]:
        result = {
            "vendor": "BrightLocal",
            "service_area": "Local SEO",
            "metrics": {
                "gbp_health_score": 0,
                "avg_map_pack_rank": None,
                "total_citations": 0,
                "nap_consistency_score": 0,
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse BrightLocal CSV file."
            return result

        try:
            rank_col = next(
                (
                    c
                    for c in self.df.columns
                    if "rank" in c or "position" in c or "map" in c
                ),
                None,
            )
            citation_col = next(
                (
                    c
                    for c in self.df.columns
                    if "citation" in c or "nap" in c or "directory" in c
                ),
                None,
            )
            score_col = next(
                (
                    c
                    for c in self.df.columns
                    if "score" in c or "health" in c or "gbp" in c
                ),
                None,
            )

            if rank_col:
                ranks = pd.to_numeric(self.df[rank_col], errors="coerce")
                if not ranks.isna().all():
                    result["metrics"]["avg_map_pack_rank"] = round(
                        float(ranks.mean()), 1
                    )

            if citation_col:
                citations = pd.to_numeric(self.df[citation_col], errors="coerce")
                result["metrics"]["total_citations"] = int(
                    citations.fillna(0).sum() if not citations.isna().all() else len(self.df)
                )

            if score_col:
                scores = pd.to_numeric(self.df[score_col], errors="coerce")
                if not scores.isna().all():
                    result["metrics"]["gbp_health_score"] = int(scores.mean())

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"BrightLocal Parsing Error: {str(e)}"

        return result


if __name__ == "__main__":
    print("--- BrightLocal Parser Loaded ---")
