# rag/build_index.py
import os
import duckdb
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json

DB_PATH = "data/db/elections.duckdb"
INDEX_PATH = "data/processed/faiss.index"
META_PATH = "data/processed/faiss_meta.json"

def row_to_text(row):
    return (
        f"Region {row['region']}, "
        f"circonscription {row['code_circo']}, "
        f"commune {row['commune']}. "
        f"Candidate {row['candidat']} from {row['parti']} "
        f"received {row['voix']} votes "
        f"({row['voix_pct']}%). "
        f"Elected: {'yes' if row['elu'] == 1 else 'no'}. "
        f"Turnout: {row['taux_part']}%."
    )

def build_index():
    print("🔹 Building FAISS index...")

    os.makedirs("data/processed", exist_ok=True)

    # 1. Load data
    con = duckdb.connect(DB_PATH)
    df = con.execute("""
        SELECT
            region,
            commune,
            candidat,
            parti,
            voix,
            voix_pct,
            elu
        FROM results
    """).df()

    if df.empty:
        raise RuntimeError("❌ results table is empty")

    # 2. Convert rows to text
    texts = []
    metadata = []

    for idx, row in df.iterrows():
        texts.append(row_to_text(row))
        metadata.append({
            "row_id": idx,
            "region": row["region"],
            "commune": row["commune"],
            "candidat": row["candidat"],
            "parti": row["parti"]
        })

    # 3. Embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    # 4. FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(np.array(embeddings).astype("float32"))

    # 5. Save index
    faiss.write_index(index, INDEX_PATH)

    # 6. Save metadata
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("✅ FAISS index created")
    print(f"📁 {INDEX_PATH}")
    print(f"📁 {META_PATH}")
    print(f"📊 Indexed rows: {len(texts)}")

if __name__ == "__main__":
    build_index()
