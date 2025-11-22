import streamlit as st
import database  # Import your database module
import authenticator as auth  # Assuming authentication is still needed

st.set_page_config(page_title="搜索用户", layout="centered")
st.title("👥 搜索用户")

# --- Authentication Check ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    auth.show_login_page()
    st.stop()

# --- Admin Check ---
current_username = st.session_state.get('username')
if current_username != "admin":
    st.error("您没有权限访问此页面。")
    st.stop()

st.info(f"当前用户: **{current_username}** (管理员)")


# --- Search Functionality ---
def get_user_by_criteria(search_type, search_value):
    conn = database.create_connection()
    users = []
    if conn:
        try:
            cursor = conn.cursor()
            if search_type == "username":
                cursor.execute("SELECT id, username, email FROM users WHERE username LIKE ?", (f"%{search_value}%",))
            elif search_type == "email":
                cursor.execute("SELECT id, username, email FROM users WHERE email LIKE ?", (f"%{search_value}%",))
            else:  # For 'display_all' case, or if search_value is empty for a general search
                cursor.execute("SELECT id, username, email FROM users ORDER BY username ASC")  # Order for consistency

            raw_results = cursor.fetchall()
            for row in raw_results:
                users.append({"id": row[0], "username": row[1], "email": row[2]})
        except sqlite3.Error as e:
            st.error(f"数据库查询失败: {e}")
        finally:
            conn.close()
    return users


# --- Helper function to display user results ---
def display_user_results(users, title=""):
    if users:
        st.subheader(f"{title} 找到 {len(users)} 个用户:")
        for user in users:
            st.markdown(f"**ID:** {user['id']}, **用户名:** {user['username']}, **邮箱:** {user['email']}")
    else:
        st.info(f"{title} 未找到用户。")


# --- Streamlit UI for Search ---
search_type = st.radio(
    "选择搜索类型:",
    ("按用户名", "按邮箱"),
    key="user_search_type_radio"
)

search_value = st.text_input(
    "输入搜索值:",
    placeholder="输入用户名或邮箱地址关键词",
    key="user_search_value_input"
)

col1, col2 = st.columns(2)

with col1:
    search_button = st.button("开始搜索用户", use_container_width=True)
with col2:
    display_all_button = st.button("显示全部用户", use_container_width=True)

# Handle button clicks
if search_button:
    if search_value:
        with st.spinner("正在搜索用户..."):
            actual_search_type = "username" if search_type == "按用户名" else "email"
            found_users = get_user_by_criteria(actual_search_type, search_value)
        display_user_results(found_users, title="搜索结果")
    else:
        st.warning("请输入搜索值。")
elif display_all_button:
    with st.spinner("正在加载全部用户..."):
        # Call get_user_by_criteria with a special type or empty values to get all
        all_users = get_user_by_criteria(None, None)  # Passing None will trigger the 'else' in get_user_by_criteria
    display_user_results(all_users, title="全部用户")