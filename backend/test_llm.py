from backend.services.llm_service import LLMService

llm = LLMService()

result = llm.generate(
    "Explain why Python is good for backend development."
)

print(result)