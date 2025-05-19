import os
import sys
from pathlib import Path

# Добавляем корень проекта (backend/) в sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

#print("Current working directory:", os.getcwd())
#print("sys.path:", sys.path)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)