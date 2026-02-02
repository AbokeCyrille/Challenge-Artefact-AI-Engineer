from sentence_transformers import SentenceTransformer, util
from agents.intent_catalog import INTENTS

model = SentenceTransformer("all-MiniLM-L6-v2")

intent_embeddings = {
    intent["id"]: model.encode(intent["examples"], convert_to_tensor=True)
    for intent in INTENTS
}

def match_intent(question: str, threshold=0.6):
    q_emb = model.encode(question, convert_to_tensor=True)

    best_intent = None
    best_score = 0

    for intent in INTENTS:
        sims = util.cos_sim(q_emb, intent_embeddings[intent["id"]])
        score = sims.max().item()

        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < threshold:
        return None

    return best_intent
