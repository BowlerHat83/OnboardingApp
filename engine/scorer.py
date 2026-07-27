from models.audit_schema import AuditSection

# engine/scorer.py

def score_technical_seo(total_issues: int, errors: int, non_indexable: int) -> int:
    """Calculates score for Technical SEO (Screaming Frog data)."""
    base = 100
    penalty = (errors * 5) + (total_issues * 0.5) + (non_indexable * 2)
    return max(0, min(100, int(base - penalty)))


def score_organic_search(total_keywords: int, page_2_opps: int) -> int:
    """Calculates score for Organic Search & Strategy (SEMrush data)."""
    if total_keywords == 0:
        return 0
    score = 50 + min(30, total_keywords // 10) + min(20, page_2_opps // 5)
    return max(0, min(100, int(score)))


def score_ppc_ads(paid_keywords: int, est_spend: float) -> int:
    """Calculates score for PPC & Paid Search (SpyFu data)."""
    if paid_keywords == 0 and est_spend == 0:
        return 50  # Neutral score if no paid activity active
    score = 60 + min(20, paid_keywords // 5) + min(20, int(est_spend // 100))
    return max(0, min(100, int(score)))


def score_local_seo(gbp_score: int, citations: int) -> int:
    """Calculates score for Local SEO (BrightLocal data)."""
    if gbp_score > 0:
        return gbp_score
    score = 40 + min(60, citations * 2)
    return max(0, min(100, int(score)))
    
    error_ratio = errors_4xx_5xx / total_urls
    non_index_ratio = non_indexable / total_urls

    # Base score of 100
    score = 100.0

    # Deduct up to 50 points for 4xx/5xx errors
    score -= min(50.0, error_ratio * 100 * 2)

    # Deduct up to 20 points for high non-indexable ratios
    score -= min(20.0, non_index_ratio * 100 * 0.5)

    return max(0, round(score))
