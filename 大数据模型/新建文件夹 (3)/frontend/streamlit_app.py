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

# 自定义CSS样式 - 极简版，避免DOM操作错误
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e8eef5 100%);
    }
    
    .message-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 25px;
        padding: 25px;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .user-message {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1a 100%);
        color: #ffffff;
        padding: 18px 24px;
        border-radius: 25px 25px 8px 25px;
        margin-bottom: 15px;
        max-width: 75%;
        margin-left: auto;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1a1a2e;
        padding: 18px 24px;
        border-radius: 25px 25px 25px 8px;
        margin-bottom: 15px;
        max-width: 75%;
    }
    
    .stTextInput>div>div>input {
        border-radius: 30px;
        padding: 18px 25px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        background: rgba(255, 255, 255, 0.98);
    }
    
    .stButton>button {
        border-radius: 30px;
        padding: 15px 35px;
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: #f7fafc;
        border: none;
    }
    
    [data-testid="stSidebar"] {
        background: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        color: #334155 !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox>div>div {
        background: #f7fafc !important;
        border-radius: 15px;
        border: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.04);
        margin-bottom: 25px;
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .status-online {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }
    
    .status-offline {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, rgba(237, 242, 247, 0.6) 0%, rgba(226, 232, 240, 0.6) 100%);
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 25px;
        padding: 35px;
        text-align: center;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# 配置
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8002")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

if "model_provider" not in st.session_state:
    st.session_state.model_provider = "deepseek"

if "model_name" not in st.session_state:
    st.session_state.model_name = "deepseek-chat"

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
    
    # 使用简单的文本选项，避免图标可能导致的问题
    provider_options = ["OpenAI", "Anthropic", "DeepSeek"]
    
    # 创建映射
    display_to_provider = {
        "OpenAI": "openai",
        "Anthropic": "anthropic",
        "DeepSeek": "deepseek"
    }
    
    # 获取当前provider对应的显示名称
    provider_to_display = {v: k for k, v in display_to_provider.items()}
    current_display = provider_to_display.get(st.session_state.model_provider, "DeepSeek")
    
    # 确保当前显示值在选项列表中
    if current_display not in provider_options:
        current_display = "DeepSeek"
    
    # 获取默认索引
    default_idx = provider_options.index(current_display)
    
    # 显示下拉框
    selected_display = st.selectbox(
        "模型提供商",
        provider_options,
        index=default_idx,
        key="provider_select_2024"
    )
    
    # 映射回实际provider值
    st.session_state.model_provider = display_to_provider[selected_display]
    
    # 模型名称选择
    model_options = {
        "deepseek": ["deepseek-chat", "deepseek-r1-chat"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    }
    
    current_models = model_options.get(st.session_state.model_provider, ["gpt-4o-mini"])
    
    # 确保默认模型有效
    if st.session_state.model_name not in current_models:
        st.session_state.model_name = current_models[0]
    
    st.session_state.model_name = st.selectbox(
        "模型名称",
        current_models,
        index=current_models.index(st.session_state.model_name),
        key="model_select"
    )
    
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
    
    # 自定义按钮样式 - 浅色背景（针对侧边栏所有按钮）
    st.markdown("""
        <style>
        /* 侧边栏中的所有按钮 */
        section[data-testid="stSidebar"] button {
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            color: #334155 !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] button:hover {
            background-color: #f1f5f9 !important;
            border-color: #cbd5e0 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        section[data-testid="stSidebar"] button:active {
            transform: scale(0.98);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 操作按钮
    st.subheader("🔧 快捷操作", divider="gray")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 清空对话", use_container_width=True, key="clear_btn"):
            st.session_state.messages = []
            st.session_state.session_id = f"session_{int(time.time())}"
            st.session_state.chat_history = []
            st.success("对话已清空")
    
    with col2:
        if st.button("🔄 刷新页面", use_container_width=True, key="refresh_btn"):
            st.rerun()
    
    # 快捷功能
    st.subheader("⚡ 快捷指令", divider="gray")
    
    quick_prompts = [
        ("✍️ 写邮件", "帮我写一封专业的商务邮件"),
        ("📝 写总结", "帮我总结以下文本内容，提取关键要点"),
        ("🌍 翻译", "将以下内容翻译成英文，保持原意"),
        ("💡 创意写作", "帮我构思一个有趣的故事开头"),
    ]
    
    for label, prompt in quick_prompts:
        if st.button(label, use_container_width=True, key=f"quick_{label}"):
            st.session_state.quick_prompt = prompt
            st.session_state.user_input = prompt
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
        # 尝试连接API获取欢迎消息
        api_connected = False
        welcome_response = None
        
        try:
            # 测试API连接
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                # API可用，获取欢迎消息
                welcome_data = {
                    "message": "你好，做个自我介绍",
                    "model_provider": st.session_state.model_provider,
                    "model_name": st.session_state.model_name,
                    "system_message": "你是谷雨，一个可爱的AI助手。请用友好、亲切的语气回答问题。"
                }
                response = requests.post(f"{API_BASE_URL}/chat", json=welcome_data, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    welcome_response = result.get("response", "")
                    api_connected = True
        except Exception as e:
            pass
        
        if api_connected and welcome_response:
            # API连接成功，显示真实欢迎消息
            st.markdown(f"""
                <div class="welcome-card">
                    <div style="font-size: 48px; margin-bottom: 15px;">🌱</div>
                    <div style="font-weight: 700; font-size: 24px; margin-bottom: 10px; color: #0f0f0f;">谷雨</div>
                    <div style="font-size: 15px; color: #3d4a5c; line-height: 1.7;">
                        {welcome_response.replace('\n', '<br>')}
                    </div>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(0,0,0,0.06);">
                        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; background: #dcfce7; color: #166534; border-radius: 20px; font-size: 12px;">
                            ✅ API已连接
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # API连接失败，显示演示模式
            st.markdown("""
                <div class="welcome-card">
                    <div style="font-size: 48px; margin-bottom: 15px;">🌱</div>
                    <div style="font-weight: 700; font-size: 24px; margin-bottom: 10px; color: #0f0f0f;">你好，我是谷雨</div>
                    <div style="font-size: 15px; color: #3d4a5c; line-height: 1.7;">
                        我可以帮助你写作、翻译、编程、问答等<br>
                        在左侧配置模型，然后开始对话吧！
                    </div>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(0,0,0,0.06);">
                        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; background: #fef3c7; color: #92400e; border-radius: 20px; font-size: 12px;">
                            ⚠️ 演示模式
                        </span>
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
