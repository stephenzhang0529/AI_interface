import streamlit as st
import authenticator as auth # Assuming you have an authenticator.py

# Placeholder for successful authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Placeholder for current page, default to 'login'
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

if st.session_state.authenticated:
    # Get the current username to determine admin status
    current_username = st.session_state.get('username')
    is_admin = (current_username == "admin")

    nav = {
        "AI TYPE": [
            st.Page("llm.py", title="LLM"),
            st.Page("vlm.py", title="VLM"),
            st.Page("word_image.py", title="WORD TO IMAGE"),
            st.Page("mcp.py", title="MCP"),
            st.Page("space_invaders.py", title="SPACE INVADERS"),
            st.Page("search_text.py", title="SEARCH CHAT"),
            st.Page("change.py", title="ACCOUNT MGR"),
            st.Page("about.py", title="ABOUT"),
        ],
    }

    # Add 'Search User' page only if the user is admin
    if is_admin:
        nav["AI TYPE"].append(st.Page("search_user.py", title="SEARCH USER"))

    pg = st.navigation(nav)
    pg.run()
elif st.session_state.current_page == "create_user":
    auth.show_create_user_page()
else: # Default to login page
    auth.show_login_page()