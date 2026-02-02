import streamlit as st

def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            if "text" in msg:
                st.markdown(msg["text"])

            if "table" in msg:
                st.dataframe(msg["table"], use_container_width=True)

            if "chart" in msg and msg["chart"] is not None:
                st.pyplot(msg["chart"])

            if "source" in msg:
                st.caption(
                    f"📄 Source — page {msg['source'].get('page')} | table {msg['source'].get('table')}"
                )
