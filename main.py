from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, ContentType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from database import SessionLocal
from models import VideoTranscript, Base

# Укажите свои данные для подключения к базе данных
DATABASE_URL = 'postgresql://username:password@localhost:5432/database_name'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Укажите токен своего бота
BOT_TOKEN = "6662145196:AAHjBaUKYWTYLPjNAthjD8lR2LV5140jGsM"

# Инициализация бота и хранилища состояний
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных
Base.metadata.create_all(bind=engine)

# Клавиатура для запроса расшифровки видеосообщения
inline_keyboard = InlineKeyboardMarkup(row_width=1)
inline_keyboard.add(
    InlineKeyboardButton("Запросить расшифровку", callback_data="request_transcript")
)

# Обработчик команды /start
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.reply("Привет! Я бот, который расшифровывает видеосообщения. Просто отправь мне видеосообщение в формате кружка, и я предоставлю тебе текстовую расшифровку.", reply_markup=inline_keyboard)

# Обработчик видеосообщений
@dp.message_handler(content_types=ContentType.VIDEO)
async def process_video(message: types.Message, state: FSMContext):
    # Получение файла видео
    video_file = await message.video.get_file()

    # Запрос расшифровки видеосообщения (здесь нужно добавить свой код или API для расшифровки видео)

    # Сохранение расшифровки в базу данных
    db = SessionLocal()
    transcript = "Текстовая расшифровка видео"
    video_transcript = VideoTranscript(video_id=video_file.file_unique_id, transcript=transcript)
    db.add(video_transcript)
    db.commit()
    db.refresh(video_transcript)

    # Отправка расшифровки пользователю
    await message.reply(transcript)

# Обработчик запроса расшифровки через inline-кнопку
@dp.callback_query_handler(text="request_transcript")
async def request_transcript(callback_query: types.CallbackQuery,state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Отправьте мне видеосообщение в формате кружка, и я предоставлю вам текстовую расшифровку.")

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)


