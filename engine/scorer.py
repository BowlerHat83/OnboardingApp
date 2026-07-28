"""
engine/scorer.py - Standardized scoring engine with N/A support for inactive channels.
"""

from typing import Optional, List


def calculate_overall_score(category_scores: List[Optional[int]]) -> Optional[int]:
    """
    Calculates the overall average score, dynamically excluding N/A (None) sections.
    """
    valid_scores = [score for score in category_scores if score is not None]
    if not valid_scores:
        return None
    return round(sum(valid_scores) / len(valid_scores))


def score_organic_search(total_keywords: int, page_2_opps: int) -> Optional[int]:
    """
    Evaluates organic search performance.
    Returns None (N/A) if no organic keywords exist.
    """
    if total_keywords == 0:
        return None  # Excluded from overall score, rendered as N/A

    score = 50
    if total_keywords > 50:
        score += 30
    elif total_keywords > 10:
        score += 15

    if page_2_opps > 5:
        score += 20
    elif page_2_opps > 0:
        score += 10

    return min(score, 100)


def score_ppc_ads(paid_keywords: int, est_spend: float) -> Optional[int]:
    """
    Evaluates active PPC campaigns.
    Returns None (N/A) if the site does not run paid ads.
    """
    if paid_keywords == 0 and est_spend == 0:
        return None  # Excluded from overall score calculation (N/A)

    score = 50
    if paid_keywords > 0:
        score += 25
    if est_spend > 0:
        score += 25

    return min(score, 100)


def score_security(has_ssl: bool, https_enforced: bool, missing_headers_count: int) -> int:
    """
    Scores security posture based on SSL, HTTPS redirection, and security headers.
    """
    score = 0
    if has_ssl:
        score += 30
    if https_enforced:
        score += 30
    
    # Deduct 8 points per missing recommended security header (max 5 headers = 40 pts)
    header_score = max(0, 40 - (missing_headers_count * 8))
    score += header_score

    return score
