from backend.services.semantic_matching_service import SemanticMatchingService

service = SemanticMatchingService()

score = service.calculate_similarity(
    "Python FastAPI AWS developer",
    "Looking for Backend Engineer with Python and AWS"
)

print(score)