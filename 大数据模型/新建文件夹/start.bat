@echo off
echo ============================================
echo    LangChain对话助手 - Windows启动脚本
echo ============================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 安装依赖
echo 📦 安装依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo ✅ 依赖安装成功

:: 启动后端服务
echo 🚀 启动后端服务...
start "LangChain Backend" python backend/main.py

:: 等待服务启动
timeout /t 3 /nobreak >nul

:: 启动前端
echo 🖥️ 启动前端界面...
start "LangChain Frontend" streamlit run frontend/app.py

echo.
echo ============================================
echo    服务已启动！
echo    - 后端API: http://localhost:8000
echo    - API文档: http://localhost:8000/docs
echo    - 前端界面: http://localhost:8501
echo ============================================
pause
