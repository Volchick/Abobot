import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('API_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден в .env файле!")

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("Не все переменные окружения для PostgreSQL заданы!")