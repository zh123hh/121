"""
LangChain对话助手 - 独立演示版本
无需后端服务，直接运行即可预览界面效果
"""
import streamlit as st
import time
import random

# 页面配置
st.set_page_config(
    page_title="LangChain对话助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主容器样式 */
    .main-container {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* 消息气泡样式 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin-bottom: 10px;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: #f1f5f9;
        color: #1e293b;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin-bottom: 10px;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input {
        border-radius: 25px;
        padding: 15px 20px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 按钮样式 */
    .stButton>button {
        border-radius: 20px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* 滑块样式 */
    .stSlider>div>div>div>div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 卡片样式 */
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* 渐变标题 */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 状态指示器动画 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    .status-pulse {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# 模拟响应数据
SIMPLE_RESPONSES = [
    "好的，我来帮您处理这个问题！",
    "这是一个很好的问题，让我仔细思考一下...",
    "根据您的需求，我建议这样做：",
    "我理解您的需求，这是我的建议：",
    "让我分析一下这个问题：",
]

DEMO_RESPONSES = {
    "你好": "👋 您好！我是LangChain对话助手，很高兴为您服务！有什么我可以帮助您的吗？",
    "你是谁": "我是基于LangChain框架开发的智能对话助手，支持多模型调用、流式输出、LangSmith监控等功能。",
    "介绍一下LangChain": "LangChain是一个用于开发由语言模型驱动的应用程序的框架。它提供了一系列工具和组件，帮助开发者快速构建强大的AI应用，包括文档检索、多轮对话、工具调用等功能。",
    "什么是RAG": "RAG（Retrieval-Augmented Generation）是一种检索增强生成技术，它结合了信息检索和生成模型，可以让AI回答基于特定知识库的问题，提高回答的准确性和可靠性。",
    "写一封邮件": "当然可以！请问您需要写什么类型的邮件？是商务邮件、感谢信还是其他类型？请告诉我收件人、主题和主要内容。",
}

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_provider" not in st.session_state:
    st.session_state.model_provider = "openai"

if "model_name" not in st.session_state:
    st.session_state.model_name = "gpt-4o-mini"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "use_streaming" not in st.session_state:
    st.session_state.use_streaming = True


def generate_response(message: str) -> str:
    """生成模拟响应"""
    # 检查是否有预设响应
    for key in DEMO_RESPONSES:
        if key in message:
            return DEMO_RESPONSES[key]
    
    # 生成随机响应
    base_response = random.choice(SIMPLE_RESPONSES)
    return f"{base_response}\n\n这是针对您的问题 \"{message}\" 的演示回复。在实际应用中，这将连接到真实的LLM模型（如GPT-4、Claude或DeepSeek）来生成准确的回答。\n\n**当前配置：**\n- 模型提供商: {st.session_state.model_provider}\n- 模型名称: {st.session_state.model_name}\n- 温度参数: {st.session_state.temperature}"


# 侧边栏配置
with st.sidebar:
    st.markdown("""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-size: 24px;">🤖 对话助手</h2>
            <p style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 5px;">LangChain Powered</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 服务状态（模拟在线）
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 12px; background: #dcfce7; border-radius: 10px; margin-bottom: 20px;">
            <div class="status-pulse" style="width: 10px; height: 10px; border-radius: 50%; background: #22c55e;"></div>
            <span style="color: #166534; font-weight: 600;">API服务: 在线</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 模型选择
    st.subheader("⚙️ 模型配置", divider="gray")
    
    provider_icons = {
        "openai": "🔵",
        "anthropic": "🟠", 
        "deepseek": "🟢"
    }
    provider_names = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "deepseek": "DeepSeek (本地)"
    }
    
    st.session_state.model_provider = st.selectbox(
        "模型提供商",
        ["openai", "anthropic", "deepseek"],
        index=0,
        format_func=lambda x: f"{provider_icons.get(x, '🔹')} {provider_names.get(x, x)}"
    )
    
    # 根据提供商显示模型列表
    model_options = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "deepseek": ["deepseek-chat", "deepseek-r1-chat", "deepseek-moe"],
    }
    
    st.session_state.model_name = st.selectbox(
        "模型名称",
        model_options[st.session_state.model_provider],
        index=0
    )
    
    # 显示模型描述
    descriptions = {
        "openai": "💡 OpenAI模型通过API调用，支持GPT-4/GPT-3.5系列",
        "anthropic": "💡 Anthropic Claude系列模型，以安全性著称",
        "deepseek": "💡 本地部署的DeepSeek模型，保护数据隐私",
    }
    st.markdown(f"""
        <div style="padding: 10px; background: #f8fafc; border-radius: 8px; font-size: 12px; color: #64748b;">
            {descriptions[st.session_state.model_provider]}
        </div>
    """, unsafe_allow_html=True)
    
    # 参数配置
    st.subheader("🎛️ 生成参数", divider="gray")
    
    st.session_state.temperature = st.slider(
        "温度参数",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="控制输出的随机性，值越高越随机"
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
        value=st.session_state.get("system_message", "你是一个 helpful 的AI助手。"),
        height=120,
        placeholder="输入自定义系统提示..."
    )
    
    # 操作按钮
    st.subheader("🔧 操作", divider="gray")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.success("对话历史已清空")
    
    with col2:
        if st.button("🔄 刷新状态", use_container_width=True):
            st.rerun()
    
    # 快捷功能
    st.subheader("⚡ 快捷功能", divider="gray")
    
    quick_prompts = [
        ("✍️ 写一封邮件", "帮我写一封商务邮件"),
        ("📝 写总结", "帮我总结这段文本"),
        ("🌍 翻译", "将以下内容翻译成英文"),
        ("💡 创意写作", "帮我构思一个故事开头"),
        ("🔍 代码解释", "解释这段Python代码"),
    ]
    
    for label, prompt in quick_prompts:
        if st.button(label, use_container_width=True):
            st.session_state.quick_prompt = prompt
            st.rerun()


# 主界面
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 class="gradient-text" style="font-size: 36px; margin-bottom: 10px;">LangChain对话助手</h1>
        <p style="color: #64748b; font-size: 16px;">基于LangChain框架 · 支持多模型 · 集成LangSmith监控</p>
    </div>
""", unsafe_allow_html=True)

# 功能特性卡片
cols = st.columns(4)
features = [
    ("🤖", "多模型支持", "OpenAI / Anthropic / DeepSeek"),
    ("📊", "LangSmith监控", "完整的调用追踪"),
    ("🚀", "LangServe部署", "RESTful API支持"),
    ("💬", "流式输出", "实时响应体验"),
]

for col, (icon, title, desc) in zip(cols, features):
    with col:
        st.markdown(f"""
            <div class="card">
                <div style="font-size: 32px; margin-bottom: 10px;">{icon}</div>
                <div style="font-weight: 600; margin-bottom: 5px;">{title}</div>
                <div style="font-size: 12px; color: #64748b;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)

# 对话区域
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # 显示欢迎消息
    if not st.session_state.messages:
        st.markdown("""
            <div class="assistant-message" style="margin: 0 auto; float: none; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 10px;">👋</div>
                <div style="font-weight: 600; margin-bottom: 5px;">欢迎使用LangChain对话助手</div>
                <div style="font-size: 14px; color: #64748b;">
                    我可以帮助您完成各种任务，包括写作、翻译、编程等。<br>
                    请在左侧配置模型参数，然后开始对话吧！
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # 显示对话历史
    for message in st.session_state.messages:
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
                        <span>🤖</span>
                        <span style="font-weight: 600;">AI助手</span>
                        <span style="font-size: 12px; color: #94a3b8; margin-left: auto;">
                            {st.session_state.model_name}
                        </span>
                    </div>
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# 用户输入
st.markdown('<div style="margin-top: 20px; padding: 20px; background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">', unsafe_allow_html=True)

col_input, col_send = st.columns([10, 1])

with col_input:
    prompt = st.text_input(
        "",
        placeholder="输入消息...",
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
if prompt and send_button:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # AI响应
    response = generate_response(prompt)
    
    # 模拟流式输出效果
    if st.session_state.use_streaming:
        message_placeholder = st.empty()
        full_response = ""
        for i, char in enumerate(response):
            full_response += char
            message_placeholder.markdown(f"""
                <div class="assistant-message">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                        <span>🤖</span>
                        <span style="font-weight: 600;">AI助手</span>
                        <span style="font-size: 12px; color: #94a3b8; margin-left: auto;">
                            {st.session_state.model_name}
                        </span>
                    </div>
                    <div>{full_response}▌</div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(0.01)
        
        # 最终响应
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 重新运行以更新界面
        st.rerun()
    else:
        # 添加AI响应到历史
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # 重新运行以更新界面
        st.rerun()


# 页脚
st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8fafc; border-radius: 15px;">
        <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 15px;">
            <span style="color: #64748b;">🔗 <a href="https://python.langchain.com" target="_blank" style="color: #667eea;">LangChain文档</a></span>
            <span style="color: #64748b;">📊 <a href="https://smith.langchain.com" target="_blank" style="color: #667eea;">LangSmith</a></span>
            <span style="color: #64748b;">💻 <a href="https://github.com/langchain-ai/langchain" target="_blank" style="color: #667eea;">GitHub</a></span>
        </div>
        <p style="color: #94a3b8; font-size: 14px;">
            Powered by LangChain · LangServe · Streamlit
        </p>
    </div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    st.write("")
