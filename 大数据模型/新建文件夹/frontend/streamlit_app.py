"""
谷雨 AI 助手 - 独立版
直接使用LangChain调用LLM，无需后端服务
"""
import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.memory import ConversationBufferMemory

# 加载环境变量
load_dotenv()

# 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "EMPTY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_provider" not in st.session_state:
    st.session_state.model_provider = "deepseek"
if "model_name" not in st.session_state:
    st.session_state.model_name = "deepseek-v4-pro"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "system_message" not in st.session_state:
    st.session_state.system_message = "你是一个友好的AI助手，请用中文回答问题。"
if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = ""
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

# 页面配置
st.set_page_config(
    page_title="谷雨 AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_llm(model_provider="deepseek", model_name="deepseek-chat", temperature=0.7):
    """获取LLM实例"""
    if model_provider == "deepseek":
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
    else:
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
        )


def stream_chat(prompt):
    """流式对话"""
    try:
        llm = get_llm(
            st.session_state.model_provider,
            st.session_state.model_name,
            st.session_state.temperature
        )
        
        chat_history = st.session_state.memory.load_memory_variables({})["history"]
        
        messages = [
            {"role": "system", "content": st.session_state.system_message}
        ]
        for i, m in enumerate(chat_history):
            role = "user" if i % 2 == 0 else "assistant"
            content = m.content if hasattr(m, 'content') else str(m)
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        
        for chunk in llm.stream(messages):
            if chunk.content:
                yield chunk.content
    except Exception as e:
        yield f"错误: {str(e)}"


# 侧边栏
with st.sidebar:
    st.title("🌱 谷雨")
    st.divider()
    
    # 模型配置
    st.subheader("模型配置")
    
    # 模型提供商
    provider_options = ["DeepSeek"]
    provider_map = {"DeepSeek": "deepseek"}
    reverse_provider_map = {"deepseek": "DeepSeek"}
    
    current_provider_display = reverse_provider_map.get(st.session_state.model_provider, "DeepSeek")
    selected_provider = st.selectbox(
        "模型提供商",
        provider_options,
        index=provider_options.index(current_provider_display)
    )
    
    # 模型名称
    model_options = {
        "deepseek": ["deepseek-v4-pro", "deepseek-v4-flash"]
    }
    
    if selected_provider != current_provider_display:
        st.session_state.model_provider = provider_map[selected_provider]
        st.session_state.model_name = model_options[provider_map[selected_provider]][0]
    
    available_models = model_options.get(st.session_state.model_provider, ["deepseek-v4-pro"])
    if st.session_state.model_name not in available_models:
        st.session_state.model_name = available_models[0]
    
    selected_model = st.selectbox(
        "模型名称",
        available_models,
        index=available_models.index(st.session_state.model_name)
    )
    st.session_state.model_name = selected_model
    
    st.divider()
    
    # 生成参数
    st.subheader("生成参数")
    st.session_state.temperature = st.slider("温度参数", 0.0, 1.0, 0.7, 0.1)
    
    st.divider()
    
    # 系统提示
    st.subheader("系统提示")
    st.session_state.system_message = st.text_area(
        "",
        st.session_state.system_message,
        height=100,
        placeholder="输入系统提示..."
    )
    
    st.divider()
    
    # 快捷操作
    st.subheader("快捷操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("清空对话"):
            st.session_state.messages = []
            st.session_state.memory = ConversationBufferMemory(return_messages=True)
    
    with col2:
        if st.button("刷新页面"):
            st.session_state.clear()
    
    st.divider()
    
    # 快捷指令
    st.subheader("快捷指令")
    
    if st.button("✍️ 写邮件"):
        st.session_state.quick_prompt = "帮我写一封专业的商务邮件，内容是关于..."
    
    if st.button("📝 写总结"):
        st.session_state.quick_prompt = "帮我总结以下内容，提取关键要点："
    
    if st.button("🌍 翻译"):
        st.session_state.quick_prompt = "将以下内容翻译成英文："
    
    if st.button("💡 创意写作"):
        st.session_state.quick_prompt = "帮我构思一个有趣的故事开头"


# 主内容区
st.title("谷雨 AI 助手")
st.caption("基于 LangChain 构建的智能对话系统")

# 欢迎消息（如果没有对话历史）
if not st.session_state.messages:
    st.info("你好！我是谷雨，你的AI助手。有什么我可以帮助你的吗？")

# 显示对话历史
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# 用户输入
prompt = st.chat_input("输入消息，与谷雨对话...")

# 如果有快捷指令，使用快捷指令
if st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = ""

# 处理用户输入
if prompt:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # AI响应
    with st.chat_message("assistant"):
        full_response = ""
        message_placeholder = st.empty()
        
        with st.spinner("思考中..."):
            for chunk in stream_chat(prompt):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        # 保存到记忆
        st.session_state.memory.save_context({"input": prompt}, {"output": full_response})
        
        # 添加AI响应到历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# 页脚
st.divider()
st.markdown("🌱 谷雨 · Powered by LangChain · DeepSeek")