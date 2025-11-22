import streamlit as st
import database as db # Import the new database module
"""admin  456"""
def show_layout_and_hide_sidebar():
    """Applies fullscreen layout and hides sidebar using CSS."""
    st.set_page_config(page_title="百家饭AI", layout="centered", initial_sidebar_state="collapsed")
    st.markdown("""
        <style>
            /* Streamlit's default header/footer/sidebar elements can sometimes be tricky to fully hide.
               We use display: none !important and visibility: hidden !important for robustness. */
            header, footer {
                visibility: hidden !important;
                height: 0px !important;
                display: none !important;
            }
            section[data-testid="stSidebar"] {
                display: none !important;
                visibility: hidden !important;
                width: 0 !important;
            }
            div[data-testid="stSidebarContent"] {
                display: none !important;
                visibility: hidden !important;
                width: 0 !important;
            }
            /* You might also need to adjust the main content area margin if the header removal causes issues */
            .main {
                margin-top: 0;
                padding-top: 0;
            }
        </style>
    """, unsafe_allow_html=True)
    # Ensure sidebar is empty explicitly
    st.sidebar.empty()


def show_login_page():
    show_layout_and_hide_sidebar()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("Login to 百家饭AI")

        # Login Form
        with st.form("login_form"):
            login_username = st.text_input("Username", key="form_login_username")
            login_password = st.text_input("Password", type="password", key="form_login_password")
            login_submitted = st.form_submit_button("Login")

            if login_submitted:
                user = db.get_user_by_username(login_username)
                if user and user['password'] == login_password: # In a real app, use hashed passwords!
                    st.session_state.authenticated = True
                    st.session_state.current_page = "home" # Go to home after login
                    st.session_state.user_id = user['id'] # Store user ID in session
                    st.session_state.username = user['username'] # Store username in session
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        st.markdown("---")

        # Create New User Button - placed in its own form to guarantee rerun
        with st.form("create_user_nav_form"):
            create_user_button_submitted = st.form_submit_button("创建新用户")
            if create_user_button_submitted:
                st.session_state.current_page = "create_user"
                st.rerun()


def show_create_user_page():
    show_layout_and_hide_sidebar()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("创建新用户")

        # Create User Registration Form
        with st.form("create_user_form"):
            new_username = st.text_input("用户名", key="form_new_username")
            new_password = st.text_input("密码", type="password", key="form_new_password")
            confirm_password = st.text_input("确认密码", type="password", key="form_confirm_password")
            new_email = st.text_input("邮箱", key="form_new_email")
            register_submitted = st.form_submit_button("注册")

            if register_submitted:
                if not new_username or not new_password or not confirm_password or not new_email:
                    st.error("所有字段都是必填项。")
                elif new_password != confirm_password:
                    st.error("密码和确认密码不匹配。")
                else:
                    result = db.add_user(new_username, new_email, new_password)
                    if result is True:
                        st.success(f"用户 {new_username} 创建成功！")
                        st.session_state.authenticated = True # Log in the new user automatically
                        user = db.get_user_by_username(new_username)
                        if user:
                            st.session_state.user_id = user['id']
                            st.session_state.username = user['username']
                        st.session_state.current_page = "home" # Go to home after creation
                        st.rerun()
                    elif result == "username_exists":
                        st.error("该用户名已存在，请选择其他用户名。")
                    elif result == "email_exists":
                        st.error("该邮箱已注册，请使用其他邮箱或登录。")
                    else:
                        st.error("创建用户失败，请稍后再试。")

        st.markdown("---")

        # Back to Login Button - placed in its own form to guarantee rerun
        with st.form("back_to_login_nav_form"):
            back_to_login_button_submitted = st.form_submit_button("返回登录")
            if back_to_login_button_submitted:
                st.session_state.current_page = "login"
                st.rerun()

# Initialize authentication state if not already present
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Initialize current_page state if not already present
if "current_page" not in st.session_state:
    st.session_state.current_page = "login" # Default to login page

# Initialize user_id and username in session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None