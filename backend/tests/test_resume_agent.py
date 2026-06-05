import fitz

from backend.agents.resume_agent import ResumeAgent


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


def test_parse_resume(tmp_path):
    pdf_path = tmp_path / "sample_resume.pdf"
    create_sample_pdf(str(pdf_path))

    agent = ResumeAgent()
    resume = agent.parse(str(pdf_path))

    assert resume.name == "John Doe"
    assert "Python" in resume.skills
    assert "B.Tech Computer Science" in resume.education
