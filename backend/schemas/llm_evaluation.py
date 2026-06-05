from pydantic import BaseModel
from typing import List


class LLMEvaluation(BaseModel):

    overall_score: int

    skill_match_score: int

    experience_match_score: int

    education_match_score: int

    strengths: List[str]

    gaps: List[str]

    recommendation: str