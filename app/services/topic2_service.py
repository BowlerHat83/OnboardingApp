import os
import glob
import subprocess
import logging
from typing import Dict, Any, Optional

# Import your Screaming Frog parser from the parsers folder
from app.parsers.screaming_frog import parse_screaming_frog_csv # adjust function name if different

logger = logging.getLogger(__name__)

class Topic2Service:
    def __init__(self):
        # Update path to match your OS:
        # Windows: r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"
        # Mac: "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/ScreamingFrogSEOSpiderLauncher"
        self.sf_path = r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"
        self.export_dir = os.path.abspath("temp_exports")

    def run_cli_crawl(self, url: str) -> Optional[str]:
        """Executes Screaming Frog CLI and outputs CSV to temp_exports."""
        os.makedirs(self.export_dir, exist_ok=True)

        cmd = [
            self.sf_path,
            "--headless",
            "--crawl", url,
            "--output-folder", self.export_dir,
            "--export-tabs", "Internal:All",
            "--overwrite"
        ]

        logger.info(f"[Topic 2] Executing CLI: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            logger.info(f"[Topic 2] CLI Output Return Code: {result.returncode}")

            # Look for generated CSV inside temp_exports (including subfolders created by SF)
            csv_files = glob.glob(os.path.join(self.export_dir, "**", "*.csv"), recursive=True)
            if csv_files:
                logger.info(f"[Topic 2] Found CSV export: {csv_files[0]}")
                return csv_files[0]
            
            logger.error("[Topic 2] Screaming Frog finished but no CSV was found.")
            return None

        except Exception as e:
            logger.error(f"[Topic 2] Failed to execute Screaming Frog CLI: {str(e)}")
            return None

    async def execute_audit(self, url: str) -> Dict[str, Any]:
        # 1. Automatically run the CLI crawl
        csv_path = self.run_cli_crawl(url)

        # 2. Parse results using your existing parser module
        parsed_data = {}
        if csv_path and os.path.exists(csv_path):
            parsed_data = parse_screaming_frog_csv(csv_path)
        else:
            logger.warning("[Topic 2] Proceeding without Screaming Frog CSV data.")

        return {
            "status": "success",
            "topic": "Topic 2: Technical SEO & Infrastructure",
            "screaming_frog_data": parsed_data
        }