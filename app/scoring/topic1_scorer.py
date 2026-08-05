from typing import Dict, Any
from app.scoring.base_scorer import BaseScorer

class Topic1Scorer:
    """
    Scoring Engine for Topic 1: Technical, Crawlability & WCAG 2.2 Accessibility.
    
    Weights:
      • Crawlability & Indexability: 30%
      • Accessibility (WCAG 2.2 AA):  40%
      • Security & Privacy:          20%
      • Sitemap Health:               10%
    """

    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data or {}

    def score_crawlability(self) -> Dict[str, Any]:
        """Calculates Crawlability sub-score (30% weight)."""
        http_ok = self.raw_data.get("http_status") == 200 or self.raw_data.get("status") == "success"
        canonical_ok = self.raw_data.get("canonical_valid", True)
        indexable = not self.raw_data.get("is_noindex", False)

        http_score = BaseScorer.score_binary(http_ok)
        canonical_score = BaseScorer.score_binary(canonical_ok)
        indexable_score = BaseScorer.score_binary(indexable)

        total = round((http_score * 0.4) + (canonical_score * 0.3) + (indexable_score * 0.3), 2)
        return {
            "score": total,
            "details": {
                "http_status_ok": http_ok,
                "canonical_valid": canonical_ok,
                "indexable": indexable
            }
        }

    def score_accessibility(self) -> Dict[str, Any]:
        """Calculates Accessibility sub-score using WCAG axe-core violations (40% weight)."""
        violations = self.raw_data.get("violations_summary", [])
        
        # Deductions
        critical_count = sum(1 for v in violations if v.get("impact") == "critical")
        serious_count = sum(1 for v in violations if v.get("impact") == "serious")
        moderate_count = sum(1 for v in violations if v.get("impact") == "moderate")
        minor_count = sum(1 for v in violations if v.get("impact") == "minor")

        total_deductions = (critical_count * 15.0) + (serious_count * 8.0) + (moderate_count * 3.0) + (minor_count * 1.0)
        score = BaseScorer.score_deductive(100.0, total_deductions)

        return {
            "score": score,
            "details": {
                "total_violations": len(violations),
                "critical": critical_count,
                "serious": serious_count,
                "moderate": moderate_count,
                "minor": minor_count,
                "total_deductions": total_deductions
            }
        }

    def score_security(self) -> Dict[str, Any]:
        """Calculates Security & Privacy sub-score (20% weight)."""
        target_url = self.raw_data.get("target_url", "")
        https_active = target_url.startswith("https://") or self.raw_data.get("https", True)
        privacy_banner = self.raw_data.get("privacy_banner_detected", True)

        https_score = BaseScorer.score_binary(https_active)
        privacy_score = BaseScorer.score_binary(privacy_banner)

        total = round((https_score * 0.6) + (privacy_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "https_active": https_active,
                "privacy_banner_detected": privacy_banner
            }
        }

    def score_sitemap(self) -> Dict[str, Any]:
        """Calculates Sitemap Health sub-score (10% weight)."""
        sitemap_found = self.raw_data.get("sitemap_found", True)
        score = BaseScorer.score_binary(sitemap_found)
        return {
            "score": score,
            "details": {
                "sitemap_found": sitemap_found
            }
        }

    def evaluate(self) -> Dict[str, Any]:
        """Runs the entire Topic 1 evaluation pipeline."""
        crawl = self.score_crawlability()
        a11y = self.score_accessibility()
        sec = self.score_security()
        sitemap = self.score_sitemap()

        final_score = round(
            (crawl["score"] * 0.30) +
            (a11y["score"] * 0.40) +
            (sec["score"] * 0.20) +
            (sitemap["score"] * 0.10),
            2
        )

        return {
            "topic": "Topic 1: Technical & Accessibility",
            "overall_score": final_score,
            "grade": BaseScorer.calculate_grade(final_score),
            "breakdown": {
                "crawlability": crawl,
                "accessibility": a11y,
                "security_privacy": sec,
                "sitemap_health": sitemap
            }
        }