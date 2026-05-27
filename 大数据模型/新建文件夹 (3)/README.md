# LangChain对话助手

一个基于LangChain框架开发的完整对话助手应用，集成了LangSmith监控、LangServe部署和官方Templates，支持前后端分离架构。

## 🌟 功能特性

- **LLM调用**: 支持 OpenAI (GPT-4/GPT-3.5) / Anthropic (Claude) 多模型
- **Prompt工程**: 支持自定义系统提示、多种预设模板
- **Chain链式调用**: 基础对话链、RAG链、翻译链、摘要链等
- **Memory记忆**: 会话级对话历史管理
- **Tool工具使用**: 支持工具调用型Agent模板
- **LangSmith监控**: 完整的调用追踪和性能监控
- **LangServe部署**: RESTful API + RemoteRunnable支持
- **流式输出**: SSE实时流式响应
- **前后端分离**: Streamlit前端 + FastAPI后端

## 📁 项目结构

```
.
├── chat_assistant/          # 后端核心模块
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── models.py            # 模型管理器
│   ├── chains.py            # Chain链定义
│   ├── server.py            # LangServe服务
│   ├── templates.py         # 官方Templates集成
│   ├── cli.py               # 命令行界面
│   └── client.py            # 客户端SDK
├── frontend/                # Streamlit前端
│   ├── streamlit_app.py     # 前端主程序
│   └── requirements.txt     # 前端依赖
├── main.py                  # 主入口
├── requirements.txt         # 后端依赖
├── .env.example             # 环境变量示例
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖（可选）
pip install -r frontend/requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写API密钥：

```bash
cp .env.example .env
```

编辑 `.env`:

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API配置 (可选)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# DeepSeek配置 (本地部署)
DEEPSEEK_API_KEY=EMPTY
DEEPSEEK_BASE_URL=http://localhost:8080/v1
DEEPSEEK_MODEL_NAME=deepseek-chat

# LangSmith配置 (可选但推荐)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=chat-assistant

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 3. 本地运行

#### 方式一：启动API服务

```bash
python main.py server
```

服务启动后：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

#### 方式二：启动前端

```bash
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

前端访问: http://localhost:8501

#### 方式三：命令行交互

```bash
python main.py cli
```

#### 方式四：运行演示

```bash
python main.py demo
```

#### 方式五：启动DeepSeek本地部署服务

```bash
# 使用默认配置启动
python app.py

# 或指定DeepSeek地址
DEEPSEEK_BASE_URL=http://localhost:8080/v1 python app.py
```

**DeepSeek本地部署说明：**

1. **启动DeepSeek本地服务**（参考DeepSeek官方文档）：
   ```bash
   # 使用vLLM部署DeepSeek
   python -m vllm.entrypoints.openai.api_server \
     --model deepseek-ai/deepseek-chat \
     --port 8080
   ```

2. **配置环境变量**：
   ```env
   DEEPSEEK_API_KEY=EMPTY
   DEEPSEEK_BASE_URL=http://localhost:8080/v1
   DEEPSEEK_MODEL_NAME=deepseek-chat
   ```

3. **测试连接**：
   ```bash
   TEST_MODE=true python app.py
   ```

## 🌐 API接口

### 基础对话

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好！",
    "system_message": "你是一个 helpful 的AI助手。",
    "model_provider": "openai",
    "model_name": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

### 流式对话

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "讲一个故事",
    "session_id": "user_123"
  }'
```

### 翻译

```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, World!",
    "target_language": "中文"
  }'
```

### 摘要

```bash
curl -X POST http://localhost:8000/summary \
  -H "Content-Type: application/json" \
  -d '{
    "text": "要摘要的长文本...",
    "max_length": 200
  }'
```

### 列出模型

```bash
curl http://localhost:8000/models
```

## 🔗 LangServe RemoteRunnable

服务提供标准的LangServe端点：

```python
from langserve import RemoteRunnable

# 连接远程服务
chat = RemoteRunnable("http://localhost:8000/langchain/chat")
translate = RemoteRunnable("http://localhost:8000/langchain/translate")
summary = RemoteRunnable("http://localhost:8000/langchain/summary")

# 使用
response = await chat.ainvoke({
    "input": "你好！",
    "chat_history": []
})
```

## 📋 可用Templates

| 模板名称 | 描述 | 使用场景 |
|---------|------|---------|
| rag | 检索增强生成 | 知识库问答 |
| sql_generator | SQL生成器 | 自然语言转SQL |
| code_explainer | 代码解释器 | 代码审查 |
| entity_extraction | 实体提取 | 信息抽取 |
| sentiment_analysis | 情感分析 | 舆情分析 |
| text_classifier | 文本分类 | 内容分类 |
| markdown_formatter | Markdown格式化 | 文档生成 |
| conversational_retrieval | 对话式检索 | 客服机器人 |

## 📊 LangSmith监控

配置LangSmith后，所有链调用将自动追踪：

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=chat-assistant
```

在 [LangSmith Dashboard](https://smith.langchain.com) 查看：
- 调用追踪
- 延迟分析
- Token使用量
- 错误监控

## 🚀 云端部署

### 部署到Streamlit Cloud

1. **创建GitHub仓库**
   - 将代码推送到GitHub仓库
   - 确保包含 `.streamlit/secrets.toml` 文件

2. **配置Streamlit Cloud**
   - 访问 [Streamlit Community Cloud](https://streamlit.io/cloud)
   - 点击 "New app"
   - 选择GitHub仓库
   - 设置路径为 `frontend/streamlit_app.py`
   - 添加环境变量到 Secrets:
     ```toml
     API_BASE_URL = "https://your-backend.onrender.com"
     ```

3. **部署后端到Render**
   - 访问 [Render](https://render.com)
   - 创建新的 Web Service
   - 选择GitHub仓库
   - 设置 Build Command: `pip install -r requirements.txt`
   - 设置 Start Command: `python main.py server`
   - 添加环境变量

### 部署到Vercel

1. **配置vercel.json**
   ```json
   {
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

2. **部署**
   ```bash
   vercel deploy
   ```

## 📝 代码引用

本项目基于以下开源框架开发：

- **LangChain**: https://github.com/langchain-ai/langchain
- **LangServe**: https://github.com/langchain-ai/langserve
- **Streamlit**: https://github.com/streamlit/streamlit

## ⚖️ License

MIT License

## 📧 联系方式

如有问题或建议，欢迎提交Issue或PR！
