"""
DeepSeek本地部署接口 - 专用启动文件

此文件专门用于调用本地部署的DeepSeek模型
默认配置：
- DeepSeek API地址: http://localhost:8080/v1
- 模型名称: deepseek-chat
- API Key: EMPTY（本地部署通常不需要）

启动方式：
python app.py

或使用自定义配置：
DEEPSEEK_BASE_URL=http://localhost:8080/v1 python app.py
"""
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from chat_assistant.config import settings
from chat_assistant.chains import ChatAssistant
from chat_assistant.server import app as fastapi_app
import uvicorn


def main():
    """主入口"""
    print("=" * 60)
    print("DeepSeek API服务启动")
    print("=" * 60)
    print(f"DeepSeek API地址: {settings.deepseek_base_url}")
    print(f"默认模型: {settings.deepseek_model_name}")
    print(f"API Key: {'已配置' if settings.deepseek_api_key else '未配置'}")
    print("=" * 60)
    
    # 启动FastAPI服务
    uvicorn.run(
        "app:fastapi_app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )


async def test_deepseek():
    """测试DeepSeek连接"""
    print("\n正在测试DeepSeek连接...")
    
    try:
        assistant = ChatAssistant(
            system_message="你是一个 helpful 的AI助手。",
            model_provider="deepseek",
            model_name=settings.deepseek_model_name,
        )
        
        response = await assistant.achat("你好！")
        print("DeepSeek连接成功！")
        print(f"响应: {response[:50]}...")
    except Exception as e:
        print(f"DeepSeek连接失败: {str(e)}")
        print("请确保DeepSeek服务已配置正确: " + settings.deepseek_base_url)


if __name__ == "__main__":
    # 如果设置了测试模式，先测试连接
    if os.getenv("TEST_MODE") == "true":
        asyncio.run(test_deepseek())
    
    main()
