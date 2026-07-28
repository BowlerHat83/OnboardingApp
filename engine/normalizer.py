"""
engine/normalizer.py - Aggregates audit checks, handles N/A exclusions, and retains market insights.
"""

from typing import Dict, Any
from pings.ai_readiness_ping import check_ai_readiness
from pings.security_ping import check_security_headers
from engine.scorer import (
    score_organic_search,
    score_ppc_ads,
    score_security,
    calculate_overall_score
)


def normalize_audit_results(csv_data: Dict[str, Any], target_url: str) -> Dict[str, Any]:
    """
    Normalizes audit metrics, excludes N/A channels from overall score, 
    and retains industry market insight data.
    """
    # 1. Live Ping Checks
    live_ai = check_ai_readiness(target_url)
    live_security = check_security_headers(target_url)

    # 2. Raw CSV Metrics
    semrush_keywords = csv_data.get("total_keywords", 0)
    semrush_p2_opps = csv_data.get("page_2_opps", 0)
    
    spyfu_paid_keywords = csv_data.get("paid_keywords", 0)
    spyfu_est_spend = csv_data.get("est_spend", 0.0)

    # 3. Market Insight Data (Passed through regardless of whether the client runs ads)
    ppc_market_insights = {
        "market_competitiveness": csv_data.get("ppc_market_competitiveness", "Moderate"),
        "avg_industry_cpc": csv_data.get("avg_industry_cpc", 0.0),
        "top_paid_competitors": csv_data.get("top_paid_competitors", []),
        "estimated_opportunity_volume": csv_data.get("ppc_opportunity_volume", 0)
    }

    # 4. Calculate Section Scores (Return None for N/A)
    content_score = score_organic_search(semrush_keywords, semrush_p2_opps)
    ppc_score = score_ppc_ads(spyfu_paid_keywords, spyfu_est_spend)
    
    security_score = score_security(
        has_ssl=live_security.get("has_ssl", False),
        https_enforced=live_security.get("https_enforced", False),
        missing_headers_count=len(live_security.get("missing_headers", []))
    )

    ai_score = csv_data.get("generative_visibility_score", live_ai.get("score", 50))

    # 5. Dynamic Overall Score (Ignores None / N/A categories)
    all_category_scores = [
        content_score,
        ppc_score,
        security_score,
        ai_score
    ]
    overall_score = calculate_overall_score(all_category_scores)

    return {
        "overall_score": overall_score if overall_score is not None else "N/A",
        "content_strategy": {
            "score": content_score if content_score is not None else "N/A",
            "total_keywords": semrush_keywords
        },
        "ppc_analytics": {
            "score": ppc_score if ppc_score is not None else "N/A",
            "is_active_advertiser": ppc_score is not None,
            "client_metrics": {
                "paid_keywords": spyfu_paid_keywords,
                "est_spend": spyfu_est_spend
            },
            # Paid market insights remain visible for strategic recommendations
            "market_insights": ppc_market_insights
        },
        "ai_readiness": {
            "score": ai_score,
            "has_llms_txt": live_ai.get("has_llms_txt", False) or csv_data.get("has_llms_txt", False)
        },
        "security": {
            "score": security_score,
            "details": live_security
        }
    }
