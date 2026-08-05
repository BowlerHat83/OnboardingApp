from typing import Dict, Any
from app.scoring.base_scorer import BaseScorer
from app.scoring.topic1_scorer import Topic1Scorer
from app.scoring.topic2_scorer import Topic2Scorer
from app.scoring.topic3_scorer import Topic3Scorer
from app.scoring.topic4_scorer import Topic4Scorer
from app.scoring.topic5_scorer import Topic5Scorer
from app.scoring.topic6_scorer import Topic6Scorer
from app.scoring.topic7_scorer import Topic7Scorer

class CompositeAuditScorer:
    """
    Master Audit Composite Scorer (7 Topics).
    """

    DEFAULT_WEIGHTS = {
        "topic1": 0.10,  # Technical & Accessibility
        "topic2": 0.15,  # CWV & Performance
        "topic3": 0.15,  # Organic Search
        "topic4": 0.15,  # AI & GEO Visibility
        "topic5": 0.15,  # Paid PPC Intelligence
        "topic6": 0.15,  # Conversion Architecture
        "topic7": 0.15   # Local SEO & BrightLocal
    }

    def __init__(self, full_audit_payload: Dict[str, Any]):
        self.payload = full_audit_payload or {}

    def evaluate_all(self) -> Dict[str, Any]:
        """Evaluates all 7 topics and generates the unified composite report."""
        t1 = Topic1Scorer(self.payload.get("topic1_accessibility_privacy", {})).evaluate()
        t2 = Topic2Scorer(self.payload.get("topic2_performance_cwv", {})).evaluate()
        t3 = Topic3Scorer(self.payload.get("topic3_search_visibility", {})).evaluate()
        t4 = Topic4Scorer(self.payload.get("topic4_ai_geo_visibility", {})).evaluate()
        t5 = Topic5Scorer(self.payload.get("topic5_paid_ppc", {})).evaluate()
        t6 = Topic6Scorer(self.payload.get("topic6_conversion_architecture", {})).evaluate()
        t7 = Topic7Scorer(self.payload.get("topic7_local_seo", {})).evaluate()

        composite_score = round(
            (t1["overall_score"] * self.DEFAULT_WEIGHTS["topic1"]) +
            (t2["overall_score"] * self.DEFAULT_WEIGHTS["topic2"]) +
            (t3["overall_score"] * self.DEFAULT_WEIGHTS["topic3"]) +
            (t4["overall_score"] * self.DEFAULT_WEIGHTS["topic4"]) +
            (t5["overall_score"] * self.DEFAULT_WEIGHTS["topic5"]) +
            (t6["overall_score"] * self.DEFAULT_WEIGHTS["topic6"]) +
            (t7["overall_score"] * self.DEFAULT_WEIGHTS["topic7"]),
        )

        return {
            "composite_score": composite_score,
            "overall_grade": BaseScorer.calculate_grade(composite_score),
            "target_url": self.payload.get("audit_metadata", {}).get("target_url", ""),
            "topic_scores": {
                "topic1": t1,
                "topic2": t2,
                "topic3": t3,
                "topic4": t4,
                "topic5": t5,
                "topic6": t6,
                "topic7": t7
            }
        }