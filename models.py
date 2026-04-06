from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class WalletSignal(BaseModel):
    wallet: str
    market_slug: str
    initial_score: float = 0.0
    breakdown: Dict = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    thematique: str
    position_size: float = 0.0
    age_days: Optional[int] = None
    risk_level: str = "Medium"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DebateResult(BaseModel):
    final_verdict: str
    confidence: int
    summary: str
    key_arguments: List[str]
    risk_assessment: str
    recommendation: str
    thematique: str