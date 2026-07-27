from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class AuditSection(BaseModel):
    score: Optional[int] = Field(None, ge=0, le=100, description="Normalized score out of 100")
    status: str = Field("pending", description="Status: success, warning, error, pending")
    findings: List[str] = Field(default_factory=list, description="Key bullet points or risks identified")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Underlying raw metrics")

class ClientAuditRecord(BaseModel):
    client_domain: str
    audit_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    overall_score: Optional[int] = None
    
    # 9 Core Service Areas
    security: AuditSection = Field(default_factory=AuditSection)
    ai_readiness: AuditSection = Field(default_factory=AuditSection)
    website_health: AuditSection = Field(default_factory=AuditSection)
    onpage_seo: AuditSection = Field(default_factory=AuditSection)
    gdpr_cookies: AuditSection = Field(default_factory=AuditSection)
    technical_seo: AuditSection = Field(default_factory=AuditSection)
    analytics_tracking: AuditSection = Field(default_factory=AuditSection)
    content_strategy: AuditSection = Field(default_factory=AuditSection)
    cro_ux: AuditSection = Field(default_factory=AuditSection)

    def calculate_overall_score(self) -> int:
        scores = [s.score for s in [self.security, self.ai_readiness, self.website_health, self.onpage_seo, self.gdpr_cookies, self.technical_seo, self.analytics_tracking, self.content_strategy, self.cro_ux] if s.score is not None]
        if not scores:
            return 0
        self.overall_score = round(sum(scores) / len(scores))
        return self.overall_score
