import duckdb
import faiss
import pickle
from sentence_transformers import SentenceTransformer

DB_PATH = "data/db/elections.duckdb"
OUT_DIR = "data/rag"

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_rag_index():
    con = duckdb.connect(DB_PATH)
    df = con.execute("SELECT rowid, * FROM resultats").df()

    rows = []
    texts = []

    for _, r in df.iterrows():
        text = (
            f"Candidat {r.candidat}, parti {r.parti}, "
            f"région {r.region}, circonscription {r.code_circo}, "
            f"voix {r.voix}, taux participation {r.taux_part}"
        )
        rows.append({
            "row_id": int(r.rowid),
            "table": "resultats",
            "text": text
        })
        texts.append(text)

    embeddings = model.encode(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    with open(f"{OUT_DIR}/rows.pkl", "wb") as f:
        pickle.dump(rows, f)

    faiss.write_index(index, f"{OUT_DIR}/faiss.index")

if __name__ == "__main__":
    build_rag_index()
