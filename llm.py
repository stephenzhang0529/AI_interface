import streamlit as st
import requests
import json
import os

# 设置API的URL和密钥
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs"

# 读取历史记录
def load_chat_history():
    history_file = 'chat_history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            return json.load(f)
    return []

# 保存聊天记录
def save_chat_history(messages):
    with open('chat_history.json', 'w') as f:
        json.dump(messages, f)

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
    ("deepseek-ai/DeepSeek-R1",
     "deepseek-ai/DeepSeek-V3",
     "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
     "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"),
    placeholder="Select one model...",
)
# 输入参数
max_token=st.slider("Max_token:", 1, 8192, 512)
temper=st.slider("Temperature:", 0.0,2.0, value=0.7)
input_data = st.chat_input("Say Something")

# 初始化会话状态中的聊天记录
if 'messages' not in st.session_state:
    st.session_state.messages = []
# 显示聊天记录
flag=1
for historymessage in st.session_state.messages:
    if flag%2==1:
        user_mess = st.chat_message("human")
        user_mess.write(historymessage)
        flag+=1
    else:
        ai_mess = st.chat_message("ai")
        ai_mess.markdown(historymessage)
        flag += 1


if input_data:
    user_mess=st.chat_message("human")
    user_mess.write(input_data)

    ai_response=asktoai(input_data,model,max_token,temper)
    ai_mess = st.chat_message("ai")
    ai_mess.markdown(ai_response)

    # 将用户输入和AI回应保存到历史记录
    st.session_state.messages.append(input_data)
    st.session_state.messages.append(ai_response)

# 添加保存聊天记录的按钮
if st.button("保存聊天记录"):
    save_chat_history(st.session_state.messages)  # 保存聊天记录到本地
    st.success("聊天记录已保存！")
    # 清空当前聊天记录并刷新页面
    st.session_state.messages = []
    st.rerun()  # 刷新页面，显示空白的聊天界面
