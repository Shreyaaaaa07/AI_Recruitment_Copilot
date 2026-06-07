from email.mime import text
from unittest import result

import fitz
import re
import pytesseract
from PIL import Image

from backend.schemas.resume import Resume

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

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

            page_text = page.get_text()

            text += page_text

            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))

            img = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            ocr_text = pytesseract.image_to_string(
                img,
                config="--oem 3 --psm 11"
            )

            text += "\n" + ocr_text

        doc.close()

        text = re.sub(r"\s+", " ", text)

        print("\n===== OCR RESULT =====")
        print(text[:2000])
        print("======================")

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

        lines = text.split()

        for i in range(len(lines) - 1):

            first = lines[i].strip()
            second = lines[i + 1].strip()

            candidate = f"{first} {second}"

            if (
                first.isalpha()
                and second.isalpha()
                and len(first) > 2
                and len(second) > 2
            ):

                blacklist = [
                    "Computer Science",
                    "Software Development",
                    "Data Analytics",
                    "Machine Learning",
                    "Deep Learning",
                    "Software Engineer",
                    "Computer Engineer",
                    "Data Scientist"
                ]

                if candidate not in blacklist:
                    return candidate

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

        print("\n================ RAW TEXT START ================\n")
        print(text[:1000])
        print("\n================ RAW TEXT END ==================\n")

        name = self.extract_name(text)

        print("\nNAME FOUND:", name)

        print("Extracted Name:", name)

        if not name:
            import os
            name = os.path.basename(pdf_path)
            name = name.replace(".pdf", "")

        result = {
            "name": name,
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "education": [],
            "experience": [],
            "certifications": [],
            "projects": []
        }

        print("Candidate Name:", result["name"])
        print("Skills Found:", result["skills"])

        return Resume(**result)

        