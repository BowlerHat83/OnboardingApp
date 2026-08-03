import os
import pandas as pd

class ScreamingFrogParser:
    """
    Parses and normalizes CSV exports from Screaming Frog CLI.
    """
    COLUMN_MAP = {
        'Address': 'url',
        'URL': 'url',
        'Content Type': 'content_type',
        'Content': 'content_type',
        'Status Code': 'status_code',
        'Status': 'status_text',  # Separate from numeric code to avoid pandas collisions
        'Indexability': 'indexability',
        'Indexability Status': 'indexability_status',
        'Title 1': 'title',
        'Meta Description 1': 'meta_description',
        'H1-1': 'h1',
        'Canonical Link Element 1': 'canonical_url',
        'Word Count': 'word_count'
    }

    def __init__(self, csv_filepath: str):
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"Export file not found at: {csv_filepath}")
        self.csv_filepath = csv_filepath
        self.clean_df = pd.DataFrame()

    def parse(self, html_only: bool = False, indexable_only: bool = False) -> pd.DataFrame:
        """
        Loads CSV and returns a cleaned DataFrame.
        Defaults html_only & indexable_only to False for full Technical Data (Topic 2) analysis.
        """
        try:
            raw_df = pd.read_csv(self.csv_filepath, encoding='utf-8')
        except UnicodeDecodeError:
            raw_df = pd.read_csv(self.csv_filepath, encoding='utf-8-sig')

        # Rename matching columns
        renamed_cols = {col: self.COLUMN_MAP[col] for col in raw_df.columns if col in self.COLUMN_MAP}
        df = raw_df.rename(columns=renamed_cols).copy()

        # Deduplicate column names if any collisions occurred
        df = df.loc[:, ~df.columns.duplicated()].copy()

        # Fill missing text fields safely
        for col in ['title', 'meta_description', 'h1', 'canonical_url', 'indexability']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str)

        # Safely parse numeric status codes
        if 'status_code' in df.columns:
            df['status_code'] = pd.to_numeric(df['status_code'], errors='coerce').fillna(0).astype(int)

        # Optional filters
        if html_only and 'content_type' in df.columns:
            df = df[df['content_type'].astype(str).str.contains('text/html', case=False, na=False)]

        if indexable_only:
            if 'status_code' in df.columns:
                df = df[df['status_code'] == 200]
            if 'indexability' in df.columns:
                df = df[df['indexability'].astype(str).str.lower() == 'indexable']

        self.clean_df = df.reset_index(drop=True)
        return self.clean_df

    # Add this at the bottom of app/parsers/screaming_frog.py:

def parse_screaming_frog_csv(csv_filepath: str, html_only: bool = False, indexable_only: bool = False) -> pd.DataFrame:
    parser = ScreamingFrogParser(csv_filepath)
    return parser.parse(html_only=html_only, indexable_only=indexable_only)