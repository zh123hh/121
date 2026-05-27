"""
LangChain对话助手 - 主入口
集成LangSmith监控、LangServe部署、官方Templates
"""
import argparse
import asyncio
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def run_server():
    """运行API服务"""
    import uvicorn
    from chat_assistant.config import settings

    print("[INFO] 启动LangChain对话助手服务...")
    print(f"[INFO] 服务地址: http://{settings.app_host}:{settings.app_port}")
    print(f"[INFO] API文档: http://{settings.app_host}:{settings.app_port}/docs")
    print(f"[INFO] LangSmith: {'已启用' if settings.langchain_tracing_v2 else '未启用'}")

    uvicorn.run(
        "chat_assistant.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )


def run_cli():
    """运行命令行界面"""
    from chat_assistant.cli import main as cli_main
    cli_main()


def run_demo():
    """运行演示示例"""
    asyncio.run(_run_demo())


async def _run_demo():
    """异步演示"""
    from chat_assistant.chains import ChatAssistant
    from chat_assistant.templates import (
        create_translation_chain,
        create_summary_chain,
        list_available_templates,
    )

    print("=" * 60)
    print("LangChain对话助手 - 演示")
    print("=" * 60)

    # 1. 基础对话演示
    print("\n【1. 基础对话演示】")
    assistant = ChatAssistant(
        system_message="你是一个 helpful 的AI助手。",
        model_provider="openai",
    )

    response = assistant.chat("你好！请介绍一下LangChain是什么？")
    print(f"用户: 你好！请介绍一下LangChain是什么？")
    print(f"AI: {response}")

    # 2. 翻译链演示
    print("\n【2. 翻译链演示】")
    translate_chain = create_translation_chain(target_language="英文")
    text = "LangChain是一个强大的LLM应用开发框架。"
    translation = await translate_chain.ainvoke({"text": text})
    print(f"原文: {text}")
    print(f"翻译: {translation}")

    # 3. 摘要链演示
    print("\n【3. 摘要链演示】")
    summary_chain = create_summary_chain(max_length=100)
    long_text = """
    LangChain是一个用于开发由语言模型驱动的应用程序的框架。
    它使得应用程序能够：
    1. 具有上下文感知能力：将语言模型连接到上下文来源（提示指令、少量示例、内容等）
    2. 进行推理：依靠语言模型进行推理（关于如何根据提供的上下文回答，采取什么操作等）
    这个框架的主要价值主张包括：
    1. 组件：用于处理语言模型的抽象，以及每个抽象的实现集合
    2. 现成的链：用于完成特定高级任务的组件的结构化组装
    """
    summary = await summary_chain.ainvoke({"text": long_text})
    print(f"原文长度: {len(long_text)} 字符")
    print(f"摘要: {summary}")

    # 4. 列出可用模板
    print("\n【4. 可用模板列表】")
    templates = list_available_templates()
    for template in templates:
        print(f"  • {template['name']}: {template['description']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="LangChain对话助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py server    # 启动API服务
  python main.py cli       # 启动命令行界面
  python main.py demo      # 运行演示示例
        """,
    )

    parser.add_argument(
        "command",
        choices=["server", "cli", "demo"],
        help="运行模式: server (API服务), cli (命令行), demo (演示)",
    )

    args = parser.parse_args()

    if args.command == "server":
        run_server()
    elif args.command == "cli":
        run_cli()
    elif args.command == "demo":
        run_demo()


if __name__ == "__main__":
    main()
