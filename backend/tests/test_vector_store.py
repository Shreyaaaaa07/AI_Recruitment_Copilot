from backend.services.embedding_service import EmbeddingService
from backend.services.vector_store_service import VectorStoreService


def test_vector_store_search():
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService(dimension=384)

    candidates = [
        ("Python FastAPI AWS", {"name": "Candidate 1"}),
        ("React JavaScript", {"name": "Candidate 2"}),
        ("Machine Learning PyTorch", {"name": "Candidate 3"})
    ]

    for text, metadata in candidates:
        vector_store.add_candidate(
            embedding_service.get_embedding(text),
            metadata
        )

    query_embedding = embedding_service.get_embedding("Backend Engineer Python AWS")
    results = vector_store.search(query_embedding)

    assert isinstance(results, list)
    assert any(item.get("name") == "Candidate 1" for item in results)

