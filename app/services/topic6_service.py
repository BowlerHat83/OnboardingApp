import re
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

class Topic6Service:
    def __init__(self):
        self.conversion_keywords = ["contact", "book", "quote", "start", "demo", "buy", "get", "submit", "apply"]
        self.social_domains = ["facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com", "youtube.com"]

    def analyze_live_url(self, url: str) -> Dict[str, Any]:
        """Scrapes target URL for CTAs, Form Structures, and Contact Links."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SEOAuditBot/1.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
        except Exception as e:
            return {
                "error": f"Failed to fetch live page: {str(e)}",
                "cta_analysis": {},
                "conversion_forms": [],
                "contact_signals": {}
            }

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Contact Signals Parsing
        tel_links = list(set([a["href"].replace("tel:", "").strip() for a in soup.find_all("a", href=re.compile(r"^tel:", re.I))]))
        mailto_links = list(set([a["href"].replace("mailto:", "").strip() for a in soup.find_all("a", href=re.compile(r"^mailto:", re.I))]))
        
        social_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(domain in href for domain in self.social_domains):
                social_links.append(a["href"])
        social_links = list(set(social_links))

        # 2. Form Structure Parsing (Filtering out duplicates)
        forms_data = []
        forms = soup.find_all("form")
        for idx, form in enumerate(forms):
            inputs = form.find_all(["input", "textarea", "select"])
            if not inputs:
                continue
            
            input_types = [inp.get("type", "text") for inp in inputs if inp.get("type") != "hidden"]
            required_count = len([inp for inp in inputs if inp.has_attr("required")])
            
            # Simple heuristic to identify footer/search vs main lead forms
            is_global_footer = len(inputs) <= 2 and any(t in ["email", "submit"] for t in input_types)
            
            forms_data.append({
                "form_id": form.get("id") or f"form_{idx+1}",
                "form_type": "Global Footer / Search" if is_global_footer else "Primary Lead Form",
                "total_inputs": len(input_types),
                "required_inputs": required_count,
                "optional_inputs": len(input_types) - required_count,
                "input_types": input_types
            })

        # 3. CTA Frequency & Anchor Text Parsing
        ctas_found = []
        for btn in soup.find_all(["a", "button"]):
            text = btn.get_text(strip=True)
            href = btn.get("href", "")
            classes = " ".join(btn.get("class", []))
            
            is_cta = any(kw in text.lower() or kw in href.lower() or kw in classes.lower() for kw in self.conversion_keywords)
            if is_cta and text:
                ctas_found.append({"anchor_text": text, "target_url": href})

        return {
            "contact_signals": {
                "phone_numbers": tel_links,
                "emails": mailto_links,
                "social_profiles": social_links
            },
            "conversion_forms": forms_data,
            "cta_analysis": {
                "total_ctas_detected": len(ctas_found),
                "ctas": ctas_found[:10]  # Top 10 CTAs
            }
        }

    def parse_screaming_frog_csv(self, csv_bytes: bytes) -> Dict[str, Any]:
        """Parses Screaming Frog internal_html.csv for Metadata length, missing tags, and thin content."""
        df = pd.read_csv(io.BytesIO(csv_bytes))
        
        # Standard Screaming Frog column normalization
        cols = {c.lower().strip(): c for c in df.columns}
        
        url_col = cols.get("address", "Address")
        title_len_col = cols.get("title 1 length", "Title 1 Length")
        meta_len_col = cols.get("meta description 1 length", "Meta Description 1 Length")
        word_count_col = cols.get("word count", "Word Count")

        total_pages = len(df)
        
        # Metadata logic rules
        title_issues = {
            "optimal_count": len(df[(df[title_len_col] >= 30) & (df[title_len_col] <= 60)]) if title_len_col in df else 0,
            "too_short": len(df[df[title_len_col] < 30]) if title_len_col in df else 0,
            "too_long": len(df[df[title_len_col] > 60]) if title_len_col in df else 0,
            "missing": len(df[df[title_len_col].isna() | (df[title_len_col] == 0)]) if title_len_col in df else 0,
        }

        meta_issues = {
            "optimal_count": len(df[(df[meta_len_col] >= 70) & (df[meta_len_col] <= 150)]) if meta_len_col in df else 0,
            "too_short": len(df[df[meta_len_col] < 70]) if meta_len_col in df else 0,
            "too_long": len(df[df[meta_len_col] > 150]) if meta_len_col in df else 0,
            "missing": len(df[df[meta_len_col].isna() | (df[meta_len_col] == 0)]) if meta_len_col in df else 0,
        }

        # Thin content rule (<300 words)
        thin_content = []
        if word_count_col in df:
            thin_df = df[df[word_count_col] < 300]
            for _, row in thin_df.head(10).iterrows():
                thin_content.append({"url": row.get(url_col, ""), "word_count": int(row.get(word_count_col, 0))})

        return {
            "total_urls_analyzed": total_pages,
            "title_tag_health": title_issues,
            "meta_description_health": meta_issues,
            "thin_content_urls": thin_content
        }

    def parse_content_gap_csv(self, csv_bytes: bytes) -> List[Dict[str, Any]]:
        """Parses Ahrefs / Semrush Content Gap export CSV."""
        df = pd.read_csv(io.BytesIO(csv_bytes))
        # Top 10 opportunities by Volume
        gaps = []
        cols = [c.lower() for c in df.columns]
        
        kw_col = next((c for c in df.columns if "keyword" in c.lower()), None)
        vol_col = next((c for c in df.columns if "volume" in c.lower()), None)
        
        if kw_col and vol_col:
            df_sorted = df.sort_values(by=vol_col, ascending=False).head(10)
            for _, row in df_sorted.iterrows():
                gaps.append({
                    "keyword": str(row[kw_col]),
                    "search_volume": int(row[vol_col])
                })
        return gaps