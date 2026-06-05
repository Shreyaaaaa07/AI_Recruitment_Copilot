from backend.schemas.job import JobDescription


class JDAgent:

    KNOWN_SKILLS = [
        "python",
        "java",
        "c++",
        "aws",
        "docker",
        "kubernetes",
        "fastapi",
        "django",
        "flask",
        "react",
        "tensorflow",
        "pytorch",
        "sql",
        "mongodb",
        "postgresql",
        "machine learning",
        "deep learning",
        "langchain",
        "langgraph",
        "llm",
        "generative ai"
    ]

    def __init__(self):
        pass

    def extract_title(
        self,
        job_description: str
    ):

        lines = job_description.strip().split("\n")

        if len(lines) > 0:
            return lines[0].strip()

        return "Unknown Role"

    def extract_skills(
        self,
        job_description: str
    ):

        text = job_description.lower()

        skills = []

        for skill in self.KNOWN_SKILLS:

            if skill in text:
                skills.append(skill)

        return list(set(skills))

    def parse(
        self,
        job_description: str
    ) -> JobDescription:

        title = self.extract_title(
            job_description
        )

        skills = self.extract_skills(
            job_description
        )

        return JobDescription(
            job_title=title,
            required_skills=skills,
            preferred_skills=[],
            experience_required="",
            education_requirement=""
        )
