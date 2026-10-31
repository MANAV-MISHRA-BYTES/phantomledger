from typing import Literal
from pydantic import BaseModel, Field


class RepositoryRequest(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class Memory(BaseModel):
    id: str
    type: str
    title: str
    score: int
    summary: str
    evidence: list[str]
    commits: list[dict]
    files: list[str]
    dates: dict[str, str | None]
    authors: list[str]
    diff_summary: str = ""


class Interpretation(BaseModel):
    title: str
    historical_summary: str
    what_is_known: list[str]
    what_is_unknown: list[str]
    interpretation: str
    confidence: Literal["high", "medium", "low"]


class ChronicleRequest(BaseModel):
    path: str

