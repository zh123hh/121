"""
LangServe服务部署模块
"""
import os
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langserve import add_routes
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from chat_assistant.config import settings
from chat_assistant.chains import (
    create_chat_chain,
    create_translation_chain,
    create_summary_chain,
    ChatAssistant,
)
from chat_assistant.models import model_manager


# 请求/响应模型定义
class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息")
    system_message: str = Field(
        default="你是谷雨，一个可爱的AI助手。请用友好、亲切的语气回答问题。",
        description="系统提示消息"
    )
    model_provider: str = Field(default="deepseek", description="模型提供商")
    model_name: str = Field(default="deepseek-chat", description="模型名称")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    chat_history: list = Field(default=[], description="对话历史")


class ChatResponse(BaseModel):
    """对话响应"""
    response: str = Field(..., description="AI回复")


class StreamChatRequest(BaseModel):
    """流式对话请求"""
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default="default", description="会话ID")
    system_message: str = Field(
        default="你是谷雨，一个可爱的AI助手。请用友好、亲切的语气回答问题。",
        description="系统提示消息"
    )
    model_provider: str = Field(default="deepseek", description="模型提供商")
    model_name: str = Field(default="deepseek-chat", description="模型名称")


class TranslateRequest(BaseModel):
    """翻译请求"""
    text: str = Field(..., description="要翻译的文本")
    target_language: str = Field(default="中文", description="目标语言")


class SummaryRequest(BaseModel):
    """摘要请求"""
    text: str = Field(..., description="要摘要的文本")
    max_length: int = Field(default=200, ge=50, le=1000, description="最大长度")


class ModelInfoResponse(BaseModel):
    """模型信息响应"""
    provider: str
    models: list


# 会话管理
session_assistants: dict = {}


def get_or_create_assistant(
    session_id: str,
    system_message: str,
    model_provider: str,
    model_name: str,
) -> ChatAssistant:
    """获取或创建对话助手"""
    if session_id not in session_assistants:
        session_assistants[session_id] = ChatAssistant(
            system_message=system_message,
            model_provider=model_provider,
            model_name=model_name,
        )
    return session_assistants[session_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("启动LangChain对话助手服务...")
    print(f"LangSmith监控: {'已启用' if settings.langchain_tracing_v2 else '未启用'}")
    print(f"默认模型: {settings.default_model}")

    yield

    # 关闭时执行
    print("关闭服务...")


# 创建FastAPI应用
app = FastAPI(
    title="LangChain对话助手API",
    description="""
基于LangChain框架开发的智能对话助手服务，集成LangSmith监控、LangServe部署、官方Templates。

**功能特性：**

- **多模型支持**: OpenAI (GPT-4/GPT-3.5) / Anthropic (Claude) / DeepSeek (本地部署)
- **LangSmith监控**: 完整的调用追踪和性能监控
- **LangServe部署**: RESTful API + RemoteRunnable支持
- **流式输出**: SSE实时流式响应
- **会话管理**: 支持多会话对话历史

**API端点：**

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 欢迎页 |
| `/health` | GET | 健康检查 |
| `/models` | GET | 列出可用模型 |
| `/chat` | POST | 单次对话 |
| `/chat/stream` | POST | 流式对话 |
| `/chat/{session_id}/clear` | POST | 清空会话 |
| `/translate` | POST | 翻译 |
| `/summary` | POST | 摘要 |

**LangServe端点：**
- `/langchain/chat` - 标准LangChain链
- `/langchain/translate` - 翻译链
- `/langchain/summary` - 摘要链
""",
    version="0.1.0",
    lifespan=lifespan,
    contact={
        "name": "LangChain对话助手",
        "url": "https://github.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ API路由 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "LangChain对话助手API",
        "version": "0.1.0",
        "docs": "/docs",
        "langsmith": settings.langchain_tracing_v2,
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "langsmith_enabled": settings.langchain_tracing_v2,
    }


@app.get("/models", response_model=list[ModelInfoResponse])
async def list_models():
    """列出可用模型"""
    return model_manager.list_available_models()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """单次对话接口"""
    try:
        chain = create_chat_chain(
            system_message=request.system_message,
            model_provider=request.model_provider,
            model_name=request.model_name,
            temperature=request.temperature,
        )

        response = await chain.ainvoke({
            "input": request.message,
            "chat_history": [
                HumanMessage(content=msg["content"])
                if msg["role"] == "human"
                else HumanMessage(content=msg["content"])
                for msg in request.chat_history
            ],
        })

        return ChatResponse(response=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def stream_chat(request: StreamChatRequest):
    """流式对话接口"""
    async def generate() -> AsyncIterator[str]:
        assistant = get_or_create_assistant(
            session_id=request.session_id,
            system_message=request.system_message,
            model_provider=request.model_provider,
            model_name=request.model_name,
        )

        async for chunk in assistant.stream_chat(request.message):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@app.post("/chat/{session_id}/clear")
async def clear_chat_history(session_id: str):
    """清空对话历史"""
    if session_id in session_assistants:
        session_assistants[session_id].clear_history()
        return {"message": f"会话 {session_id} 历史已清空"}
    return {"message": "会话不存在"}


@app.post("/translate")
async def translate(request: TranslateRequest):
    """翻译接口"""
    try:
        chain = create_translation_chain(
            target_language=request.target_language,
        )
        result = await chain.ainvoke({"text": request.text})
        return {"translation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summary")
async def summary(request: SummaryRequest):
    """摘要接口"""
    try:
        chain = create_summary_chain(max_length=request.max_length)
        result = await chain.ainvoke({"text": request.text})
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ LangServe路由 ============

# 尝试添加LangServe路由（需要API密钥）
try:
    # 添加标准LangChain链路由
    add_routes(
        app,
        create_chat_chain(),
        path="/langchain/chat",
        enabled_endpoints=["invoke", "batch", "stream"],
    )

    add_routes(
        app,
        create_translation_chain(),
        path="/langchain/translate",
        enabled_endpoints=["invoke", "batch"],
    )

    add_routes(
        app,
        create_summary_chain(),
        path="/langchain/summary",
        enabled_endpoints=["invoke", "batch"],
    )
    print("[INFO] LangServe routes added successfully")
except Exception as e:
    print(f"[WARNING] Could not add LangServe routes: {e}")
    print("[INFO] LangServe routes will be unavailable without API keys")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "chat_assistant.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
