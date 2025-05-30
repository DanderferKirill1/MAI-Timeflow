import os
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Проверяем, что Flask установлен
try:
    import flask
    print(f"Flask version: {flask.__version__}")
except ImportError:
    print("Flask не установлен. Устанавливаем...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==2.3.3"])
    import flask
    print(f"Flask установлен, версия: {flask.__version__}")

#print("Current working directory:", os.getcwd())
#print("sys.path:", sys.path)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.debug = True  # Включаем отладочный режим
    app.run(host='127.0.0.1', port=5000)