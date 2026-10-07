from pydantic import BaseModel, Field
from typing import List, Literal


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=3, max_length=12000)


class Finding(BaseModel):
    category: str
    explanation: str
    severity: Literal["low", "medium", "high"]


class AnalyzeResponse(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal["Safe", "Suspicious", "High Risk", "Critical Risk"]
    verdict: str
    findings: List[Finding]
    recommendation: str
    engine: Literal["AI", "Rule-based"]
