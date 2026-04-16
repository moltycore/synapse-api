from pydantic import BaseModel
from typing import Optional, List


class FileContext(BaseModel):
    name: str
    content: str
    size: int


class AnalysisRequest(BaseModel):
    text: str
    mode: Optional[str] = "nexus"
    fileContext: Optional[List[FileContext]] = None
