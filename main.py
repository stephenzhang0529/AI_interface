import streamlit as st

nav = {
    "AI TYPE": [
        st.Page("llm.py", title="LLM"),
        st.Page("vlm.py", title="VLM"),
        st.Page("word_image.py", title="WORD TO IMAGE"),
        st.Page("space_invaders.py", title="SPACE INVADERS"),
    ],
}

pg = st.navigation(nav)
pg.run()