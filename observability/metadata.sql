-- metadata.sql
-- Dataset versioning & ingestion metadata

CREATE TABLE IF NOT EXISTS metadata (
    pdf_hash TEXT NOT NULL,
    ingestion_date TIMESTAMP NOT NULL
);
