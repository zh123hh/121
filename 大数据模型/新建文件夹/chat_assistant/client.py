"""
LangServe客户端
用于调用部署的LangServe服务
"""
from typing import Optional, AsyncIterator, Dict, Any
import httpx
from langserve import RemoteRunnable


class ChatAssistantClient:
    """对话助手客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.http_client = httpx.AsyncClient(base_url=base_url, timeout=60.0)

        # LangServe远程runnable
        self.chat_runnable = RemoteRunnable(f"{base_url}/langchain/chat")
        self.translate_runnable = RemoteRunnable(f"{base_url}/langchain/translate")
        self.summary_runnable = RemoteRunnable(f"{base_url}/langchain/summary")

    async def chat(
        self,
        message: str,
        system_message: str = "你是一个 helpful 的AI助手。",
        model_provider: str = "openai",
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        chat_history: list = None,
    ) -> str:
        """
        单次对话

        Args:
            message: 用户消息
            system_message: 系统提示
            model_provider: 模型提供商
            model_name: 模型名称
            temperature: 温度参数
            chat_history: 对话历史

        Returns:
            AI回复
        """
        response = await self.http_client.post(
            "/chat",
            json={
                "message": message,
                "system_message": system_message,
                "model_provider": model_provider,
                "model_name": model_name,
                "temperature": temperature,
                "chat_history": chat_history or [],
            },
        )
        response.raise_for_status()
        return response.json()["response"]

    async def stream_chat(
        self,
        message: str,
        session_id: str = "default",
        system_message: str = "你是一个 helpful 的AI助手。",
        model_provider: str = "openai",
        model_name: str = "gpt-4o-mini",
    ) -> AsyncIterator[str]:
        """
        流式对话

        Args:
            message: 用户消息
            session_id: 会话ID
            system_message: 系统提示
            model_provider: 模型提供商
            model_name: 模型名称

        Yields:
            流式响应块
        """
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/stream",
                json={
                    "message": message,
                    "session_id": session_id,
                    "system_message": system_message,
                    "model_provider": model_provider,
                    "model_name": model_name,
                },
                timeout=60.0,
            ) as response:
                async for chunk in response.aiter_text():
                    yield chunk

    async def translate(
        self,
        text: str,
        target_language: str = "中文",
    ) -> str:
        """
        翻译文本

        Args:
            text: 要翻译的文本
            target_language: 目标语言

        Returns:
            翻译结果
        """
        response = await self.http_client.post(
            "/translate",
            json={
                "text": text,
                "target_language": target_language,
            },
        )
        response.raise_for_status()
        return response.json()["translation"]

    async def summary(
        self,
        text: str,
        max_length: int = 200,
    ) -> str:
        """
        文本摘要

        Args:
            text: 要摘要的文本
            max_length: 最大长度

        Returns:
            摘要结果
        """
        response = await self.http_client.post(
            "/summary",
            json={
                "text": text,
                "max_length": max_length,
            },
        )
        response.raise_for_status()
        return response.json()["summary"]

    async def list_models(self) -> list:
        """列出可用模型"""
        response = await self.http_client.get("/models")
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = await self.http_client.get("/health")
        response.raise_for_status()
        return response.json()

    async def clear_session(self, session_id: str):
        """清空会话历史"""
        response = await self.http_client.post(f"/chat/{session_id}/clear")
        response.raise_for_status()
        return response.json()

    # ============ LangServe RemoteRunnable 方法 ============

    async def chat_with_runnable(self, message: str) -> str:
        """使用RemoteRunnable进行对话"""
        result = await self.chat_runnable.ainvoke({
            "input": message,
            "chat_history": [],
        })
        return result

    async def translate_with_runnable(self, text: str) -> str:
        """使用RemoteRunnable进行翻译"""
        result = await self.translate_runnable.ainvoke({"text": text})
        return result

    async def summary_with_runnable(self, text: str) -> str:
        """使用RemoteRunnable进行摘要"""
        result = await self.summary_runnable.ainvoke({"text": text})
        return result

    async def close(self):
        """关闭客户端"""
        await self.http_client.aclose()


# 同步客户端包装
class ChatAssistantClientSync:
    """同步对话助手客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.http_client = httpx.Client(base_url=base_url, timeout=60.0)

        # LangServe远程runnable
        self.chat_runnable = RemoteRunnable(f"{base_url}/langchain/chat")
        self.translate_runnable = RemoteRunnable(f"{base_url}/langchain/translate")
        self.summary_runnable = RemoteRunnable(f"{base_url}/langchain/summary")

    def chat(
        self,
        message: str,
        system_message: str = "你是一个 helpful 的AI助手。",
        model_provider: str = "openai",
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        chat_history: list = None,
    ) -> str:
        """单次对话"""
        response = self.http_client.post(
            "/chat",
            json={
                "message": message,
                "system_message": system_message,
                "model_provider": model_provider,
                "model_name": model_name,
                "temperature": temperature,
                "chat_history": chat_history or [],
            },
        )
        response.raise_for_status()
        return response.json()["response"]

    def translate(self, text: str, target_language: str = "中文") -> str:
        """翻译文本"""
        response = self.http_client.post(
            "/translate",
            json={
                "text": text,
                "target_language": target_language,
            },
        )
        response.raise_for_status()
        return response.json()["translation"]

    def summary(self, text: str, max_length: int = 200) -> str:
        """文本摘要"""
        response = self.http_client.post(
            "/summary",
            json={
                "text": text,
                "max_length": max_length,
            },
        )
        response.raise_for_status()
        return response.json()["summary"]

    def list_models(self) -> list:
        """列出可用模型"""
        response = self.http_client.get("/models")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.http_client.get("/health")
        response.raise_for_status()
        return response.json()

    def close(self):
        """关闭客户端"""
        self.http_client.close()
