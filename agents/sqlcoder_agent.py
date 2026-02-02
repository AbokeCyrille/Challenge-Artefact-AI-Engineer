from llama_cpp import Llama
import duckdb
import time
from agents.schema import SCHEMA
from safety.sql_validator import validate_sql
from app.charts import render_chart

DB_PATH = "data/db/elections.duckdb"
DEFAULT_LIMIT = 100
MODEL_PATH = "models/sqlcoder-7b-q5_k_m.gguf"


# -------------------------
# LLM Init (optimisé CPU)
# -------------------------

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=1024,        # suffisant pour du SQL
    n_threads=8,
    n_batch=512,       # gros gain de perf
)


# -------------------------
# SQL Generation
# -------------------------

def generate_sql(question: str) -> str:
    prompt = f"""
### Instructions:
Your task is to convert the user's natural language question into a single, valid DuckDB SQL query based on the Ivory Coast election results dataset provided below.

### Rules:
- Output ONLY a single SELECT query.
- Use ONLY the table and columns defined in the schema.
- ALWAYS include a LIMIT {DEFAULT_LIMIT} clause.
- Do not provide any explanations, comments, or prose. Just the SQL.

### Schema:
Table name: resultats
Columns and descriptions:
- region: Administrative region name (e.g., 'AGNEBY-TIASSA', 'PORO').
- code_circo: Unique numerical code for the electoral constituency.
- commune: Name of the specific commune or locality.
- candidat: Full name of the candidate or list title.
- parti: Political group or party acronym (e.g., 'RHDP', 'PDCI-RDA').
- voix: Total number of votes obtained by the candidate (Integer).
- voix_pct: Percentage of votes obtained by the candidate relative to expressed votes (Float).
- inscrits: Total number of registered voters in that area (Integer).
- votants: Total number of people who actually voted (Integer).
- taux_part: Voter turnout percentage for that specific area (Float).
- bull_nuls: Number of invalid/null ballots (Integer).
- bull_blancs_nom: Number of blank ballots (Integer).
- bull_blancs_pct: Percentage of blank ballots (Float).
- elu: Winner indicator. Use 'WHERE elu = 1' to find elected candidates or lists.

### Question:
{question}

### SQL:
"""
    output = llm(
        prompt,
        max_tokens=200,
        stop=["###"],     # on enlève ";"
        temperature=0
    )

    return output["choices"][0]["text"].strip().rstrip(";")


# -------------------------
# SQLCoder Agent
# -------------------------

CHART_KEYWORDS = {
    "bar": ["bar", "classement", "top", "ranking"],
    "hist": ["histogramme", "distribution"],
    "pie": ["répartition", "part", "pourcentage"],
    "line": ["évolution", "trend"]
}

def detect_chart_type(question: str):
    q = question.lower()
    for chart_type, keywords in CHART_KEYWORDS.items():
        if any(k in q for k in keywords):
            return chart_type
    return None


def run_sqlcoder(question: str):
    start_time = time.time()

    try:
        sql = generate_sql(question)
        validate_sql(sql)

        if not sql.lower().startswith("select"):
            return {
                "type": "refusal",
                "answer": "Seules les requêtes SELECT sont autorisées."
            }

        if "limit" not in sql.lower():
            sql = f"{sql} LIMIT {DEFAULT_LIMIT}"

        con = duckdb.connect(DB_PATH, read_only=True)
        df = con.execute(sql).df()

        if df.empty:
            return {
                "type": "no_answer",
                "answer": "Aucune donnée correspondante dans le dataset."
            }

        # Détection graphique
        chart_type = detect_chart_type(question)
        chart = None
        if chart_type:
            chart = render_chart(df, chart_type)

        return {
            "type": "sqlcoder", 
            "answer": "Voici les résultats extraits du dataset électoral.",
            "table": df,
            "chart": chart,
            "meta": {
                "agent": "sqlcoder",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "rows": len(df)
            }
        }

    except Exception as e:
        return {
            "type": "error",
            "answer": f"Je ne connais pas la réponse à cette question."
        }

