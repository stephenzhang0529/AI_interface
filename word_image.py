import streamlit as st
import requests
import os # Added for environment variable access

# --- Configuration ---
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/images/generations"
# Prefer environment variable for API key, fallback to hardcoded for development
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs")

# --- API Call Functions ---
def asktostabilityai(model_selected, current_prompt, batch_size_val, guidance_scale_val, image_size_val):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_selected,
        "prompt": current_prompt,
        "batch_size": batch_size_val,
        "guidance_scale": guidance_scale_val,
        "image_size": image_size_val,
    }
    # Debug lines removed

    with st.spinner("AI is generating image(s)..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180) # Added timeout

    # Image output
    if response.status_code == 200:
        try:
            ai_image_data = response.json()
            if "images" in ai_image_data and ai_image_data["images"]:
                with st.chat_message("ai"):
                    st.write("Here is the generated image(s):")
                    for img in ai_image_data["images"]:
                        st.image(img["url"], caption=f"AI Generated: {model_selected}")
            else:
                st.error("API returned success but no images found in response.")
                st.json(ai_image_data)
        except requests.exceptions.JSONDecodeError:
            st.error("Failed to decode API JSON response.")
            st.text(response.text)
    else:
        st.error(f"API call failed with status code: {response.status_code}")
        st.text(response.text)
        try:
            st.json(response.json()) # Try to show JSON error from API
        except requests.exceptions.JSONDecodeError:
            pass # If response is not JSON
        with st.chat_message("ai"): # Keep consistent chat message for failure
            st.write("No images were generated due to an error.")


def asktoFLUX1schnell(model_selected, current_prompt, image_size_val):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_selected,
        "prompt": current_prompt,
        "image_size": image_size_val,
    }
    # Debug lines removed

    with st.spinner("AI is generating image(s)..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180)

    if response.status_code == 200:
        try:
            ai_image_data = response.json()
            if "images" in ai_image_data and ai_image_data["images"]:
                with st.chat_message("ai"):
                    st.write("Here is the generated image(s):")
                    for img in ai_image_data["images"]:
                        st.image(img["url"], caption=f"AI Generated: {model_selected}")
            else:
                st.error("API returned success but no images found in response.")
                st.json(ai_image_data)
        except requests.exceptions.JSONDecodeError:
            st.error("Failed to decode API JSON response.")
            st.text(response.text)
    else:
        st.error(f"API call failed with status code: {response.status_code}")
        st.text(response.text)
        try:
            st.json(response.json())
        except requests.exceptions.JSONDecodeError:
            pass
        with st.chat_message("ai"):
            st.write("No images were generated due to an error.")

def asktoFLUX1pro(model_selected, current_prompt, height_val, width_val):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_selected,
        "prompt": current_prompt,
        "height": height_val,
        "width": width_val,
    }
    # Debug lines removed

    with st.spinner("AI is generating image(s)..."):
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180)

    if response.status_code == 200:
        try:
            ai_image_data = response.json()
            if "images" in ai_image_data and ai_image_data["images"]:
                with st.chat_message("ai"):
                    st.write("Here is the generated image(s):")
                    for img in ai_image_data["images"]:
                        st.image(img["url"], caption=f"AI Generated: {model_selected}")
            else:
                st.error("API returned success but no images found in response.")
                st.json(ai_image_data)
        except requests.exceptions.JSONDecodeError:
            st.error("Failed to decode API JSON response.")
            st.text(response.text)
    else:
        st.error(f"API call failed with status code: {response.status_code}")
        st.text(response.text)
        try:
            st.json(response.json())
        except requests.exceptions.JSONDecodeError:
            pass
        with st.chat_message("ai"):
            st.write("No images were generated due to an error.")


# --- Streamlit App UI ---
st.set_page_config(page_title="百家饭AI - Image Generation", layout="wide")
st.title("百家饭AI")

# Shared image size options
COMMON_IMAGE_SIZES = (
    "1024x1024", "512x1024", "768x512",
    "768x1024", "1024x576", "576x1024"
)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ 模型与参数设置")

    # Model selection
    selected_model = st.selectbox(
        "选择图像生成模型:",
        ("stabilityai/stable-diffusion-3-5-large",
         "stabilityai/stable-diffusion-3-5-large-turbo",
         "black-forest-labs/FLUX.1-schnell",
         "Pro/black-forest-labs/FLUX.1-schnell", # Assuming this is a distinct variant for API
         "black-forest-labs/FLUX.1-pro"),
        index=0,
        placeholder="选择一个模型...",
        key="image_model_select"
    )

    st.markdown("---") # Visual separator

    # Conditional parameters based on selected model
    if selected_model in ("stabilityai/stable-diffusion-3-5-large", "stabilityai/stable-diffusion-3-5-large-turbo"):
        st.subheader(f"参数 for {selected_model.split('/')[-1]}")
        batch_size_input = st.slider("生成图片数量:", 1, 4, 1, key="sd_batch_size")
        guidance_scale_input = st.slider("提示词相关性 (Guidance Scale):", 0.0, 20.0, 7.0, step=0.5, key="sd_guidance")
        image_size_input = st.selectbox(
            "图片尺寸:",
            COMMON_IMAGE_SIZES,
            index=0,
            placeholder="选择图片尺寸...",
            key="sd_image_size"
        )
    elif selected_model in ("black-forest-labs/FLUX.1-schnell", "Pro/black-forest-labs/FLUX.1-schnell"):
        st.subheader(f"参数 for {selected_model.split('/')[-1]}")
        image_size_input = st.selectbox(
            "图片尺寸:",
            COMMON_IMAGE_SIZES,
            index=0,
            placeholder="选择图片尺寸...",
            key="flux_schnell_image_size"
        )
    elif selected_model == "black-forest-labs/FLUX.1-pro":
        st.subheader(f"参数 for {selected_model.split('/')[-1]}")
        height_input = st.slider("图片高度 (Height):", 256, 1440, value=1024, step=32, key="flux_pro_height")
        width_input = st.slider("图片宽度 (Width):", 256, 1440, value=1024, step=32, key="flux_pro_width")
    else:
        # This case should ideally not be reached if selected_model is always one of the options
        st.info("选择一个模型以查看其参数。")




# Main area for prompt input and image display
st.markdown("---")
prompt_input = st.chat_input("输入描述词来生成图片...")

if prompt_input:
    with st.chat_message("user"):
        st.write(f"提示词: {prompt_input}")

    # Call the appropriate function based on the selected model
    if selected_model in ("stabilityai/stable-diffusion-3-5-large", "stabilityai/stable-diffusion-3-5-large-turbo"):
        # Ensure these variables are defined if this branch is taken
        # They should be from the sidebar's conditional block
        asktostabilityai(selected_model, prompt_input, batch_size_input, guidance_scale_input, image_size_input)
    elif selected_model in ("black-forest-labs/FLUX.1-schnell", "Pro/black-forest-labs/FLUX.1-schnell"):
        # Ensure image_size_input is defined
        asktoFLUX1schnell(selected_model, prompt_input, image_size_input)
    elif selected_model == "black-forest-labs/FLUX.1-pro":
        # Ensure height_input and width_input are defined
        asktoFLUX1pro(selected_model, prompt_input, height_input, width_input)
    else:
        st.error("无效的模型选择，无法处理请求。此错误不应发生。")