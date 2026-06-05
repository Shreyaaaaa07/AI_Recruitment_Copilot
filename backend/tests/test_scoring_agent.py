from backend.agents.scoring_agent import ScoringAgent
from backend.schemas.resume import Resume
from backend.schemas.job import JobDescription


def test_evaluate_scores():
    resume = Resume(
        name="John Doe",
        email="john@gmail.com",
        phone="1234567890",
        skills=["Python", "AWS", "FastAPI"],
        education=["B.Tech Computer Science"],
        experience=["Software Engineer"],
        certifications=[],
        projects=["Resume Screener"]
    )

    job = JobDescription(
        job_title="Backend Engineer",
        required_skills=["Python", "AWS", "FastAPI"],
        preferred_skills=["Docker"],
        experience_required="3+ years",
        education_requirement="Bachelor Degree"
    )

    result = ScoringAgent().evaluate(resume, job)

    assert result.overall_score == 86
    assert result.recommendation == "Shortlist"
