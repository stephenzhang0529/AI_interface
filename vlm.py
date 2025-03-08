import streamlit as st
import requests
import json
import os
import base64

# 设置API的URL和密钥
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs"

# 用于将图片文件转换为Base64编码的函数
def encode_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def asktovlmai(input_data,option,max_token,temper,uploaded_file):
    # 如果文件上传的是图片，则将其转换为Base64编码
    if uploaded_file:
        image_url = encode_image_to_base64(uploaded_file)
    else:
        image_url = ""  # 如果没有上传图片，则设置为空字符串

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": option,  # 模型名称
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",  # 文本类型
                    "text": input_data  # 用户输入的文本
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "image_url",  # 图片类型
                    "image_url": {
                        "url":"https://sf-maas-uat-prod.oss-cn-shanghai.aliyuncs.com/dog.png",  # 使用Base64编码的图片数据
                        "detail": "auto"  # 图片的细节级别
                    }
                }
            }
        ],
        "stream": False,  # 流式输出
        "max_tokens": max_token,  # 最大token数
        "stop": ["null"],  # 停止词
        "temperature": 0.7,  # 温度参数
        "top_p": temper,  # top_p参数
        "top_k": 50,  # top_k参数
        "frequency_penalty": 0.5,  # 频率惩罚
        "n": 1,  # 返回结果的数量
        "response_format": {"type": "text"},  # 响应格式
    }

    # 调试：打印实际请求的内容
    st.write("Request Payload:")
    st.json(payload)

    # 发送POST请求
    with st.spinner("AI is thinking..."):
       response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        return ai_response
    else:
        st.error(f"API调用失败，状态码：{response.status_code}")
        st.text(response.text)  # 显示错误信息
        return "error"

# Streamlit应用标题
st.title("百家饭AI")
# 模型选择
model=st.selectbox(
    "Which model would you like?",
    ("Qwen/QVQ-72B-Preview",
     "deepseek-ai/deepseek-vl2"),
    placeholder="Select one model...",
)
# 输入参数
max_token=st.slider("Max_token:", 1, 8192, 512)
temper=st.slider("Temperature:", 0.0,2.0, value=0.7)
uploaded_file = st.file_uploader("Choose a file...", type=["jpg", "jpeg", "png", "gif"])
input_data = st.chat_input("Say Something")

# 判断是否输入了文本，并且是否上传了图片
if input_data:
    user_mess = st.chat_message("human")
    user_mess.write(input_data)
    if uploaded_file:
        # 调用asktovlmai函数，并获取AI的响应
        ai_response = asktovlmai(input_data, model, max_token, temper, uploaded_file)
        # 输出AI的回答
        ai_mess = st.chat_message("ai")
        ai_mess.write(ai_response)

