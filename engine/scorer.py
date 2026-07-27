from models.audit_schema import AuditSection

def score_technical_seo(total_urls: int, errors_4xx_5xx: int, non_indexable: int) -> int:
    """Calculates a balanced Technical SEO score based on site size and error ratios."""
    if total_urls == 0:
        return 0

    error_ratio = errors_4xx_5xx / total_urls
    non_index_ratio = non_indexable / total_urls

    # Base score of 100
    score = 100.0

    # Deduct up to 50 points for 4xx/5xx errors
    score -= min(50.0, error_ratio * 100 * 2)

    # Deduct up to 20 points for high non-indexable ratios
    score -= min(20.0, non_index_ratio * 100 * 0.5)

    return max(0, round(score))
