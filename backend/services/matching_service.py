from backend.schemas import job
from backend.schemas.resume import Resume
from backend.schemas.job import JobDescription
from backend.schemas.candidate_score import CandidateScore
from backend.services.semantic_matching_service import SemanticMatchingService


SKILL_ALIASES = {
    "aws": ["amazon web services"],
    "sql": ["mysql", "postgresql"],
    "python": ["python programming"],
    "javascript": ["js"]
}

ALIAS_LOOKUP = {
    alias: canonical
    for canonical, aliases in SKILL_ALIASES.items()
    for alias in aliases + [canonical]
}


class MatchingService:

    def __init__(self):

        self.semantic_service = SemanticMatchingService()

    def _normalize_skill(self, skill: str) -> str:
        normalized = skill.strip().lower()
        return ALIAS_LOOKUP.get(normalized, normalized)

    def calculate_skill_match(
        self,
        resume: Resume,
        job: JobDescription
    ):

        # ----------------------------
        # Skill Match
        # ----------------------------

        resume_skills = {
            self._normalize_skill(skill)
            for skill in resume.skills
        }

        required_skills = {
            self._normalize_skill(skill)
            for skill in job.required_skills
        }

        matched_skills = sorted(
            resume_skills.intersection(required_skills)
        )

        missing_skills = sorted(
            required_skills - resume_skills
        )

        if len(required_skills) == 0:
            skill_score = 0
        else:
            skill_score = (
                len(matched_skills)
                /
                len(required_skills)
            ) * 100

        # ----------------------------
        # Semantic Score
        # ----------------------------

        resume_text = " ".join(
            resume.skills +
            resume.experience +
            resume.projects
        )

        job_text = " ".join(
            job.required_skills +
            job.preferred_skills +
            [job.job_title]
        )

        semantic_score = (
            self.semantic_service.calculate_similarity(
                resume_text,
                job_text
            )
        )

        # ----------------------------
        # Experience Score
        # ----------------------------

        experience_score = 100

        if len(resume.experience) == 0:
            experience_score = 50

        # ----------------------------
        # Education Score
        # ----------------------------

        education_score = 100

        if len(resume.education) == 0:
            education_score = 50

        # ----------------------------
        # Final ATS Score
        # ----------------------------

        overall_score = (
            0.50 * skill_score +
            0.30 * semantic_score +
            0.10 * experience_score +
            0.10 * education_score
        )

        return CandidateScore(
            overall_score=round(
            overall_score,
            2
        ),
            skill_score=round(
            skill_score,
            2
        ),
            semantic_score=round(
            semantic_score,
            2
        ),
            matched_skills=matched_skills,
            missing_skills=missing_skills
    )