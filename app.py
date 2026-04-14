import base64
import os
import re
import wave
from typing import Generator

import requests
import streamlit as st
import time
import json


from game_words import sc_special_words, GAME_CONFIG
from tts_utils import generate_sichuan_tts
from video_generation import SichuanVideoGenerator
from dotenv import load_dotenv
import random
# 加载环境变量
load_dotenv()
# ====================== 页面设置 ======================
st.set_page_config(
    page_title="川渝方言趣玩平台",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================== 方言词汇库 ======================
dialect_words = [
    "巴适", "安逸", "耍", "火锅", "串串", "麻辣烫", "幺妹儿", "耙耳朵",
    "雄起", "瓜娃子", "假打", "扯拐", "归一", "恼火", "不存在", "莫得",
    "啥子", "咋个", "晓得", "要得", "巴适得板", "不摆了", "搞不醒豁",
    "哦豁", "格老子", "龟儿子", "仙人板板", "哈戳戳", "闷墩儿", "灯儿晃",
    "打牙祭", "洗白", "搞事情", "扎起", "装疯迷窍", "扯把子", "踏血",
    "洗白", "巴到烫", "背时", "挨球", "扯筋", "关火", "耿直", "假老练"
]

# ====================== 生成随机方言飘字HTML ======================
def generate_floating_words():
    words_html = ""
    for i in range(50):
        word = random.choice(dialect_words)
        left = random.randint(5, 95)
        top = random.randint(100, 150)
        size = random.randint(30, 50)
        duration = random.randint(8, 15)
        delay = random.randint(0, 10)
        
        colors = [
            "rgba(255, 255, 255, 0.95)", "rgba(255, 215, 0, 0.95)", "rgba(255, 182, 193, 0.95)",
            "rgba(173, 216, 230, 0.95)", "rgba(255, 240, 245, 0.95)", "rgba(255, 250, 205, 0.95)",
            "rgba(144, 238, 144, 0.95)", "rgba(255, 165, 0, 0.95)"
        ]
        color = random.choice(colors)
        rotation = random.randint(-15, 15)
        
        words_html += f"""
        <div class="floating-word" data-direction="up" 
             style="left: {left}%; top: {top}vh; font-size: {size}px; color: {color}; 
                    animation-duration: {duration}s; animation-delay: {delay}s;
                    transform: rotate({rotation}deg);">
            {word}
        </div>
        """
    return words_html

# ====================== 样式 ======================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=ZCOOL+KuaiLe&family=ZCOOL+QingKe+HuangYou&display=swap');

/* 全局字体设置 - 所有文字使用与飘字相同的字体 */
* {{
    font-family: "ZCOOL KuaiLe", "Ma Shan Zheng", "ZCOOL QingKe HuangYou", "Comic Sans MS", "幼圆", "黑体", "PingFang SC", "HarmonyOS Sans SC" !important;
}}

/* 确保页面可以正常滚动 */
.stApp {{
    background: linear-gradient(45deg, #2E8B57, #90EE90, #3CB371, #00FF7F, #98FB98, #ADFF2F, #7FFF00, #32CD32);
    background-attachment: fixed;
    background-size: 800% 800%;
    animation: gradientShift 15s ease infinite;
    height: auto !important;
    min-height: 100vh !important;
    overflow: visible !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
}}


@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    25% {{ background-position: 25% 25%; }}
    50% {{ background-position: 100% 50%; }}
    75% {{ background-position: 75% 75%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* 修复飘字容器可能导致的滚动问题 */
.floating-container {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    pointer-events: none !important; /* 让飘字不影响点击 */
    z-index: 1 !important;
}}

.floating-word {{
    position: absolute;
    font-family: "ZCOOL KuaiLe", "Ma Shan Zheng", "ZCOOL QingKe HuangYou", "Comic Sans MS", "幼圆", "黑体", "PingFang SC", "HarmonyOS Sans SC" !important;
    font-weight: bold;
    border-radius: 8px;
    padding: 2px 8px;
    opacity: 0;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
    transform-origin: center;
    transition: all 0.3s ease;
    cursor: pointer;
    user-select: none;
    animation-iteration-count: infinite;
    animation-timing-function: linear;
    letter-spacing: 2px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

.floating-word[data-direction="up"] {{
    animation-name: floatUp;
}}

/* 全局分隔线样式 - 上移并缩小间距 */
div[data-testid="stDivider"],
.stDivider {{
    margin: 0.2rem 0 !important; /* 上下间距缩小到0.2rem */
    padding: 0 !important;
}}

div[data-testid="stDivider"] > hr,
.stDivider > hr {{
    border-color: rgba(255, 255, 255, 0.3) !important; /* 分隔线颜色 */
    margin: 0 !important; /* 确保内部没有额外间距 */
    padding: 0 !important;
}}

@keyframes floatUp {{
    0% {{
        transform: translateY(0px) translateX(0px) rotate(var(--rotation, 0deg)) scale(0.8);
        opacity: 0;
        top: 100vh;
    }}
    10% {{
        opacity: 0.9;
    }}
    50% {{
        transform: translateY(-50vh) translateX(50px) rotate(var(--rotation, 0deg)) scale(1.1);
    }}
    90% {{
        opacity: 0.9;
    }}
    100% {{
        transform: translateY(-100vh) translateX(-30px) rotate(var(--rotation, 0deg)) scale(0.8);
        opacity: 0;
        top: -10vh;
    }}
}}

.floating-word:hover {{
    animation-play-state: paused;
    opacity: 1 !important;
    transform: scale(2) rotate(0deg) !important;
    filter: brightness(1.5) drop-shadow(0 0 15px rgba(255,255,255,0.8));
    z-index: 100;
    transition: all 0.3s ease;
}}

.title-container {{
    position: relative;
    z-index: 10;
    text-align: center;
    margin: 1rem auto 1rem auto;
    pointer-events: none;
    width: 100%;
    max-width: 1200px;
}}

.main-title {{
    font-size: 9rem !important;
    color: #FFFFFF !important;
    text-align: center !important;
    margin: 0 auto !important;
    text-shadow: 
        0 6px 15px rgba(0,0,0,0.6), 
        0 0 30px rgba(255,255,255,0.8);
    letter-spacing: 10px;
    position: relative;
    display: block;
    font-weight: bold;
    width: 100%;
    animation: titleGlow 2s ease-in-out infinite alternate;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

@keyframes titleGlow {{
    from {{
        text-shadow: 0 6px 15px rgba(0,0,0,0.6), 0 0 30px rgba(255,255,255,0.8);
    }}
    to {{
        text-shadow: 0 8px 20px rgba(0,0,0,0.7), 0 0 40px rgba(255,255,255,1), 0 0 50px rgba(144,238,144,0.8);
    }}
}}

/* ====================== 熊猫区域 ====================== */
.panda-section {{
    text-align: center;
    margin: 0 auto 1.5rem auto;
    position: relative;
    z-index: 5;
    height: 180px;
    padding: 10px 0;
}}

/* 熊猫容器 */
.panda-container {{
    display: inline-block;
    position: relative;
    cursor: pointer;
    transition: transform 0.3s ease;
    z-index: 10;
}}

/* 熊猫主表情 - 增大到140px */
.panda-emoji {{
    font-size: 140px !important;
    display: inline-block;
    animation: pandaFloat 3s ease-in-out infinite;
    filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    transform-origin: center center !important; /* 确保以中心点旋转 */
}}

/* 悬停效果：放大 + 发光 + 以中心点歪头 */
.panda-container:hover .panda-emoji {{
    transform: scale(1.2) rotate(15deg) translateY(-5px) !important; /* 放大 + 中心歪头 + 轻微上移 */
    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.8)) 
            drop-shadow(0 0 30px rgba(144, 238, 144, 0.6)) 
            drop-shadow(0 8px 25px rgba(0,0,0,0.3));
    animation-play-state: paused; /* 悬停时暂停浮动动画 */
}}

@keyframes pandaFloat {{
    0%, 100% {{ 
        transform: translateY(0) rotate(0deg); 
    }}
    50% {{ 
        transform: translateY(-20px) rotate(2deg); 
    }}
}}

/* 装饰物 */
.decoration-left, .decoration-right {{
    position: absolute;
    font-size: 40px !important;
    top: 50px;
    filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
    transition: all 0.3s ease;
    z-index: 9;
    transform-origin: center; /* 装饰物也以中心旋转 */
}}

.decoration-left {{
    left: -50px;
    animation: swingLeft 2s infinite;
}}

.decoration-right {{
    right: -50px;
    animation: swingRight 2s infinite;
}}

/* 悬停时装饰物也跟着动 */
.panda-container:hover .decoration-left {{
    transform: translateX(-10px) rotate(-30deg) scale(1.1);
    filter: drop-shadow(0 0 10px rgba(255, 100, 100, 0.7));
}}

.panda-container:hover .decoration-right {{
    transform: translateX(10px) rotate(30deg) scale(1.1);
    filter: drop-shadow(0 0 10px rgba(144, 238, 144, 0.7));
}}

@keyframes swingLeft {{
    0%, 100% {{ transform: translateY(0) rotate(-20deg); }}
    50% {{ transform: translateY(-15px) rotate(10deg); }}
}}

@keyframes swingRight {{
    0%, 100% {{ transform: translateY(0) rotate(20deg); }}
    50% {{ transform: translateY(-15px) rotate(-10deg); }}
}}

/* 表情变化 */
.expression-wrapper {{
    position: relative;
    display: inline-block;
    z-index: 10;
}}

.expression-wrapper::after {{
    content: "😊";
    position: absolute;
    top: -20px;
    right: -20px;
    font-size: 28px !important;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    width: 45px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    animation: expressionChange 4s infinite;
    z-index: 11;
    transform-origin: center; /* 表情也以中心旋转 */
}}

/* 悬停时表情也变化 */
.panda-container:hover .expression-wrapper::after {{
    content: "😍" !important;
    transform: scale(1.2) rotate(-10deg); /* 表情也轻微旋转 */
    background: rgba(255, 255, 255, 1);
    box-shadow: 0 6px 15px rgba(255, 215, 0, 0.5);
}}

@keyframes expressionChange {{
    0% {{ content: "😊"; opacity: 1; }}
    25% {{ content: "😋"; opacity: 1; }}
    50% {{ content: "😎"; opacity: 1; }}
    75% {{ content: "🤩"; opacity: 1; }}
    100% {{ content: "😊"; opacity: 1; }}
}}

/* 按钮容器 */
.buttons-container {{
    position: relative;
    z-index: 10;
    margin: 1rem auto 2rem auto;
    max-width: 1400px;
    padding: 0 2rem;
    width: 100%;
}}

/* 按钮样式 */
.stButton > button {{
    width: 220px !important;
    height: 80px !important;
    font-size: 1.4rem !important;
    font-weight: bold !important;
    margin: 10px !important;
    background: rgba(255, 255, 255, 0.3) !important; /* 透明度从0.8改为0.3 */
    color: #228B22 !important;
    border: none !important; 
    border-radius: 15px !important;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
    position: relative;
    z-index: 10;
    text-transform: none !important;
    letter-spacing: 1px;
}}


.stButton > button:hover {{
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3), 0 0 15px rgba(255,255,255,0.7);
    background: rgba(255, 255, 255, 1) !important;
    color: #32CD32 !important;
    letter-spacing: 2px;
}}

/* 内容卡片 */
.content-card {{
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    border-left: 5px solid #228B22;
}}

@media (max-width: 768px) {{
    .main-title {{
        font-size: 5rem !important;
        letter-spacing: 4px;
    }}
    
    .panda-emoji {{
        font-size: 100px !important;
    }}
    
    .decoration-left, .decoration-right {{
        font-size: 30px !important;
        top: 35px;
    }}
    
    .decoration-left {{
        left: -35px;
    }}
    
    .decoration-right {{
        right: -35px;
    }}
    
    .buttons-container {{
        margin: 1rem auto 2rem auto;
    }}
    
    .stButton > button {{
        width: 180px !important;
        height: 70px !important;
        font-size: 1.2rem !important;
        margin: 8px !important;
    }}
    
    .fun-button {{
        width: 220px !important;
        height: 100px !important;
        font-size: 1.5rem !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ====================== 页面状态 ======================
if "page" not in st.session_state:
    st.session_state.page = "home"
    # 游戏相关状态
if "game_score" not in st.session_state:
    st.session_state.game_score = 0
    st.session_state.current_question = 0
    st.session_state.game_completed = False
    st.session_state.selected_option = None
    st.session_state.correct_answer = None
    st.session_state.game_words = []

# ====================== 首页 ======================
if st.session_state.page == "home":
    # 方言飘字容器
    st.markdown('<div class="floating-container">', unsafe_allow_html=True)
    st.markdown(generate_floating_words(), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 标题容器
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">川渝方言趣玩平台</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ====================== 熊猫区域 ======================
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # 创建熊猫 
            st.markdown("""
            <div class="panda-section">
                <div class="expression-wrapper">
                    <div class="panda-container">
                        <div class="panda-emoji">🐼</div>
                        <div class="decoration-left">🌶️</div>
                        <div class="decoration-right">🎋</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ====================== 功能按钮区域 ======================
    st.markdown('<div class="buttons-container">', unsafe_allow_html=True)
    
    # 使用4列布局
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("川音翻译官", key="btn_translate", use_container_width=True):
            st.session_state.page = "translate"
            st.rerun()
    
    with col2:
        if st.button("方言解码师", key="btn_recognize", use_container_width=True):
            st.session_state.page = "recognize"
            st.rerun()
    
    with col3:
        if st.button("方言趣玩馆", key="btn_fun", use_container_width=True):
            st.session_state.page = "fun"
            st.rerun()
    
    with col4:
        if st.button("方言文创局", key="btn_culture", use_container_width=True):
            st.session_state.page = "culture"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 功能页 ======================
else:
    # 返回按钮 - 根据当前页面决定返回位置
    if st.session_state.page in ["game_play","drama"]:
        if st.button("返回", key="back_button"):
            st.session_state.page = "fun"
            st.rerun()
    else:
        if st.button("返回首页", key="back_button"):
            st.session_state.page = "home"
            st.rerun()
    
    # 方言飘字容器
    st.markdown('<div class="floating-container">', unsafe_allow_html=True)
    st.markdown(generate_floating_words(), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 使用自定义的分隔线，完全控制样式
    st.markdown('<hr style="margin: 0.2rem 0; border-color: rgba(255,255,255,0.3);"/>', unsafe_allow_html=True)

    # 1. 川音翻译官
    if st.session_state.page == "translate":
        st.markdown("## 川音翻译官")
        input_text = st.text_input("输入普通话内容：", placeholder="比如：今天去吃火锅", key="input_translate")
        
        # 固定使用sunny音色生成四川话语音
        selected_voice = "sunny"
        voice_display = "四川-晴儿"
        if st.button("生成四川话", key="btn_generate_audio") and input_text:
            with st.spinner("正在调用API转换..."):
                try:
                    # 通义千问API配置
                    API_KEY = os.getenv('BAILIAN_API_KEY') or os.getenv('DASHSCOPE_API_KEY') or os.getenv(
            'BAILIAN_ACCESS_KEY_SECRET')
                    API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
 
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    }
 
                    data = {
                        "model": "qwen-plus",
                        "input": {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"请将以下普通话翻译成地道的四川话：{input_text}"
                                }
                            ]
                        }
                    }
 
                    response = requests.post(API_URL, headers=headers, json=data)
 
                    if response.status_code == 200:
                        result = response.json()
                        sichuan_text = result.get("output", {}).get("text", "转换失败")
                        st.success(f"四川话：{sichuan_text}")
                        
                        # 使用与方言猜猜乐相同的TTS模型生成音频
                        st.info("🔊 正在合成语音...")
                        import tempfile
                        
                        # 创建临时文件
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            temp_path = tmp_file.name
                        
                        # 生成音频文件
                        audio_file = generate_sichuan_tts(sichuan_text, voice=selected_voice, output_file=temp_path)
 
                        if audio_file and os.path.exists(audio_file):
                            # 播放音频
                            st.success("✅ 语音合成成功！")
                            st.audio(audio_file, format='audio/mp3')
 
                            # 下载按钮
                            with open(audio_file, 'rb') as f:
                                audio_bytes = f.read()
                                st.download_button(
                                    label="📥 下载四川话音频",
                                    data=audio_bytes,
                                    file_name=f"四川话_{voice_display}.mp3",
                                    mime="audio/mp3"
                                )
 
                            # 清理临时文件
                            os.unlink(audio_file)
                        else:
                            st.error("❌ 音频生成失败，请检查API密钥配置")
                    else:
                        st.error("API调用失败")
 
                except ImportError:
                    st.error("请安装requests库：pip install requests")
                except Exception as e:
                    st.error(f"错误：{str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. 方言解码师
    elif st.session_state.page == "recognize":
        # 读取API密钥（兼容多种环境变量名称）
        ALIBABA_CLOUD_API_KEY = os.getenv('BAILIAN_API_KEY') or os.getenv('DASHSCOPE_API_KEY') or os.getenv(
            'BAILIAN_ACCESS_KEY_SECRET')
        # 使用最新 ASR 模型名称
        MODEL = "qwen3-asr-flash"


        def transcribe_audio_to_putonghua(audio_file):
            """
            使用通义千问音频模型将方言音频转换为普通话文本
            """
            try:
                # 准备音频数据
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

                # 构建 API 请求（OpenAI 兼容 ASR 接口）
                url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

                headers = {
                    "Authorization": f"Bearer {ALIBABA_CLOUD_API_KEY}",
                    "Content-Type": "application/json"
                }

                # 参考官方文档，使用 Base64 Data URL 作为音频输入
                mime_type = audio_file.type or "audio/mpeg"
                data_uri = f"data:{mime_type};base64,{audio_base64}"

                payload = {
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_audio",
                                    "input_audio": {
                                        "data": data_uri
                                    }
                                }
                            ]
                        }
                    ],
                    "stream": False,
                    "extra_body": {
                        "asr_options": {
                            # 按文档使用 zh（中文，包括四川话等方言）
                            "language": "zh",
                            "enable_itn": True
                        }
                    }
                }

                # 发送请求
                response = requests.post(url, headers=headers, json=payload, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    try:
                        return result["choices"][0]["message"]["content"]
                    except Exception:
                        return f"识别失败：未返回有效文本结果，响应内容：{result}"
                else:
                    return f"API请求失败：{response.status_code} - {response.text}"

            except Exception as e:
                return f"处理过程中发生错误：{str(e)}"


        # Streamlit界面
        st.markdown("## 方言解码师")
        st.markdown("上传方言音频文件，系统将自动转换为普通话文本")

        uploaded_file = st.file_uploader(
            "上传方言音频（MP3/WAV）：",
            type=["mp3", "wav"],
            key="audio_uploader",
            help="支持普通话及多种方言识别"
        )

        if uploaded_file is not None:
            # 显示音频信息
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📁 文件: {uploaded_file.name}")
            with col2:
                st.info(f"📊 大小: {uploaded_file.size / 1024:.1f} KB")

            # 播放音频预览
            st.audio(uploaded_file, format=uploaded_file.type)

            # 识别按钮
            if st.button("🎤 开始识别转换", type="primary", use_container_width=True):
                with st.spinner("正在识别方言并转换为普通话文本..."):
                    # 重置文件指针
                    uploaded_file.seek(0)

                    # 调用识别函数
                    result = transcribe_audio_to_putonghua(uploaded_file)

                    # 显示结果
                    st.success("识别完成！")

                    # 结果显示区域
                    st.markdown("### 📝 转换结果（普通话文本）")

                    # 可编辑的文本区域
                    if isinstance(result, str) and "失败" not in result and "错误" not in result:
                        edited_text = st.text_area(
                            "识别文本",
                            value=result,
                            height=200,
                            help="您可以直接在此编辑识别结果"
                        )

                        # 添加操作按钮
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("📋 复制文本", use_container_width=True):
                                st.code(result, language="text")
                                st.toast("文本已复制到剪贴板！", icon="✅")
                        with col2:
                            if st.button("💾 保存结果", use_container_width=True):
                                # 创建下载链接
                                st.download_button(
                                    label="下载文本文件",
                                    data=result,
                                    file_name=f"{uploaded_file.name.split('.')[0]}_转换结果.txt",
                                    mime="text/plain"
                                )
                        with col3:
                            if st.button("🔄 重新识别", use_container_width=True):
                                st.rerun()
                    else:
                        st.error(f"识别失败：{result}")
                        if st.button("🔄 重试", use_container_width=True):
                            st.rerun()

        else:
            st.info("👆 请先上传音频文件，支持MP3或WAV格式")
    # 3. 方言趣玩馆
    elif st.session_state.page == "fun":
        st.markdown("## 方言趣玩馆")
        
        # 创建两个大按钮
        st.markdown('<div class="fun-buttons-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            if st.button("方言猜猜乐", key="btn_guess_game", use_container_width=True):
                # 初始化游戏状态
                st.session_state.game_score = 0
                st.session_state.current_question = 0
                st.session_state.game_completed = False
                st.session_state.selected_option = None
                st.session_state.correct_answer = None
                # 随机选择游戏词汇
                import random
                st.session_state.game_words = random.sample(sc_special_words, GAME_CONFIG["total_questions"])
                st.session_state.page = "game_play"
                st.rerun()

        
        with col2:
            if st.button("方言小剧场", key="btn_drama", use_container_width=True):
                st.session_state.page = "drama"
                st.rerun()

    # 4. 方言文创局
    elif st.session_state.page == "culture":
        st.markdown("## 方言文创局")
        st.markdown("探索四川方言的文创魅力")
        
        # 文创项目数据
        文创项目 = [
                {
                    "id": 1,
                    "名称": "“巴适得板”挂件",
                    "设计图位置": "D:\Sichuan_dialect\images\“巴适得板”挂件.png",
                    "理念": "本作品以四川经典方言“巴适得板”为创意核心，将“得板”按照表面字义具像化，并同时展现真正含义“巴适”的状态，于是打造了一只抱着板的惬意熊猫形象。设计选用 Q 版圆润字体，搭配熊猫爪印等趣味元素，既展现四川安逸巴适的生活态度，又让传统方言年轻化、趣味化，打造极具地域特色的文创表达。"
                },
                {
                    "id": 2,
                    "名称": "“邦重&捞轻”挂件",
                    "设计图位置": "D:\Sichuan_dialect\images\“邦重&捞轻”挂件.png",
                    "理念": "本设计以四川方言 “邦重”“捞轻” 为核心，用熊猫与竹子的天平意象，生动诠释方言中 “极重”“极轻” 的趣味表达。卡通熊猫代表着四川地区的特色形象，搭配 Q 版字体与清新配色，既展现四川特色，又让方言文化更具亲和力，适合作为兼具纪念意义与实用性的文创产品。"
                },
                {
                    "id": 3,
                    "名称": "“痨肠寡肚”冰箱贴",
                    "设计图位置": "D:\Sichuan_dialect\images\“痨肠寡肚”冰箱贴.png",
                    "理念": "本设计聚焦四川方言 “痨肠寡肚”，以小孩肚子咕咕作响并哭泣的卡通形象为核心，用夸张的神态直观演绎 “极度饥饿” 的状态。色调选用复古泛黄底色搭配浓黑手绘线条，营造出怀旧市井氛围，既贴合方言的烟火气，又通过萌趣的视觉表达让方言文化更具亲和力，将方言用漫画的形式解释出来，实现实用与文化传播的双重价值。"
                },
                {
                    "id": 4,
                    "名称": "“毛焦火辣”冰箱贴",
                    "设计图位置": "D:\Sichuan_dialect\images\“毛焦火辣”冰箱贴.png",
                    "理念": "本设计以四川方言 “毛焦火辣” 为核心，用头顶红辣椒、焦躁跺脚的卡通形象，直观诠释 “极度焦躁” 的状态，呼应四川人对 “辣” 的独特表达。色调延续复古泛黄底色，以鲜红辣椒作为视觉焦点，既强化了 “火辣” 的情绪张力，又通过夸张的视觉符号让方言文化更具记忆点，传递出鲜活的市井烟火气。"
                },
                {
                    "id": 5,
                    "名称": "四川方言词云明信片",
                    "设计图位置": "D:\Sichuan_dialect\images\四川方言词云明信片.png",
                    "理念": "本设计以四川方言为创意内核，正面将 “巴适”“摆龙门阵” 等方言以“弹幕”的形式展现出来，绿色色调配合竹子元素；背面融入熊猫剪影，剪影由方言词云的形式构成，搭配淡雅竹影背景，既彰显川渝地域标识，又传递出安逸自在的生活态度。明信片以轻盈载体承载厚重乡音，让方言文化以诗意方式走进日常，成为连接故土与远方的情感纽带。"
                },
                {
                    "id": 6,
                    "名称": "“巴适”艺术字",
                    "设计图位置": "D:\Sichuan_dialect\images\“巴适”艺术字.png",
                    "理念": "黑白线条化字体为基底，“巴” 字融入重庆传统民居吊脚楼、盖碗茶与火锅热气，“适” 字嵌入熊猫、单轨与竹编纹理。厚重的笔画承载着盖碗茶的温润与竹编的细腻，灵动的线条勾勒出单轨穿行的悠然，整体设计将川渝人 “慢慢享受、自在从容” 的慢生活节奏视觉化，直观传递出 “巴适” 所代表的舒适、惬意与独特的城市生活哲学。"
                },
                {
                    "id": 7,
                    "名称": "“雄起”艺术字",
                    "设计图位置": "D:\Sichuan_dialect\images\“雄起”艺术字.png",
                    "理念": "“雄起” 是川渝方言中极具力量感的精神符号，设计以线条化字体为骨架，融入火锅、骰子、盖碗茶、辣椒、洪崖洞、麻将 “發” 等本土元素，将市井烟火与城市精神融为一体。线条的律动既呼应火锅沸腾的热气，也象征川渝人坚韧向上的生命力，让方言文化以视觉化方式传递出 “不服输、敢争先” 的城市底气。"
                },
                {
                    "id": 8,
                    "名称": "“巴适得板”明信片",
                    "设计图位置": "D:\Sichuan_dialect\images\“巴适得板”明信片.png",
                    "理念": "明信片正面以洪崖洞、盖碗茶、小面等元素构建出立体的川渝烟火气，左侧 “巴适得板” 书法遒劲暗含川渝文字的自由松弛，让外地游客直观读懂 “舒服到极致” 的生活态度；背面则用熊猫吃火锅的萌趣形象，搭配方言拼音与释义，同时还用盲文和二维码，兼顾多元体验与文化传播，让方言可感可触。"
                },
                {
                    "id": 9,
                    "名称": "“雄起”明信片",
                    "设计图位置": "D:\Sichuan_dialect\images\“雄起”明信片.png",
                    "理念": "以 “雄起” 为核心，把解放碑、穿楼轻轨、火锅这些重庆地标和美食符号，用水彩画风和暖色调，体现地区和语言的蓬勃和生命力。背面用 “加油” 和 “Stay Strong, Keep Going” 双语释义，再配上盲文和能跳转数字平台的二维码，既有方言的本土温度，又用国际化、数字化的方式传递精神力量，兼顾不同群体和感官体验，让每一次投递，都是对这座城 “雄起” 精神的一次致敬与传递。"
                }
            ]
            
        # 添加CSS样式
        st.markdown("""
        <style>
        .culture-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .culture-item {
            position: relative;
            width: 600px;
            height: 600px;
            margin: 30px auto;
            overflow: visible;
            transition: all 0.3s ease;
        }
        
        .culture-item:hover {
            transform: translateX(-20px);
        }
                    
        .culture-image {
            position: absolute;
            left: 0;
            top: 0;
            width: 600px;
            height: 600px;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
        }
        
        .culture-info {
            position: absolute;
            left: 600px;
            top: 0;
            width: 0;
            height: 600px;
            background: linear-gradient(45deg, #90EE90, #006400, #3cB371, #228B22, #2E8B57, #001F3F);
            background-size: 800% 800%;
            animation: gradientShift 15s ease infinite;
            overflow: hidden;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            padding: 0;
            box-sizing: border-box;
            border-radius: 10px;
        }
        
        .culture-item:hover .culture-info {
            width: 300px;
            padding: 0 20px;
        }
        
        
        .culture-description {
            color: white;
            line-height: 1.4;
            font-size: 18px;
        }
        
        .file-placeholder {
            color:  #228B22;
            font-size: 18px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 渲染文创项目
        st.markdown('<div class="culture-container">', unsafe_allow_html=True)
        for 项目 in 文创项目:
            # 读取图片并转换为base64
            import base64
            
            # 构建图片路径
            image_path = f"images/{项目['名称']}.png"
            try:
                with open(image_path, "rb") as img_file:
                    img_data = img_file.read()
                # 转换为base64
                img_base64 = base64.b64encode(img_data).decode("utf-8")
                # 创建data URL
                img_src = f"data:image/png;base64,{img_base64}"
            except Exception as e:
                # 如果图片加载失败，显示占位符
                img_src = ""
            st.markdown(f"""
            <div class="culture-item">
                <div class="culture-image">
                    <img src="{img_src}" alt="{项目['名称']}" style="width: 100%; height: 100%; object-fit: contain;">
                </div>
                <div class="culture-info">
                    <div class="culture-description">
                        <strong>{项目['名称']}</strong><br>
                        设计理念：{项目['理念']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 7. 游戏进行页面
    elif st.session_state.page == "game_play":
        # 使用两列布局，将标题和得分进度并排显示
        col_left, col_right = st.columns([3, 1])  # 左侧标题占3份，右侧信息占1份
        
        with col_left:
            st.markdown("## 方言猜猜乐 - 游戏中")
        
        with col_right:
            # 右侧显示得分和进度
            st.write("")  # 添加一个空行调整垂直位置
            st.write(f"**当前得分：** {st.session_state.game_score}")
            st.write(f"**题目进度：** {st.session_state.current_question + 1}/{GAME_CONFIG['total_questions']}")
            
        if not st.session_state.game_completed:
        # 获取当前题目
            current_word = st.session_state.game_words[st.session_state.current_question]
            st.markdown(f"\n### 请听音频，选择正确的释义：")

            # 使用会话状态缓存音频，避免重复生成
            audio_cache_key = f"audio_cache_{st.session_state.current_question}"
            
            if audio_cache_key not in st.session_state:
                try:
                    # 生成临时音频文件
                    audio_file = f"temp_audio_{st.session_state.current_question}.mp3"
                    
                    # 调用TTS函数，使用正确的四川话音色名称
                    generated_file = generate_sichuan_tts(current_word['word'], voice='Sunny', output_file=audio_file)
                    
                    # 保存到缓存
                    st.session_state[audio_cache_key] = generated_file
                except Exception as e:
                    st.session_state[audio_cache_key] = None
                    print(f"音频生成失败: {str(e)}")
            
            # 播放生成的音频
            if st.session_state[audio_cache_key] and os.path.exists(st.session_state[audio_cache_key]):
                st.audio(st.session_state[audio_cache_key], format="audio/mp3")
            else:
                # 失败时显示词汇和拼音，让用户可以继续游戏
                st.write(f"词汇: **{current_word['word']}**")
                st.write(f"拼音: {current_word['pinyin']}")
                
            # 生成选项（1个正确，3个错误）
            import random
            
            # 确保选项只在需要时生成，避免重复生成
            if ('current_options' not in st.session_state or 
                'last_question_index' not in st.session_state or 
                st.session_state.last_question_index != st.session_state.current_question or
                'selected_option' not in st.session_state or 
                st.session_state.selected_option is not None):
                
                print(f"\n=== 生成新选项 ===")
                
                # 确保正确选项是当前词语的解释（去除前后空格）
                correct_explain = current_word['explain'].strip()
                
                # 生成选项列表
                options = [correct_explain]
                
                # 收集其他错误选项（确保不重复）
                other_words = [word for word in sc_special_words if word['explain'].strip() != correct_explain]
                random.shuffle(other_words)
                
                # 添加3个错误选项
                wrong_options = [word['explain'].strip() for word in other_words[:3]]
                options.extend(wrong_options)
                
                # 打乱选项顺序
                random.shuffle(options)
                
                # 保存选项和相关信息到会话状态
                st.session_state.current_options = options
                st.session_state.correct_answer = correct_explain
                st.session_state.last_question_index = st.session_state.current_question
                
                # 调试信息
                print(f"当前词语: {current_word['word']}")
                print(f"正确答案: '{correct_explain}'")
                print(f"所有选项: {options}")
            
            # 使用会话状态中保存的选项
            options = st.session_state.current_options
                
            # 显示选项按钮
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                if st.button(options[0], key="opt1", use_container_width=True):
                    st.session_state.selected_option = options[0]
            with col2:
                if st.button(options[1], key="opt2", use_container_width=True):
                    st.session_state.selected_option = options[1]
            
            col3, col4 = st.columns(2, gap="medium")
            with col3:
                if st.button(options[2], key="opt3", use_container_width=True):
                    st.session_state.selected_option = options[2]
            with col4:
                if st.button(options[3], key="opt4", use_container_width=True):
                    st.session_state.selected_option = options[3]
                
            # 显示结果
            if st.session_state.selected_option:
                # 去除用户选择的前后空格，确保准确比较
                user_choice = st.session_state.selected_option.strip()
                correct_answer = st.session_state.correct_answer.strip()
                
                # 直接显示结果，不使用容器
                if user_choice == correct_answer:
                    st.success("✅ 回答正确！")
                    st.session_state.game_score += GAME_CONFIG["correct_score"]
                else:
                    st.error("❌ 回答错误！")
                    st.info(f"正确答案：{correct_answer}")
                
                # 延迟2秒后进入下一题
                import time
                time.sleep(2)
                
                # 下一题或结束游戏
                if st.session_state.current_question + 1 < GAME_CONFIG["total_questions"]:
                    st.session_state.current_question += 1
                    st.session_state.selected_option = None
                else:
                    # 已经是最后一题，直接结束游戏
                    st.session_state.game_completed = True
                
                # 重绘页面
                st.rerun()

        else:
            # 游戏结束
            st.markdown(f"\n## 🎉 游戏结束！")
            st.markdown(f"**最终得分：** {st.session_state.game_score}/{GAME_CONFIG['total_questions']*GAME_CONFIG['correct_score']}")
            
            # 重新开始按钮
            if st.button("重新开始", key="btn_restart", use_container_width=True):
                # 初始化游戏状态
                st.session_state.game_score = 0
                st.session_state.current_question = 0
                st.session_state.game_completed = False
                st.session_state.selected_option = None
                st.session_state.correct_answer = None
                # 随机选择新的游戏词汇
                import random
                st.session_state.game_words = random.sample(sc_special_words, GAME_CONFIG["total_questions"])
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. 方言小剧场页面
    elif st.session_state.page == "drama":
        st.markdown("## 方言小剧场")
        
        # 生成歌谣的栏目
        st.markdown("### 🎵 川话歌谣创作")
        song_prompt = st.text_area(
            "输入你想要生成的歌谣主题或内容要求：",
            placeholder="例如：生成一首关于四川火锅的幽默歌谣，要求押韵",
            key="song_prompt",
            height=80
        )
        if st.button("生成四川话歌谣", key="btn_generate_song", use_container_width=True):
            if song_prompt:
                st.info("正在生成四川话歌谣，请稍候...")
                
                try:
                    # 调用通义千问-Plus生成四川话歌谣
                    import http.client
                    import json
                    import os
                    from dotenv import load_dotenv
                    
                    # 加载环境变量
                    load_dotenv()
                    
                    # 读取API密钥
                    api_key = os.getenv('BAILIAN_API_KEY') or os.getenv('DASHSCOPE_API_KEY') or os.getenv('BAILIAN_ACCESS_KEY_SECRET')
                    
                    if not api_key:
                        st.error("未配置API密钥，请设置BAILIAN_API_KEY环境变量")
                    else:
                        # 通义千问API配置
                        host = "dashscope.aliyuncs.com"
                        path = "/api/v1/services/aigc/text-generation/generation"
                        
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        }
                        
                        # 构建请求体
                        prompt = f"请用四川方言创作一首关于{song_prompt}的简短歌谣，语言生动有趣，押韵顺口。歌谣长度控制在4-6句左右。"
                        
                        payload = {
                            "model": "qwen-plus",
                            "input": {
                                "prompt": prompt
                            },
                            "parameters": {
                                "temperature": 0.7,
                                "top_p": 0.8,
                                "max_tokens": 200
                            }
                        }
                        
                        # 发送API请求
                        conn = http.client.HTTPSConnection(host, timeout=30)
                        conn.request("POST", path, json.dumps(payload), headers)
                        response = conn.getresponse()
                        
                        if response.status == 200:
                            response_data = response.read()
                            data = json.loads(response_data.decode('utf-8'))
                            
                            if "output" in data and "text" in data["output"]:
                                song_text = data["output"]["text"].strip()
                                
                                # 显示生成的歌谣文本
                                st.success("四川话歌谣生成成功！")
                                st.markdown("#### 生成的四川话歌谣：")
                                st.markdown(f"> {song_text}")

                                # 同时生成四川话歌谣音频，方便直接收听
                                try:
                                    # 使用现有四川话 TTS 工具，将整首歌谣读出来
                                    audio_file = f"sichuan_song_{int(time.time())}.mp3"
                                    audio_path = generate_sichuan_tts(song_text, voice='Sunny', output_file=audio_file)

                                    if audio_path and os.path.exists(audio_path):
                                        st.markdown("#### 🎧 歌谣语音朗读")
                                        st.audio(audio_path, format="audio/mp3")
                                        st.download_button(
                                            label="下载歌谣音频",
                                            data=open(audio_path, "rb").read(),
                                            file_name=os.path.basename(audio_path),
                                            mime="audio/mpeg",
                                        )
                                    else:
                                        st.warning("歌谣文本已生成，但音频合成暂时失败，可以稍后重试。")
                                except Exception as e:
                                    st.warning(f"歌谣文本已生成，但生成音频时出错：{e}")
                            else:
                                st.error("歌谣生成失败，API响应格式异常")
                        else:
                            st.error(f"歌谣生成失败，状态码：{response.status}")
                            
                        conn.close()
                    
                except Exception as e:
                    st.error(f"生成歌谣时发生错误：{str(e)}")
            else:
                st.warning("请输入歌谣生成要求")
        
        st.markdown("\n\n")  # 添加间距
        
        # 生成视频的栏目
        st.markdown("### 🎬 川剧视频创作")
        video_prompt = st.text_area(
            "输入你想要生成的川剧主题、角色和剧情要求：",
            placeholder="例如：生成一段关于四川人的日常对话，角色是老板和顾客",
            key="video_prompt",
            height=80
        )
        if st.button("生成四川话话剧视频", key="btn_generate_video", use_container_width=True):
            if video_prompt:
                try:
                    # 使用独立的视频生成模块
                    generator = SichuanVideoGenerator()

                    # 前端进度条与状态提示：根据轮询次数渐进，成功时直接 100%
                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    status_placeholder.write("视频生成中，已提交任务，请稍候...")

                    def progress_callback(poll_index, status):
                        # 轮询次数转换为一个“接近但不到 100%”的进度，避免误导用户
                        # 例如每次轮询 +3%，最多到 95%，真正成功时再拉到 100%
                        percent = min(95, poll_index * 3)
                        progress_bar.progress(percent)
                        status_text = status or "等待中"
                        status_placeholder.write(f"视频生成中，当前状态：{status_text}，请稍候...")

                    # 生成四川方言视频（带进度回调）
                    success, result = generator.generate_sichuan_video(
                        video_prompt,
                        duration=10,
                        progress_callback=progress_callback,
                    )

                    # 生成结束，将进度条置为 100%
                    progress_bar.progress(100)

                    if success:
                        status_placeholder.write("视频生成完成！")
                        st.success("四川话话剧视频生成成功！")
                        st.markdown("#### 生成的川剧视频：")
                        st.video(result)

                        # 提供下载链接
                        st.markdown(f"[点击下载视频]({result})", unsafe_allow_html=True)
                    else:
                        status_placeholder.write("视频生成失败。")
                        st.error(f"视频生成失败：{result}")
                        
                except Exception as e:
                    st.error(f"生成视频时发生错误：{str(e)}")
            else:
                st.warning("请输入视频生成要求")
