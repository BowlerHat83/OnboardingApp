from typing import Dict, Any
from app.scoring.base_scorer import BaseScorer

class Topic2Scorer:
    """
    Scoring Engine for Topic 2: Performance, Core Web Vitals & Content Architecture.
    
    Weights:
      • Core Web Vitals (LCP, INP, CLS): 45%
      • On-Page Metadata Health:          25%
      • Content Structure & Headings:     15%
      • Page Weight & Speed Metrics:      15%
    """

    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data or {}

    def score_core_web_vitals(self) -> Dict[str, Any]:
        """Calculates Core Web Vitals sub-score (45% weight)."""
        cwv = self.raw_data.get("core_web_vitals", {}) or self.raw_data.get("cwv", {})
        
        # Extracts values or provides default acceptable fallbacks if unmeasured
        lcp = float(cwv.get("lcp", cwv.get("largest_contentful_paint", 2.5)))
        inp = float(cwv.get("inp", cwv.get("interaction_to_next_paint", 200)))
        cls = float(cwv.get("cls", cwv.get("cumulative_layout_shift", 0.05)))

        lcp_score = BaseScorer.score_ranged(lcp, best=2.5, worst=4.0)
        inp_score = BaseScorer.score_ranged(inp, best=200.0, worst=500.0)
        cls_score = BaseScorer.score_ranged(cls, best=0.10, worst=0.25)

        total = round((lcp_score * 0.40) + (inp_score * 0.35) + (cls_score * 0.25), 2)
        
        return {
            "score": total,
            "details": {
                "lcp_seconds": lcp, "lcp_score": lcp_score,
                "inp_ms": inp, "inp_score": inp_score,
                "cls_value": cls, "cls_score": cls_score
            }
        }

    def score_metadata(self) -> Dict[str, Any]:
        """Calculates Metadata Health sub-score (25% weight)."""
        meta = self.raw_data.get("metadata", {}) or self.raw_data
        title = meta.get("title", "") or ""
        desc = meta.get("meta_description", "") or meta.get("description", "") or ""

        title_len = len(title.strip())
        desc_len = len(desc.strip())

        # Title Tag Score
        if 40 <= title_len <= 65:
            title_score = 100.0
        elif 20 <= title_len < 40 or 65 < title_len <= 80:
            title_score = 70.0
        elif title_len > 0:
            title_score = 40.0
        else:
            title_score = 0.0

        # Description Score
        if 110 <= desc_len <= 165:
            desc_score = 100.0
        elif 70 <= desc_len < 110 or 165 < desc_len <= 200:
            desc_score = 70.0
        elif desc_len > 0:
            desc_score = 40.0
        else:
            desc_score = 0.0

        total = round((title_score * 0.5) + (desc_score * 0.5), 2)
        return {
            "score": total,
            "details": {
                "title_length": title_len, "title_score": title_score,
                "desc_length": desc_len, "desc_score": desc_score
            }
        }

    def score_structure(self) -> Dict[str, Any]:
        """Calculates Content Structure sub-score (15% weight)."""
        structure = self.raw_data.get("structure", {}) or self.raw_data
        h1_count = int(structure.get("h1_count", 1))
        
        if h1_count == 1:
            h1_score = 100.0
        elif h1_count > 1:
            h1_score = 60.0
        else:
            h1_score = 0.0

        hierarchy_ok = structure.get("heading_hierarchy_valid", True)
        hierarchy_score = BaseScorer.score_binary(hierarchy_ok)

        total = round((h1_score * 0.6) + (hierarchy_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "h1_count": h1_count,
                "heading_hierarchy_valid": hierarchy_ok
            }
        }

    def score_page_weight(self) -> Dict[str, Any]:
        """Calculates Page Weight & Load Speed sub-score (15% weight)."""
        ttfb = float(self.raw_data.get("ttfb", 0.5))
        dom_size = int(self.raw_data.get("dom_element_count", 800))

        ttfb_score = BaseScorer.score_ranged(ttfb, best=0.8, worst=3.0)
        dom_score = BaseScorer.score_ranged(dom_size, best=800, worst=3000)

        total = round((ttfb_score * 0.6) + (dom_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "ttfb_seconds": ttfb, "ttfb_score": ttfb_score,
                "dom_elements": dom_size, "dom_score": dom_score
            }
        }

    def evaluate(self) -> Dict[str, Any]:
        """Runs the complete Topic 2 evaluation pipeline."""
        cwv = self.score_core_web_vitals()
        meta = self.score_metadata()
        struct = self.score_structure()
        weight = self.score_page_weight()

        final_score = round(
            (cwv["score"] * 0.45) +
            (meta["score"] * 0.25) +
            (struct["score"] * 0.15) +
            (weight["score"] * 0.15),
            2
        )

        return {
            "topic": "Topic 2: Performance & Core Web Vitals",
            "overall_score": final_score,
            "grade": BaseScorer.calculate_grade(final_score),
            "breakdown": {
                "core_web_vitals": cwv,
                "metadata_health": meta,
                "content_structure": struct,
                "page_weight_speed": weight
            }
        }