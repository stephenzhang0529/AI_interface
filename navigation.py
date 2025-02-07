import streamlit as st

nav = {
    "AI TYPE": [
        st.Page("llm.py", title="LLM"),
        st.Page("word_image.py", title="WORD TO IMAGE"),
    ],
}

pg = st.navigation(nav)
pg.run()