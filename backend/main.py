from fastapi import FastAPI, UploadFile, File
import os
import shutil

from backend.agents.resume_agent import ResumeAgent
from backend.agents.jd_agent import JDAgent
from backend.services.matching_service import MatchingService
from backend.services.llm_service import LLMService
from backend.services.semantic_matching_service import SemanticMatchingService
from backend.schemas.match_request import MatchRequest
from backend.services.ranking_service import RankingService
from backend.schemas.ranking_request import RankingRequest
from backend.schemas.ai_requests import (
    StrengthsRequest,
    SummarizeRequest,
    InterviewQuestionRequest,
    SearchRequest,
    ChatRequest,
)


app = FastAPI(
    title="AI Recruitment Copilot"
)

resume_agent = ResumeAgent()
jd_agent = JDAgent()
matching_service = MatchingService()
ranking_service = RankingService()
llm_service = LLMService()
semantic_service = SemanticMatchingService()


@app.get("/")
def home():
    return {
        "message": "AI Recruitment Copilot Running"
    }


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "path": file_path
    }

from pydantic import BaseModel


class JobInput(BaseModel):
    job_description: str


@app.post("/upload-job")
async def upload_job(
    job: JobInput
):

    parsed_job = jd_agent.parse(
        job.job_description
    )

    return parsed_job.model_dump()

@app.post("/match-candidate")
async def match_candidate(
    request: MatchRequest
):

    resume = resume_agent.parse(
        request.resume_path
    )

    job = jd_agent.parse(
        request.job_description
    )

    score = matching_service.calculate_skill_match(
        resume,
        job
    )

    return score.model_dump()

@app.post("/rank-candidates")
async def rank_candidates(
    request: RankingRequest
):

    results = ranking_service.rank_candidates(
        request.resume_paths,
        request.job_description
    )

    return results


@app.post("/extract-strengths")
async def extract_strengths(
    request: StrengthsRequest
):

    resume = resume_agent.parse(
        request.resume_path
    )

    resume_text = resume_agent.extract_text(
        request.resume_path
    )

    strengths = llm_service.extract_strengths(
        resume.name,
        resume_text
    )

    return {
        "strengths": strengths
    }


@app.post("/summarize-resume")
async def summarize_resume(
    request: SummarizeRequest
):

    resume = resume_agent.parse(
        request.resume_path
    )

    resume_text = resume_agent.extract_text(
        request.resume_path
    )

    summary = llm_service.summarize_resume(
        resume.name,
        resume_text
    )

    return {
        "summary": summary
    }


@app.post("/generate-interview-questions")
async def generate_interview_questions(
    request: InterviewQuestionRequest
):

    resume = resume_agent.parse(
        request.resume_path
    )

    job = jd_agent.parse(
        request.job_description
    )

    score = matching_service.calculate_skill_match(
        resume,
        job
    )

    questions = llm_service.generate_interview_questions(
        resume.name,
        score.missing_skills,
        job.job_title
    )

    return {
        "questions": questions
    }


@app.post("/search-candidates")
async def search_candidates(
    request: SearchRequest
):

    results = []

    for resume_path in request.resume_paths:

        resume = resume_agent.parse(
            resume_path
        )

        resume_text = resume_agent.extract_text(
            resume_path
        )

        similarity = semantic_service.calculate_similarity(
            resume_text,
            request.query
        )

        results.append(
            {
                "candidate": resume.name,
                "resume_path": resume_path,
                "score": round(similarity, 2)
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "results": results
    }


@app.post("/chat")
async def chat(
    request: ChatRequest
):

    context = ""

    if request.resume_paths:
        lines = []
        for resume_path in request.resume_paths:
            resume = resume_agent.parse(
                resume_path
            )
            lines.append(
                f"{resume.name}: skills={resume.skills}, education={resume.education}, experience={resume.experience}"
            )
        context = "\n".join(lines)

    response = llm_service.chat(
        request.prompt,
        context
    )

    return {
        "response": response
    }



