# Pydantic schemas that will validate LLM JSON output okay??? UNDERSTOOD?!?!?!? 

import re
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

REAL_BRANDS = re.compile(
    r"\b(hdfc|icici|sbi|axis bank|kotak|yes bank|pnb|bank of baroda|"
    r"paypal|amazon|google|microsoft|apple|netflix|paytm|phonepe)\b",
    re.I,
)
ALLOWED_HOST = re.compile(r"(\.example|\.test|\.invalid|^localhost|^scam-demo\.xyz)$", re.I)
URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
TEN_DIGITS = re.compile(r"\b\d{10}\b")

class ScenarioSchema(BaseModel):
    category: str
    difficulty: str
    channel: str
    sender: str
    subject: str | None = None
    body: str
    is_scam: bool
    correct_answer: str
    explanation: str
    red_flags: list[str] = Field(default_factory=list)

    @field_validator("correct_answer")
    @classmethod
    def answer_valid(cls, v):
        v = str(v).strip().lower()
        if v not in ("scam", "legit"):
            raise ValueError("correct_answer must be 'scam' or 'legit'")
        return v

    @field_validator("difficulty")
    @classmethod
    def difficulty_valid(cls, v):
        v = str(v).strip().lower()
        if v not in ("easy", "medium", "hard"):
            raise ValueError("difficulty must be easy/medium/hard")
        return v

    # "after" validators see ALL FIELDS
    @model_validator(mode="after")
    def consistent(self):
        if self.is_scam != (self.correct_answer=="scam"):
            raise ValueError("is_scam doesn't match correct_answer")
        return self

    def is_safe(self) -> bool:
        '''REJECT ANYTHING THAT COULD POINT TO A REAL SITE OR A PERSON (bro, we wanna protect our legal AHH)'''
        text = " ".join(str(v) for v in self.model_dump().values())
        if REAL_BRANDS.search(text) or TEN_DIGITS.search(text):
            return False
        for u in URL_RE.findall(text):
            host = urlparse(u.rstrip(".,);")).hostname or ""
            if not ALLOWED_HOST.search(host):
                return False
        for dom in re.findall(r"@([\w.\-]+)", text): #This will email and UPI STYLE ids~
            if not ALLOWED_HOST.search(dom.rstrip(".")):
                return False
        return True

class VerdictExplanationSchema(BaseModel):
    explanation: str

class NewsClassificationSchema(BaseModel):
    is_security_relevant:bool
    reason: str=""
    
