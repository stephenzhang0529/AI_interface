import streamlit as st
import requests
import json
import os

# --- Configuration ---
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ["API_KEY"]

# Mapping from user-friendly display names to actual VLM model identifiers for the API
# Ensure these actual model identifiers are exactly what the SiliconFlow API expects.
VLM_MODEL_OPTIONS_MAP = {
    "Qwen-VL-72B": "Qwen/Qwen2.5-VL-72B-Instruct",  # More descriptive display name
    "DeepSeek-VL-7B": "deepseek-vl-7b-chat",  # Per your request, API ID is 'deepseek-vl-7b-chat'
    # If the DeepSeek model actually needs 'deepseek-ai/' prefix for API, it would be:
    # "DeepSeek-VL (7B Chat)": "deepseek-ai/deepseek-vl-7b-chat",
}


# Original example values from user's initial code (commented out):
# ("Qwen/QVQ-72B-Preview", "deepseek-ai/deepseek-vl2"),

# --- API Communication Function ---
def asktovlmai(input_text, image_url_val, model_option, max_tokens_val, top_p_val_api):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    content_parts = []
    if input_text and input_text.strip():
        content_parts.append({"type": "text", "text": input_text})
    if image_url_val and image_url_val.strip():
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": image_url_val, "detail": "auto"}
        })
    if not content_parts:
        st.warning("请至少提供文本或图片URL。")
        return "error: no input provided"

    payload = {
        "model": model_option,  # This will use the mapped model ID
        "messages": [{"role": "user", "content": content_parts}],
        "stream": False,
        "max_tokens": max_tokens_val,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": top_p_val_api,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }

    st.sidebar.write("Request Payload (for debugging):")
    st.sidebar.json(payload)

    try:
        with st.spinner("AI 正在思考中 (VLM)..."):
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
        st.error("API请求超时。请稍后再试。")
        return "error: request timeout"
    except requests.exceptions.RequestException as e:
        st.error(f"API调用失败: {e}")
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
st.set_page_config(page_title="百家饭AI - VLM", layout="wide")
st.title("百家饭AI")

with st.sidebar:
    st.header("⚙️ 设置")

    # VLM Model selection
    display_vlm_model_names = list(VLM_MODEL_OPTIONS_MAP.keys())
    selected_vlm_display_name = st.selectbox(
        "选择模型:",
        options=display_vlm_model_names,
        index=0,
        placeholder="选择一个视觉语言模型...",
        key="vlm_model_select_display",
        help="选择您想使用的视觉语言模型。"
    )
    # The actual model identifier to be used in API calls
    model_selected_vlm = VLM_MODEL_OPTIONS_MAP[selected_vlm_display_name]

    st.subheader("🛠️ 参数调整")
    max_token_val = st.slider(
        "Max Tokens:",
        min_value=50, max_value=4096, value=1024, step=64,
        key="vlm_max_token_slider",
        help="AI回复的最大长度（以tokens计算）。"
    )
    top_p_val = st.slider(
        "Temperature:",
        min_value=0.0, max_value=1.0, value=0.7, step=0.01,
        key="vlm_top_p_slider",
        help="控制输出文本的随机性。\n(API的temperature参数固定为0.7)"
    )


st.markdown("---")
st.subheader("🖼️ 图像输入")
image_url_input = st.text_input(
    "请输入图片的URL地址:",
    placeholder="例如: https://example.com/image.jpg",
    key="image_url_field"
)
if image_url_input:
    if image_url_input.startswith("http://") or image_url_input.startswith("https://"):
        st.image(image_url_input, caption="您提供的图片", width=300)
    else:
        st.warning("请输入有效的图片URL (以 http:// 或 https:// 开头)。")
        image_url_input = None

st.markdown("---")
st.subheader("💬 提问")
text_input_data = st.chat_input("关于图片，您想问什么？或者直接描述任务。")

if text_input_data or (image_url_input and not text_input_data):  # Allow if text OR (image and no text yet)
    if not image_url_input:
        st.warning("请提供图片URL以便进行视觉问答。")
    else:
        user_message_display = ""
        if image_url_input:
            user_message_display += f"图片URL: {image_url_input}\n"
        if text_input_data:  # Will be non-empty if this branch is taken due to text_input_data
            user_message_display += f"问题: {text_input_data}"
        elif image_url_input:  # Only image was provided, text_input_data is empty
            user_message_display += f"问题: (无文本输入，尝试分析图片)"

        with st.chat_message("user"):
            st.markdown(user_message_display.strip())

        ai_response = asktovlmai(
            input_text=text_input_data if text_input_data else "",
            image_url_val=image_url_input,
            model_option=model_selected_vlm,  # Use the mapped VLM model ID
            max_tokens_val=max_token_val,
            top_p_val_api=top_p_val
        )

        if ai_response and not ai_response.startswith("error:"):
            with st.chat_message("ai"):
                st.markdown(ai_response)

# This separate button logic might become redundant if chat_input handles the "enter" key well
# even when it's empty but other fields are filled. Consider simplifying if not strictly needed.
elif st.button("发送", key="send_button_vlm", help="如果您只输入了URL，点击此处发送进行分析（如果模型支持）。"):
    if image_url_input and not text_input_data:
        st.info("将尝试分析图片。建议也输入一个问题或指令。")
        with st.chat_message("user"):
            st.markdown(f"图片URL: {image_url_input}\n问题: (无文本输入，尝试分析图片)")
        ai_response = asktovlmai(
            input_text="",
            image_url_val=image_url_input,
            model_option=model_selected_vlm,
            max_tokens_val=max_token_val,
            top_p_val_api=top_p_val
        )
        if ai_response and not ai_response.startswith("error:"):
            with st.chat_message("ai"):
                st.markdown(ai_response)
    elif not image_url_input:
        st.warning("请输入图片URL。")
    else:  # Text input exists, but button was clicked instead of enter in chat_input
        st.info("请通过上方的输入框提问，或直接按回车。")