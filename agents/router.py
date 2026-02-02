# agents/router.py
from agents.greetings import is_greeting, greeting_response
from agents.intent_matcher import match_intent
from agents.sql_agent import run_sql_from_intent
from agents.sqlcoder_agent import run_sqlcoder
from rag.rag_agent import run_rag_agent
from agents.entity_resolver import resolve_entities
from agents.param_extractor import extract_range_params
from agents.agents_normalizer import normalize_text
from safety.policy import is_allowed_question
from observability.tracer import TraceRun
from agents.disambiguator import (
    detect_ambiguity,
    build_clarification_response,
    handle_user_selection
)

import re
import streamlit as st


# -------------------------
# UTILS
# -------------------------

def extract_required_params(sql: str):
    return set(re.findall(r":(\w+)", sql))


def has_local_entity(entities: dict) -> bool:
    """
    Toute présence de localité bloque SQLCoder
    """
    return any(k in entities for k in ["commune", "region", "code_circo", "location"])


# -------------------------
# ROUTER (LEVEL 3 AGENTIC)
# -------------------------

def route(question: str):

    trace = TraceRun(question)

    # 0️⃣ AMBIGUÏTÉ EN COURS
    if "pending_ambiguity" in st.session_state:
        trace.log("pending_ambiguity_active")

        selection = handle_user_selection(question)
        if selection:
            trace.log("ambiguity_resolved", selection)

            response = {
                "type": "info",
                "answer": (
                    f"Parfait 👍 Nous utiliserons désormais : "
                    f"{selection['commune']} — {selection['region']} "
                    f"(circonscription {selection['code_circo']})."
                )
            }

            trace.finish(response["answer"])
            st.session_state.setdefault("traces", []).append(trace.to_dict())
            return response

        trace.finish("Awaiting clarification")
        st.session_state.setdefault("traces", []).append(trace.to_dict())
        return {
            "type": "clarification",
            "answer": "Merci de préciser votre choix en répondant par un numéro 🙏"
        }

    # 1️⃣ SALUTATIONS
    if is_greeting(question):
        trace.log("greeting_detected")
        response = greeting_response(question=question)

        trace.finish(response["answer"])
        st.session_state.setdefault("traces", []).append(trace.to_dict())
        return response

    # 2️⃣ SÉCURITÉ
    if not is_allowed_question(question):
        trace.log("security_blocked")

        response = {
            "type": "refusal",
            "answer": "Ce type de question n'est pas autorisé."
        }

        trace.finish(response["answer"])
        st.session_state.setdefault("traces", []).append(trace.to_dict())
        return response

    # 3️⃣ DÉTECTION D’AMBIGUÏTÉ
    ambiguity = detect_ambiguity(question)
    trace.log("ambiguity_check", {"found": bool(ambiguity)})

    if ambiguity:
        st.session_state["pending_ambiguity"] = ambiguity
        response = build_clarification_response(ambiguity)

        trace.finish(response["answer"])
        st.session_state.setdefault("traces", []).append(trace.to_dict())
        return response

    # 4️⃣ NORMALISATION
    q_norm = normalize_text(question)
    trace.log("normalization_done", {"normalized": q_norm})

    # 5️⃣ ENTITÉS & PARAMÈTRES
    entities = resolve_entities(q_norm)
    trace.log("entities_resolved", entities)

    if "resolved_entities" in st.session_state:
        entities |= st.session_state["resolved_entities"]

    params = entities | extract_range_params(q_norm)
    trace.log("params_extracted", params)

    # 6️⃣ INTENT MATCHING
    trace.log("intent_detection_start")
    intent = match_intent(q_norm)
    trace.log("intent_result", {"intent": intent["id"] if intent else None})

    if intent:
        required = extract_required_params(intent["sql"])
        missing = required - params.keys()

        if missing:
            trace.log("missing_parameters", list(missing))

            response = {
                "type": "clarification",
                "answer": "Pouvez-vous préciser : " + ", ".join(sorted(missing))
            }

            trace.finish(response["answer"])
            st.session_state.setdefault("traces", []).append(trace.to_dict())
            return response

        # 🔹 SQL GENERATION
        trace.log("sql_generation", {"sql": intent["sql"]})
        trace.log("sql_validation", {"status": "ok"})

        response = run_sql_from_intent(intent, params, trace=trace)

        trace.log(
            "sql_execution",
            {
                "rows": len(response.get("table", [])) if response.get("table") is not None else 0
            }
        )

        trace.finish(response.get("answer", ""))
        st.session_state.setdefault("traces", []).append(trace.to_dict())
        return response

    # 7️⃣ SQLCODER
    if not has_local_entity(entities):
        trace.log("sqlcoder_attempt")

        sqlcoder_response = run_sqlcoder(q_norm)

        trace.log("sqlcoder_result", {"type": sqlcoder_response.get("type")})

        if sqlcoder_response.get("type") in ["sql", "sqlcoder"]:
            trace.finish(sqlcoder_response.get("answer", ""))
            st.session_state.setdefault("traces", []).append(trace.to_dict())
            return sqlcoder_response

    # 8️⃣ RAG
    trace.log("rag_fallback")
    response = run_rag_agent(q_norm)

    trace.finish(response.get("answer", ""))
    st.session_state.setdefault("traces", []).append(trace.to_dict())
    return response
