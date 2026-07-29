def score_security(has_ssl: bool, https_enforced: bool) -> int:
    """
    Scores Section 1 (Technical Security).
    Each check is binary (Pass/Fail) and worth 50 points (Max 100).
    """
    score = 0
    if has_ssl:
        score += 50
    if https_enforced:
        score += 50

    return score

"""
engine/scorer.py - Audit scoring calculations across all sections.
"""

from typing import List, Dict, Any


def score_security(has_ssl: bool, https_enforced: bool) -> int:
    """
    Scores Section 1 (Technical Security).
    Each check is binary (Pass/Fail) and worth 50 points (Max 100).
    """
    score = 0
    if has_ssl:
        score += 50
    if https_enforced:
        score += 50

    return score


def score_organic_search(
    page_1_keywords: List[Dict[str, Any]],
    page_2_keywords: List[Dict[str, Any]],
    serp_distribution: Dict[str, int],
    client_traffic: int,
    avg_competitor_traffic: int,
    client_authority: int,
    avg_competitor_authority: int
) -> Dict[str, Any]:
    """
    Scores Section 2 (Organic Search & Content Strategy) on a 100-point scale.
    - Footprint Score (Max 40 pts): Pos 1-3 (5pts), Pos 4-10 (2pts), Pos 11-20 (1pt), Pos 21-30 (0.5pts)
    - Traffic Score vs Competitors (Max 30 pts)
    - Authority Score vs Competitors (Max 30 pts)
    """

    # -------------------------------------------------------------
    # 1. High-Value Keyword Footprint (Capped at 40 Points)
    # -------------------------------------------------------------
    raw_kw_points = 0.0

    # Evaluate Page 1 (Pos 1-3 = 5pts, Pos 4-10 = 2pts)
    for kw in page_1_keywords:
        vol = kw.get("search_volume", 0)
        pos = kw.get("position", 999)
        if vol >= 30:
            if 1 <= pos <= 3:
                raw_kw_points += 5.0
            elif 4 <= pos <= 10:
                raw_kw_points += 2.0

    # Evaluate Page 2 (Pos 11-20 = 1pt)
    for kw in page_2_keywords:
        vol = kw.get("search_volume", 0)
        if vol >= 30:
            raw_kw_points += 1.0

    # Evaluate Page 3 (Pos 21-30 = 0.5pts)
    raw_kw_points += (serp_distribution.get("page_3", 0) * 0.5)

    footprint_score = min(40.0, raw_kw_points)

    # -------------------------------------------------------------
    # 2. Organic Traffic vs Competitors (Capped at 30 Points)
    # -------------------------------------------------------------
    if avg_competitor_traffic > 0:
        traffic_ratio = client_traffic / avg_competitor_traffic
    else:
        traffic_ratio = 1.0 if client_traffic > 0 else 0.0

    if traffic_ratio >= 1.5:
        traffic_score = 30
    elif traffic_ratio >= 0.9:
        traffic_score = 22
    elif traffic_ratio >= 0.4:
        traffic_score = 12
    elif client_traffic > 0:
        traffic_score = 5
    else:
        traffic_score = 0

    # -------------------------------------------------------------
    # 3. Domain Authority vs Competitors (Capped at 30 Points)
    # -------------------------------------------------------------
    authority_diff = client_authority - avg_competitor_authority

    if authority_diff >= 5:
        authority_score = 30
    elif -5 <= authority_diff < 5:
        authority_score = 20  # "Good/Parity" score
    elif -15 <= authority_diff < -5:
        authority_score = 10
    else:
        authority_score = 0

    # Total Section 2 Score
    total_score = round(footprint_score + traffic_score + authority_score)

    return {
        "score": min(100, total_score),
        "breakdown": {
            "footprint_points": round(footprint_score, 1),
            "traffic_points": traffic_score,
            "authority_points": authority_score
        }
    }


