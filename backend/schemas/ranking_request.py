from pydantic import BaseModel
from typing import List


class RankingRequest(BaseModel):

    resume_paths: List[str]

    job_description: str