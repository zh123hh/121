"""
配置管理模块
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
    """应用配置类"""

    # API Keys
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = "https://api.openai.com/v1"
    anthropic_api_key: Optional[str] = None

    # DeepSeek配置（云端API）
    deepseek_api_key: Optional[str] = "EMPTY"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model_name: str = "deepseek-chat"

    # LangSmith配置
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: Optional[str] = None
    langchain_project: str = "chat-assistant"

    # 应用配置
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    # 模型配置
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.7
    max_tokens: int = 2048


def load_settings() -> Settings:
    """从环境变量加载配置"""
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "EMPTY"),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "http://localhost:8080/v1"),
        deepseek_model_name=os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat"),
        langchain_tracing_v2=os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true",
        langchain_endpoint=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        langchain_api_key=os.getenv("LANGCHAIN_API_KEY"),
        langchain_project=os.getenv("LANGCHAIN_PROJECT", "chat-assistant"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        default_model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return load_settings()


settings = get_settings()
