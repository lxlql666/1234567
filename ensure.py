import streamlit as st
import random
import time

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

.stApp {{
    background: linear-gradient(45deg, #2E8B57, #90EE90, #3CB371, #00FF7F, #98FB98, #ADFF2F, #7FFF00, #32CD32);
    background-attachment: fixed;
    background-size: 800% 800%;
    animation: gradientShift 15s ease infinite;
    overflow-x: hidden;
    overflow-y: auto;
}}

@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    25% {{ background-position: 25% 25%; }}
    50% {{ background-position: 100% 50%; }}
    75% {{ background-position: 75% 75%; }}
    100% {{ background-position: 0% 50%; }}
}}

.floating-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: auto;
    z-index: 1;
    overflow: hidden;
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
    font-family: "Ma Shan Zheng", "ZCOOL KuaiLe", "PingFang SC", "HarmonyOS Sans SC", cursive !important;
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
    width: 350px !important;
    height: 120px !important;
    font-size: 2.2rem !important;
    font-weight: bold !important;
    margin: 15px !important;
    background: linear-gradient(135deg, #228B22 0%, #32CD32 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.35);
    transition: all 0.3s ease;
    position: relative;
    z-index: 10;
    font-family: "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei UI", sans-serif !important;
    text-transform: none !important;
    letter-spacing: 1px;
}}

.stButton > button:hover {{
    transform: translateY(-4px) scale(1.05);
    box-shadow: 0 15px 35px rgba(0,0,0,0.45), 0 0 20px rgba(144,238,144,0.5);
    background: linear-gradient(135deg, #32CD32 0%, #98FB98 100%) !important;
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

/* 方言趣玩馆大按钮样式 */
.fun-buttons-container {{
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}}

.fun-button {{
    width: 400px !important;
    height: 200px !important;
    font-size: 2.5rem !important;
    font-weight: bold !important;
    background: linear-gradient(135deg, #228B22 0%, #32CD32 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
    font-family: "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei UI", sans-serif !important;
    text-transform: none !important;
    letter-spacing: 2px;
}}

.fun-button:hover {{
    transform: translateY(-8px) scale(1.05);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 25px rgba(144,238,144,0.6);
    background: linear-gradient(135deg, #32CD32 0%, #98FB98 100%) !important;
    letter-spacing: 3px;
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
        width: 220px !important;
        height: 80px !important;
        font-size: 1.4rem !important;
        margin: 10px !important;
    }}
    
    .fun-button {{
        width: 280px !important;
        height: 150px !important;
        font-size: 2rem !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ====================== 页面状态 ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

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
            # 创建熊猫 - 现在只悬停不点击
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
        if st.button("🔥 川音翻译官", key="btn_translate", use_container_width=True):
            st.session_state.page = "translate"
            st.rerun()
    
    with col2:
        if st.button("🎤 方言解码师", key="btn_recognize", use_container_width=True):
            st.session_state.page = "recognize"
            st.rerun()
    
    with col3:
        if st.button("🎮 方言趣玩馆", key="btn_fun", use_container_width=True):
            st.session_state.page = "fun"
            st.rerun()
    
    with col4:
        if st.button("🎨 方言文创局", key="btn_culture", use_container_width=True):
            st.session_state.page = "culture"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 功能页 ======================
else:
    # 返回首页按钮
    if st.button("🏠 返回首页", key="back_button"):
        st.session_state.page = "home"
        st.rerun()
    
    # 方言飘字容器
    st.markdown('<div class="floating-container">', unsafe_allow_html=True)
    st.markdown(generate_floating_words(), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

    # 1. 川音翻译官
    if st.session_state.page == "translate":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("## 🔥 川音翻译官")
        st.text_input("输入普通话内容：", placeholder="比如：今天去吃火锅", key="input_translate")
        st.selectbox("选择方言音色：", ["普通", "豪爽老板", "温柔幺妹儿"], key="select_voice")
        st.button("生成音频", key="btn_generate_audio")
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. 方言解码师
    elif st.session_state.page == "recognize":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("## 🎤 方言解码师")
        st.file_uploader("上传方言音频（MP3/WAV）：", type=["mp3", "wav"], key="upload_audio")
        st.empty()
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. 方言趣玩馆
    elif st.session_state.page == "fun":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("## 🎮 方言趣玩馆")
        
        # 创建两个大按钮
        st.markdown('<div class="fun-buttons-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            if st.button("🎧 方言猜猜乐", key="btn_guess_game", use_container_width=True):
                st.write("方言猜猜乐功能开发中...")
        
        with col2:
            if st.button("✍️ 方言小剧场", key="btn_drama", use_container_width=True):
                st.write("方言小剧场功能开发中...")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 4. 方言文创局
    elif st.session_state.page == "culture":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("## 🎨 方言文创局")
        st.write("方言文创局功能开发中...")
        st.markdown('</div>', unsafe_allow_html=True)