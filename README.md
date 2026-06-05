# AI Recruitment Copilot

AI Recruitment Copilot is a recruitment support system designed to help HR teams and hiring managers automatically parse job descriptions, evaluate candidate resumes, score candidate fit, and rank the strongest matches using AI and semantic search techniques.

## Project overview

The goal of this project is to make candidate sourcing and screening faster and more reliable by combining several AI-powered capabilities:

- Job Description Parsing: Understand skills, qualifications, responsibilities, and role expectations from posted job descriptions.
- Resume Understanding: Extract candidate experience, education, skills, and achievements from uploaded resumes.
- Semantic Matching: Compare candidate profiles to job requirements using embeddings and vector similarity rather than simple keyword matching.
- Candidate Scoring & Ranking: Score each candidate for a role and rank the top matches to simplify decision-making.

## Key features

- `backend/agents/`: custom AI agent logic that reads jobs, resumes, and computes candidate scores.
- `backend/services/`: modular services for embeddings, vector search, matching, ranking, and prompt-based reasoning.
- `backend/schemas/`: strongly typed request and domain models to keep backend inputs and outputs consistent.
- `backend/data/`: dataset and training data used by the system.
- `frontend/app.py`: lightweight frontend interface for interacting with the project.

## Architecture

1. A job description is submitted and analyzed for required skills and priorities.
2. Candidate resumes are processed and converted into structured representations.
3. Both job and candidate data are embedded into a vector space.
4. Semantic similarity and scoring logic identify the best candidate matches.
5. The system returns ranked candidates along with scoring details.

## Repository structure

- `backend/`
  - `main.py`: backend application entrypoint
  - `agents/`: AI agent implementation for job descriptions, resumes, and scoring
  - `schemas/`: domain models and request schemas
  - `services/`: embedding, matching, ranking, semantic search, and vector store services
  - `data/`: training data and dataset resources
  - `tests/`: unit tests for backend components
- `frontend/`
  - `app.py`: frontend application
- `docs/`
  - project documentation and notes
- `uploads/`
  - sample resume and candidate assets used for testing

## Setup

1. Create and activate a Python virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install backend dependencies:

   ```powershell
   pip install -r backend/requirements.txt
   ```

3. (Optional) If the frontend has additional dependencies, install them separately.

## Running

- Start the backend from the repository root:

  ```powershell
  python backend/main.py
  ```

- Start the frontend from the repository root:

  ```powershell
  python frontend/app.py
  ```

## Testing

Run backend tests with:

```powershell
pytest backend/tests
```

## Recommended improvements

- Add a `.gitignore` file to exclude `.venv/`, `__pycache__/`, and other local artifacts.
- Document any API endpoints, environment variables, or external service keys required by the backend.
- Add deployment instructions for production usage.

## Notes

This repository is a starting point for an AI-driven recruitment copilot. As the project evolves, you can extend it with support for more resume formats, additional job scoring criteria, a richer web UI, and integration with applicant tracking systems (ATS).