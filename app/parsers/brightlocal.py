import csv
import io
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

class BrightLocalCSVParser:
    """
    Parses BrightLocal export CSVs (Local Audit / Citation Tracker / Rank Tracker)
    into standard dictionary format for Topic7Scorer.
    """

    @staticmethod
    def parse_csv_content(csv_input: Union[str, bytes]) -> Dict[str, Any]:
        """
        Parses raw CSV string or bytes content into Topic 7 schema.
        """
        if isinstance(csv_input, bytes):
            csv_input = csv_input.decode("utf-8", errors="ignore")

        reader = csv.DictReader(io.StringIO(csv_input))
        
        # Default fallback structure
        parsed_data = {
            "map_pack_rank": 10,
            "average_rating": 0.0,
            "review_count": 0,
            "nap_consistency_pct": 0.0,
            "gbp_verified": True,
            "gbp_photos_count": 0,
            "has_primary_category": True,
            "citations_found_count": 0
        }

        row_count = 0
        consistent_citations = 0

        for row in reader:
            row_count += 1
            # Standardize key names (lowercased and stripped)
            clean_row = {str(k).lower().strip(): str(v).strip() for k, v in row.items() if k}

            # 1. Extract Map Pack / Organic Local Rank
            if "map_rank" in clean_row or "google_places_rank" in clean_row:
                rank_val = clean_row.get("map_rank") or clean_row.get("google_places_rank")
                if rank_val and rank_val.isdigit():
                    parsed_data["map_pack_rank"] = min(parsed_data["map_pack_rank"], int(rank_val))

            # 2. Extract Reviews & Rating
            if "rating" in clean_row or "avg_rating" in clean_row:
                r_val = clean_row.get("rating") or clean_row.get("avg_rating")
                try:
                    parsed_data["average_rating"] = float(r_val)
                except ValueError:
                    pass

            if "reviews_count" in clean_row or "total_reviews" in clean_row:
                rev_val = clean_row.get("reviews_count") or clean_row.get("total_reviews")
                if rev_val and rev_val.isdigit():
                    parsed_data["review_count"] = int(rev_val)

            # 3. Citation & NAP Consistency Check
            if "nap_status" in clean_row or "consistency" in clean_row:
                status = (clean_row.get("nap_status") or clean_row.get("consistency")).lower()
                if "match" in status or "correct" in status or "100" in status:
                    consistent_citations += 1

        if row_count > 0:
            parsed_data["citations_found_count"] = row_count
            parsed_data["nap_consistency_pct"] = round((consistent_citations / row_count) * 100.0, 2)

        return parsed_data