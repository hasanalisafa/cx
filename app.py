import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

# تحميل التوكن من .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# إعداد البوت
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# رد على /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("✅ Bot is working!")

# تشغيل البوت
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)