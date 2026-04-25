from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone

class WalletSignal(BaseModel):
    wallet: str
    market_slug: str  # <--- On utilise bien ce nom
    initial_score: float = 0.0
    breakdown: Dict = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    thematique: str
    position_size: float = 0.0
    age_days: Optional[int] = None
    risk_level: str = "Medium"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DebateResult(BaseModel):
    final_verdict: str
    confidence: int
    summary: str
    key_arguments: List[str]
    risk_assessment: str
    recommendation: str
    thematique: str