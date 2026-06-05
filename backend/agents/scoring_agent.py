from backend.schemas.resume import Resume
from backend.schemas.job import JobDescription
from backend.schemas.llm_evaluation import LLMEvaluation

class ScoringAgent:

    def __init__(self):
        pass

    def build_prompt(
        self,
        resume: Resume,
        job: JobDescription
    ):

        return f"""
You are a senior technical recruiter.

Evaluate the candidate.

Job Title:
{job.job_title}

Required Skills:
{job.required_skills}

Candidate Skills:
{resume.skills}

Experience:
{resume.experience}

Education:
{resume.education}

Return JSON:

{{
    "overall_score": 0-100,
    "skill_match_score": 0-100,
    "experience_match_score": 0-100,
    "education_match_score": 0-100,
    "strengths": [],
    "gaps": [],
    "recommendation": ""
}}
"""

    def mock_evaluation(self):

        return {
            "overall_score": 86,
            "skill_match_score": 90,
            "experience_match_score": 82,
            "education_match_score": 85,
            "strengths": [
                "Strong Python skills",
                "Relevant cloud experience"
            ],
            "gaps": [
                "Missing Kubernetes"
            ],
            "recommendation": "Shortlist"
        }

    def evaluate(
        self,
        resume: Resume,
        job: JobDescription
    ) -> LLMEvaluation:

        prompt = self.build_prompt(
            resume,
            job
        )

        result = self.mock_evaluation()

        return LLMEvaluation(
            **result
        )