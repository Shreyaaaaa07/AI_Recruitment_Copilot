from pydantic import BaseModel


class TrainingExample(BaseModel):

    resume: str

    job_description: str

    score: int

    reason: str