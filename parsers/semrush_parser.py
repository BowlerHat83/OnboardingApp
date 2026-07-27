from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class SemrushParser(BaseCSVParser):
    """Parses Semrush Domain Overview and Keyword CSV exports for Organic Search Data."""

    def parse(self) -> Dict[str, Any]:
        result = {
            "vendor": "Semrush",
            "service_area": "Organic Search Visibility",
            "metrics": {
                "total_keywords": 0,
                "organic_traffic_est": 0,
                "authority_score": None,
                "top_keywords": [],
                "page_2_opportunities": 0,  # Keywords on positions 11-20
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse CSV file."
            return result

        try:
            # Standard Semrush Keyword Export Column Names
            # Columns typically: 'Keyword', 'Position', 'Search Volume', 'Organic Traffic', etc.

            col_map = {col: col for col in self.df.columns}

            # Check if this is a Keyword export
            if "keyword" in self.df.columns:
                result["metrics"]["total_keywords"] = len(self.df)

                # Page 2 Opportunities (Positions 11 to 20)
                if "position" in self.df.columns:
                    # Clean position column to numeric
                    positions = pd.to_numeric(
                        self.df["position"], errors="coerce"
                    )
                    page_2_mask = (positions >= 11) & (positions <= 20)
                    result["metrics"]["page_2_opportunities"] = int(
                        page_2_mask.sum()
                    )

                # Extract Top 5 Keywords by Volume or Position
                kw_col = "keyword"
                vol_col = "search volume" if "search volume" in self.df.columns else None

                if vol_col:
                    top_df = self.df.sort_values(
                        by=vol_col, ascending=False
                    ).head(5)
                    result["metrics"]["top_keywords"] = top_df[
                        kw_col
                    ].tolist()
                else:
                    result["metrics"]["top_keywords"] = self.df[kw_col].head(5).tolist()

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"Semrush Parsing Error: {str(e)}"

        return result


# Quick Local Standalone Test Example
if __name__ == "__main__":
    import json

    print("--- Semrush Parser Loaded Successfully ---")
