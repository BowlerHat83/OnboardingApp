import pandas as pd
import numpy as np
from typing import Dict, Any, List

class Topic4Service:
    """
    Service for Topic 4: AI Visibility & Generative Engine Optimization (GEO).
    Analyzes prompt tracking, brand occurrences, AI platform coverage, and competitor citations.
    """

    def __init__(self, raw_data: List[Dict[str, Any]]):
        self.df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

    def process_intelligence(self) -> Dict[str, Any]:
        if self.df.empty:
            return {
                "status": "warning",
                "message": "No Waikay AI visibility data available.",
                "summary": {},
                "ai_triggered_keywords": []
            }

        # 1. Sanitize boolean and text indicators
        for model in ['ai_triggered', 'brand_mentioned', 'chatgpt', 'claude', 'sonar', 'gemini']:
            if model in self.df.columns:
                self.df[model] = self.df[model].astype(str).str.lower().isin(['true', '1', 'yes', 't', 'x'])
            else:
                self.df[model] = False

        self.df['keyword'] = self.df['keyword'].fillna('Unknown Prompt').astype(str)
        self.df['top_competitor'] = self.df['top_competitor'].fillna('').astype(str)

        total_keywords = int(len(self.df))

        # 2. Keywords triggering AI visibility & Brand Mentions
        triggered_df = self.df[self.df['ai_triggered']]
        ai_triggered_count = int(len(triggered_df))
        brand_mentioned_count = int(self.df['brand_mentioned'].sum())
        
        brand_visibility_rate = round((brand_mentioned_count / total_keywords * 100), 1) if total_keywords > 0 else 0.0

        # 3. Model Platform Breakdown
        platform_breakdown = {
            "chatgpt": {
                "mentions": int(self.df['chatgpt'].sum()),
                "visibility_pct": round(float(self.df['chatgpt'].mean() * 100), 1) if total_keywords > 0 else 0.0
            },
            "sonar_perplexity": {
                "mentions": int(self.df['sonar'].sum()),
                "visibility_pct": round(float(self.df['sonar'].mean() * 100), 1) if total_keywords > 0 else 0.0
            },
            "gemini": {
                "mentions": int(self.df['gemini'].sum()),
                "visibility_pct": round(float(self.df['gemini'].mean() * 100), 1) if total_keywords > 0 else 0.0
            },
            "claude": {
                "mentions": int(self.df['claude'].sum()),
                "visibility_pct": round(float(self.df['claude'].mean() * 100), 1) if total_keywords > 0 else 0.0
            }
        }

        # 4. Extract List of AI-Triggered Keywords
        ai_triggered_keywords = []
        for _, row in triggered_df.iterrows():
            active_platforms = []
            if row['chatgpt']: active_platforms.append("ChatGPT")
            if row['sonar']: active_platforms.append("Sonar (Perplexity)")
            if row['gemini']: active_platforms.append("Gemini")
            if row['claude']: active_platforms.append("Claude")

            ai_triggered_keywords.append({
                "keyword": row['keyword'],
                "brand_mentioned": bool(row['brand_mentioned']),
                "active_platforms": active_platforms,
                "top_competitor_cited": row['top_competitor'] if row['top_competitor'] else "None"
            })

        # 5. Aggregate Competitor Share of Voice
        competitor_counts = self.df[self.df['top_competitor'] != '']['top_competitor'].value_counts()
        competitor_comparison = []
        
        # Add primary brand first
        competitor_comparison.append({
            "brand": "Your Brand",
            "mentions": brand_mentioned_count,
            "share_of_voice_pct": brand_visibility_rate
        })

        for comp_name, count in competitor_counts.items():
            competitor_comparison.append({
                "brand": str(comp_name),
                "mentions": int(count),
                "share_of_voice_pct": round((int(count) / total_keywords * 100), 1) if total_keywords > 0 else 0.0
            })

        return {
            "status": "success",
            "summary": {
                "total_prompts_analyzed": total_keywords,
                "ai_triggered_keywords_count": ai_triggered_count,
                "brand_mention_count": brand_mentioned_count,
                "brand_visibility_rate_pct": brand_visibility_rate,
                "platform_visibility": platform_breakdown,
                "historic_geo_performance": {
                    "current_visibility_score": brand_visibility_rate,
                    "trend_status": "Active Tracking"
                }
            },
            "competitor_comparison": competitor_comparison,
            "ai_triggered_keywords": ai_triggered_keywords
        }