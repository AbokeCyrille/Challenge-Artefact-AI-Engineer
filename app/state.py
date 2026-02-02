import streamlit as st

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
