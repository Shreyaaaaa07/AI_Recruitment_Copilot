from backend.services.embedding_service import EmbeddingService


def test_similarity_score():
    service = EmbeddingService()
    score = service.similarity(
        "FastAPI Backend Development",
        "REST API Development"
    )

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
