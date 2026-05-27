"""
LangChain对话助手 - 后端主入口
集成LangSmith监控、LangServe部署、官方Templates
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置LangSmith
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "chat-assistant")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langserve import add_routes
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, ConversationChain
from pydantic import BaseModel, Field
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager

# 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "EMPTY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "http://localhost:8080/v1")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    system_message: str = Field(default="你是一个 helpful 的AI助手。", description="系统提示")
    model_provider: str = Field(default="openai", description="模型提供商")
    model_name: str = Field(default="gpt-4o-mini", description="模型名称")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI回复")


# 会话存储
sessions = {}


def get_memory(session_id: str):
    """获取或创建会话记忆"""
    if session_id not in sessions:
        sessions[session_id] = ConversationBufferMemory(return_messages=True)
    return sessions[session_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 启动LangChain对话助手服务...")
    print(f"📡 服务地址: http://{APP_HOST}:{APP_PORT}")
    print(f"📚 API文档: http://{APP_HOST}:{APP_PORT}/docs")
    yield
    print("👋 关闭服务...")


app = FastAPI(
    title="🤖 LangChain对话助手API",
    description="""
基于LangChain框架开发的智能对话助手服务。

**核心功能：**
- LLM调用：支持OpenAI、DeepSeek等模型
- Prompt工程：自定义系统提示
- Chain链式调用：构建复杂工作流
- Memory记忆：会话级对话历史
- Tool工具使用：支持工具调用

**API端点：**
- `/chat` - 单次对话
- `/chat/stream` - 流式对话
- `/chat/{session_id}/clear` - 清空会话
- `/models` - 列出可用模型
- `/langchain/chat` - LangServe标准端点
""",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_llm(model_provider: str = "openai", model_name: str = "gpt-4o-mini", temperature: float = 0.7):
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
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )


# 创建基础对话链
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_message}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

chat_chain = prompt | get_llm() | StrOutputParser()


@app.get("/")
async def root():
    return {"message": "LangChain对话助手API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/models")
async def list_models():
    return [
        {"provider": "openai", "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]},
        {"provider": "deepseek", "models": ["deepseek-chat", "deepseek-r1-chat"]},
    ]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session_id: str = "default"):
    """单次对话接口"""
    try:
        memory = get_memory(session_id)
        chat_history = memory.load_memory_variables({})["history"]
        
        response = chat_chain.invoke({
            "system_message": request.system_message,
            "input": request.message,
            "chat_history": chat_history,
        })
        
        # 保存到记忆
        memory.save_context({"input": request.message}, {"output": response})
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def stream_chat(request: ChatRequest, session_id: str = "default"):
    """流式对话接口"""
    memory = get_memory(session_id)
    chat_history = memory.load_memory_variables({})["history"]
    
    llm = get_llm(request.model_provider, request.model_name, request.temperature)
    llm.streaming = True
    
    async def generate():
        full_response = ""
        async for chunk in llm.astream([
            {"role": "system", "content": request.system_message},
            *[{"role": "m" + ("essage" if isinstance(m, dict) else "essage"), 
               "content": m.get("content", str(m))} for m in chat_history],
            {"role": "user", "content": request.message},
        ]):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
        
        # 保存到记忆
        memory.save_context({"input": request.message}, {"output": full_response})
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/chat/{session_id}/clear")
async def clear_session(session_id: str):
    """清空会话历史"""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": f"会话 {session_id} 已清空"}


# 添加LangServe标准路由
add_routes(
    app,
    chat_chain,
    path="/langchain/chat",
    enabled_endpoints=["invoke", "batch", "stream"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
