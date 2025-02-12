import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.omdb_api import omdb_client

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN отсутствует в .env!")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния
class FilmState(StatesGroup):
    waiting_for_movie_name = State()
    waiting_for_plot_type = State()

# Команда /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer('👋 Hello! Send me the name of a movie, and I will summarize it for you.')
    await state.set_state(FilmState.waiting_for_movie_name)

# Обработчик ввода названия фильма
@dp.message(FilmState.waiting_for_movie_name)
async def get_movie_name(message: Message, state: FSMContext):
    movie_name = message.text.strip()
    movie_details = omdb_client.search_movie(movie_name)

    if "Error" in movie_details:
        await message.answer("❌ I couldn't find a movie with that name. Please try again.")
        return

    await state.update_data(movie_name=movie_name)
    await message.answer(
        "🎬 What would you like to know about the movie?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📝 Short description")],
                [KeyboardButton(text="ℹ️ Information")],
                [KeyboardButton(text="🔄 Another movie")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(FilmState.waiting_for_plot_type)

@dp.message(FilmState.waiting_for_plot_type)
async def send_plot(message: Message, state: FSMContext):
    plot_type = message.text.strip()
    user_data = await state.get_data()
    movie_name = user_data.get('movie_name')

    movie_details = omdb_client.search_movie(movie_name)
    plot = movie_details.get("Plot", "Description not available.")

    if plot_type == "📝 Short description":
        await message.answer(f"📝 *Short Description* of '{movie_name}':\n\n{plot}")
    elif plot_type == "ℹ️ Information":
        movie_info = {
            "🎥 Title": movie_details.get("Title"),
            "📅 Year": movie_details.get("Year"),
            "🎭 Genre": movie_details.get("Genre"),
            "🎬 Director": movie_details.get("Director"),
            "👥 Actors": movie_details.get("Actors"),
            "⭐ IMDB Rating": movie_details.get("imdbRating"),
            "🌐 Language": movie_details.get("Language"),
            "🌍 Country": movie_details.get("Country"),
        }
        info_message = "\n".join([f"{key}: {value}" for key, value in movie_info.items()])
        poster_url = movie_details.get("Poster")

        if poster_url != "N/A":
            await message.answer_photo(poster_url, caption=f"📚 *Movie Information for '{movie_name}':*\n\n{info_message}")
        else:
            await message.answer(f"📚 *Movie Information for '{movie_name}':*\n\n{info_message}")
    elif plot_type == "🔄 Another movie":
        await message.answer('📲 Send the name of another movie:')
        await state.set_state(FilmState.waiting_for_movie_name)
    else:
        await message.answer("❗ Please choose either '📝 Short description' or 'ℹ️ Information'.")

# Основная функция
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
