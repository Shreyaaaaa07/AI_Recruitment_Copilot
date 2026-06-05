from pydantic import BaseModel
from typing import List

class CandidateScore(BaseModel):

    overall_score: float

    skill_score: float

    semantic_score: float

    matched_skills: List[str]

    missing_skills: List[str]