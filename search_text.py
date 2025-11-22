import streamlit as st
import sqlite3
import database  # Import your database module
import authenticator as auth  # Assuming you still want authentication for searching
import datetime # For date handling

# --- Streamlit App UI ---
st.set_page_config(page_title="搜索聊天记录", layout="wide")
st.title("🔎 搜索聊天记录")

# Check authentication status first
if not st.session_state.get("authenticated"):
    auth.show_login_page()  # Redirect to login if not authenticated
    st.stop()  # Stop further execution of this script until authenticated

# Retrieve current user's ID and username
current_username = st.session_state.get('username')
current_user = database.get_user_by_username(current_username)
current_user_id = current_user['id'] if current_user else None

if not current_user_id:
    st.error("无法获取当前用户信息，请尝试重新登录。")
    st.stop()

# Determine if the current user is an admin
is_admin = (current_username == "admin")

# Define available models for selection
AVAILABLE_MODELS = {
    "DeepSeek-R1": "deepseek-ai/DeepSeek-R1",
    "DeepSeek-V3": "deepseek-ai/DeepSeek-V3",
    "DeepSeek-R1-70B": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    "DeepSeek-R1-14B": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
}


# --- Search/Display Function ---
def display_chat_results(search_results, title_prefix=""):
    """Helper function to display chat results in a consistent format."""
    if search_results:
        st.subheader(f"{title_prefix} 找到 {len(search_results)} 个相关会话:")
        for session in search_results:
            expander_title = (
                f"用户: **{session['username']}** | "  # Display username
                f"会话 ID: {session['session_id']} | "
                f"模型: {session['model_name']} | "
                f"开始时间: {session['started_at']}"
            )
            with st.expander(expander_title):
                st.write("---")  # Separator for clarity within expander
                for message in session['messages']:
                    role_name = "human" if message['role'] == "user" else "ai"
                    with st.chat_message(name=role_name):
                        st.markdown(message['content'])
                        st.caption(f"_{message['created_at']}_")  # Optional: show message timestamp
                st.write("---")  # Separator for clarity within expander
    else:
        st.info(f"{title_prefix} 未找到聊天记录。")


def search_chat_history(user_id, search_type, search_value, is_admin_user):
    conn = database.create_connection()
    results = []
    if conn:
        try:
            cursor = conn.cursor()

            query = """
                SELECT
                    cs.session_id,
                    u.username,
                    cs.model_name,
                    cs.started_at,
                    cm.role,
                    cm.content,
                    cm.created_at
                FROM
                    chat_messages cm
                JOIN
                    chat_sessions cs ON cm.session_id = cs.session_id
                JOIN
                    users u ON cs.user_id = u.id
                WHERE
                    1=1
            """
            params = []

            # Add user ID restriction for non-admin users
            if not is_admin_user and search_type != "by_username": # Admins can search by username for all users
                query += " AND cs.user_id = ?"
                params.append(user_id)
            elif search_type == "by_username" and not is_admin_user:
                 st.error("您没有权限按用户名搜索其他用户。")
                 return [] # Prevent non-admin from searching by username

            # Add conditions based on search_type
            if search_type == "by_keyword" and search_value:
                query += " AND cm.content LIKE ?"
                params.append(f'%{search_value}%')
            elif search_type == "by_model" and search_value:
                query += " AND cs.model_name = ?"
                params.append(search_value)
            elif search_type == "by_date" and search_value:
                # Ensure date format is correct for database comparison
                query += " AND DATE(cs.started_at) = ?"
                params.append(search_value) # Assuming search_value is already 'YYYY-MM-DD'
            elif search_type == "by_username" and search_value:
                # This condition is specifically for admin to search by username
                query += " AND u.username LIKE ?"
                params.append(f'%{search_value}%')
            elif search_type == "all": # For "查看全部" button
                # No specific content/model/date/username filter needed, user_id filter already handled
                pass
            else: # If search_type or search_value is empty/invalid for a specific search
                # This case might cover the initial load or empty search inputs for specific types
                if search_type != "all": # Only show warning for non-"all" empty searches
                    st.warning("请输入有效的搜索条件。")
                return []


            query += " ORDER BY cs.started_at DESC, cm.created_at ASC;"

            cursor.execute(query, tuple(params))
            raw_results = cursor.fetchall()

            session_dict = {}
            for row in raw_results:
                session_id, username, model_name, started_at, role, content, created_at = row
                if session_id not in session_dict:
                    session_dict[session_id] = {
                        "session_id": session_id,
                        "username": username,
                        "model_name": model_name,
                        "started_at": started_at,
                        "messages": []
                    }
                session_dict[session_id]["messages"].append({
                    "role": role,
                    "content": content,
                    "created_at": created_at
                })
            results = list(session_dict.values())

        except sqlite3.Error as e:
            st.error(f"数据库查询失败: {e}")
        except Exception as e:
            st.error(f"处理搜索请求时发生错误: {e}")
        finally:
            conn.close()
    return results


# --- Search Interface ---
st.info(f"当前用户: **{current_username}** {'(管理员)' if is_admin else '(普通用户)'}")

search_option = st.radio(
    "选择查找方式:",
    ("关键词查找", "模型查找", "日期查找") + (("用户名查找",) if is_admin else ()), # Only show username search for admin
    key="search_option_radio"
)

search_value = None
selected_model_api_name = None

if search_option == "关键词查找":
    search_value = st.text_input("请输入关键词：", placeholder="例如：人工智能、Python 代码", key="keyword_input")
elif search_option == "模型查找":
    model_display_names = list(AVAILABLE_MODELS.keys())
    selected_model_display_name = st.selectbox("选择模型：", options=model_display_names, key="model_select_box")
    selected_model_api_name = AVAILABLE_MODELS[selected_model_display_name] if selected_model_display_name else None
    search_value = selected_model_api_name # Set search_value to the API name of the selected model
elif search_option == "日期查找":
    date_input = st.date_input("选择日期：", key="date_picker")
    search_value = date_input.strftime('%Y-%m-%d') if date_input else None # Format date to 'YYYY-MM-DD'
elif search_option == "用户名查找" and is_admin:
    search_value = st.text_input("请输入用户名：", placeholder="例如：testuser", key="username_input")


col1, col2 = st.columns([3, 1]) # Use columns for input and buttons

with col1:
    st.write("") # Add some vertical space
    search_button = st.button("开始查找", use_container_width=True) # Changed button text
with col2:
    st.write("") # Add some vertical space
    st.write("") # Add some vertical space
    view_all_button = st.button("查看全部", use_container_width=True)

# Handle button clicks
if search_button:
    if search_value: # Check if search_value is valid for the selected option
        actual_search_type = {
            "关键词查找": "by_keyword",
            "模型查找": "by_model",
            "日期查找": "by_date",
            "用户名查找": "by_username",
        }.get(search_option)

        with st.spinner(f"正在按 {search_option} 查找..."):
            search_results = search_chat_history(current_user_id, actual_search_type, search_value, is_admin)
        display_chat_results(search_results, title_prefix="查找结果")
    else:
        st.warning(f"请为 '{search_option}' 输入有效的查找条件。")
elif view_all_button:
    with st.spinner("正在加载全部聊天记录..."):
        # Call search_chat_history with "all" type and no specific search value
        all_results = search_chat_history(current_user_id, "all", None, is_admin)
    display_chat_results(all_results, title_prefix="全部聊天记录")