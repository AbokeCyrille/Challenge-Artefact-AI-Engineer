import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, index_path: str, meta_path: str):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.read_index(index_path)

        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(self, query: str, k: int = 5):
        q_emb = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        D, I = self.index.search(
            np.array(q_emb).astype("float32"),
            k
        )

        results = []
        for idx in I[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results
