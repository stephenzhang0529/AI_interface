import streamlit as st
import requests
import json # For parsing potential error responses
import os

# --- Configuration ---
DEEPSEEK_CHAT_API_URL = "https://api.siliconflow.cn/v1/chat/completions" # For keyword extraction
DEEPSEEK_IMAGE_API_URL = "https://api.siliconflow.cn/v1/images/generations"  # For image generation

# Prefer environment variable for API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-udnaeovaprogkphwacdfxgypeswdwbnniijoxzrqyhjnhnjs") # Ensure this key works for both APIs

# --- Hardcoded Model Identifiers and Parameters ---
POEM_ANALYSIS_MODEL_ID = "deepseek-ai/DeepSeek-R1"
IMAGE_GENERATION_MODEL_ID = "stabilityai/stable-diffusion-3-5-large"
# Hardcoded parameters for keyword extraction
KEYWORD_MAX_TOKENS = 100
KEYWORD_TEMPERATURE = 0.4 # Slightly lower for more deterministic keywords
KEYWORD_TOP_P = 0.9

# Hardcoded parameters for image generation (using stabilityai/stable-diffusion-3-large)
IMAGE_BATCH_SIZE = 1  # Generate 1 image
IMAGE_GUIDANCE_SCALE = 7.0
IMAGE_SIZE = "1024x1024" # Common default, ensure model supports it


# --- API Call Functions ---

def extract_keywords_from_poem(poem_text):
    """
    Extracts keywords from a poem using the hardcoded POEM_ANALYSIS_MODEL_ID.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt_content = (
        "You are an expert in analyzing the artistic conception of poetry. "
        "Carefully read the poem provided by the user. "
        "Extract 3-7 keywords or phrases that best reflect the visual imagery and core mood. "
        "These keywords will be used for AI painting. "
        "Please output the keywords separated by English commas, ensuring the keywords are in English or Pinyin. "
        "For example: moon, frost, homesickness, ancient road, setting sun, west wind, thin horse. "
        "If the poem is in English, extract English keywords. "
        "If it's difficult to extract specific visual keywords, try to summarize its core atmosphere or scene in an English description."
    )

    payload = {
        "model": POEM_ANALYSIS_MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt_content},
            {"role": "user", "content": f"Please extract keywords from this poem:\n\n{poem_text}"}
        ],
        "stream": False,
        "max_tokens": KEYWORD_MAX_TOKENS,
        "temperature": KEYWORD_TEMPERATURE,
        "top_p": KEYWORD_TOP_P,
    }

    with st.spinner(f"AI ({POEM_ANALYSIS_MODEL_ID.split('/')[-1]}) 正在分析诗句提取关键词..."):
        try:
            response = requests.post(DEEPSEEK_CHAT_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("choices") and response_data["choices"][0].get("message"):
                keywords = response_data["choices"][0]["message"]["content"].strip()
                if keywords:
                    return keywords
                else:
                    st.error("关键词提取AI返回了空内容。")
                    return None
            else:
                st.error("关键词提取API响应格式不正确。")
                st.json(response_data)
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"关键词提取API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.text(f"错误详情: {e.response.text}")
            return None
        except Exception as e:
            st.error(f"处理关键词提取时发生未知错误: {e}")
            return None

def generate_image_from_keywords(keywords_prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    # Ensure parameter names match SiliconFlow's API for the specific model
    # Common names are 'prompt', 'model', 'n' (for number of images), 'size', 'guidance_scale'
    payload = {
        "model": IMAGE_GENERATION_MODEL_ID,
        "prompt": keywords_prompt,
        "n": IMAGE_BATCH_SIZE,
        "guidance_scale": IMAGE_GUIDANCE_SCALE,
        "size": IMAGE_SIZE,
    }

    with st.spinner(f"AI ({IMAGE_GENERATION_MODEL_ID.split('/')[-1]}) 正在根据关键词生成图像..."):
        try:
            response = requests.post(DEEPSEEK_IMAGE_API_URL, headers=headers, json=payload, timeout=180) # Increased timeout
            response.raise_for_status()
            ai_image_data = response.json()

            # SiliconFlow typically returns images in a "data" list, where each item is an object with "url" or "b64_json"
            if "data" in ai_image_data and ai_image_data["data"] and isinstance(ai_image_data["data"], list):
                images_to_display = ai_image_data["data"]
                if images_to_display:
                    with st.chat_message("ai"):
                        st.write("AI生成图像如下:")
                        for img_data in images_to_display:
                            if isinstance(img_data, dict) and "url" in img_data:
                                st.image(img_data["url"], caption=f"AI Generated: {IMAGE_GENERATION_MODEL_ID.split('/')[-1]}")
                            elif isinstance(img_data, dict) and "b64_json" in img_data:
                                # Displaying base64 encoded image
                                st.image(f"data:image/png;base64,{img_data['b64_json']}", caption=f"AI Generated (b64): {IMAGE_GENERATION_MODEL_ID.split('/')[-1]}")
                            else:
                                st.warning(f"未识别的图像数据格式: {img_data}")
                    return True # Success
                else:
                    st.error("API成功返回，但在响应中未找到图像。")
                    st.json(ai_image_data)
            else:
                st.error("API成功返回，但响应中未找到预期的 'data' 列表。")
                st.json(ai_image_data)

        except requests.exceptions.Timeout:
            st.error("图像生成API请求超时。")
        except requests.exceptions.RequestException as e:
            st.error(f"图像生成API调用失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                st.text(f"错误详情: {e.response.text}")
                try:
                    st.json(e.response.json())
                except json.JSONDecodeError:
                    pass # If error response is not JSON
        except json.JSONDecodeError:
            st.error("无法解码API的JSON响应。")
            if 'response' in locals(): st.text(response.text) # Show raw text if response object exists
        except Exception as e:
            st.error(f"处理图像生成时发生未知错误: {e}")

    # If any error occurred and we didn't return True
    with st.chat_message("ai"): # Keep consistent chat message for failure
        st.write("由于发生错误，未能生成图像。")
    return False


# --- Streamlit App UI ---
st.set_page_config(page_title="百家饭AI-诗画创作", layout="centered") # Centered layout might be nice for simplicity
st.title("📜 诗画创作AI")
st.markdown(f"""
输入诗句，AI将使用 **{POEM_ANALYSIS_MODEL_ID.split('/')[-1]}** 进行分析并提取关键词，
然后使用 **{IMAGE_GENERATION_MODEL_ID.split('/')[-1]}** 根据这些关键词生成图像。
所有参数已预设。
""")
st.markdown("---")

poem_input = st.text_area("请输入诗句:", height=150, key="poem_input_area",
                          placeholder="例如：\n枯藤老树昏鸦，\n小桥流水人家，\n古道西风瘦马。\n夕阳西下，\n断肠人在天涯。")

if st.button("从诗句生成画作", key="generate_from_poem_button", type="primary"):
    if not poem_input.strip():
        st.warning("请输入诗句！")
    else:
        with st.chat_message("user"):
            st.write(f"**待分析诗句:**\n```\n{poem_input}\n```")

        extracted_keywords = extract_keywords_from_poem(poem_input)

        if extracted_keywords:
            st.info(f"**AI提取的图像提示词:** `{extracted_keywords}`")
            st.write(f"正在使用模型 `{IMAGE_GENERATION_MODEL_ID.split('/')[-1]}` 和以上提示词生成图像...")
            generate_image_from_keywords(extracted_keywords)
        else:
            st.error("未能从诗句中提取关键词，因此无法生成图像。")

