from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class WaikayParser(BaseCSVParser):
    """Parses Waikay Generative Engine Optimization (GEO) CSV exports for AI Visibility data."""

    def parse(self) -> Dict[str, Any]:
        result = {
            "vendor": "Waikay",
            "service_area": "AI Visibility (GEO)",
            "metrics": {
                "brand_mention_rate": 0.0,
                "generative_visibility_score": 0,
                "top_ai_platforms": [],
                "sentiment_positive_pct": 0.0,
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse Waikay CSV file."
            return result

        try:
            # Detect typical Waikay export column headers
            platform_col = next(
                (
                    c
                    for c in self.df.columns
                    if "platform" in c or "engine" in c or "ai" in c
                ),
                None,
            )
            mention_col = next(
                (
                    c
                    for c in self.df.columns
                    if "mention" in c or "cited" in c or "visibility" in c
                ),
                None,
            )
            score_col = next(
                (
                    c
                    for c in self.df.columns
                    if "score" in c or "rate" in c or "index" in c
                ),
                None,
            )

            if platform_col:
                result["metrics"]["top_ai_platforms"] = (
                    self.df[platform_col].dropna().unique().tolist()[:5]
                )

            if mention_col:
                mentions = pd.to_numeric(self.df[mention_col], errors="coerce")
                if not mentions.isna().all():
                    result["metrics"]["brand_mention_rate"] = round(
                        float(mentions.mean()), 2
                    )

            if score_col:
                scores = pd.to_numeric(self.df[score_col], errors="coerce")
                if not scores.isna().all():
                    result["metrics"]["generative_visibility_score"] = int(
                        scores.mean()
                    )

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"Waikay Parsing Error: {str(e)}"

        return result


if __name__ == "__main__":
    print("--- Waikay Parser Loaded ---")
