import streamlit as st
import requests

# 设置API的URL和密钥
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/images/generations"
DEEPSEEK_API_KEY = "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs"

def asktostabilityai(model,prompt,batch_size,guidance_scale,image_size):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,  # 模型名称
        "prompt":prompt,
        "batch_size": batch_size,
        "guidance_scale": guidance_scale,
        "image_size": image_size,
    }
    with st.spinner("AI is thinking..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        ai_mess = st.chat_message("ai")
    #图片输出
    if response.status_code == 200:
        ai_image = response.json()
        ai_mess.write("Here is the generated image:")

        for img in ai_image["images"]:
            st.image(img["url"], caption="AI 生成的图片")  # 使用 st.image 显示图片
    else:
        st.error(f"API调用失败，状态码：{response.status_code}")
        st.text(response.text)  # 显示错误信息
        ai_mess.write("No images generated.")

def asktoFLUX1schnell(model,prompt,image_size):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,  # 模型名称
        "prompt":prompt,
        "image_size": image_size,
    }
    with st.spinner("AI is thinking..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        ai_mess = st.chat_message("ai")
    #图片输出
    if response.status_code == 200:
        ai_image = response.json()
        ai_mess.write("Here is the generated image:")

        for img in ai_image["images"]:
            st.image(img["url"], caption="AI 生成的图片")  # 使用 st.image 显示图片
    else:
        st.error(f"API调用失败，状态码：{response.status_code}")
        st.text(response.text)  # 显示错误信息
        ai_mess.write("No images generated.")

def asktoFLUX1pro(model,prompt,height,width):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,  # 模型名称
        "prompt":prompt,
        "height":height,
        "width":width,
    }
    with st.spinner("AI is thinking..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        ai_mess = st.chat_message("ai")
    #图片输出
    if response.status_code == 200:
        ai_image = response.json()
        ai_mess.write("Here is the generated image:")

        for img in ai_image["images"]:
            st.image(img["url"], caption="AI 生成的图片")  # 使用 st.image 显示图片
    else:
        st.error(f"API调用失败，状态码：{response.status_code}")
        st.text(response.text)  # 显示错误信息
        ai_mess.write("No images generated.")

# Streamlit应用标题
st.title("百家饭AI")
# 模型选择
model=st.selectbox(
    "Which model would you like?",
    ("stabilityai/stable-diffusion-3-5-large",
     "stabilityai/stable-diffusion-3-5-large-turbo",
     "black-forest-labs/FLUX.1-schnell",
     "Pro/black-forest-labs/FLUX.1-schnell",
     "black-forest-labs/FLUX.1-pro"),
    placeholder="Select one model...",
)

if model in ("stabilityai/stable-diffusion-3-5-large","stabilityai/stable-diffusion-3-5-large-turbo"):
    # stability models
    # number of generated photos
    batch_size=st.slider("Number of generated photo(s) per time:", 1, 4, 1)
    guidance_scale=st.slider("The match of prompt:", 0, 20, 7)
    image_size=st.selectbox(
    "The scale of photo:",
    ("1024x1024",
     "512x1024",
     "768x512",
     "768x1024",
     "1024x576",
     "576x1024"
     ),
    placeholder="Select one scale...",
    )
    # 输入参数
    prompt = st.chat_input("Describe the photo...")
    if prompt:
        user_mess = st.chat_message("human")
        user_mess.write(prompt)

        asktostabilityai(model,prompt,batch_size,guidance_scale,image_size)
elif model in ("black-forest-labs/FLUX.1-schnell","Pro/black-forest-labs/FLUX.1-schnell"):
    image_size = st.selectbox(
        "The scale of photo:",
        ("1024x1024",
         "512x1024",
         "768x512",
         "768x1024",
         "1024x576",
         "576x1024"
         ),
        placeholder="Select one scale...",
    )
    # 输入参数
    prompt = st.chat_input("Describe the photo...")
    if prompt:
        user_mess = st.chat_message("human")
        user_mess.write(prompt)

        asktoFLUX1schnell(model,prompt,image_size)
else:
    height = st.slider("The height of photo:", 256, 1440, value=1024,step=32)
    width = st.slider("The width of photo:", 256, 1440, value=1024,step=32)
    # 输入参数
    prompt = st.chat_input("Describe the photo...")
    if prompt:
        user_mess = st.chat_message("human")
        user_mess.write(prompt)

        asktoFLUX1pro(model,prompt,height,width)