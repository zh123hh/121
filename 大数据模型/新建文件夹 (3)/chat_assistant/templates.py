"""
LangChain官方Templates集成模块
集成常用的LangChain模板和预设链
"""
from typing import Optional, List, Dict, Any
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    PydanticOutputParser,
)
from langchain_core.runnables import RunnableSerializable, RunnablePassthrough
from pydantic import BaseModel, Field

from chat_assistant.models import model_manager


# ============ Pydantic输出模型定义 ============

class EntityExtraction(BaseModel):
    """实体提取模型"""
    entities: List[Dict[str, str]] = Field(
        description="提取的实体列表，每个实体包含name和type"
    )


class SentimentAnalysis(BaseModel):
    """情感分析模型"""
    sentiment: str = Field(description="情感类型: positive/negative/neutral")
    confidence: float = Field(description="置信度 0-1")
    explanation: str = Field(description="分析解释")


class CodeReview(BaseModel):
    """代码审查模型"""
    issues: List[Dict[str, Any]] = Field(description="发现的问题列表")
    suggestions: List[str] = Field(description="改进建议")
    score: int = Field(description="代码质量评分 1-10")


# ============ Template预设 ============

class TemplateManager:
    """模板管理器 - 集成LangChain官方Templates"""

    @staticmethod
    def get_rag_template() -> ChatPromptTemplate:
        """
        RAG (Retrieval-Augmented Generation) 模板
        用于基于检索的问答
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """你是一个专业的AI助手。请基于以下检索到的上下文信息回答问题。
如果上下文中没有相关信息，请明确说明。

上下文信息：
{context}

请根据以上上下文回答用户的问题。如果无法从上下文中找到答案，请说"根据提供的信息，我无法回答这个问题。""""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}"),
        ])

    @staticmethod
    def get_sql_generator_template() -> ChatPromptTemplate:
        """
        SQL生成器模板
        用于自然语言转SQL
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """你是一个SQL专家。根据提供的数据库表结构，将用户的自然语言查询转换为SQL语句。

数据库表结构：
{schema}

要求：
1. 只返回SQL语句，不要添加任何解释
2. 使用标准的SQL语法
3. 如果查询不明确，请返回最合理的假设"""
            ),
            HumanMessagePromptTemplate.from_template("{query}"),
        ])

    @staticmethod
    def get_code_explainer_template() -> ChatPromptTemplate:
        """
        代码解释器模板
        用于解释代码功能
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """你是一个专业的代码解释专家。请详细解释以下代码的功能、逻辑和实现细节。

编程语言: {language}

请从以下几个方面解释：
1. 代码的整体功能
2. 关键函数/类的说明
3. 算法逻辑分析
4. 潜在的问题或改进建议"""
            ),
            HumanMessagePromptTemplate.from_template("```\n{code}\n```"),
        ])

    @staticmethod
    def get_markdown_formatter_template() -> ChatPromptTemplate:
        """
        Markdown格式化模板
        用于将文本转换为Markdown格式
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """你是一个Markdown格式化专家。请将用户提供的内容转换为格式良好的Markdown文档。

要求：
1. 使用适当的标题层级
2. 使用列表、表格等增强可读性
3. 添加代码块（如适用）
4. 保持内容的完整性和准确性"""
            ),
            HumanMessagePromptTemplate.from_template("{content}"),
        ])

    @staticmethod
    def get_json_formatter_template() -> ChatPromptTemplate:
        """
        JSON格式化/提取模板
        用于从文本中提取结构化JSON数据
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """你是一个JSON数据处理专家。请从用户提供的文本中提取信息并格式化为JSON。

提取要求：
{extraction_requirements}

只返回JSON格式的结果，不要添加任何其他文本。"""
            ),
            HumanMessagePromptTemplate.from_template("{text}"),
        ])

    @staticmethod
    def get_classifier_template(categories: List[str]) -> ChatPromptTemplate:
        """
        文本分类模板

        Args:
            categories: 分类类别列表
        """
        categories_str = ", ".join(categories)
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                f"""你是一个文本分类专家。请将用户输入分类到以下类别之一：

类别: {categories_str}

只返回类别名称，不要添加任何解释。"""
            ),
            HumanMessagePromptTemplate.from_template("{text}"),
        ])

    @staticmethod
    def get_conversational_retrieval_template() -> ChatPromptTemplate:
        """
        对话式检索模板
        用于多轮对话中的检索增强
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """你是一个 helpful 的AI助手。请基于检索到的信息回答问题，同时保持对话的连贯性。

检索到的相关信息：
{context}

聊天历史摘要：
{history_summary}

请自然地回答问题，必要时可以参考之前的对话内容。"""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}"),
        ])

    @staticmethod
    def get_agent_prompt_template(tools_description: str) -> ChatPromptTemplate:
        """
        Agent代理模板
        用于工具调用型Agent

        Args:
            tools_description: 可用工具的描述
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                f"""你是一个智能助手，可以使用以下工具来帮助用户：

可用工具：
{tools_description}

请根据用户的需求选择合适的工具。如果需要多个步骤，请按顺序执行。
始终用中文回复用户。"""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{{input}}"),
            HumanMessagePromptTemplate.from_template("{{agent_scratchpad}}"),
        ])


# ============ 预设链工厂 ============

def create_rag_chain(
    retriever,
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """
    创建RAG链

    Args:
        retriever: 文档检索器
        model_provider: 模型提供商
        model_name: 模型名称

    Returns:
        RAG链
    """
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    template = TemplateManager.get_rag_template()

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "chat_history": lambda x: [],
        }
        | template
        | model
        | StrOutputParser()
    )

    return chain


def create_entity_extraction_chain(
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """创建实体提取链"""
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    parser = PydanticOutputParser(pydantic_object=EntityExtraction)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """从以下文本中提取命名实体。实体类型包括：人名、组织、地点、时间、产品等。

{format_instructions}"""
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    return prompt | model | parser


def create_sentiment_analysis_chain(
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """创建情感分析链"""
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    parser = PydanticOutputParser(pydantic_object=SentimentAnalysis)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """分析以下文本的情感倾向。

{format_instructions}"""
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    return prompt | model | parser


def create_sql_generator_chain(
    schema: str,
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """
    创建SQL生成链

    Args:
        schema: 数据库表结构
        model_provider: 模型提供商
        model_name: 模型名称
    """
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    template = TemplateManager.get_sql_generator_template()

    chain = (
        RunnablePassthrough.assign(schema=lambda x: schema)
        | template
        | model
        | StrOutputParser()
    )

    return chain


def create_code_explainer_chain(
    language: str = "python",
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """
    创建代码解释链

    Args:
        language: 编程语言
        model_provider: 模型提供商
        model_name: 模型名称
    """
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    template = TemplateManager.get_code_explainer_template()

    chain = (
        RunnablePassthrough.assign(language=lambda x: language)
        | template
        | model
        | StrOutputParser()
    )

    return chain


def create_text_classifier_chain(
    categories: List[str],
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """
    创建文本分类链

    Args:
        categories: 分类类别
        model_provider: 模型提供商
        model_name: 模型名称
    """
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    template = TemplateManager.get_classifier_template(categories)

    return template | model | StrOutputParser()


def create_structured_output_chain(
    output_model: type[BaseModel],
    instruction: str,
    model_provider: str = "openai",
    model_name: Optional[str] = None,
) -> RunnableSerializable:
    """
    创建结构化输出链

    Args:
        output_model: Pydantic输出模型类
        instruction: 处理指令
        model_provider: 模型提供商
        model_name: 模型名称

    Returns:
        结构化输出链
    """
    model = model_manager.get_model(provider=model_provider, model_name=model_name)
    parser = PydanticOutputParser(pydantic_object=output_model)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """{instruction}

{format_instructions}"""
        ),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]).partial(
        instruction=instruction,
        format_instructions=parser.get_format_instructions(),
    )

    return prompt | model | parser


# ============ 模板列表 ============

def list_available_templates() -> List[Dict[str, Any]]:
    """列出所有可用模板"""
    return [
        {
            "name": "rag",
            "description": "检索增强生成 - 基于文档检索的问答",
            "use_case": "知识库问答、文档查询",
        },
        {
            "name": "sql_generator",
            "description": "SQL生成器 - 自然语言转SQL",
            "use_case": "数据库查询、数据分析",
        },
        {
            "name": "code_explainer",
            "description": "代码解释器 - 解释代码功能",
            "use_case": "代码审查、学习理解",
        },
        {
            "name": "entity_extraction",
            "description": "实体提取 - 提取文本中的命名实体",
            "use_case": "信息抽取、NLP任务",
        },
        {
            "name": "sentiment_analysis",
            "description": "情感分析 - 分析文本情感倾向",
            "use_case": "舆情分析、评论分析",
        },
        {
            "name": "text_classifier",
            "description": "文本分类 - 将文本分类到预定义类别",
            "use_case": "内容分类、标签生成",
        },
        {
            "name": "markdown_formatter",
            "description": "Markdown格式化 - 将文本转为Markdown",
            "use_case": "文档生成、内容美化",
        },
        {
            "name": "conversational_retrieval",
            "description": "对话式检索 - 多轮对话中的检索增强",
            "use_case": "客服机器人、智能问答",
        },
    ]
