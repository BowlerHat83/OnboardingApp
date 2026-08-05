from typing import Dict, Any, List
from app.scoring.base_scorer import BaseScorer

class Topic3Scorer:
    """
    Scoring Engine for Topic 3: Organic Search Visibility & Keyword Health.
    
    Weights:
      • Rank Distribution & SERP Positions: 40%
      • Search Intent & Non-Branded Share: 25%
      • Domain Authority & Trust:           20%
      • Backlink & Referring Domain Profile:15%
    """

    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data or {}

    def score_rank_distribution(self) -> Dict[str, Any]:
        """Calculates Rank Distribution sub-score (40% weight)."""
        keywords = self.raw_data.get("keywords", []) or self.raw_data.get("rankings", [])
        
        if not keywords:
            # Fallback if summarized counts provided directly
            top3 = int(self.raw_data.get("top_3_count", 0))
            top10 = int(self.raw_data.get("top_10_count", 0))
            top20 = int(self.raw_data.get("top_20_count", 0))
            total = top3 + top10 + top20 or 1
            
            distribution_score = min(100.0, ((top3 * 100.0) + (top10 * 75.0) + (top20 * 40.0)) / total)
            return {
                "score": round(distribution_score, 2),
                "details": {"top_3": top3, "top_10": top10, "top_20": top20}
            }

        scores = []
        for kw in keywords:
            pos = int(kw.get("position", 100))
            if pos <= 3: scores.append(100.0)
            elif pos <= 10: scores.append(75.0)
            elif pos <= 20: scores.append(40.0)
            elif pos <= 50: scores.append(15.0)
            else: scores.append(0.0)

        total = round(sum(scores) / len(scores), 2) if scores else 0.0
        return {
            "score": total,
            "details": {"tracked_keywords_count": len(keywords), "average_position_score": total}
        }

    def score_search_intent(self) -> Dict[str, Any]:
        """Calculates Non-Branded & Intent match sub-score (25% weight)."""
        non_branded_count = int(self.raw_data.get("non_branded_keywords_count", 5))
        intent_match_pct = float(self.raw_data.get("intent_match_pct", 80.0))

        nb_score = BaseScorer.score_ranged(non_branded_count, best=50, worst=0)
        intent_score = BaseScorer.score_ranged(intent_match_pct, best=100.0, worst=30.0)

        total = round((nb_score * 0.5) + (intent_score * 0.5), 2)
        return {
            "score": total,
            "details": {
                "non_branded_count": non_branded_count,
                "intent_match_pct": intent_match_pct
            }
        }

    def score_domain_authority(self) -> Dict[str, Any]:
        """Calculates Domain Authority sub-score (20% weight)."""
        da = float(self.raw_data.get("domain_authority", self.raw_data.get("domain_rating", 35)))
        da_score = BaseScorer.score_ranged(da, best=60.0, worst=10.0)

        return {
            "score": da_score,
            "details": {"domain_authority": da}
        }

    def score_backlink_profile(self) -> Dict[str, Any]:
        """Calculates Backlinks & Referring Domains sub-score (15% weight)."""
        referring_domains = int(self.raw_data.get("referring_domains_count", 50))
        dofollow_pct = float(self.raw_data.get("dofollow_pct", 75.0))

        rd_score = BaseScorer.score_ranged(referring_domains, best=250, worst=5)
        df_score = BaseScorer.score_ranged(dofollow_pct, best=80.0, worst=20.0)

        total = round((rd_score * 0.6) + (df_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "referring_domains": referring_domains,
                "dofollow_pct": dofollow_pct
            }
        }

    def evaluate(self) -> Dict[str, Any]:
        """Runs the complete Topic 3 evaluation pipeline."""
        rank_dist = self.score_rank_distribution()
        intent = self.score_search_intent()
        da = self.score_domain_authority()
        backlinks = self.score_backlink_profile()

        final_score = round(
            (rank_dist["score"] * 0.40) +
            (intent["score"] * 0.25) +
            (da["score"] * 0.20) +
            (backlinks["score"] * 0.15),
            2
        )

        return {
            "topic": "Topic 3: Organic Search Visibility",
            "overall_score": final_score,
            "grade": BaseScorer.calculate_grade(final_score),
            "breakdown": {
                "rank_distribution": rank_dist,
                "search_intent": intent,
                "domain_authority": da,
                "backlink_profile": backlinks
            }
        }