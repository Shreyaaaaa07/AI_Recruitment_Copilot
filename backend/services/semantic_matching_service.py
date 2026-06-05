from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


class SemanticMatchingService:

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    @lru_cache(maxsize=128)
    def _encode(self, text: str):
        return self.model.encode(
            text,
            convert_to_tensor=True
        )

    def calculate_similarity(
        self,
        resume_text: str,
        job_text: str
    ):

        resume_embedding = self._encode(resume_text)
        job_embedding = self._encode(job_text)

        similarity = cos_sim(
            resume_embedding,
            job_embedding
        )

        return float(
            similarity.item() * 100
        )



