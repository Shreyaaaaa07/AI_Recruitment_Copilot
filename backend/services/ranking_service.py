from backend.agents.resume_agent import ResumeAgent
from backend.agents.jd_agent import JDAgent
from backend.services.matching_service import MatchingService
from backend.services.llm_service import LLMService

class RankingService:

    def __init__(self):

        self.resume_agent = ResumeAgent()

        self.jd_agent = JDAgent()

        self.matching_service = MatchingService()

        self.llm_service = LLMService()

    def rank_candidates(
        self,
        resume_paths: list,
        job_description: str
    ):

        job = self.jd_agent.parse(
            job_description
        )

        results = []

        for resume_path in resume_paths:

            resume = self.resume_agent.parse(
                resume_path
            )

            score = self.matching_service.calculate_skill_match(
                resume,
                job
            )

            print("Job Skills:", job.required_skills)
            print("Resume Skills:", resume.skills)

            if score.overall_score >= 80:
                recommendation = "Strong Hire"
            elif score.overall_score >= 60:
                recommendation = "Interview"
            else:
                recommendation = "Reject"

            feedback = self.llm_service.generate_feedback(
                resume.name,
                score.matched_skills,
                score.missing_skills,
                score.overall_score,
            )

            total_required = (
                len(score.matched_skills) +
                len(score.missing_skills)
            )

            results.append(
                {
                    "candidate": resume.name,
                    "resume_path": resume_path,
                    "score": score.overall_score,
                    "semantic_score": score.semantic_score,
                    "matched_skills": score.matched_skills,
                    "missing_skills": score.missing_skills,
                    "skills_match": f"{len(score.matched_skills)}/{total_required}",
                    "matched_count": len(score.matched_skills),
                    "required_count": total_required,
                    "recommendation": recommendation,
                    "ai_feedback": feedback,
                }
            )

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        top_candidate = results[0]["candidate"] if results else None

        return {
            "top_candidate": top_candidate,
            "rankings": results
        }