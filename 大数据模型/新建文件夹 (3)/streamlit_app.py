import subprocess
import os

# 切换到frontend目录并运行Streamlit
os.chdir(os.path.join(os.path.dirname(__file__), 'frontend'))
subprocess.run(["streamlit", "run", "streamlit_app.py"])