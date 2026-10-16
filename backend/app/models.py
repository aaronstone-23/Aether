# Pydantic models!! for supabase rows and API payloads~
from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

class Verdict(BaseModel):
    job_id: str
    verdict: str = "unknown"
    confidence: str = "low"
    risk_score: int = 0
    claimed_identity: Optional[str] = ""
    red_flags: list[str] = Field(default_factory= list)
    recommended_actions: list[str] = Field(default_factory=list)
    explanation: Optional[str] = ""
    origin_country: Optional[str] = ""
    channel: Optional[str] = "email"
    created_at: Optional[datetime] = None

class AnalyzeRequest(BaseModel):
    text: str = Field(min_length= 1, max_length=20000)
    channel: str = "auto"

class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)

class ChatRequest(BaseModel):
    session_id: str = "anon"
    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatTurn] = Field(default_factory=list, max_length= 10)
    context: Optional[dict[str, Any]] = None

class PanicRequest(BaseModel):
    situation: str = ""

class DemoRegisterRequest(BaseModel):
    email: str = Field(max_length=254)
    consent: bool = False

class SimulationScoreRequest(BaseModel):
    scenario: dict[str, Any]
    answer: str  #"scam" / "Legit"
    
