from sentence_transformers import SentenceTransformer
from sentence_transformers import util


class EmbeddingService:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def get_embedding(
        self,
        text: str
    ):

        return self.model.encode(text)

    def similarity(
        self,
        text1: str,
        text2: str
    ):

        emb1 = self.model.encode(
            text1,
            convert_to_tensor=True
        )

        emb2 = self.model.encode(
            text2,
            convert_to_tensor=True
        )

        score = util.cos_sim(
            emb1,
            emb2
        )

        return float(score)