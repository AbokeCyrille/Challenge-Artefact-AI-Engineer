GREETINGS = [
    "bonjour", "bonsoir", "salut", "ça va", "ca va", "comment ca va", "comment ça va ?", "qui es-tu",
    "hello", "hi", "good morning", "good evening", "how are you", "who are you", "qui es-tu ?"
]

def is_greeting(question: str) -> bool:
    q = question.lower()
    return any(g in q for g in GREETINGS)

def greeting_response(question: str):
    q = question.lower()
    
    # --- DÉTECTION ANGLAIS ---
    is_english = any(w in q for w in ["hello", "hi", "good", "how", "who"])
    
    if is_english:
        intro = "👋 Hello! I am your AI Electoral Assistant. I'm doing well, thank you! "
        if "who" in q or "qui" in q:
            intro = "🤖 I am an AI specialized in analyzing Ivory Coast election results from official PDF data. "
            
        return {
            "type": "static",
            "answer": (
                f"{intro}I can answer your questions based on the official dataset.\n\n"
                "Examples:\n"
                "- How many seats did RHDP win?\n"
                "- Voter turnout by region\n"
                "- Draw a pie chart of blank ballots"
            )
        }
    
    # --- RÉPONSE FRANÇAIS (PAR DÉFAUT) ---
    intro = "👋 Bonjour ! Je suis votre assistant IA électoral. Je vais très bien, merci ! "
    if any(w in q for w in ["qui", "who", "présente", "presente"]):
        intro = "🤖 Je suis une IA spécialisée dans l'analyse des résultats électoraux de Côte d'Ivoire basés sur le PDF officiel. "
        
    return {
        "type": "static",
        "answer": (
            f"{intro}Je peux répondre à vos questions analytiques avec des tableaux et graphiques.\n\n"
            "Exemples :\n"
            "- Combien de sièges a remporté le PDCI ?\n"
            "- Taux de participation par région\n"
            "- Fais un diagramme circulaire des bulletins blancs"
        )
    }