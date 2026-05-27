#!/bin/bash

echo "🚀 启动LangChain对话助手"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 启动后端服务
echo "🖥️ 启动后端服务..."
cd backend
python main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端服务
echo "🌐 启动前端服务..."
cd ../frontend
streamlit run app.py &
FRONTEND_PID=$!

echo "✅ 服务已启动"
echo "📡 后端API: http://localhost:8000"
echo "🌐 前端界面: http://localhost:8501"
echo "📚 API文档: http://localhost:8000/docs"

# 等待用户输入停止
read -p "按Enter键停止服务..."

# 停止服务
kill $BACKEND_PID
kill $FRONTEND_PID
echo "👋 服务已停止"
