from backend.agents.jd_agent import JDAgent


def test_parse_job_description():
    agent = JDAgent()
    job = agent.parse(
        """
        Backend Engineer

        Required:
        Python
        FastAPI
        AWS
        """
    )

    assert job.job_title == "Backend Engineer"
    assert "Python" in job.required_skills
    assert "AWS" in job.required_skills
