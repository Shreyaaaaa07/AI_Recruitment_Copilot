import faiss
import numpy as np


class VectorStoreService:

    def __init__(
        self,
        dimension
    ):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.metadata = []

    def add_candidate(
        self,
        embedding,
        candidate_data
    ):

        vector = np.array(
            [embedding]
        ).astype("float32")

        self.index.add(vector)

        self.metadata.append(
            candidate_data
        )

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        query_vector = np.array(
            [query_embedding]
        ).astype("float32")

        distances, indices = (
            self.index.search(
                query_vector,
                top_k
            )
        )

        results = []

        for idx in indices[0]:
            results.append(
                self.metadata[idx]
            )

        return results