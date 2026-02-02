import faiss
import pickle
from sentence_transformers import SentenceTransformer
from agents.agents_normalizer import normalize_text

INDEX_PATH = "data/rag/faiss.index"
ROWS_PATH = "data/rag/rows.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(INDEX_PATH)
rows = pickle.load(open(ROWS_PATH, "rb"))

def run_rag_agent(question: str, k=3):
    q_norm = normalize_text(question)
    q_emb = model.encode([q_norm])

    distances, indices = index.search(q_emb, k)

    hits = []
    for idx, dist in zip(indices[0], distances[0]):
        r = rows[idx]
        hits.append({
            "row_id": r["row_id"],
            "table": r["table"],
            "excerpt": r["text"],
            "score": round(float(dist), 4)
        })

    if not hits:
        return {
            "type": "rag",
            "answer": "Aucune information pertinente trouvée dans le dataset.",
            "sources": []
        }

    return {
        "type": "rag",
        "answer": "Voici des informations pertinentes issues du dataset électoral.",
        "sources": hits
    }
