import streamlit as st
import requests
from sympy.physics.units import temperature

# 设置API的URL和密钥
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs"

def asktoai(input_data,option,max_token,temper):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": option,  # 模型名称
        "messages": [
            {
                "content": input_data, # 用户输入的内容
                "role": "user"
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
    ("deepseek-ai/DeepSeek-R1",
     "deepseek-ai/DeepSeek-V3",
     "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
     "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"),
    placeholder="Select one model...",
)
# 输入参数
max_token=st.slider("max_token:", 1, 8192, 512)
temper=st.slider("max_token:", 0.0,2.0, value=0.7)
input_data = st.chat_input("Say Something")

if input_data:
    user_mess=st.chat_message("human")
    user_mess.write(input_data)

    ai_response=asktoai(input_data,model,max_token,temper)
    ai_mess = st.chat_message("ai")
    ai_mess.markdown(ai_response)

