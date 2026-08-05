from typing import Dict, Any
from app.scoring.base_scorer import BaseScorer

class Topic5Scorer:
    """
    Scoring Engine for Topic 5: Paid PPC & Search Advertising Intelligence.
    
    Weights:
      • Paid Search Visibility & Active Ads: 35%
      • Impression Share & Top Position:     25%
      • Ad Copy & Asset Extension Quality:  20%
      • Competitor Threat & Conquesting:    20%
    """

    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data or {}

    def score_ad_presence(self) -> Dict[str, Any]:
        """Calculates Paid Search Ad Presence sub-score (35% weight)."""
        active_ads = self.raw_data.get("active_ads_detected", True)
        ad_count = int(self.raw_data.get("active_ad_variations_count", 4))

        presence_score = BaseScorer.score_binary(active_ads)
        count_score = BaseScorer.score_ranged(ad_count, best=5, worst=0)

        total = round((presence_score * 0.7) + (count_score * 0.3), 2)
        return {
            "score": total,
            "details": {
                "active_ads_detected": active_ads,
                "active_ad_variations_count": ad_count
            }
        }

    def score_impression_share(self) -> Dict[str, Any]:
        """Calculates Impression Share & Top-of-Page sub-score (25% weight)."""
        top_page_pct = float(self.raw_data.get("top_of_page_rate", 75.0))
        imp_share_pct = float(self.raw_data.get("search_impression_share", 65.0))

        top_score = BaseScorer.score_ranged(top_page_pct, best=80.0, worst=20.0)
        imp_score = BaseScorer.score_ranged(imp_share_pct, best=80.0, worst=20.0)

        total = round((top_score * 0.5) + (imp_score * 0.5), 2)
        return {
            "score": total,
            "details": {
                "top_of_page_rate": top_page_pct,
                "search_impression_share": imp_share_pct
            }
        }

    def score_asset_extensions(self) -> Dict[str, Any]:
        """Calculates Ad Asset Extensions quality sub-score (20% weight)."""
        has_sitelinks = self.raw_data.get("has_sitelinks", True)
        has_callouts = self.raw_data.get("has_callouts", True)
        has_image_extensions = self.raw_data.get("has_image_extensions", True)

        sitelink_score = BaseScorer.score_binary(has_sitelinks)
        callout_score = BaseScorer.score_binary(has_callouts)
        image_score = BaseScorer.score_binary(has_image_extensions)

        total = round((sitelink_score * 0.4) + (callout_score * 0.3) + (image_score * 0.3), 2)
        return {
            "score": total,
            "details": {
                "has_sitelinks": has_sitelinks,
                "has_callouts": has_callouts,
                "has_image_extensions": has_image_extensions
            }
        }

    def score_competitor_threat(self) -> Dict[str, Any]:
        """Calculates Competitor Conquesting & Threat level sub-score (20% weight)."""
        threat_level = str(self.raw_data.get("competitor_threat_level", "low")).lower()
        bidding_competitors = int(self.raw_data.get("bidding_competitors_count", 1))

        if threat_level == "low":
            threat_score = 100.0
        elif threat_level == "medium":
            threat_score = 65.0
        else:
            threat_score = 25.0

        comp_score = BaseScorer.score_ranged(bidding_competitors, best=0, worst=5)

        total = round((threat_score * 0.6) + (comp_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "competitor_threat_level": threat_level,
                "bidding_competitors_count": bidding_competitors
            }
        }

    def evaluate(self) -> Dict[str, Any]:
        """Runs the complete Topic 5 evaluation pipeline."""
        presence = self.score_ad_presence()
        impression = self.score_impression_share()
        assets = self.score_asset_extensions()
        threat = self.score_competitor_threat()

        final_score = round(
            (presence["score"] * 0.35) +
            (impression["score"] * 0.25) +
            (assets["score"] * 0.20) +
            (threat["score"] * 0.20),
            2
        )

        return {
            "topic": "Topic 5: Paid PPC & Ad Intelligence",
            "overall_score": final_score,
            "grade": BaseScorer.calculate_grade(final_score),
            "breakdown": {
                "ad_presence": presence,
                "impression_share": impression,
                "asset_extensions": assets,
                "competitor_threat": threat
            }
        }