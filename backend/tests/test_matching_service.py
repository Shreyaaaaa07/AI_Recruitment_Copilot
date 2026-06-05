import fitz

from backend.agents.resume_agent import ResumeAgent
from backend.agents.jd_agent import JDAgent
from backend.services.matching_service import MatchingService


def create_sample_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), """John Doe
Email: john@gmail.com
Phone: 1234567890
Skills: Python, AWS, FastAPI
Education: B.Tech Computer Science
Experience: Software Engineer""")
    doc.save(path)
    doc.close()


def test_calculate_skill_match(tmp_path):
    pdf_path = tmp_path / "sample_resume.pdf"
    create_sample_pdf(str(pdf_path))

    resume = ResumeAgent().parse(str(pdf_path))
    job = JDAgent().parse(
        """
        Backend Engineer

        Required:
        Python
        FastAPI
        AWS
        """
    )

    result = MatchingService().calculate_skill_match(resume, job)

    assert result.overall_score == 100.0
    assert "python" in [skill.lower() for skill in result.matched_skills]
