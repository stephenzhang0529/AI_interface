import streamlit as st
import requests
import json

# 设置API的URL和密钥
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs"

# 发送请求的主函数
def asktovlmai(input_data, option, max_token, temper, image_url):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # 构造 payload：包括文字和图片URL
    payload = {
        "model": option,
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": input_data
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": "auto"
                    }
                }
            }
        ],
        "stream": False,
        "max_tokens": max_token,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": temper,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }

    # 调试输出请求数据
    st.write("Request Payload:")
    st.json(payload)

    # 发送请求
    with st.spinner("AI is thinking..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)

    # 处理响应
    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        return ai_response
    else:
        st.error(f"API调用失败，状态码：{response.status_code}")
        st.text(response.text)
        return "error"

# 页面标题
st.title("百家饭AI")

# 模型选择
model = st.selectbox(
    "Which model would you like?",
    ("Qwen/QVQ-72B-Preview", "deepseek-ai/deepseek-vl2"),
    placeholder="Select one model..."
)

# 参数配置
max_token = st.slider("Max_token:", 1, 8192, 512)
temper = st.slider("Temperature:", 0.0, 2.0, value=0.7)

# 用户输入图片URL
image_url = st.text_input("Please Enter The URL Address Of The Image")

# 用户输入文本
input_data = st.chat_input("Say Something")

# 提交请求
if input_data and image_url:
    st.chat_message("human").write(f"图片URL: {image_url}\n问题: {input_data}")
    ai_response = asktovlmai(input_data, model, max_token, temper, image_url)
    st.chat_message("ai").write(ai_response)
