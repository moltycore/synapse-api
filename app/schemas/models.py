from pydantic import BaseModel, field_validator
from typing import Optional, List, Literal

MAX_TEXT_LENGTH = 5000
MAX_FILE_COUNT = 5
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE_BYTES = 10 * 1024 * 1024


class FileContext(BaseModel):
    name: str
    content: str
    size: int

    @field_validator("size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File exceeds 10MB limit.")
        return v


class AnalysisRequest(BaseModel):
    text: str
    mode: Literal["nexus", "solo"] = "nexus"
    fileContext: Optional[List[FileContext]] = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Input cannot be empty.")
        if len(v) > MAX_TEXT_LENGTH:
            raise ValueError(f"Input exceeds {MAX_TEXT_LENGTH} character limit.")
        return v

    @field_validator("fileContext")
    @classmethod
    def validate_files(cls, v: Optional[List[FileContext]]) -> Optional[List[FileContext]]:
        if not v:
            return v
        if len(v) > MAX_FILE_COUNT:
            raise ValueError(f"Max {MAX_FILE_COUNT} files allowed.")
        total = sum(f.size for f in v)
        if total > MAX_TOTAL_SIZE_BYTES:
            raise ValueError("Total file size exceeds 10MB limit.")
        return v
