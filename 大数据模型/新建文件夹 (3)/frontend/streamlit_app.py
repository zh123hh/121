"""
LangChain对话助手 - Streamlit前端
美观的现代化界面设计
"""
import streamlit as st
import requests
import time
from typing import Optional

# 页面配置
st.set_page_config(
    page_title="谷雨 - AI助手",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义CSS样式 - 优雅白色系配色
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e8eef5 100%);
        min-height: 100vh;
    }
    
    .main-container {
        padding: 30px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .message-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 25px;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.06);
        min-height: auto;
        max-height: 550px;
        overflow-y: auto;
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .user-message {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1a 100%);
        color: #ffffff;
        padding: 18px 24px;
        border-radius: 25px 25px 8px 25px;
        margin-bottom: 15px;
        max-width: 75%;
        float: right;
        clear: both;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .user-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1a1a2e;
        padding: 18px 24px;
        border-radius: 25px 25px 25px 8px;
        margin-bottom: 15px;
        max-width: 75%;
        float: left;
        clear: both;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .assistant-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput>div>div>input {
        border-radius: 30px;
        padding: 18px 25px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        transition: all 0.4s ease;
        background: rgba(255, 255, 255, 0.98);
        font-size: 16px;
        color: #2d3748;
    }
    
    .stTextInput>div>div>input::placeholder {
        color: rgba(45, 55, 72, 0.6);
    }
    
    .stTextInput>div>div>input:focus {
        border-color: rgba(45, 55, 72, 0.3);
        box-shadow: 0 0 0 3px rgba(45, 55, 72, 0.06), 0 0 40px rgba(45, 55, 72, 0.03);
        background: rgba(255, 255, 255, 0.99);
    }
    
    .stButton>button {
        border-radius: 30px;
        padding: 15px 35px;
        font-weight: 500;
        font-size: 16px;
        transition: all 0.4s ease;
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: #f7fafc;
        border: none;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.18);
        background: linear-gradient(135deg, #3d4a5c 0%, #2a303c 100%);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    .stSlider>div>div>div>div {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        border-radius: 10px;
    }
    
    .stSlider>div>div>div>div:nth-child(2) {
        background: #ffffff;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 0, 0, 0.04);
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #2d3748 !important;
        --text-color: #2d3748 !important;
        --primary-text-color: #2d3748 !important;
        --secondary-text-color: #4a5568 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stTextArea,
    [data-testid="stSidebar"] .stButton {
        color: #2d3748 !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox>div>div {
        background: #f7fafc !important;
        border-radius: 15px;
        color: #2d3748 !important;
        border: 1px solid rgba(0, 0, 0, 0.06);
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox>div>div>div {
        color: #2d3748 !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox>div>div>div>span {
        color: #2d3748 !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] .stTextArea>div>textarea {
        background: #f7fafc !important;
        border-radius: 15px;
        color: #2d3748 !important;
        border: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    [data-testid="stSidebar"] .css-1x8cf1d,
    [data-testid="stSidebar"] .css-1cpxqw2,
    [data-testid="stSidebar"] .css-1p3m7a8,
    [data-testid="stSidebar"] .css-1y4p8pa {
        color: #2d3748 !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] [role="listbox"] {
        background: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] [role="option"] {
        color: #2d3748 !important;
        background: #ffffff !important;
        padding: 10px 15px !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] [role="option"]:hover {
        background: #f7fafc !important;
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] [role="option"] span {
        color: #2d3748 !important;
        opacity: 1 !important;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.04);
        margin-bottom: 25px;
        border: 1px solid rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.06);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 50%, #4a5568 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .status-online {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        width: 14px;
        height: 14px;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: 0 0 15px rgba(72, 187, 120, 0.4);
    }
    
    .status-offline {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        width: 14px;
        height: 14px;
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(245, 101, 101, 0.3);
    }
    
    @keyframes pulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(72, 187, 120, 0.5);
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
        70% { 
            box-shadow: 0 0 0 10px rgba(72, 187, 120, 0);
            transform: scale(1);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(72, 187, 120, 0);
            transform: scale(1);
        }
    }
    
    .stSelectbox>div>div {
        border-radius: 15px;
        padding: 12px 15px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.98);
        color: #2d3748;
    }
    
    .stSelectbox>div>div:hover {
        border-color: rgba(45, 55, 72, 0.2);
        box-shadow: 0 0 20px rgba(45, 55, 72, 0.06);
    }
    
    .stTextArea>div>textarea {
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        resize: none;
        background: rgba(255, 255, 255, 0.98);
        color: #2d3748;
    }
    
    .stTextArea>div>textarea:focus {
        border-color: rgba(45, 55, 72, 0.2);
        box-shadow: 0 0 0 3px rgba(45, 55, 72, 0.04);
    }
    
    [data-testid="stSwitch"] {
        background: rgba(237, 242, 247, 0.9);
        border-radius: 20px;
    }
    
    [data-testid="stSwitch"] [role="switch"] {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stHorizontalRule"] {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.06), transparent);
    }
    
    .welcome-card {
        background: linear-gradient(135deg, rgba(237, 242, 247, 0.6) 0%, rgba(226, 232, 240, 0.6) 100%);
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 25px;
        padding: 35px;
        text-align: center;
        margin-bottom: 25px;
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .footer-links a {
        color: rgba(45, 55, 72, 0.6);
        text-decoration: none;
        transition: all 0.3s ease;
        padding: 10px 20px;
        border-radius: 25px;
    }
    
    .footer-links a:hover {
        color: #1a202c;
        background: rgba(45, 55, 72, 0.06);
    }
    
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.02);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #cbd5e0 0%, #a0aec0 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
    }
</style>
""", unsafe_allow_html=True)

# 配置
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

if "model_provider" not in st.session_state:
    st.session_state.model_provider = "openai"

if "model_name" not in st.session_state:
    st.session_state.model_name = "gpt-4o-mini"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "use_streaming" not in st.session_state:
    st.session_state.use_streaming = True

if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = True


def call_api(endpoint: str, method: str = "POST", data: dict = None) -> dict:
    """调用API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=60)
        else:
            response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API调用失败: {str(e)}")
        return {"error": str(e)}


def stream_chat(message: str) -> str:
    """流式对话"""
    url = f"{API_BASE_URL}/chat/stream"
    data = {
        "message": message,
        "session_id": st.session_state.session_id,
        "system_message": st.session_state.get("system_message", "你是谷雨，一个可爱的AI助手。请用友好、亲切的语气回答问题。"),
        "model_provider": st.session_state.model_provider,
        "model_name": st.session_state.model_name,
    }
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=60)
        response.raise_for_status()
        
        full_response = ""
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                full_response += chunk.decode("utf-8")
                yield full_response
        return full_response
    except requests.exceptions.RequestException as e:
        # 演示模式：返回模拟响应
        demo_response = f"🎯 演示模式响应\n\n您的问题: {message}\n\n📝 这是一个演示响应。要使用真实的AI模型，请在 `.env` 文件中配置有效的API密钥。\n\n支持的模型:\n- OpenAI: GPT-4, GPT-3.5\n- Anthropic: Claude-3-opus, Claude-3-sonnet\n- DeepSeek: 本地部署模型\n\n请在服务器端配置相应的API密钥。"
        for i in range(0, len(demo_response), 10):
            yield demo_response[:i+10]
        yield demo_response


def get_available_models() -> list:
    """获取可用模型列表"""
    try:
        response = requests.get(f"{API_BASE_URL}/models", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []


def check_api_status() -> bool:
    """检查API状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# 侧边栏配置
with st.sidebar:
    st.markdown("""
        <div style="padding: 20px 15px; background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); border-radius: 15px; margin-bottom: 20px; text-align: center;">
            <div style="font-size: 36px; margin-bottom: 8px;">🌱</div>
            <h2 style="color: white; margin: 0; font-size: 20px; font-weight: 600;">谷雨</h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 12px; margin-top: 5px;">LangChain 智能助手</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 服务状态
    status = check_api_status()
    status_color = "#48bb78" if status else "#f56565"
    status_bg = "#dcfce7" if status else "#fee2e2"
    status_text_color = "#166534" if status else "#991b1b"
    status_text = "在线" if status else "离线"
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: {status_bg}; border-radius: 10px; margin-bottom: 20px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: {status_color};"></div>
            <span style="color: {status_text_color}; font-weight: 600; font-size: 14px;">API服务: {status_text}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 模型选择
    st.subheader("⚙️ 模型配置", divider="gray")
    
    models = get_available_models()
    
    if models:
        providers = [p["provider"] for p in models]
        provider_icons = {
            "openai": "🔵",
            "anthropic": "🟠", 
            "deepseek": "🟢"
        }
        provider_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "deepseek": "DeepSeek"
        }
        
        st.session_state.model_provider = st.selectbox(
            "模型提供商",
            providers,
            index=providers.index(st.session_state.model_provider) if st.session_state.model_provider in providers else 0,
            format_func=lambda x: f"{provider_icons.get(x, '🔹')} {provider_names.get(x, x)}"
        )
        
        current_provider_info = next((p for p in models if p["provider"] == st.session_state.model_provider), {})
        current_provider_models = current_provider_info.get("models", [])
        
        if current_provider_models:
            st.session_state.model_name = st.selectbox(
                "模型名称",
                current_provider_models,
                index=current_provider_models.index(st.session_state.model_name) if st.session_state.model_name in current_provider_models else 0
            )
    else:
        st.session_state.model_provider = st.selectbox(
            "模型提供商", 
            ["openai", "anthropic", "deepseek"], 
            index=0,
            format_func=lambda x: {
                "openai": "🔵 OpenAI",
                "anthropic": "🟠 Anthropic",
                "deepseek": "🟢 DeepSeek"
            }[x]
        )
        
        if st.session_state.model_provider == "deepseek":
            st.session_state.model_name = st.selectbox("模型名称", ["deepseek-chat", "deepseek-r1-chat"], index=0)
        else:
            st.session_state.model_name = st.selectbox("模型名称", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
    
    # 参数配置
    st.subheader("🎛️ 生成参数", divider="gray")
    
    st.session_state.temperature = st.slider(
        "温度参数",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="控制输出的随机性"
    )
    
    st.session_state.use_streaming = st.toggle(
        "💬 流式输出", 
        value=st.session_state.use_streaming,
        help="启用实时流式响应"
    )
    
    # 系统提示
    st.subheader("📝 系统提示", divider="gray")
    st.session_state.system_message = st.text_area(
        "",
        value=st.session_state.get("system_message", "你是谷雨，一个可爱的AI助手。请用友好、亲切的语气回答问题。"),
        height=100,
        placeholder="输入自定义系统提示..."
    )
    
    # 操作按钮
    st.subheader("🔧 快捷操作", divider="gray")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = f"session_{int(time.time())}"
            st.success("已清空")
    
    with col2:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    # 快捷功能
    st.subheader("⚡ 快捷指令", divider="gray")
    
    quick_prompts = [
        ("✍️ 写邮件", "帮我写一封商务邮件"),
        ("📝 写总结", "帮我总结文本内容"),
        ("🌍 翻译", "翻译成英文"),
        ("💡 创意写作", "构思一个故事开头"),
    ]
    
    for label, prompt in quick_prompts:
        if st.button(label, use_container_width=True):
            st.session_state.quick_prompt = prompt
            st.rerun()


# 主界面
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px; padding-top: 15px;">
        <div style="font-size: 48px; margin-bottom: 10px;">🌱</div>
        <h1 style="color: #1a202c; font-size: 38px; margin-bottom: 10px; font-weight: 700; letter-spacing: -0.5px;">谷雨</h1>
        <div style="display: inline-flex; align-items: center; gap: 15px; padding: 8px 20px; background: #f1f5f9; border-radius: 20px;">
            <span style="color: #64748b; font-size: 13px;">LangChain</span>
            <span style="color: #cbd5e0;">·</span>
            <span style="color: #64748b; font-size: 13px;">多模型支持</span>
            <span style="color: #cbd5e0;">·</span>
            <span style="color: #64748b; font-size: 13px;">LangSmith监控</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 对话区域
chat_container = st.container()

with chat_container:
    st.markdown('<div class="message-container" style="margin-bottom: 20px;">', unsafe_allow_html=True)
    
    # 显示欢迎消息
    if not st.session_state.messages:
        st.markdown("""
            <div class="welcome-card">
                <div style="font-size: 48px; margin-bottom: 15px;">🌱</div>
                <div style="font-weight: 700; font-size: 24px; margin-bottom: 10px; color: #0f0f0f;">你好，我是谷雨</div>
                <div style="font-size: 15px; color: #3d4a5c; line-height: 1.7;">
                    我可以帮助你写作、翻译、编程、问答等<br>
                    在左侧配置模型，然后开始对话吧！
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # 显示对话历史
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
                <div class="user-message">
                    <div style="font-weight: 600; margin-bottom: 5px;">您</div>
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="assistant-message">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                        <span>🌱</span>
                        <span style="font-weight: 600;">谷雨</span>
                        <span style="font-size: 12px; color: #94a3b8; margin-left: auto;">
                            {st.session_state.model_name}
                        </span>
                    </div>
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# 用户输入
st.markdown("""
    <div style="margin-top: 10px; padding: 12px; background: #ffffff; border-radius: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.04);">
""", unsafe_allow_html=True)

col_input, col_send = st.columns([10, 1])

with col_input:
    prompt = st.text_input(
        "",
        placeholder="输入消息，与谷雨对话...",
        key="user_input",
        value=st.session_state.get("quick_prompt", ""),
        label_visibility="collapsed"
    )
    st.session_state.pop("quick_prompt", None)

with col_send:
    send_button = st.button(
        "➤",
        use_container_width=True,
        type="primary",
        key="send_button"
    )

st.markdown('</div>', unsafe_allow_html=True)

# 处理用户输入
if (prompt and send_button) or (prompt and st.session_state.get("enter_pressed")):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # AI响应
    with st.chat_message("assistant"):
        if st.session_state.use_streaming:
            full_response = ""
            message_placeholder = st.empty()
            
            with st.spinner("思考中..."):
                for chunk in stream_chat(prompt):
                    full_response = chunk
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        else:
            with st.spinner("思考中..."):
                result = call_api("/chat", data={
                    "message": prompt,
                    "system_message": st.session_state.system_message,
                    "model_provider": st.session_state.model_provider,
                    "model_name": st.session_state.model_name,
                    "temperature": st.session_state.temperature,
                    "chat_history": []
                })
                full_response = result.get("response", "发生错误")
                st.markdown(full_response)
        
        # 添加AI响应到历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # 重新运行以更新界面
        st.rerun()


# 页脚
st.markdown("""
    <div style="text-align: center; margin-top: 35px; padding: 25px; background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.3);">
        <div class="footer-links" style="display: flex; justify-content: center; gap: 35px; margin-bottom: 18px;">
            <a href="http://localhost:8000/docs" target="_blank" style="display: flex; align-items: center; gap: 8px;">
                <span>📚</span>
                <span>API文档</span>
            </a>
            <a href="https://smith.langchain.com" target="_blank" style="display: flex; align-items: center; gap: 8px;">
                <span>📊</span>
                <span>LangSmith</span>
            </a>
            <a href="https://github.com" target="_blank" style="display: flex; align-items: center; gap: 8px;">
                <span>💻</span>
                <span>GitHub</span>
            </a>
        </div>
        <p style="color: rgba(0,0,0,0.5); font-size: 14px; font-weight: 500;">
            🌱 谷雨 · Powered by <span style="color: #667eea;">LangChain</span> · <span style="color: #764ba2;">LangServe</span> · <span style="color: #f093fb;">Streamlit</span>
        </p>
    </div>
""", unsafe_allow_html=True)
