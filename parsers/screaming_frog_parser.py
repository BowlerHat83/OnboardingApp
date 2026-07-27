from typing import Any, Dict
import pandas as pd
from parsers.base_parser import BaseCSVParser


class ScreamingFrogParser(BaseCSVParser):
    """Parses Screaming Frog exports for Technical SEO, Indexability, and Canonical Tag Errors."""

    def parse(self) -> Dict[str, Any]:
        result = {
            "vendor": "Screaming Frog",
            "service_area": "Technical SEO",
            "metrics": {
                "total_issues": 0,
                "high_priority_errors": 0,
                "missing_titles": 0,
                "missing_h1s": 0,
                "broken_links_404": 0,
                "missing_canonical_tags": 0,  # Canonical tag gaps
                "non_indexable_url_count": 0,  # Noindex or canonicalized out
            },
            "status": "error",
        }

        if not self.load_csv():
            result["error"] = "Failed to parse Screaming Frog CSV file."
            return result

        try:
            name_col = next(
                (c for c in self.df.columns if "issue name" in c or "issue" in c),
                None,
            )
            type_col = next((c for c in self.df.columns if "type" in c), None)
            total_col = next(
                (c for c in self.df.columns if "total" in c or "count" in c),
                None,
            )

            # 1. Process Issues Summary Export
            if name_col and total_col:
                result["metrics"]["total_issues"] = int(
                    pd.to_numeric(self.df[total_col], errors="coerce")
                    .fillna(0)
                    .sum()
                )

                for _, row in self.df.iterrows():
                    issue_name = str(row[name_col]).lower()
                    count = (
                        int(row[total_col])
                        if pd.notnull(row[total_col])
                        else 0
                    )

                    if "title" in issue_name and "missing" in issue_name:
                        result["metrics"]["missing_titles"] += count
                    elif "h1" in issue_name and "missing" in issue_name:
                        result["metrics"]["missing_h1s"] += count
                    elif (
                        "404" in issue_name
                        or "client error" in issue_name
                        or "broken" in issue_name
                    ):
                        result["metrics"]["broken_links_404"] += count
                    elif "canonical" in issue_name and "missing" in issue_name:
                        result["metrics"]["missing_canonical_tags"] += count
                    elif "noindex" in issue_name or "non-indexable" in issue_name:
                        result["metrics"]["non_indexable_url_count"] += count

            # 2. Count High-Priority Errors
            if type_col:
                errors_df = self.df[
                    self.df[type_col].astype(str).str.lower() == "error"
                ]
                result["metrics"]["high_priority_errors"] = len(errors_df)

            result["status"] = "success"

        except Exception as e:
            result["error"] = f"Screaming Frog Parsing Error: {str(e)}"

        return result


if __name__ == "__main__":
    print("--- Extended Screaming Frog Parser Loaded ---")
