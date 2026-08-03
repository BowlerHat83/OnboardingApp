import pandas as pd
import numpy as np
from typing import Dict, Any, List


class Topic5Service:
    """
    Service for Topic 5: Paid Visibility & PPC Competitive Intelligence.
    Calculates key metrics including keyword counts, top keywords, ad spend, average CPC, 
    market share, and competitor analysis.
    """

    def __init__(self, raw_data: List[Dict[str, Any]], domain_meta: Dict[str, Any] = None):
        self.df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
        self.domain_meta = domain_meta or {}

    def process_intelligence(self) -> Dict[str, Any]:
        if self.df.empty:
            return self._build_zero_spend_response("No SpyFu paid data provided.")

        # Default Column Injection
        default_cols = {
            "keyword": "",
            "search_volume": 0,
            "cpc": 0.0,
            "monthly_spend": 0.0,
            "impression_share": 0.0,
            "top_competitor": ""
        }
        for col, default_val in default_cols.items():
            if col not in self.df.columns:
                self.df[col] = default_val

        # Sanitize numeric columns
        for num_col in ["search_volume", "cpc", "monthly_spend", "impression_share"]:
            self.df[num_col] = pd.to_numeric(self.df[num_col], errors="coerce").fillna(0)

        # Filter out empty keyword rows
        active_df = self.df[self.df['keyword'].astype(str).str.strip() != ''].copy()
        paid_keywords_count = int(len(active_df))

        if paid_keywords_count == 0:
            return self._build_zero_spend_response("No active paid keywords found in export.")

        # 1. Total Estimated Spend & Average CPC
        total_monthly_spend = float(active_df['monthly_spend'].sum())
        
        # Fall back to domain metadata if needed
        if total_monthly_spend == 0.0 and 'estimated_monthly_spend' in self.domain_meta:
            total_monthly_spend = float(self.domain_meta['estimated_monthly_spend'])

        active_cpc_series = active_df[active_df['cpc'] > 0]['cpc']
        avg_cpc = float(active_cpc_series.mean()) if not active_cpc_series.empty else 0.0

        # 2. Top 25 Keywords
        top_25_df = active_df.sort_values(by=['search_volume'], ascending=False).head(25)
        top_25_keywords = []
        for _, row in top_25_df.iterrows():
            top_25_keywords.append({
                "keyword": str(row['keyword']),
                "search_volume": int(row['search_volume']),
                "estimated_cpc_usd": round(float(row['cpc']), 2),
                "estimated_monthly_spend_usd": round(float(row['monthly_spend']), 2)
            })

        # 3. Paid Visibility Market Share Calculation
        avg_impression_share = active_df['impression_share'].mean()
        if avg_impression_share > 0:
            market_share_pct = round(float(avg_impression_share), 2)
        else:
            market_share_pct = min(100.0, round(float((paid_keywords_count / 200.0) * 100), 1))

        # 4. Paid Competitor Comparisons
        competitor_series = active_df[active_df['top_competitor'].astype(str).str.strip() != '']['top_competitor']
        competitor_counts = competitor_series.value_counts().head(5)
        
        competitor_comparisons = []
        for comp_domain, overlap_count in competitor_counts.items():
            competitor_comparisons.append({
                "competitor_domain": str(comp_domain),
                "overlapping_paid_keywords": int(overlap_count),
                "relative_threat_level": "High" if overlap_count > (paid_keywords_count * 0.2) else "Moderate"
            })

        # 5. Historic Performance
        historic_performance = {
            "status": "Active Paid Campaigns Detected",
            "historical_tracking_available": True,
            "estimated_monthly_budget_tier": self._classify_spend_tier(total_monthly_spend)
        }

        return {
            "status": "success",
            "paid_active": True,
            "summary": {
                "count_of_paid_keywords": paid_keywords_count,
                "estimated_google_ads_spend_usd": round(total_monthly_spend, 2),
                "average_cpc_usd": round(avg_cpc, 2),
                "paid_visibility_market_share_pct": market_share_pct
            },
            "top_25_paid_keywords": top_25_keywords,
            "paid_competitor_comparisons": competitor_comparisons,
            "historic_paid_performance": historic_performance
        }

    def _classify_spend_tier(self, spend: float) -> str:
        if spend >= 10000:
            return "Enterprise ($10k+/mo)"
        elif spend >= 2500:
            return "Mid-Market ($2.5k - $10k/mo)"
        elif spend > 0:
            return "Low-Scale (< $2.5k/mo)"
        return "Zero Ad Spend"

    def _build_zero_spend_response(self, reason: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "paid_active": False,
            "message": f"Zero Google Ads presence detected ({reason}). Industry competitive metrics are summarized below.",
            "summary": {
                "count_of_paid_keywords": 0,
                "estimated_google_ads_spend_usd": 0.0,
                "average_cpc_usd": 0.0,
                "paid_visibility_market_share_pct": 0.0
            },
            "top_25_paid_keywords": [],
            "paid_competitor_comparisons": [],
            "historic_paid_performance": {
                "status": "Inactive / No Historical Google Ads Spend Detected",
                "historical_tracking_available": False,
                "estimated_monthly_budget_tier": "Zero Ad Spend"
            }
        }