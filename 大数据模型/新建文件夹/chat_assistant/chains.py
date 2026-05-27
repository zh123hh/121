"""
LangChain链定义模块
"""
from typing import Optional, AsyncIterator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from chat_assistant.models import model_manager


def create_chat_chain(
    system_message: Optional[str] = None,
    model_provider: str = "openai",
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
) -> RunnableSerializable:
    """
    创建基础对话链

    Args:
        system_message: 系统提示消息
        model_provider: 模型提供商 (openai/anthropic)
        model_name: 模型名称
        temperature: 温度参数

    Returns:
        可运行的对话链
    """
    # 获取模型
    model = model_manager.get_model(
        provider=model_provider,
        model_name=model_name,
        temperature=temperature,
    )

    # 构建提示模板
    messages = []
    if system_message:
        messages.append(("system", system_message))

    messages.append(MessagesPlaceholder(variable_name="chat_history"))
    messages.append(("human", "{input}"))

    prompt = ChatPromptTemplate.from_messages(messages)

    # 构建链
    chain = prompt | model | StrOutputParser()

    return chain


def create_qa_chain(
    context: str,
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """
    创建问答链

    Args:
        context: 上下文信息
        model_provider: 模型提供商
        model_name: 模型名称

    Returns:
        可运行的问答链
    """
    model = model_manager.get_model(
        provider=model_provider,
        model_name=model_name,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个 helpful 的AI助手。请基于以下上下文回答问题。\n\n上下文：{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    chain = prompt | model | StrOutputParser()

    return chain


def create_translation_chain(
    target_language: str = "中文",
    model_provider: str = "openai",
) -> RunnableSerializable:
    """
    创建翻译链

    Args:
        target_language: 目标语言
        model_provider: 模型提供商

    Returns:
        可运行的翻译链
    """
    model = model_manager.get_model(provider=model_provider)

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"你是一个专业的翻译助手。请将用户输入翻译成{target_language}，只返回翻译结果，不要添加任何解释。"),
        ("human", "{text}"),
    ])

    chain = prompt | model | StrOutputParser()

    return chain


def create_summary_chain(
    max_length: int = 200,
    model_provider: str = "openai",
) -> RunnableSerializable:
    """
    创建摘要链

    Args:
        max_length: 摘要最大长度
        model_provider: 模型提供商

    Returns:
        可运行的摘要链
    """
    model = model_manager.get_model(provider=model_provider)

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"你是一个专业的文本摘要助手。请将用户提供的文本总结为{max_length}字以内的摘要。"),
        ("human", "{text}"),
    ])

    chain = prompt | model | StrOutputParser()

    return chain


class ChatAssistant:
    """对话助手类"""

    def __init__(
        self,
        system_message: Optional[str] = None,
        model_provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.system_message = system_message or "你是谷雨，一个可爱的AI助手。请用友好、亲切的语气回答问题。"
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.chat_history: list = []

        # 初始化对话链
        self.chain = create_chat_chain(
            system_message=self.system_message,
            model_provider=model_provider,
            model_name=model_name,
            temperature=temperature,
        )

    def chat(self, message: str) -> str:
        """同步对话"""
        response = self.chain.invoke({
            "input": message,
            "chat_history": self.chat_history,
        })

        # 更新历史记录
        self.chat_history.append(HumanMessage(content=message))
        self.chat_history.append(AIMessage(content=response))

        return response

    async def achat(self, message: str) -> str:
        """异步对话"""
        response = await self.chain.ainvoke({
            "input": message,
            "chat_history": self.chat_history,
        })

        # 更新历史记录
        self.chat_history.append(HumanMessage(content=message))
        self.chat_history.append(AIMessage(content=response))

        return response

    async def stream_chat(self, message: str) -> AsyncIterator[str]:
        """流式对话"""
        try:
            # 获取流式模型
            stream_model = model_manager.get_model(
                provider=self.model_provider,
                model_name=self.model_name,
                temperature=self.temperature,
                streaming=True,
            )

            # 构建提示
            messages = []
            if self.system_message:
                messages.append(SystemMessage(content=self.system_message))
            messages.extend(self.chat_history)
            messages.append(HumanMessage(content=message))

            full_response = ""
            async for chunk in stream_model.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content

            # 更新历史记录
            self.chat_history.append(HumanMessage(content=message))
            self.chat_history.append(AIMessage(content=full_response))
        except Exception as e:
            # 调试：打印错误信息
            import traceback
            print(f"DeepSeek调用失败: {str(e)}")
            print(traceback.format_exc())
            # 演示模式：返回内置回答
            demo_response = self._get_demo_response(message)
            for i in range(0, len(demo_response), 5):
                yield demo_response[i:i+5]
            # 更新历史记录
            self.chat_history.append(HumanMessage(content=message))
            self.chat_history.append(AIMessage(content=demo_response))

    def _get_demo_response(self, message: str) -> str:
        """获取演示模式的内置回答"""
        message_lower = message.lower().strip()
        
        # 简单数学问题
        if '1+1' in message_lower or '一加一' in message_lower:
            return '1 + 1 = 2'
        elif '2+2' in message_lower or '二加二' in message_lower:
            return '2 + 2 = 4'
        elif '3*3' in message_lower or '三乘三' in message_lower or '3x3' in message_lower:
            return '3 × 3 = 9'
        elif '10-5' in message_lower or '十减五' in message_lower:
            return '10 - 5 = 5'
        
        # 问候语
        elif '你好' in message_lower or 'hello' in message_lower:
            return '你好！我是谷雨，很高兴认识你！有什么我可以帮助你的吗？'
        elif '早上好' in message_lower:
            return '早上好！祝你今天有个美好的一天！'
        elif '下午好' in message_lower:
            return '下午好！忙碌了半天，记得休息一下哦！'
        elif '晚上好' in message_lower:
            return '晚上好！辛苦了一天，好好放松一下吧！'
        
        # 身份与介绍
        elif '你是谁' in message_lower or 'what are you' in message_lower:
            return '我是谷雨，一个基于LangChain框架构建的AI助手，可以帮助您解答问题、翻译文本、总结内容等。'
        elif '你能做什么' in message_lower or '你会做什么' in message_lower:
            return '我是谷雨，我可以回答问题、进行对话、翻译文本、总结内容等。如果有真实的AI模型API密钥，我还能做更多事情！'
        
        # 情感与关怀
        elif '开心' in message_lower or '高兴' in message_lower:
            return '太棒了！看到你开心我也很开心！继续保持这份好心情！'
        elif '难过' in message_lower or '伤心' in message_lower or '不开心' in message_lower:
            return '听到你这么说我很担心。有什么烦心事可以和我说说，我会尽力安慰你的。'
        elif '生气' in message_lower or '愤怒' in message_lower:
            return '别生气，深呼吸。生气解决不了问题，我们可以一起想想办法。'
        
        # 日常对话
        elif '吃饭了吗' in message_lower or '吃了吗' in message_lower:
            return '我不需要吃饭，但谢谢你关心我！你吃饭了吗？'
        elif '最近怎么样' in message_lower or '最近好吗' in message_lower:
            return '我很好，谢谢你的关心！你最近过得怎么样呢？'
        elif '周末愉快' in message_lower or '周末好' in message_lower:
            return '周末愉快！祝你有个轻松愉快的周末！'
        
        # 感谢与告别
        elif '谢谢' in message_lower or 'thank you' in message_lower:
            return '不客气！如果您还有其他问题，随时可以问我。'
        elif '再见' in message_lower or '拜拜' in message_lower or 'bye' in message_lower:
            return '再见！祝你一切顺利，期待下次再见！'
        elif '晚安' in message_lower:
            return '晚安！祝你做个好梦！'
        
        # 实用信息
        elif '天气' in message_lower:
            return '抱歉，我无法获取实时天气信息。您可以通过天气应用或网站查询当前天气。'
        elif '时间' in message_lower:
            import datetime
            now = datetime.datetime.now()
            return f'当前时间是：{now.strftime("%Y年%m月%d日 %H:%M:%S")}'
        elif '星期' in message_lower or '周几' in message_lower:
            import datetime
            week_days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            now = datetime.datetime.now()
            return f'今天是{week_days[now.weekday()]}'
        
        # 英语翻译
        elif '翻译' in message_lower or '英语' in message_lower or 'english' in message_lower:
            # 中译英
            if '我爱你' in message:
                return 'I love you'
            elif '你好' in message and not ('用英语' in message or '英文' in message):
                pass  # 让问候语处理
            elif '谢谢' in message and not ('用英语' in message or '英文' in message):
                pass  # 让感谢处理
            elif '再见' in message and not ('用英语' in message or '英文' in message):
                pass  # 让告别处理
            elif '早上好' in message:
                return 'Good morning'
            elif '晚上好' in message:
                return 'Good evening'
            elif '下午好' in message:
                return 'Good afternoon'
            elif '欢迎' in message:
                return 'Welcome'
            elif '对不起' in message:
                return 'Sorry'
            elif '没关系' in message:
                return 'It doesn\'t matter'
            elif '请' in message:
                return 'Please'
            elif '你叫什么名字' in message:
                return 'What is your name?'
            elif '很高兴认识你' in message:
                return 'Nice to meet you'
            elif '谢谢' in message:
                return 'Thank you'
            elif '再见' in message:
                return 'Goodbye'
            elif '你好' in message:
                return 'Hello'
            else:
                return f'这是演示模式响应\n\n您的问题：{message}\n\n当前演示模式支持基础翻译功能，如需更完整的翻译能力，请配置真实的AI模型API密钥。'
        
        # 默认回答
        else:
            return f'这是演示模式响应\n\n您的问题：{message}\n\n要使用真实的AI模型，请在服务器端的 `.env` 文件中配置有效的API密钥。\n\n支持的模型：\n- OpenAI: GPT-4, GPT-3.5\n- Anthropic: Claude-3-opus, Claude-3-sonnet\n- DeepSeek: 本地部署模型'


    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []

    def get_history(self) -> list:
        """获取对话历史"""
        return self.chat_history
