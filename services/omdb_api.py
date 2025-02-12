import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

if not OMDB_API_KEY:
    raise ValueError("❌ OMDB_API_KEY отсутствует в .env!")

BASE_URL = "http://www.omdbapi.com/"

class OMDbAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _make_request(self, params: dict) -> dict:
        params["apikey"] = self.api_key
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Ошибка: {response.status_code} - {response.text}")
        data = response.json()
        if data.get("Response") == "False":
            raise Exception(f"Ошибка: {data.get('Error', 'Unknown error')}")
        return data

    def search_movie(self, title: str) -> dict:
        return self._make_request({"t": title})

omdb_client = OMDbAPI(api_key=OMDB_API_KEY)
