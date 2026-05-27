"""
LangChain对话助手 - 前端界面
"""
import streamlit as st
import requests
import time

# 页面配置
st.set_page_config(
    page_title="LangChain对话助手",
    page_icon="🤖",
    layout="wide",
)

# 自定义样式
st.markdown("""
<style>
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 8px 0;
        max-width: 75%;
        float: right;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-bubble {
        background: #f1f5f9;
        color: #1e293b;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 8px 0;
        max-width: 75%;
        float: left;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 20px;
    }
    
    .input-box {
        border-radius: 25px;
        padding: 12px 20px;
        border: 2px solid #e2e8f0;
        width: 100%;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .gradient-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .status-online {
        background: #22c55e;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
</style>
""", unsafe_allow_html=True)

# 配置
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# 初始化状态
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
if "system_message" not in st.session_state:
    st.session_state.system_message = "你是一个 helpful 的AI助手。"


def call_api(endpoint, method="POST", data=None):
    try:
        url = f"{API_URL}{endpoint}"
        if method == "POST":
            resp = requests.post(url, json=data, timeout=60)
        else:
            resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API错误: {str(e)}")
        return None


def stream_chat(message):
    url = f"{API_URL}/chat/stream"
    data = {
        "message": message,
        "system_message": st.session_state.system_message,
        "model_provider": st.session_state.model_provider,
        "model_name": st.session_state.model_name,
        "temperature": st.session_state.temperature,
    }
    
    try:
        with requests.post(url, json=data, stream=True, timeout=60) as resp:
            full_response = ""
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    full_response += chunk.decode("utf-8")
                    yield full_response
            return full_response
    except Exception as e:
        yield f"错误: {str(e)}"


# 侧边栏
with st.sidebar:
    st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-size: 24px;">🤖 对话助手</h2>
            <p style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 5px;">LangChain Powered</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 服务状态
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        status = "在线" if resp.status_code == 200 else "离线"
        status_color = "#22c55e" if status == "在线" else "#ef4444"
    except:
        status = "离线"
        status_color = "#ef4444"
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: {'#dcfce7' if status == '在线' else '#fee2e2'}; border-radius: 10px; margin-bottom: 20px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: {status_color}; animation: {'pulse 2s infinite' if status == '在线' else 'none'};"></div>
            <span style="color: {'#166534' if status == '在线' else '#991b1b'}; font-weight: 600;">API服务: {status}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 模型配置
    st.subheader("⚙️ 模型配置", divider="gray")
    
    providers = ["openai", "deepseek"]
    provider_names = {"openai": "🔵 OpenAI", "deepseek": "🟢 DeepSeek (本地)"}
    default_provider_index = providers.index(st.session_state.model_provider)
    st.session_state.model_provider = st.selectbox(
        "模型提供商", providers, index=default_provider_index, format_func=lambda x: provider_names[x]
    )
    
    model_options = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "deepseek": ["deepseek-chat", "deepseek-r1-chat"],
    }
    st.session_state.model_name = st.selectbox("模型名称", model_options[st.session_state.model_provider])
    
    # 参数配置
    st.subheader("🎛️ 生成参数", divider="gray")
    st.session_state.temperature = st.slider("温度参数", 0.0, 2.0, 0.7, 0.1)
    
    # 系统提示
    st.subheader("📝 系统提示", divider="gray")
    st.session_state.system_message = st.text_area("", st.session_state.system_message, height=100)
    
    # 操作按钮
    st.subheader("🔧 操作", divider="gray")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = f"session_{int(time.time())}"
            st.success("已清空")
    with col2:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    # 中翻英功能
    st.subheader("🌐 中文翻译", divider="gray")
    translate_input = st.text_area("输入要翻译的中文文本", height=80)
    if st.button("🔤 翻译成英文", use_container_width=True):
        if translate_input.strip():
            with st.spinner("翻译中..."):
                translate_prompt = f"""Translate the following Chinese text to English. Only output the English translation, no additional explanation.

Chinese text: {translate_input}

English translation:"""
                url = f"{API_URL}/chat/stream"
                data = {
                    "message": translate_prompt,
                    "system_message": "You are a professional translator. Translate Chinese to English accurately.",
                    "model_provider": st.session_state.model_provider,
                    "model_name": st.session_state.model_name,
                    "temperature": 0.0,
                }
                try:
                    with requests.post(url, json=data, stream=True, timeout=60) as resp:
                        full_response = ""
                        for chunk in resp.iter_content(chunk_size=1024):
                            if chunk:
                                full_response += chunk.decode("utf-8")
                        st.success("翻译结果：")
                        st.markdown(f"""
                            <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; border-radius: 0 10px 10px 0;">
                                <div style="font-weight: 600; color: #166534; margin-bottom: 5px;">English Translation</div>
                                <div style="color: #15803d; font-size: 16px;">{full_response.strip()}</div>
                            </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"翻译失败: {str(e)}")
        else:
            st.warning("请输入要翻译的文本")


# 主界面
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 class="gradient-title" style="font-size: 36px;">LangChain对话助手</h1>
        <p style="color: #64748b;">基于LangChain框架 · 集成LangSmith监控 · LangServe部署</p>
    </div>
""", unsafe_allow_html=True)

# 功能卡片
cols = st.columns(4)
features = [
    ("🤖", "多模型支持", "OpenAI / DeepSeek"),
    ("📊", "LangSmith监控", "完整调用追踪"),
    ("🚀", "LangServe部署", "RESTful API"),
    ("💬", "流式输出", "实时响应"),
]
for col, (icon, title, desc) in zip(cols, features):
    with col:
        st.markdown(f"""
            <div style="background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                <div style="font-size: 32px; margin-bottom: 10px;">{icon}</div>
                <div style="font-weight: 600; margin-bottom: 5px;">{title}</div>
                <div style="font-size: 12px; color: #64748b;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)

# 对话区域
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
        <div class="assistant-bubble" style="margin: 0 auto; float: none; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">👋</div>
            <div style="font-weight: 600;">欢迎使用LangChain对话助手</div>
            <div style="font-size: 14px; color: #64748b; margin-top: 5px;">
                请在左侧配置模型，然后开始对话！
            </div>
        </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
            <div class="user-bubble">
                <div style="font-weight: 600; margin-bottom: 5px;">您</div>
                <div>{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="assistant-bubble">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                    <span>🤖</span>
                    <span style="font-weight: 600;">AI助手</span>
                    <span style="font-size: 12px; color: #94a3b8; margin-left: auto;">{st.session_state.model_name}</span>
                </div>
                <div>{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 输入区域
st.markdown('<div style="margin-top: 20px; padding: 20px; background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
col_input, col_send = st.columns([10, 1])

with col_input:
    prompt = st.text_input("", placeholder="输入消息...", label_visibility="collapsed")

with col_send:
    send_btn = st.button("➤", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# 处理输入
if prompt and send_btn:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        for chunk in stream_chat(prompt):
            full_response = chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        st.rerun()

# 页脚
st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8fafc; border-radius: 15px;">
        <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 15px;">
            <span style="color: #64748b;">🔗 <a href="http://localhost:8000/docs" target="_blank" style="color: #667eea;">API文档</a></span>
            <span style="color: #64748b;">📊 <a href="https://smith.langchain.com" target="_blank" style="color: #667eea;">LangSmith</a></span>
        </div>
        <p style="color: #94a3b8; font-size: 14px;">Powered by LangChain · LangServe · Streamlit</p>
    </div>
""", unsafe_allow_html=True)
