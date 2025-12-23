import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Ключи из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен от BotFather
API_KEY = os.getenv('API_KEY')      # API-Sports
API_HOST = 'v1.hockey.api-sports.io'