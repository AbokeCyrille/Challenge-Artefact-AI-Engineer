# agents/disambiguator.py

# agents/disambiguator.py

import unicodedata
import re
import duckdb
import streamlit as st

DB_PATH = "data/db/elections.duckdb"

# -------------------------
# ALIASES & NORMALISATION
# -------------------------

ALIASES = {
    "rhdp": "RHDP",
    "r.h.d.p": "RHDP",
    "R.H.D.P":"RHDP",
    "pdcirda": "PDCI-RDA",
    "pdci": "PDCI-RDA",
    "pdci rda": "PDCI-RDA",
}

STOPWORDS = {
    "who", "won", "win", "winner", "result", "results",
    "in", "at", "the", "show", "top", "of",
    "de", "du", "dans", "a", "au", "la", "le"
}

def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

def normalize_entities(question: str) -> str:
    q = question.lower()
    q = strip_accents(q)
    q = re.sub(r"[^\w\s-]", " ", q)

    for alias, canonical in ALIASES.items():
        q = q.replace(alias, canonical.lower())

    return re.sub(r"\s+", " ", q).strip()

# -------------------------
# DB LOOKUP
# -------------------------

def _lookup_location(name: str):
    """
    Recherche large : commune OU région
    + détection de scope (commune / region)
    """
    con = duckdb.connect(DB_PATH, read_only=True)

    query = """
    SELECT DISTINCT
        region,
        commune,
        code_circo,
        CASE
            WHEN LOWER(commune) LIKE LOWER(?) THEN 'commune'
            WHEN LOWER(region) LIKE LOWER(?) THEN 'region'
            ELSE 'unknown'
        END AS scope
    FROM resultats
    WHERE LOWER(commune) LIKE LOWER(?)
       OR LOWER(region) LIKE LOWER(?)
    """

    rows = con.execute(
        query,
        (name, name, f"%{name}%", f"%{name}%")
    ).fetchall()

    return [
        {
            "region": r[0],
            "commune": r[1],
            "code_circo": r[2],
            "scope": r[3]
        }
        for r in rows
    ]

# -------------------------
# AMBIGUITY DETECTION
# -------------------------

def detect_ambiguity(question: str):
    """
    Détecte automatiquement les entités ambiguës
    (localités multi-scopes ou multi-circonscriptions)
    """
    q = normalize_entities(question)
    tokens = q.split()

    for token in tokens:
        if token in STOPWORDS or len(token) < 3:
            continue

        matches = _lookup_location(token)

        if len(matches) > 1:
            return {
                "type": "ambiguity",
                "entity": token,
                "options": matches
            }

    return None

# -------------------------
# CLARIFICATION RESPONSE
# -------------------------

def build_clarification_response(ambiguity: dict):
    """
    Génère une clarification claire et agentique
    """
    options = ambiguity["options"]

    msg = (
        f"⚠️ **Ambiguïté détectée pour** « **{ambiguity['entity']}** ».\n\n"
        "Merci de préciser laquelle tu veux :\n"
    )

    for i, opt in enumerate(options, 1):
        label = opt["commune"] or opt["region"]
        msg += (
            f"\n**{i}.** {label} — "
            f"{opt['region']} "
            f"(scope: {opt['scope']}, circonscription {opt['code_circo']})"
        )

    msg += "\n\n👉 Réponds simplement par le numéro (ex: `1`)."

    return {
        "type": "clarification",
        "answer": msg,
        "options": options
    }

# -------------------------
# SESSION MEMORY (LEVEL 3 BONUS)
# -------------------------

def handle_user_selection(user_input: str):
    """
    Intercepte une réponse utilisateur type "1", "2", etc.
    et mémorise le choix pour la session
    """
    if "pending_ambiguity" not in st.session_state:
        return None

    if not user_input.strip().isdigit():
        return None

    idx = int(user_input.strip()) - 1
    ambiguity = st.session_state["pending_ambiguity"]

    if idx < 0 or idx >= len(ambiguity["options"]):
        return None

    choice = ambiguity["options"][idx]

    # mémoire de session
    st.session_state.setdefault("resolved_entities", {})
    st.session_state["resolved_entities"]["location"] = choice

    del st.session_state["pending_ambiguity"]

    return choice
