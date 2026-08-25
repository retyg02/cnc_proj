import os
from pathlib import Path
from dotenv import load_dotenv

# 📂 МАГИЯ ПУТИ: Находим корень проекта (выходим на 1 уровень вверх из папки бота)
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

# Загружаем файл .env из корня в память Python
load_dotenv(dotenv_path=dotenv_path)


DB_HOST = os.getenv('DB_HOST', 'PostgreSQL-16')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password') 

TOKEN = '8932169588:AAHCJNQofWGP6ajSvmOAjHqipT_X-7uP82M'

ONEC_API_KEY = "secret_123"

# Настройки MongoDB (NoSQL)
MONGO_HOST = os.getenv('MONGO_HOST', 'MongoDB-5.0')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017')) # Порт должен быть числом int в Django
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'ai_analytics_db')
