from pydantic import BaseModel


class MatchRequest(BaseModel):

    resume_path: str

    job_description: str