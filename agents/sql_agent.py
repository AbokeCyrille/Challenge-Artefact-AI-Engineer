import duckdb
import re
from safety.sql_validator import validate_sql
from app.charts import render_chart

DB_PATH = "data/db/elections.duckdb"
DEFAULT_LIMIT = 100


# -----------------------------
# SQL utilities
# -----------------------------

def extract_sql_params(sql: str):
    """
    Extract named parameters from SQL (e.g. :region, :parti)
    """
    return re.findall(r":(\w+)", sql)


def apply_limit(sql: str, limit: int = DEFAULT_LIMIT) -> str:
    """
    Enforce a LIMIT if none is present
    """
    if "LIMIT" not in sql.upper():
        return f"{sql.strip()} LIMIT {limit}"
    return sql


def prepare_sql(sql: str, params: dict):
    """
    Convert :param -> ? and return ordered values
    """
    param_names = extract_sql_params(sql)

    values = []
    for name in param_names:
        if name not in params:
            raise ValueError(f"Missing required SQL parameter: {name}")
        values.append(params[name])

    # DuckDB-compatible placeholders
    sql_prepared = re.sub(r":\w+", "?", sql)

    return sql_prepared, values


# -----------------------------
# Main SQL agent
# -----------------------------

def run_sql_from_intent(intent: dict, params: dict | None = None, trace=None):
    sql = intent["sql"]
    validate_sql(sql)

    sql = apply_limit(sql)
    params = params or {}

    try:
        sql_prepared, values = prepare_sql(sql, params)
        con = duckdb.connect(DB_PATH, read_only=True)
        df = con.execute(sql_prepared, values).df()

    except Exception as e:
        return {
            "type": "error",
            "answer": f"SQL execution failed: {str(e)}"
        }

    chart = None
    if intent.get("chart_capable"):
        # choix simple : premier graphique supporté
        chart_type = intent["chart_capable"][0]
        chart = render_chart(
            df=df,
            chart_type=chart_type,
            trace=trace
        )

    return {
        "type": "sql",
        "answer": "Voici les résultats extraits du dataset électoral.",
        "table": df,
        "chart": chart
    }
