import streamlit as st
import requests
import json
import os
import authenticator as auth
import database # Import the database module

# --- Configuration ---
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ["API_KEY"]
# CHAT_HISTORY_FILE = 'chat_history.json' # No longer needed for file-based saving

# Mapping from user-friendly display names to actual model identifiers for the API
MODEL_PREFIX = "deepseek-ai/"
MODEL_OPTIONS_MAP = {
    "DeepSeek-R1": f"{MODEL_PREFIX}DeepSeek-R1",
    "DeepSeek-V3": f"{MODEL_PREFIX}DeepSeek-V3",  # As per original list
    "DeepSeek-R1-70B": f"{MODEL_PREFIX}DeepSeek-R1-Distill-Llama-70B",
    "DeepSeek-R1-14B": f"{MODEL_PREFIX}DeepSeek-R1-Distill-Qwen-14B",
}


# --- Helper Functions (removed file-based load/save, now use database) ---
# def load_chat_history():
#     if os.path.exists(CHAT_HISTORY_FILE):
#         try:
#             with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             st.error(f"Error reading chat history file '{CHAT_HISTORY_FILE}'. File might be corrupted.")
#             return []
#     return []


# def save_chat_history(messages):
#     try:
#         with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
#             json.dump(messages, f, ensure_ascii=False, indent=4)
#     except IOError as e:
#         st.error(f"Error saving chat history: {e}")


def asktoai(user_input, system_prompt_content, conversation_history, model_option, max_tokens_val, top_p_val):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    api_messages = []
    if system_prompt_content and system_prompt_content.strip():
        api_messages.append({"role": "system", "content": system_prompt_content})
    for i, msg_content in enumerate(conversation_history):
        role = "user" if i % 2 == 0 else "assistant"
        api_messages.append({"role": role, "content": msg_content})
    api_messages.append({"role": "user", "content": user_input})

    payload = {
        "model": model_option,  # This will now use the prefixed model name
        "messages": api_messages,
        "stream": False,
        "max_tokens": max_tokens_val,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": top_p_val,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }

    try:
        with st.spinner("AI正在思考中..."):
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("choices") and len(response_data["choices"]) > 0 and response_data["choices"][0].get(
                "message"):
            ai_response = response_data["choices"][0]["message"]["content"]
            return ai_response.strip() if ai_response else "error: empty response from AI"
        else:
            st.error("API响应格式不正确或choices为空。")
            st.json(response_data)
            return "error: API response format issue"
    except requests.exceptions.Timeout:
        st.error("API请求超时。请稍后再试或增加超时时间。")
        return "error: request timeout"
    except requests.exceptions.RequestException as e:
        st.error(f"API请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"服务器响应码: {e.response.status_code}")
            st.text(f"错误详情: {e.response.text}")
            try:
                st.json(e.response.json())
            except json.JSONDecodeError:
                pass
        return "error: request failed"
    except Exception as e:
        st.error(f"处理API请求时发生未知错误: {e}")
        return "error: unknown processing error"


# --- Streamlit App UI ---
st.set_page_config(page_title="百家饭AI", layout="wide")
st.title("百家饭AI")

# Check authentication status first
if not st.session_state.get("authenticated"):
    auth.show_login_page() # Redirect to login if not authenticated
    st.stop() # Stop further execution of this script until authenticated

# Retrieve current user's ID
# Assuming 'username' is stored in session_state after successful login
current_username = st.session_state.get('username')
current_user = database.get_user_by_username(current_username)
current_user_id = current_user['id'] if current_user else None

if not current_user_id:
    st.error("无法获取当前用户信息，请尝试重新登录。")
    st.stop()


# Sidebar for settings
with st.sidebar:
    st.header("⚙️ 设置")

    # Model selection
    display_model_names = list(MODEL_OPTIONS_MAP.keys())
    selected_display_name = st.selectbox(
        "选择模型:",
        options=display_model_names,
        index=0,
        placeholder="选择一个模型...",
        key="model_select",  # This key associates with selected_display_name state
        help="选择您想使用的AI模型。"
    )
    # The actual model identifier to be used in API calls
    model_selected = MODEL_OPTIONS_MAP[selected_display_name]

    st.subheader("📝 System Prompt")
    system_prompt_input = st.text_area(
        "设定AI的角色或行为指令:",
        placeholder="例如：你是一个乐于助人的AI助手，请用中文回答所有问题。",
        height=120,
        key="system_prompt_area",
        help="在这里输入全局指令，AI会在每次对话时参考这个提示。"
    )

    st.subheader("🛠️ 参数调整")
    max_token_val = st.slider(
        "Max Tokens:",
        min_value=50, max_value=8192, value=2048, step=64, key="max_token_slider",
        help="AI回复的最大长度（以tokens计算）。"
    )
    top_p_slider_val = st.slider(
        "Temperature:",
        min_value=0.0, max_value=1.0, value=0.7, step=0.01, key="top_p_slider",
        help="控制输出文本的随机性。较低的值使输出更集中和确定性，较高的值更多样化。\n(原代码中此滑块名为Temperature，但实际控制API的top_p参数，temperature参数固定为0.7)"
    )


if 'messages' not in st.session_state:
    if not st.session_state.get('messages'):
        st.session_state.messages = []
# Initialize session state for the current model in use for saving
if 'current_session_model' not in st.session_state:
    st.session_state.current_session_model = model_selected


for i, msg_content in enumerate(st.session_state.messages):
    role_name = "human" if i % 2 == 0 else "ai"
    with st.chat_message(name=role_name):
        st.markdown(msg_content)

user_chat_input = st.chat_input("您好，请问有什么可以帮助您的？")

if user_chat_input:
    # Update the model used for the current session if it changed
    # Only if there are no messages yet, or if we decide to allow changing mid-session
    # For now, let's assume if a new chat input comes, we use the currently selected model
    if not st.session_state.messages or st.session_state.current_session_model != model_selected:
        st.session_state.current_session_model = model_selected

    with st.chat_message("human"):
        st.markdown(user_chat_input)
    history_for_api = list(st.session_state.messages)
    st.session_state.messages.append(user_chat_input)

    ai_response = asktoai(
        user_input=user_chat_input,
        system_prompt_content=system_prompt_input,
        conversation_history=history_for_api,
        model_option=model_selected,  # Use the derived model_selected here
        max_tokens_val=max_token_val,
        top_p_val=top_p_slider_val
    )

    if ai_response and not ai_response.startswith("error:"):
        with st.chat_message("ai"):
            st.markdown(ai_response)
        st.session_state.messages.append(ai_response)
    else:
        if st.session_state.messages and st.session_state.messages[-1] == user_chat_input:
            st.session_state.messages.pop()

st.markdown("---", unsafe_allow_html=True)
if st.button("💾 保存聊天记录并开始新对话", help="保存当前对话到本地文件，并清空当前聊天界面。"):
    if st.session_state.messages:
        # Pass the current_user_id, the model used for this session, and messages to the database function
        success = database.save_chat_session(current_user_id, st.session_state.current_session_model, st.session_state.messages)
        if success:
            st.success("聊天记录已保存到数据库！将开始新的对话。")
            st.session_state.messages = []
            st.session_state.current_session_model = model_selected # Reset model for new session
            st.rerun()
        else:
            st.error("保存聊天记录到数据库失败。")
    else:
        st.info("当前没有聊天记录可保存。")