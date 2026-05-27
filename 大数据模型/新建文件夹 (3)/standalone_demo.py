#!/usr/bin/env python3
"""
LangChain对话助手 - 独立演示版本
无需任何外部依赖，纯Python实现
"""

import http.server
import socketserver
import json
import urllib.parse
import threading
import webbrowser
import time

# 模拟响应数据
RESPONSES = {
    "你好": "👋 您好！我是LangChain对话助手，很高兴为您服务！",
    "你是谁": "我是基于LangChain框架开发的智能对话助手，支持多模型调用、流式输出、LangSmith监控等功能。",
    "介绍一下LangChain": "LangChain是一个用于开发由语言模型驱动的应用程序的框架。它提供了一系列工具和组件，帮助开发者快速构建强大的AI应用，包括文档检索、多轮对话、工具调用等功能。",
    "什么是RAG": "RAG（Retrieval-Augmented Generation）是一种检索增强生成技术，它结合了信息检索和生成模型，可以让AI回答基于特定知识库的问题，提高回答的准确性和可靠性。",
    "写一封邮件": "当然可以！请问您需要写什么类型的邮件？是商务邮件、感谢信还是其他类型？请告诉我收件人、主题和主要内容。",
}


def generate_response(message):
    """生成模拟响应"""
    for key, value in RESPONSES.items():
        if key in message:
            return value
    return f"这是针对您的问题 \"{message}\" 的演示回复。\n\n在实际应用中，这将连接到真实的LLM模型（如GPT-4、Claude或DeepSeek）来生成准确的回答。"


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(self.get_frontend_html().encode("utf-8"))
        elif self.path == "/health":
            self.send_json_response(200, {"status": "healthy"})
        elif self.path == "/models":
            self.send_json_response(200, [
                {"provider": "openai", "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]},
                {"provider": "deepseek", "models": ["deepseek-chat", "deepseek-r1-chat"]},
            ])
        else:
            self.send_json_response(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/chat":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(post_data)
            
            message = data.get("message", "")
            response = generate_response(message)
            
            self.send_json_response(200, {"response": response})
        
        elif self.path == "/chat/stream":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(post_data)
            
            message = data.get("message", "")
            response = generate_response(message)
            
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            for i in range(len(response)):
                self.wfile.write(response[:i+1].encode("utf-8"))
                self.wfile.flush()
                time.sleep(0.02)
        
        else:
            self.send_json_response(404, {"error": "Not found"})

    def get_frontend_html(self):
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangChain对话助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 36px; margin-bottom: 10px; }
        .header p { color: #64748b; }
        
        .features { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .feature-card { background: white; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
        .feature-card .icon { font-size: 32px; margin-bottom: 10px; }
        .feature-card .title { font-weight: 600; margin-bottom: 5px; }
        .feature-card .desc { font-size: 12px; color: #64748b; }
        
        .chat-area { display: flex; gap: 20px; }
        
        .sidebar { width: 320px; background: white; border-radius: 20px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
        .sidebar-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; }
        .sidebar-header h2 { color: white; font-size: 20px; margin: 0; }
        .sidebar-header p { color: rgba(255,255,255,0.8); font-size: 12px; margin-top: 5px; }
        
        .status { display: flex; align-items: center; gap: 10px; padding: 12px; background: #dcfce7; border-radius: 10px; margin-bottom: 20px; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #22c55e; animation: pulse 2s infinite; }
        .status-text { color: #166534; font-weight: 600; }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
            100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
        
        .config-section { margin-bottom: 20px; }
        .config-section h3 { font-size: 14px; color: #374151; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }
        .config-section select, .config-section input, .config-section textarea { width: 100%; padding: 10px; border: 2px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; }
        .config-section select:focus, .config-section input:focus, .config-section textarea:focus { outline: none; border-color: #667eea; }
        .config-section textarea { height: 100px; resize: none; }
        
        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .btn { padding: 12px; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: #f1f5f9; color: #374151; }
        .btn-secondary:hover { background: #e2e8f0; }
        
        .chat-container { flex: 1; display: flex; flex-direction: column; background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); overflow: hidden; }
        
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; height: 500px; }
        
        .message { margin-bottom: 15px; clear: both; }
        .message.user .bubble { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; float: right; border-radius: 20px 20px 5px 20px; }
        .message.assistant .bubble { background: #f1f5f9; color: #1e293b; float: left; border-radius: 20px 20px 20px 5px; }
        .bubble { max-width: 75%; padding: 16px 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        .bubble .name { font-weight: 600; margin-bottom: 5px; }
        .bubble .content { line-height: 1.5; }
        
        .welcome-message { text-align: center; padding: 40px; }
        .welcome-message .icon { font-size: 64px; margin-bottom: 15px; }
        .welcome-message .title { font-size: 20px; font-weight: 600; margin-bottom: 10px; }
        .welcome-message .desc { color: #64748b; font-size: 14px; }
        
        .input-area { padding: 20px; border-top: 1px solid #e5e7eb; }
        .input-row { display: flex; gap: 10px; }
        .input-row input { flex: 1; padding: 15px 20px; border: 2px solid #e2e8f0; border-radius: 25px; font-size: 16px; }
        .input-row input:focus { outline: none; border-color: #667eea; }
        .input-row button { padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .input-row button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        
        .footer { text-align: center; padding: 20px; background: #f8fafc; border-radius: 15px; margin-top: 30px; }
        .footer-links { display: flex; justify-content: center; gap: 30px; margin-bottom: 15px; }
        .footer-links a { color: #667eea; text-decoration: none; }
        .footer p { color: #94a3b8; font-size: 14px; }
        
        @media (max-width: 900px) {
            .chat-area { flex-direction: column; }
            .sidebar { width: 100%; }
            .features { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LangChain对话助手</h1>
            <p>基于LangChain框架 · 集成LangSmith监控 · LangServe部署</p>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="icon">🤖</div>
                <div class="title">多模型支持</div>
                <div class="desc">OpenAI / DeepSeek</div>
            </div>
            <div class="feature-card">
                <div class="icon">📊</div>
                <div class="title">LangSmith监控</div>
                <div class="desc">完整调用追踪</div>
            </div>
            <div class="feature-card">
                <div class="icon">🚀</div>
                <div class="title">LangServe部署</div>
                <div class="desc">RESTful API</div>
            </div>
            <div class="feature-card">
                <div class="icon">💬</div>
                <div class="title">流式输出</div>
                <div class="desc">实时响应</div>
            </div>
        </div>
        
        <div class="chat-area">
            <div class="sidebar">
                <div class="sidebar-header">
                    <h2>🤖 对话助手</h2>
                    <p>LangChain Powered</p>
                </div>
                
                <div class="status">
                    <div class="status-dot"></div>
                    <span class="status-text">API服务: 在线</span>
                </div>
                
                <div class="config-section">
                    <h3>⚙️ 模型配置</h3>
                    <select id="modelProvider">
                        <option value="openai">🔵 OpenAI</option>
                        <option value="deepseek">🟢 DeepSeek (本地)</option>
                    </select>
                    <select id="modelName">
                        <option value="gpt-4o-mini">gpt-4o-mini</option>
                        <option value="gpt-4o">gpt-4o</option>
                        <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                    </select>
                </div>
                
                <div class="config-section">
                    <h3>🎛️ 生成参数</h3>
                    <input type="range" id="temperature" min="0" max="2" step="0.1" value="0.7">
                    <label style="font-size: 12px; color: #64748b;">温度: <span id="tempValue">0.7</span></label>
                </div>
                
                <div class="config-section">
                    <h3>📝 系统提示</h3>
                    <textarea id="systemMessage">你是一个 helpful 的AI助手。</textarea>
                </div>
                
                <div class="config-section">
                    <h3>🔧 操作</h3>
                    <div class="btn-group">
                        <button class="btn btn-secondary" onclick="clearChat()">🗑️ 清空</button>
                        <button class="btn btn-secondary" onclick="refreshPage()">🔄 刷新</button>
                    </div>
                </div>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="welcome-message">
                        <div class="icon">👋</div>
                        <div class="title">欢迎使用LangChain对话助手</div>
                        <div class="desc">请在左侧配置模型参数，然后开始对话！</div>
                    </div>
                </div>
                
                <div class="input-area">
                    <div class="input-row">
                        <input type="text" id="messageInput" placeholder="输入消息..." onkeydown="if(event.keyCode===13) sendMessage()">
                        <button onclick="sendMessage()">➤</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-links">
                <a href="/docs" target="_blank">🔗 API文档</a>
                <a href="https://smith.langchain.com" target="_blank">📊 LangSmith</a>
                <a href="https://github.com/langchain-ai/langchain" target="_blank">💻 GitHub</a>
            </div>
            <p>Powered by LangChain · LangServe · Python</p>
        </div>
    </div>
    
    <script>
        let messages = [];
        const API_URL = '';
        
        document.getElementById('temperature').addEventListener('input', function(e) {
            document.getElementById('tempValue').textContent = e.target.value;
        });
        
        document.getElementById('modelProvider').addEventListener('change', function(e) {
            const provider = e.target.value;
            const modelSelect = document.getElementById('modelName');
            modelSelect.innerHTML = '';
            
            if (provider === 'openai') {
                ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'].forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m; opt.textContent = m;
                    modelSelect.appendChild(opt);
                });
            } else {
                ['deepseek-chat', 'deepseek-r1-chat'].forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m; opt.textContent = m;
                    modelSelect.appendChild(opt);
                });
            }
        });
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            input.value = '';
            addMessage('user', message);
            
            const data = {
                message: message,
                system_message: document.getElementById('systemMessage').value,
                model_provider: document.getElementById('modelProvider').value,
                model_name: document.getElementById('modelName').value,
                temperature: parseFloat(document.getElementById('temperature').value)
            };
            
            try {
                const response = await fetch(API_URL + '/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                addMessage('assistant', result.response);
            } catch (error) {
                console.error('Error:', error);
                addMessage('assistant', '抱歉，服务暂时不可用，请稍后重试。');
            }
        }
        
        function addMessage(role, content) {
            const container = document.getElementById('chatMessages');
            container.innerHTML = '';
            
            messages.push({ role, content });
            
            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = `message ${msg.role}`;
                div.innerHTML = `
                    <div class="bubble">
                        <div class="name">${msg.role === 'user' ? '您' : '🤖 AI助手'}</div>
                        <div class="content">${msg.content.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
                container.appendChild(div);
            });
            
            container.scrollTop = container.scrollHeight;
        }
        
        function clearChat() {
            messages = [];
            const container = document.getElementById('chatMessages');
            container.innerHTML = `
                <div class="welcome-message">
                    <div class="icon">👋</div>
                    <div class="title">欢迎使用LangChain对话助手</div>
                    <div class="desc">请在左侧配置模型参数，然后开始对话！</div>
                </div>
            `;
        }
        
        function refreshPage() {
            location.reload();
        }
    </script>
</body>
</html>
            """

def start_server(port=8000):
    """启动HTTP服务器"""
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), RequestHandler) as httpd:
        print(f"🚀 LangChain对话助手服务已启动")
        print(f"📡 服务地址: http://localhost:{port}")
        print(f"👈 请在浏览器中打开上述地址")
        httpd.serve_forever()

if __name__ == "__main__":
    # 启动服务器
    server_thread = threading.Thread(target=start_server, args=(8000,))
    server_thread.daemon = True
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(1)
    
    # 打开浏览器
    webbrowser.open("http://localhost:8000")
    
    # 保持主线程运行
    while True:
        time.sleep(1)
