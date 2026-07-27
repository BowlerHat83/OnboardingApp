from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class SemrushParser(BaseCSVParser):
    """Parses Semrush Domain Overview and Keyword CSV exports for Organic Search & Competitor Data."""

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
                "competitors": [],  # Extracted organic competitors
                "keyword_gap_count": 0,  # Missing keywords competitors rank for
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse CSV file."
            return result

        try:
            # 1. Standard Keyword & Traffic Analysis
            if "keyword" in self.df.columns:
                result["metrics"]["total_keywords"] = len(self.df)

                # Page 2 Opportunities (Positions 11 to 20)
                if "position" in self.df.columns:
                    positions = pd.to_numeric(
                        self.df["position"], errors="coerce"
                    )
                    page_2_mask = (positions >= 11) & (positions <= 20)
                    result["metrics"]["page_2_opportunities"] = int(
                        page_2_mask.sum()
                    )

                # Top Keywords
                vol_col = (
                    "search volume"
                    if "search volume" in self.df.columns
                    else None
                )
                if vol_col:
                    top_df = self.df.sort_values(
                        by=vol_col, ascending=False
                    ).head(5)
                    result["metrics"]["top_keywords"] = top_df[
                        "keyword"
                    ].tolist()
                else:
                    result["metrics"]["top_keywords"] = (
                        self.df["keyword"].head(5).tolist()
                    )

            # 2. Competitor Domain & Organic Gap Extraction
            competitor_cols = [
                c
                for c in self.df.columns
                if "competitor" in c or "domain" in c or "overlap" in c
            ]
            if competitor_cols:
                comp_col = competitor_cols[0]
                unique_comps = (
                    self.df[comp_col]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .unique()
                    .tolist()
                )
                result["metrics"]["competitors"] = unique_comps[:5]

            # Estimate Keyword Gaps (e.g., Competitor rank <= 10, Client rank > 20 or NaN)
            if "competitor position" in self.df.columns and "position" in self.df.columns:
                comp_pos = pd.to_numeric(self.df["competitor position"], errors="coerce")
                client_pos = pd.to_numeric(self.df["position"], errors="coerce")
                gap_mask = (comp_pos <= 10) & ((client_pos > 20) | (client_pos.isna()))
                result["metrics"]["keyword_gap_count"] = int(gap_mask.sum())

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"Semrush Parsing Error: {str(e)}"

        return result


if __name__ == "__main__":
    print("--- Extended Semrush Parser Loaded ---")
