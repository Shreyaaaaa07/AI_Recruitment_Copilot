from pydantic import BaseModel
from typing import List


class Resume(BaseModel):
    name: str
    email: str
    phone: str

    skills: List[str]

    education: List[str]

    experience: List[str]

    certifications: List[str]

    projects: List[str]