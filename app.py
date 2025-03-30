import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get bot token from environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Command handler for '/start'
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Welcome! This bot is working!")

# Echo handler for any other message
@dp.message_handler(lambda message: True)
async def echo_message(message: types.Message):
    await message.answer(f"Received: {message.text}")

# Main function to start polling
async def on_start():
    logging.info("Bot started")
    await dp.start_polling()

# Run bot
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)