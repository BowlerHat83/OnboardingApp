import pandas as pd
from typing import Dict, Any

def parse_screaming_frog_csv(file_path: str) -> Dict[str, Any]:
    """
    Parses Screaming Frog crawl export CSV and extracts comprehensive technical SEO metrics:
    - Total URLs crawled
    - Content/File Type Breakdown (HTML, JS, CSS, Images, PDF, Flash, Other)
    - Status Codes & 4xx Broken Links
    - Self-Referencing vs Mismatched Canonicals
    - Meta Descriptions (Missing & Overlong)
    - Image Alt Text Optimization
    - Thin / Low Quality Content (< 200 words)
    - Missing H1 & Title Tags
    - Non-Indexable Count
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {
            "error": f"Failed to read Screaming Frog CSV: {str(e)}",
            "total_urls": 0,
            "status_4xx_errors": 0,
            "status_5xx_errors": 0,
            "non_indexable_count": 0,
            "missing_titles": 0,
            "missing_h1s": 0,
            "missing_meta_descriptions": 0,
            "thin_content_pages": 0,
            "self_referencing_canonicals": 0,
            "file_type_breakdown": {},
            "total_images": 0,
            "missing_alt_text": 0
        }

    # Normalize column headers
    df.columns = [c.strip() for c in df.columns]

    total_urls = len(df)

    # 1. File Type Breakdown
    file_type_breakdown = {
        "HTML": 0,
        "JavaScript": 0,
        "CSS": 0,
        "Images": 0,
        "PDF": 0,
        "Flash": 0,
        "Other": 0
    }

    content_type_col = None
    for col in ['Content Type', 'Content', 'Type']:
        if col in df.columns:
            content_type_col = col
            break

    if content_type_col:
        for val in df[content_type_col].dropna().astype(str):
            val_lower = val.lower()
            if 'html' in val_lower:
                file_type_breakdown["HTML"] += 1
            elif 'javascript' in val_lower or 'js' in val_lower:
                file_type_breakdown["JavaScript"] += 1
            elif 'css' in val_lower:
                file_type_breakdown["CSS"] += 1
            elif any(ext in val_lower for ext in ['image', 'png', 'jpeg', 'jpg', 'webp', 'gif']):
                file_type_breakdown["Images"] += 1
            elif 'pdf' in val_lower:
                file_type_breakdown["PDF"] += 1
            elif 'flash' in val_lower or 'swf' in val_lower:
                file_type_breakdown["Flash"] += 1
            else:
                file_type_breakdown["Other"] += 1

    # 2. Status Codes & 4xx Broken Links
    status_4xx = 0
    status_5xx = 0
    if 'Status Code' in df.columns:
        status_codes = pd.to_numeric(df['Status Code'], errors='coerce')
        status_4xx = int(((status_codes >= 400) & (status_codes < 500)).sum())
        status_5xx = int(((status_codes >= 500) & (status_codes < 600)).sum())

    # 3. Non-Indexable URLs
    non_indexable = 0
    if 'Indexability' in df.columns:
        non_indexable = int((df['Indexability'].astype(str).str.lower() == 'non-indexable').sum())

    # 4. Missing Title Tags
    missing_titles = 0
    title_col = None
    for col in ['Title 1', 'Title', 'Page Title']:
        if col in df.columns:
            title_col = col
            break
    if title_col:
        missing_titles = int(df[title_col].isna().sum() + (df[title_col].astype(str).str.strip() == '').sum())

    # 5. Missing H1 Headers
    missing_h1s = 0
    h1_col = None
    for col in ['H1-1', 'H1 1', 'H1']:
        if col in df.columns:
            h1_col = col
            break
    if h1_col:
        missing_h1s = int(df[h1_col].isna().sum() + (df[h1_col].astype(str).str.strip() == '').sum())

    # 6. Meta Descriptions
    missing_meta_descriptions = 0
    meta_col = None
    for col in ['Meta Description 1', 'Meta Description', 'Description']:
        if col in df.columns:
            meta_col = col
            break
    if meta_col:
        missing_meta_descriptions = int(df[meta_col].isna().sum() + (df[meta_col].astype(str).str.strip() == '').sum())

    # 7. Self-Referencing Canonicals
    self_referencing_canonicals = 0
    addr_col = 'Address' if 'Address' in df.columns else ('URL' if 'URL' in df.columns else None)
    canon_col = None
    for col in ['Canonical Link Element 1', 'Canonical', 'Canonical URL']:
        if col in df.columns:
            canon_col = col
            break

    if addr_col and canon_col:
        valid_mask = df[addr_col].notna() & df[canon_col].notna()
        self_referencing_canonicals = int((df.loc[valid_mask, addr_col].astype(str).str.strip().str.rstrip('/') ==
                                            df.loc[valid_mask, canon_col].astype(str).str.strip().str.rstrip('/')).sum())

    # 8. Thin Content (< 200 Words on HTML Pages)
    thin_content_pages = 0
    word_col = None
    for col in ['Word Count', 'Words']:
        if col in df.columns:
            word_col = col
            break

    if word_col:
        word_counts = pd.to_numeric(df[word_col], errors='coerce').fillna(0)
        if content_type_col:
            is_html = df[content_type_col].astype(str).str.lower().str.contains('html', na=False)
            thin_content_pages = int(((word_counts < 200) & is_html).sum())
        else:
            thin_content_pages = int((word_counts < 200).sum())

    # 9. Image Alt Text Metrics
    total_images = file_type_breakdown["Images"]
    missing_alt_text = 0
    alt_col = None
    for col in ['Alt Text', 'Missing Alt Text', 'Alt Text 1']:
        if col in df.columns:
            alt_col = col
            break

    if alt_col:
        missing_alt_text = int(df[alt_col].isna().sum() + (df[alt_col].astype(str).str.strip() == '').sum())

    return {
        "total_urls": total_urls,
        "file_type_breakdown": file_type_breakdown,
        "status_4xx_errors": status_4xx,
        "status_5xx_errors": status_5xx,
        "non_indexable_count": non_indexable,
        "missing_titles": missing_titles,
        "missing_h1s": missing_h1s,
        "missing_meta_descriptions": missing_meta_descriptions,
        "self_referencing_canonicals": self_referencing_canonicals,
        "thin_content_pages": thin_content_pages,
        "total_images": total_images,
        "missing_alt_text": missing_alt_text
    }
