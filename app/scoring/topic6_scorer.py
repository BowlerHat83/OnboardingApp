from typing import Dict, Any
from app.scoring.base_scorer import BaseScorer

class Topic6Scorer:
    """
    Scoring Engine for Topic 6: Conversion Architecture & Lead Capture.
    
    Weights:
      • CTA Visibility & Above-the-Fold Placement: 35%
      • Lead Capture Form Friction & Field Count:  25%
      • Trust & Social Proof Reassurance:          20%
      • Direct Contact Signals & Accessibility:    20%
    """

    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data or {}

    def score_cta_visibility(self) -> Dict[str, Any]:
        """Calculates CTA Visibility & Above-the-Fold Placement sub-score (35% weight)."""
        ctas = self.raw_data.get("cta_buttons", []) or self.raw_data.get("ctas", [])
        cta_count = len(ctas) if isinstance(ctas, list) else int(self.raw_data.get("cta_count", 2))
        above_fold = self.raw_data.get("cta_above_fold", True)

        fold_score = BaseScorer.score_binary(above_fold)
        count_score = BaseScorer.score_ranged(cta_count, best=3, worst=0)

        total = round((fold_score * 0.6) + (count_score * 0.4), 2)
        return {
            "score": total,
            "details": {
                "cta_above_fold": above_fold,
                "cta_count": cta_count
            }
        }

    def score_form_health(self) -> Dict[str, Any]:
        """Calculates Form Friction & Field Count sub-score (25% weight)."""
        forms = self.raw_data.get("forms", [])
        form_detected = self.raw_data.get("has_lead_form", len(forms) > 0)
        
        if not form_detected:
            return {
                "score": 0.0,
                "details": {"has_lead_form": False, "field_count": 0}
            }

        field_count = int(self.raw_data.get("form_field_count", 4))
        
        # 1-4 fields ideal, penalties for excessive fields causing friction
        if 1 <= field_count <= 4:
            field_score = 100.0
        elif 5 <= field_count <= 7:
            field_score = 70.0
        else:
            field_score = 30.0

        form_score = BaseScorer.score_binary(form_detected)
        total = round((form_score * 0.4) + (field_score * 0.6), 2)

        return {
            "score": total,
            "details": {
                "has_lead_form": form_detected,
                "field_count": field_count,
                "field_friction_score": field_score
            }
        }

    def score_social_proof(self) -> Dict[str, Any]:
        """Calculates Trust & Social Proof sub-score (20% weight)."""
        proof = self.raw_data.get("social_proof", {}) or self.raw_data
        
        has_testimonials = proof.get("has_testimonials", True)
        has_logos = proof.get("has_client_logos", True)
        has_guarantees = proof.get("has_trust_badges", False)

        test_score = BaseScorer.score_binary(has_testimonials)
        logo_score = BaseScorer.score_binary(has_logos)
        badge_score = BaseScorer.score_binary(has_guarantees)

        total = round((test_score * 0.4) + (logo_score * 0.4) + (badge_score * 0.2), 2)
        return {
            "score": total,
            "details": {
                "has_testimonials": has_testimonials,
                "has_client_logos": has_logos,
                "has_trust_badges": has_guarantees
            }
        }

    def score_contact_signals(self) -> Dict[str, Any]:
        """Calculates Direct Contact Accessibility sub-score (20% weight)."""
        phone = self.raw_data.get("has_phone_link", True)
        email = self.raw_data.get("has_email_link", True)
        chat = self.raw_data.get("has_live_chat", False)

        phone_score = BaseScorer.score_binary(phone)
        email_score = BaseScorer.score_binary(email)
        chat_score = BaseScorer.score_binary(chat)

        total = round((phone_score * 0.4) + (email_score * 0.4) + (chat_score * 0.2), 2)
        return {
            "score": total,
            "details": {
                "has_phone_link": phone,
                "has_email_link": email,
                "has_live_chat": chat
            }
        }

    def evaluate(self) -> Dict[str, Any]:
        """Runs the complete Topic 6 evaluation pipeline."""
        cta = self.score_cta_visibility()
        form = self.score_form_health()
        proof = self.score_social_proof()
        contact = self.score_contact_signals()

        final_score = round(
            (cta["score"] * 0.35) +
            (form["score"] * 0.25) +
            (proof["score"] * 0.20) +
            (contact["score"] * 0.20),
            2
        )

        return {
            "topic": "Topic 6: Conversion Architecture",
            "overall_score": final_score,
            "grade": BaseScorer.calculate_grade(final_score),
            "breakdown": {
                "cta_visibility": cta,
                "form_health": form,
                "social_proof": proof,
                "contact_signals": contact
            }
        }