"""
parsers/semrush_parser.py - Processes raw SEMrush export CSVs.
"""

import csv
from typing import Dict, Any, List


def parse_semrush_csv(file_path: str) -> Dict[str, Any]:
    """
    Parses a SEMrush organic CSV export and returns structured keyword distribution,
    Page 1 & 2 keyword details (volume >= 30), authority, traffic, and historical data.
    """
    total_keywords = 0
    serp_distribution = {
        "page_1_top_3": 0,    # Pos 1-3
        "page_1_rest": 0,     # Pos 4-10
        "page_2": 0,          # Pos 11-20
        "page_3": 0,          # Pos 21-30
        "page_4_plus": 0      # Pos 31+
    }
    
    page_1_keywords = []
    page_2_keywords = []

    # Default metadata placeholders (overridden if present in CSV header/meta rows)
    domain_authority = 0
    est_monthly_traffic = 0
    historical_traffic = []

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Handle flexible header naming from SEMrush exports
                keyword = row.get("Keyword", row.get("keyword", "")).strip()
                pos_str = row.get("Position", row.get("position", "0"))
                vol_str = row.get("Search Volume", row.get("volume", row.get("Search volume", "0")))
                url = row.get("URL", row.get("url", "")).strip()

                if not keyword:
                    continue

                total_keywords += 1

                try:
                    position = int(pos_str)
                except ValueError:
                    position = 999

                try:
                    volume = int(vol_str.replace(",", ""))
                except ValueError:
                    volume = 0

                kw_item = {
                    "keyword": keyword,
                    "position": position,
                    "search_volume": volume,
                    "url": url
                }

                # SERP Distribution & Page 1/2 Preservation
                if 1 <= position <= 3:
                    serp_distribution["page_1_top_3"] += 1
                    if volume >= 30:
                        page_1_keywords.append(kw_item)
                elif 4 <= position <= 10:
                    serp_distribution["page_1_rest"] += 1
                    if volume >= 30:
                        page_1_keywords.append(kw_item)
                elif 11 <= position <= 20:
                    serp_distribution["page_2"] += 1
                    if volume >= 30:
                        page_2_keywords.append(kw_item)
                elif 21 <= position <= 30:
                    serp_distribution["page_3"] += 1
                else:
                    serp_distribution["page_4_plus"] += 1

                # Capture domain-level metrics if exported in the row
                if "Authority Score" in row and row["Authority Score"]:
                    try:
                        domain_authority = int(row["Authority Score"])
                    except ValueError:
                        pass
                if "Traffic" in row and row["Traffic"]:
                    try:
                        est_monthly_traffic = int(row["Traffic"].replace(",", ""))
                    except ValueError:
                        pass

    except FileNotFoundError:
        pass  # File missing handled gracefully

    return {
        "metrics": {
            "total_keywords": total_keywords,
            "domain_authority": domain_authority,
            "est_monthly_traffic": est_monthly_traffic,
            "serp_distribution": serp_distribution
        },
        "page_1_keywords": page_1_keywords,
        "page_2_keywords": page_2_keywords,
        "historical_traffic": historical_traffic
    }
