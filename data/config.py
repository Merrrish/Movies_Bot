import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

if not bot_token or not OMDB_API_KEY:
    raise ValueError("❌ BOT_TOKEN или OMDB_API_KEY отсутствуют в .env!")
