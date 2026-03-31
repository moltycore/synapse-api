from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    text: str
    mode: Optional[str] = "nexus"
