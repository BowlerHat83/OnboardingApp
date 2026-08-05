from typing import Dict, Any


class Topic7Scorer:
    """
    Evaluates Local SEO & Google Business Profile (Topic 7) metrics.
    Pure scoring logic—no service dependency.
    """

    def __init__(self, telemetry_data: Dict[str, Any]):
        self.data = telemetry_data or {}

    def evaluate(self) -> Dict[str, Any]:
        """Calculates score and generates actionable local SEO recommendations."""
        score = 0
        max_score = 100
        findings = []

        # 1. Map Pack Rank Scoring (Up to 30 pts)
        map_rank = self.data.get("map_pack_rank")
        if map_rank is not None:
            if map_rank <= 3:
                score += 30
            elif map_rank <= 10:
                score += 15
                findings.append("Business ranks outside Top 3 Local Map Pack.")
            else:
                findings.append("Business is not ranking in top 10 for local map searches.")
        else:
            findings.append("Map pack rank data missing.")

        # 2. Ratings & Review Count (Up to 25 pts)
        rating = self.data.get("average_rating", 0.0)
        reviews = self.data.get("review_count", 0)

        if rating >= 4.5:
            score += 15
        elif rating >= 4.0:
            score += 10
        else:
            findings.append(f"Average rating of {rating} is below target (4.5+).")

        if reviews >= 50:
            score += 10
        elif reviews >= 10:
            score += 5
        else:
            findings.append("Review count is low (fewer than 10 reviews).")

        # 3. NAP Consistency (Up to 20 pts)
        nap_consistency = self.data.get("nap_consistency_pct", 0.0)
        if nap_consistency >= 90.0:
            score += 20
        elif nap_consistency >= 70.0:
            score += 10
            findings.append(f"NAP consistency at {nap_consistency}%—minor discrepancies found.")
        else:
            findings.append(f"Low NAP consistency ({nap_consistency}%). Fix local citations.")

        # 4. GBP Verification & Setup (Up to 25 pts)
        if self.data.get("gbp_verified", False):
            score += 10
        else:
            findings.append("Google Business Profile is unverified.")

        if self.data.get("has_primary_category", False):
            score += 5

        photos = self.data.get("gbp_photos_count", 0)
        if photos >= 10:
            score += 10
        elif photos > 0:
            score += 5
            findings.append("Fewer than 10 photos on GBP profile.")

        final_score = min(score, max_score)

        return {
            "topic": "Topic 7 - Local SEO & GBP",
            "score": final_score,
            "max_score": max_score,
            "status": "PASS" if final_score >= 70 else "NEEDS_IMPROVEMENT",
            "findings": findings,
        }