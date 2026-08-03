import os
import glob
import subprocess
import pandas as pd

# Import the exact parser class from app/parsers/screaming_frog.py
from app.parsers.screaming_frog import ScreamingFrogParser


# CONFIGURATION
TARGET_URL = "https://example.com"  # Replace with the URL you want to crawl
EXPORT_DIR = os.path.abspath("temp_exports")

# Screaming Frog CLI path for Windows
SF_CLI_PATH = r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"


def run_crawl(url: str, output_folder: str) -> str | None:
    os.makedirs(output_folder, exist_ok=True)
    
    cmd = [
        SF_CLI_PATH,
        "--headless",
        "--crawl", url,
        "--output-folder", output_folder,
        "--export-tabs", "Internal:All",
        "--overwrite"
    ]
    
    print(f"\n[1/3] Launching Screaming Frog CLI for: {url}")
    print(f"      Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"[2/3] CLI finished with exit code: {result.returncode}")
        
        if result.returncode != 0:
            print(f"      STDERR Output:\n{result.stderr[:500]}")
            return None
            
        # Screaming Frog saves output inside output_folder (sometimes in a subfolder)
        csv_files = glob.glob(os.path.join(output_folder, "**", "*.csv"), recursive=True)
        
        if csv_files:
            print(f"      Success! Found CSV: {csv_files[0]}")
            return csv_files[0]
        else:
            print(f"      ERROR: Screaming Frog finished, but no CSV was found in {output_folder}")
            return None

    except FileNotFoundError:
        print(f"      ERROR: Screaming Frog executable not found at: {SF_CLI_PATH}")
        return None
    except Exception as e:
        print(f"      ERROR: Failed during execution: {str(e)}")
        return None


if __name__ == "__main__":
    # 1. Run the crawl
    csv_path = run_crawl(TARGET_URL, EXPORT_DIR)
    
    # 2. Parse the CSV using your ScreamingFrogParser
    if csv_path:
        print("\n[3/3] Parsing CSV data...")
        
        # Instantiate your class with the file path
        parser = ScreamingFrogParser(csv_filepath=csv_path)
        
        # Run parse()
        df = parser.parse()
        
        print("\n================ DATA RECEIVED ================")
        print(f"Total Rows Parsed: {len(df)}")
        print(f"Columns Found: {list(df.columns)}")
        print("\nFirst 3 rows preview:")
        print(df.head(3))
        print("===============================================")
    else:
        print("\nPipeline failed before parsing could take place.")