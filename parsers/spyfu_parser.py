from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class SpyFuParser(BaseCSVParser):
    """Parses SpyFu PPC Keyword CSV exports for Paid Search Visibility data."""

    def parse(self) -> Dict[str, Any]:
        result = {
            "vendor": "SpyFu",
            "service_area": "Paid Search Visibility",
            "metrics": {
                "total_paid_keywords": 0,
                "est_monthly_spend": 0.0,
                "top_paid_keywords": [],
                "avg_cpc": 0.0,
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse SpyFu CSV file."
            return result

        try:
            # Check for keyword column variants
            kw_col = next(
                (c for c in self.df.columns if "keyword" in c), None
            )
            cpc_col = next((c for c in self.df.columns if "cpc" in c), None)
            cost_col = next(
                (c for c in self.df.columns if "cost" in c or "spend" in c),
                None,
            )

            if kw_col:
                result["metrics"]["total_paid_keywords"] = len(self.df)
                result["metrics"]["top_paid_keywords"] = (
                    self.df[kw_col].head(5).tolist()
                )

            if cpc_col:
                cpc_vals = pd.to_numeric(self.df[cpc_col], errors="coerce")
                result["metrics"]["avg_cpc"] = round(float(cpc_vals.mean()), 2)

            if cost_col:
                cost_vals = pd.to_numeric(self.df[cost_col], errors="coerce")
                result["metrics"]["est_monthly_spend"] = round(
                    float(cost_vals.sum()), 2
                )

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"SpyFu Parsing Error: {str(e)}"

        return result


if __name__ == "__main__":
    print("--- SpyFu Parser Loaded ---")
