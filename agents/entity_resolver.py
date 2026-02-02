import duckdb
from rapidfuzz import fuzz
import re
from agents.entity_registry import ENTITY_REGISTRY

DB_PATH = "data/db/elections.duckdb"


def fetch_distinct(table, column):
    con = duckdb.connect(DB_PATH)
    rows = con.execute(
        f"SELECT DISTINCT {column} FROM {table}"
    ).fetchall()
    return [r[0] for r in rows if r[0] is not None]


def resolve_entities(question: str, threshold=80):
    resolved = {}
    q_lower = question.lower()

    match_circo = re.search(r'\b(\d{1,3})\b', q_lower)
    if match_circo:
        # On formate immédiatement en 3 chiffres; c'est à dire 1 devient 001
        resolved["code_circo"] = match_circo.group(1).zfill(3)

    for name, cfg in ENTITY_REGISTRY.items():

        if name == "code_circo" and name in resolved:
            continue

        entity_type = cfg.get("type")

        # -------------------------
        # Metrics (taux_part, voix…)
        # -------------------------
        if entity_type == "metric":
            if name.replace("_", " ") in q_lower:
                resolved[name] = True
            continue

        # -------------------------
        # Boolean flags (elu, etc.)
        # -------------------------
        if entity_type == "boolean":
            if name in q_lower:
                resolved[name] = True
            continue

        # -------------------------
        # Value-based entities
        # -------------------------
        values = fetch_distinct(cfg["table"], cfg["column"])

        # 1️⃣ Aliases (safe)
        aliases = cfg.get("aliases") or {}
        if not isinstance(aliases, dict):
            raise ValueError(
                f"aliases for entity '{name}' must be a dict"
            )

        for alias, canonical in aliases.items():
            if alias.lower() in q_lower:
                resolved[name] = canonical
                break

        if name in resolved:
            continue

        # 2️⃣ Exact / substring match
        for v in values:
            if str(v).lower() in q_lower:
                resolved[name] = v
                break

        if name in resolved:
            continue

        # 3️⃣ Fuzzy match (VALUE vs QUESTION)
        if cfg.get("fuzzy"):
            best_match = None
            best_score = 0

            for v in values:
                score = fuzz.token_set_ratio(
                    str(v).lower(),
                    q_lower
                )
                if score > best_score:
                    best_score = score
                    best_match = v

            if best_score >= threshold:
                resolved[name] = best_match

    return resolved
