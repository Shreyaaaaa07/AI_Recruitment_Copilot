from pydantic import BaseModel
from typing import List, Optional


class StrengthsRequest(BaseModel):
    resume_path: str


class SummarizeRequest(BaseModel):
    resume_path: str


class InterviewQuestionRequest(BaseModel):
    resume_path: str
    job_description: str


class SearchRequest(BaseModel):
    resume_paths: List[str]
    query: str


class ChatRequest(BaseModel):
    prompt: str
    resume_paths: Optional[List[str]] = None
