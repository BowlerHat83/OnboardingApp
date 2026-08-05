from typing import Dict, Any, List
from app.scoring.base_scorer import BaseScorer

class Topic4Scorer:
    """
    Scoring Engine for Topic 4: AI & Generative Engine Visibility (GEO / LLM Share of Voice).
    
    Weights:
      • Brand Citation Share / Share of Voice:  40%
      • Recommendation Rank in LLM Prompts:    25%
      • Sentiment & Context Accuracy:          20%
      • Direct Citation / Footnote Hyperlink:   15%
    """

    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data or {}

    def score_citation_share(self) -> Dict[str, Any]:
        """Calculates Brand Citation Share of Voice sub-score (40% weight)."""
        prompt_results = self.raw_data.get("prompt_results", []) or self.raw_data.get("llm_mentions", [])
        
        if not prompt_results:
            # Fallback if pre-aggregated percentage is supplied
            mention_pct = float(self.raw_data.get("brand_mention_pct", 35.0))
            share_score = BaseScorer.score_ranged(mention_pct, best=60.0, worst=0.0)
            return {
                "score": share_score,
                "details": {"brand_mention_pct": mention_pct}
            }

        total_prompts = len(prompt_results)
        mentioned_prompts = sum(1 for p in prompt_results if p.get("brand_mentioned", False))
        mention_pct = (mentioned_prompts / total_prompts * 100.0) if total_prompts > 0 else 0.0

        share_score = BaseScorer.score_ranged(mention_pct, best=60.0, worst=0.0)
        return {
            "score": share_score,
            "details": {
                "total_prompts_tested": total_prompts,
                "mentioned_count": mentioned_prompts,
                "mention_pct": round(mention_pct, 2)
            }
        }

    def score_recommendation_rank(self) -> Dict[str, Any]:
        """Calculates Recommendation Rank in LLM outputs (25% weight)."""
        prompt_results = self.raw_data.get("prompt_results", []) or self.raw_data.get("llm_mentions", [])
        
        if not prompt_results:
            avg_rank = float(self.raw_data.get("average_llm_rank", 3.0))
            rank_score = BaseScorer.score_ranged(avg_rank, best=1.0, worst=6.0)
            return {
                "score": rank_score,
                "details": {"average_llm_rank": avg_rank}
            }

        rank_scores = []
        for p in prompt_results:
            rank = p.get("rank_position")
            if rank == 1: rank_scores.append(100.0)
            elif rank in [2, 3]: rank_scores.append(80.0)
            elif rank in [4, 5]: rank_scores.append(50.0)
            elif rank and rank > 5: rank_scores.append(25.0)
            elif p.get("brand_mentioned", False): rank_scores.append(40.0)
            else: rank_scores.append(0.0)

        total = round(sum(rank_scores) / len(rank_scores), 2) if rank_scores else 0.0
        return {
            "score": total,
            "details": {"average_rank_score": total}
        }

    def score_sentiment_accuracy(self) -> Dict[str, Any]:
        """Calculates Brand Sentiment & Context Accuracy sub-score (20% weight)."""
        sentiment = str(self.raw_data.get("sentiment", "positive")).lower()
        context_accurate = self.raw_data.get("context_accurate", True)

        if sentiment == "positive" and context_accurate:
            sentiment_score = 100.0
        elif sentiment == "neutral" or context_accurate:
            sentiment_score = 65.0
        else:
            sentiment_score = 20.0

        return {
            "score": sentiment_score,
            "details": {
                "sentiment": sentiment,
                "context_accurate": context_accurate
            }
        }

    def score_direct_citations(self) -> Dict[str, Any]:
        """Calculates Direct Hyperlink Inclusion sub-score (15% weight)."""
        has_direct_links = self.raw_data.get("has_direct_url_citations", True)
        citation_count = int(self.raw_data.get("footnote_citation_count", 3))

        link_score = BaseScorer.score_binary(has_direct_links)
        count_score = BaseScorer.score_ranged(citation_count, best=5, worst=0)

        total = round((link_score * 0.6) + (count_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "has_direct_url_citations": has_direct_links,
                "footnote_citation_count": citation_count
            }
        }

    def evaluate(self) -> Dict[str, Any]:
        """Runs the complete Topic 4 evaluation pipeline."""
        share = self.score_citation_share()
        rank = self.score_recommendation_rank()
        sentiment = self.score_sentiment_accuracy()
        citations = self.score_direct_citations()

        final_score = round(
            (share["score"] * 0.40) +
            (rank["score"] * 0.25) +
            (sentiment["score"] * 0.20) +
            (citations["score"] * 0.15),
            2
        )

        return {
            "topic": "Topic 4: AI & GEO Visibility",
            "overall_score": final_score,
            "grade": BaseScorer.calculate_grade(final_score),
            "breakdown": {
                "citation_share": share,
                "recommendation_rank": rank,
                "sentiment_accuracy": sentiment,
                "direct_citations": citations
            }
        }