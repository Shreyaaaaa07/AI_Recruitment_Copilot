import json
import ollama
import logging

logger = logging.getLogger(__name__)


class LLMService:

    def _call_llm(self, prompt: str):
        try:
            response = ollama.chat(
                model="llama3",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            return f"AI service unavailable: {str(e)}"

    def _parse_json_list(self, text: str, key: str):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and key in data and isinstance(data[key], list):
                return data[key]
        except json.JSONDecodeError:
            pass

        lines = []
        for line in text.splitlines():
            stripped = line.strip().lstrip("-*").strip()
            if stripped:
                lines.append(stripped)
        return lines

    def generate_feedback(
        self,
        candidate_name,
        matched_skills,
        missing_skills,
        score
    ):

        prompt = f"""
You are a technical recruiter.

Candidate: {candidate_name}

Score: {score}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Provide:

1. Summary
2. Strengths
3. Skill Gaps
4. Interview Recommendation

Keep response under 150 words.
"""

        return self._call_llm(prompt)

    def extract_strengths(
        self,
        candidate_name,
        resume_text
    ):
        prompt = f"""
You are a technical recruiter reviewing a resume.

Candidate: {candidate_name}

Resume:
{resume_text}

Return a JSON object with a single key `strengths` containing the candidate's top 5 strengths as an array.
"""

        response = self._call_llm(prompt)
        return self._parse_json_list(response, "strengths")

    def generate_interview_questions(
        self,
        candidate_name,
        missing_skills,
        job_title
    ):
        prompt = f"""
You are a technical recruiter.

Candidate: {candidate_name}
Job Title: {job_title}
Missing Skills: {missing_skills}

Return a JSON object with a single key `questions` containing 3–5 personalized interview questions that test the candidate's gaps.
"""

        response = self._call_llm(prompt)
        return self._parse_json_list(response, "questions")

    def summarize_resume(
        self,
        candidate_name,
        resume_text
    ):
        prompt = f"""
You are a technical recruiter.

Candidate: {candidate_name}

Resume:
{resume_text}

Return a JSON object with a single key `summary` containing 4 concise bullet points about this candidate.
"""

        response = self._call_llm(prompt)
        return self._parse_json_list(response, "summary")

    def chat(
        self,
        prompt: str,
        context: str = ""
    ):
        if context:
            prompt = f"Context:\n{context}\n\nUser: {prompt}"
        return self._call_llm(prompt)