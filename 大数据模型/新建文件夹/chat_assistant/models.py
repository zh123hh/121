"""
模型配置与管理模块
支持DeepSeek本地部署接口
"""
from typing import Optional, Dict, Any, List
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from chat_assistant.config import settings


class ModelManager:
    """模型管理器"""

    _instance = None
    _models: Dict[str, BaseChatModel] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_openai_model(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
    ) -> ChatOpenAI:
        """获取OpenAI模型实例"""
        config_key = f"openai_{model_name}_{temperature}_{max_tokens}_{streaming}"

        if config_key not in self._models:
            self._models[config_key] = ChatOpenAI(
                model=model_name or settings.default_model,
                temperature=temperature or settings.default_temperature,
                max_tokens=max_tokens or settings.max_tokens,
                streaming=streaming,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

        return self._models[config_key]

    def get_anthropic_model(
        self,
        model_name: str = "claude-3-sonnet-20240229",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
    ) -> ChatAnthropic:
        """获取Anthropic模型实例"""
        config_key = f"anthropic_{model_name}_{temperature}_{max_tokens}_{streaming}"

        if config_key not in self._models:
            self._models[config_key] = ChatAnthropic(
                model=model_name,
                temperature=temperature or settings.default_temperature,
                max_tokens=max_tokens or settings.max_tokens,
                streaming=streaming,
                api_key=settings.anthropic_api_key,
            )

        return self._models[config_key]

    def get_deepseek_model(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
    ) -> ChatOpenAI:
        """获取DeepSeek模型实例（本地部署）"""
        config_key = f"deepseek_{model_name}_{temperature}_{max_tokens}_{streaming}"

        if config_key not in self._models:
            self._models[config_key] = ChatOpenAI(
                model=model_name or settings.deepseek_model_name,
                temperature=temperature or settings.default_temperature,
                max_tokens=max_tokens or settings.max_tokens,
                streaming=streaming,
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )

        return self._models[config_key]

    def get_model(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
    ) -> BaseChatModel:
        """获取指定提供商的模型"""
        if provider.lower() == "openai":
            return self.get_openai_model(model_name, temperature, max_tokens, streaming)
        elif provider.lower() == "anthropic":
            return self.get_anthropic_model(
                model_name or "claude-3-sonnet-20240229",
                temperature,
                max_tokens,
                streaming,
            )
        elif provider.lower() == "deepseek":
            return self.get_deepseek_model(model_name, temperature, max_tokens, streaming)
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")

    def list_available_models(self) -> List[Dict[str, Any]]:
        """列出可用模型"""
        return [
            {
                "provider": "openai",
                "models": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-4",
                    "gpt-3.5-turbo",
                ],
            },
            {
                "provider": "anthropic",
                "models": [
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307",
                ],
            },
            {
                "provider": "deepseek",
                "models": [
                    "deepseek-chat",
                    "deepseek-r1-chat",
                    "deepseek-moe",
                ],
                "description": "本地部署的DeepSeek模型",
            },
        ]


# 全局模型管理器实例
model_manager = ModelManager()
