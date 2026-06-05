import fitz
import re

from backend.schemas.resume import Resume


class ResumeAgent:

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

    def extract_text(self, pdf_path: str) -> str:

        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        text = re.sub(r"\s+", " ", text)

        print("\n========== RESUME ==========\n")
        print(text)
        print("============================\n")

        return text.strip()

    def extract_email(self, text: str) -> str:

        match = re.search(
            r"[\w\.-]+@[\w\.-]+\.\w+",
            text
        )

        if match:
            return match.group()

        return ""

    def extract_phone(self, text: str) -> str:

        match = re.search(
            r"(\+?\d[\d\s\-]{8,15})",
            text
        )

        if match:
            return match.group()

        return ""

    def extract_name(self, text: str) -> str:

        words = text.split()

        if len(words) >= 2:
            return f"{words[0]} {words[1]}"

        elif len(words) == 1:
            return words[0]

        return ""

    def extract_skills(self, text: str):

        text_lower = text.lower()

        skills = []

        for skill in self.KNOWN_SKILLS:

            if skill in text_lower:
                skills.append(skill)

        return list(set(skills))

    def parse(self, pdf_path: str) -> Resume:

        text = self.extract_text(pdf_path)

        result = {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "education": [],
            "experience": [],
            "certifications": [],
            "projects": []
        }

        print("Skills Found:", result["skills"])

        return Resume(**result)