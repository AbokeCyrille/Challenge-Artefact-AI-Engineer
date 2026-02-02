# observability/dataset_version.py
import hashlib
import duckdb
from datetime import datetime

DB_PATH = "data/db/elections.duckdb"


def compute_pdf_hash(path: str) -> str:
    """Compute a stable hash of the source PDF"""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def store_pdf_hash(pdf_hash: str):
    """Store the PDF hash and ingestion timestamp"""
    con = duckdb.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            pdf_hash TEXT,
            ingestion_date TIMESTAMP
        )
    """)

    con.execute("""
        INSERT INTO metadata VALUES (?, ?)
    """, (pdf_hash, datetime.utcnow()))


def get_latest_pdf_hash():
    """Return last ingested PDF hash"""
    con = duckdb.connect(DB_PATH)
    res = con.execute("""
        SELECT pdf_hash
        FROM metadata
        ORDER BY ingestion_date DESC
        LIMIT 1
    """).fetchone()

    return res[0] if res else None


def check_dataset_version(pdf_path: str):
    """
    Compare current PDF hash with stored version.
    Raises error if dataset changed.
    """
    current = compute_pdf_hash(pdf_path)
    stored = get_latest_pdf_hash()

    if stored and stored != current:
        raise RuntimeError(
            "⚠️ Dataset version mismatch. "
            "PDF has changed. Re-ingestion required."
        )

    if not stored:
        store_pdf_hash(current)
