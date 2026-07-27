from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class SpyFuParser(BaseCSVParser):
    """Parses SpyFu PPC CSV exports for Paid Search Visibility, Competitor PPC, and Historical Peak Performance."""

    def parse(self) -> Dict[str, Any]:
        result = {
            "vendor": "SpyFu",
            "service_area": "Paid Search Visibility",
            "metrics": {
                "total_paid_keywords": 0,
                "est_monthly_spend": 0.0,
                "top_paid_keywords": [],
                "avg_cpc": 0.0,
                "top_ppc_competitors": [],  # Top paid search competitors
                "historical_peak_period": None,  # Top performing historical month/year
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse SpyFu CSV file."
            return result

        try:
            kw_col = next((c for c in self.df.columns if "keyword" in c), None)
            cpc_col = next((c for c in self.df.columns if "cpc" in c), None)
            cost_col = next(
                (c for c in self.df.columns if "cost" in c or "spend" in c), None
            )
            comp_col = next(
                (c for c in self.df.columns if "competitor" in c or "domain" in c),
                None,
            )
            date_col = next(
                (c for c in self.df.columns if "date" in c or "month" in c or "period" in c),
                None,
            )

            # 1. Standard Paid Search Metrics
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

            # 2. PPC Competitor Extraction
            if comp_col:
                result["metrics"]["top_ppc_competitors"] = (
                    self.df[comp_col].dropna().astype(str).unique().tolist()[:5]
                )

            # 3. Historical Peak Performance Analysis
            if date_col and cost_col:
                self.df["numeric_cost"] = pd.to_numeric(
                    self.df[cost_col], errors="coerce"
                )
                peak_row = self.df.sort_values(
                    by="numeric_cost", ascending=False
                ).head(1)
                if not peak_row.empty and pd.notnull(peak_row[date_col].values[0]):
                    result["metrics"]["historical_peak_period"] = str(
                        peak_row[date_col].values[0]
                    )

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"SpyFu Parsing Error: {str(e)}"

        return result


if __name__ == "__main__":
    print("--- Extended SpyFu Parser Loaded ---")
