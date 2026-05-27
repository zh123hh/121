"""
命令行交互界面
"""
import asyncio
import sys
from typing import Optional

from chat_assistant.chains import ChatAssistant
from chat_assistant.models import model_manager
from chat_assistant.config import settings


def print_banner():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                LangChain 对话助手 CLI                        ║
╠══════════════════════════════════════════════════════════════╣
║  功能:                                                       ║
║    • 支持 OpenAI / Anthropic 多模型                          ║
║    • 集成 LangSmith 监控                                     ║
║    • 流式输出支持                                            ║
║                                                              ║
║  命令:                                                       ║
║    /help     - 显示帮助                                      ║
║    /clear    - 清空对话历史                                  ║
║    /models   - 列出可用模型                                  ║
║    /switch   - 切换模型                                      ║
║    /stream   - 切换流式输出                                  ║
║    /exit     - 退出程序                                      ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_help():
    """打印帮助信息"""
    print("""
可用命令:
  /help     - 显示此帮助信息
  /clear    - 清空当前对话历史
  /models   - 列出所有可用模型
  /switch   - 切换模型提供商和模型
  /stream   - 开启/关闭流式输出
  /history  - 显示对话历史
  /save     - 保存对话历史到文件
  /exit     - 退出程序

直接输入消息开始对话...
""")


def print_models():
    """打印可用模型"""
    models = model_manager.list_available_models()
    print("\n可用模型列表:")
    print("-" * 50)
    for provider_info in models:
        print(f"\n【{provider_info['provider'].upper()}】")
        for model in provider_info['models']:
            print(f"  • {model}")
    print()


class ChatCLI:
    """对话CLI类"""

    def __init__(self):
        self.assistant: Optional[ChatAssistant] = None
        self.model_provider = "openai"
        self.model_name = settings.default_model
        self.temperature = settings.default_temperature
        self.use_streaming = False
        self._init_assistant()

    def _init_assistant(self):
        """初始化对话助手"""
        self.assistant = ChatAssistant(
            system_message="你是一个 helpful 的AI助手。",
            model_provider=self.model_provider,
            model_name=self.model_name,
            temperature=self.temperature,
        )
        print(f"\n✓ 已初始化模型: {self.model_provider} / {self.model_name}")

    def _switch_model(self):
        """切换模型"""
        print("\n选择模型提供商:")
        print("1. OpenAI")
        print("2. Anthropic")

        choice = input("请输入选项 (1/2): ").strip()

        if choice == "1":
            self.model_provider = "openai"
            print("\n可用模型:")
            print("1. gpt-4o")
            print("2. gpt-4o-mini")
            print("3. gpt-4-turbo")
            print("4. gpt-3.5-turbo")

            model_choice = input("请选择模型 (1-4): ").strip()
            model_map = {
                "1": "gpt-4o",
                "2": "gpt-4o-mini",
                "3": "gpt-4-turbo",
                "4": "gpt-3.5-turbo",
            }
            self.model_name = model_map.get(model_choice, "gpt-4o-mini")

        elif choice == "2":
            self.model_provider = "anthropic"
            print("\n可用模型:")
            print("1. claude-3-opus-20240229")
            print("2. claude-3-sonnet-20240229")
            print("3. claude-3-haiku-20240307")

            model_choice = input("请选择模型 (1-3): ").strip()
            model_map = {
                "1": "claude-3-opus-20240229",
                "2": "claude-3-sonnet-20240229",
                "3": "claude-3-haiku-20240307",
            }
            self.model_name = model_map.get(model_choice, "claude-3-sonnet-20240229")

        else:
            print("无效选项")
            return

        # 重新初始化助手
        self._init_assistant()
        print(f"✓ 已切换到: {self.model_provider} / {self.model_name}")

    def _toggle_streaming(self):
        """切换流式输出"""
        self.use_streaming = not self.use_streaming
        status = "开启" if self.use_streaming else "关闭"
        print(f"\n流式输出已{status}")

    def _show_history(self):
        """显示对话历史"""
        history = self.assistant.get_history()
        if not history:
            print("\n对话历史为空")
            return

        print("\n" + "=" * 50)
        print("对话历史:")
        print("=" * 50)
        for msg in history:
            role = "用户" if msg.type == "human" else "AI"
            print(f"\n【{role}】")
            print(msg.content)
        print("\n" + "=" * 50)

    def _save_history(self):
        """保存对话历史"""
        filename = input("请输入保存文件名 (默认: chat_history.txt): ").strip()
        if not filename:
            filename = "chat_history.txt"

        history = self.assistant.get_history()
        with open(filename, "w", encoding="utf-8") as f:
            for msg in history:
                role = "用户" if msg.type == "human" else "AI"
                f.write(f"【{role}】\n{msg.content}\n\n")

        print(f"\n✓ 对话历史已保存到: {filename}")

    async def _chat(self, message: str):
        """发送消息并获取回复"""
        if self.use_streaming:
            print("\nAI: ", end="", flush=True)
            async for chunk in self.assistant.stream_chat(message):
                print(chunk, end="", flush=True)
            print()
        else:
            print("\nAI: ", end="", flush=True)
            response = await self.assistant.achat(message)
            print(response)

    def run(self):
        """运行CLI"""
        print_banner()

        async def main_loop():
            while True:
                try:
                    user_input = input("\n你: ").strip()

                    if not user_input:
                        continue

                    if user_input.startswith("/"):
                        command = user_input.lower()

                        if command == "/exit":
                            print("\n再见！")
                            break

                        elif command == "/help":
                            print_help()

                        elif command == "/clear":
                            self.assistant.clear_history()
                            print("\n✓ 对话历史已清空")

                        elif command == "/models":
                            print_models()

                        elif command == "/switch":
                            self._switch_model()

                        elif command == "/stream":
                            self._toggle_streaming()

                        elif command == "/history":
                            self._show_history()

                        elif command == "/save":
                            self._save_history()

                        else:
                            print(f"\n未知命令: {command}")
                            print("输入 /help 查看可用命令")

                    else:
                        await self._chat(user_input)

                except KeyboardInterrupt:
                    print("\n\n再见！")
                    break
                except Exception as e:
                    print(f"\n错误: {e}")

        asyncio.run(main_loop())


def main():
    """主入口"""
    cli = ChatCLI()
    cli.run()


if __name__ == "__main__":
    main()
