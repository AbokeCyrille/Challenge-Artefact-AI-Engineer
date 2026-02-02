import streamlit as st
from app.state import init_state
from agents.router import route
from app.ui import render_chat
import time
import random

# ---------- STYLE ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #4361ee;
    --primary-light: #e8f0fe;
    --secondary: #f5f7fb;
    --text: #1a1a1a;
    --text-light: #666;
    --white: #ffffff;
    --shadow: 0 4px 12px rgba(0,0,0,0.08);
    --radius: 12px;
    --transition: all 0.3s ease;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--secondary);
    color: var(--text);
}

.stApp {
    background: var(--secondary);
}

.stTextInput>div>div>input {
    background: var(--white);
    border: 1px solid #e0e0e0;
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 14px;
    transition: var(--transition);
}

.stTextInput>div>div>input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
    outline: none;
}

.stButton>button {
    background: var(--primary);
    color: var(--white);
    border: none;
    border-radius: var(--radius);
    padding: 12px 24px;
    font-weight: 500;
    transition: var(--transition);
    box-shadow: var(--shadow);
}

.stButton>button:hover {
    background: #3a56d4;
    transform: translateY(-1px);
}

.stButton>button:active {
    transform: translateY(0);
}

.stChatInput {
    position: fixed;
    bottom: 20px;
    width: calc(100% - 40px);
    max-width: 800px;
    z-index: 100;
}

.user-message {
    background-color: var(--primary-light);
    border-radius: var(--radius) var(--radius) 0 var(--radius);
    padding: 16px;
    margin-bottom: 16px;
    position: relative;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--primary);
}

.assistant-message {
    background-color: var(--white);
    border-radius: var(--radius) var(--radius) var(--radius) 0;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: var(--shadow);
    border-right: 4px solid #e0e0e0;
}

.message-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 24px;
}

.message-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 12px;
    color: var(--text-light);
}

.message-content {
    line-height: 1.5;
}

.avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: white;
}

.user-avatar {
    background: var(--primary);
}

.assistant-avatar {
    background: #666;
}

.thinking-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-light);
    font-style: italic;
    margin: 16px 0;
}

.dot-typing {
    display: flex;
    gap: 4px;
    align-items: center;
}

.dot-typing span {
    width: 8px;
    height: 8px;
    background-color: var(--primary);
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out;
}

.dot-typing span:nth-child(1) {
    animation-delay: -0.32s;
}

.dot-typing span:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes bounce {
    0%, 80%, 100% {
        transform: scale(0);
    }
    40% {
        transform: scale(1);
    }
}

.stExpander {
    border-radius: var(--radius);
    margin-top: 24px;
    box-shadow: var(--shadow);
}

.stExpander > details > summary {
    padding: 12px 16px;
    font-weight: 500;
    color: var(--text);
}

.stExpander > details > div {
    padding: 16px;
    background: var(--white);
    border-radius: 0 0 var(--radius) var(--radius);
}

.table-container {
    overflow-x: auto;
    margin: 16px 0;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

table {
    width: 100%;
    border-collapse: collapse;
    background: var(--white);
}

th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
}

th {
    background: #f8f9fa;
    font-weight: 600;
    color: var(--text);
}

tr:hover {
    background: #f8f9fa;
}

.chart-container {
    background: var(--white);
    border-radius: var(--radius);
    padding: 16px;
    margin: 16px 0;
    box-shadow: var(--shadow);
}

.sources {
    font-size: 12px;
    color: var(--text-light);
    margin-top: 8px;
    padding: 8px;
    background: #f8f9fa;
    border-radius: var(--radius);
}

.footer {
    text-align: center;
    margin-top: 32px;
    padding: 16px;
    color: var(--text-light);
    font-size: 12px;
    border-top: 1px solid #e0e0e0;
}

@media (max-width: 768px) {
    .stApp {
        padding: 16px 8px;
    }

    .user-message, .assistant-message {
        padding: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- CONFIG ----------
st.set_page_config(
    page_title="EDAN Election Chat",
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- HEADER ----------
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Ivory_Coast.svg/1200px-Flag_of_Ivory_Coast.svg.png", width=60)
with col2:
    st.title("🗳️ EDAN Election Chat")
    st.caption("Analysez les résultats officiels des élections ELECTION DES DEPUTES A L'ASSEMBLEE NATIONALE — basés exclusivement sur les données du PDF officiel")

# ---------- STATE ----------
init_state()

# ---------- CHAT HISTORY ----------
chat_container = st.container()

def display_message(message):
    role = message["role"]
    text = message["text"]

    if role == "user":
        avatar = "👤"
        avatar_class = "user-avatar"
        message_class = "user-message"
    else:
        avatar = "🤖"
        avatar_class = "assistant-avatar"
        message_class = "assistant-message"

    with st.chat_message(role):
        st.markdown(f"""
        <div class="message-container">
            <div class="message-header">
                <div class="{avatar_class}">{avatar}</div>
                <span>{role.capitalize()} • {time.strftime("%H:%M", time.localtime())}</span>
            </div>
            <div class="message-content">{text}</div>
            {"<div class='sources'>Sources: " + message.get("sources", "") + "</div>" if "sources" in message else ""}
        </div>
        """, unsafe_allow_html=True)

        if "table" in message:
            st.markdown("<div class='table-container'>", unsafe_allow_html=True)
            st.table(message["table"])
            st.markdown("</div>", unsafe_allow_html=True)

        if "chart" in message:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.pyplot(message["chart"])
            st.markdown("</div>", unsafe_allow_html=True)

with chat_container:
    for message in st.session_state.messages:
        display_message(message)

# ---------- OBSERVABILITY ----------
with st.expander("🔍 **Observabilité – Traces de débogage**", expanded=False):
    if "traces" in st.session_state and st.session_state["traces"]:
        st.json(st.session_state["traces"])
    else:
        st.info("Aucune trace enregistrée pour l'instant. Posez une question pour commencer.")

# ---------- INPUT ----------
if question := st.chat_input("Posez votre question sur les résultats des élections ivoiriennes 2020..."):
    # Ajout du message utilisateur
    st.session_state.messages.append({
        "role": "user",
        "text": question
    })

    # Affichage immédiat du message utilisateur
    display_message(st.session_state.messages[-1])

    # Indicateur de réflexion
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("""
        <div class="thinking-indicator">
            <div class="dot-typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span>Analyse des données électorales en cours...</span>
        </div>
        """, unsafe_allow_html=True)

    # Traitement de la question
    with st.spinner(""):
        response = route(question)

    # Suppression de l'indicateur de réflexion
    thinking_placeholder.empty()

    # Préparation du message assistant
    msg = {
        "role": "assistant",
        "text": response.get("answer", "Aucune réponse trouvée dans les données électorales.")
    }

    if response.get("table") is not None:
        msg["table"] = response["table"]

    if response.get("chart") is not None:
        msg["chart"] = response["chart"]

    if response.get("sources") is not None:
        msg["sources"] = response["sources"]

    # Ajout et affichage du message assistant
    st.session_state.messages.append(msg)
    display_message(msg)

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
    <p>Données officielles des élections ivoiriennes 2025 • EDAN Election Chat v1.0</p>
</div>
""", unsafe_allow_html=True)
