import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('API_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Токен бота не найден в .env файле!")

GPT_TOKEN = os.getenv('GPT_TOKEN')
if not GPT_TOKEN:
    raise ValueError("Токен GPT не найден в .env файле!")

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("Не все переменные окружения для PostgreSQL заданы!")

VK_CLIENT_ID = os.getenv('VK_CLIENT_ID')
if not VK_CLIENT_ID:
    raise ValueError("VK_CLIENT_ID не найден в .env файле!")

VK_REDIRECT_URI = os.getenv('VK_REDIRECT_URI')
if not VK_REDIRECT_URI:
    raise ValueError("VK_REDIRECT_URI не найден в .env файле!")

VK_CLIENT_SECRET = os.getenv('VK_CLIENT_SECRET')
if not VK_CLIENT_SECRET:
    raise ValueError("VK_CLIENT_SECRET не найден в .env файле!")

GPT_CONTEXT = """
Ты - рыцарь раб Гаэль из игры Dark Souls 3. Ты получил тёмную душу, достигнув пика своей силы. 
Твоя задача - помогать игрокам, отвечая на их вопросы и предоставляя советы по игре. 
Ты должен быть дружелюбным, но при этом сохранять атмосферу игры. 
Используй терминологию Dark Souls 3 и старайся быть максимально полезным.
"""