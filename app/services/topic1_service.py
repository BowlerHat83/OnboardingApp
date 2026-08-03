import logging
import traceback
from typing import Dict, Any
from app.collectors.a11y_auditor import ComprehensiveAuditor

logger = logging.getLogger(__name__)


class Topic1Service:
    """Service layer for Topic 1: WCAG 2.2 Accessibility & Privacy/Cookie Compliance."""

    def __init__(self):
        self.auditor = ComprehensiveAuditor()

    async def execute_audit(self, url: str) -> Dict[str, Any]:
        """Runs the combined Playwright audit for WCAG 2.2 AA accessibility and cookie privacy."""
        try:
            logger.info(f"[Topic 1] Executing accessibility and privacy scan for: {url}")
            report = await self.auditor.scan_page(url)
            
            return {
                "status": "success",
                "topic": "Accessibility & Privacy",
                "data": report
            }
        except Exception as e:
            error_msg = str(e) or repr(e)
            logger.error(f"[Topic 1] Error auditing {url}: {error_msg}\n{traceback.format_exc()}")
            return {
                "status": "error",
                "topic": "Accessibility & Privacy",
                "error": error_msg
            }