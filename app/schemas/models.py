from pydantic import BaseModel
from typing import Optional

class Soru(BaseModel):
    text: str
    mode: Optional[str] = "nexus"
