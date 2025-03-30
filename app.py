import os
import logging
from datetime import datetime
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

user_steps = {}
logging.basicConfig(level=logging.INFO)

DB_FILE = "data/users.db"

async def init_db():
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                name TEXT,
                service TEXT,
                code TEXT,
                birthdate TEXT,
                auto_book BOOLEAN,
                registered_at TEXT,
                skipped_dates TEXT
            )
        """)
        await db.commit()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    user_steps[chat_id] = {'step': 1}
    await message.answer("Welcome! Please enter the service type (e.g., Segurança Privada):")

@dp.message_handler(lambda message: True)
async def handle_steps(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_steps:
        await message.answer("Please type /start to begin.")
        return

    step_data = user_steps[chat_id]
    step = step_data.get("step", 1)

    if step == 1:
        step_data["service"] = text
        step_data["step"] = 2
        await message.answer("Please enter your request number:")

    elif step == 2:
        step_data["code"] = text
        step_data["step"] = 3
        await message.answer("Please enter your date of birth (dd/mm/yyyy):")

    elif step == 3:
        step_data["birthdate"] = text
        step_data["step"] = 4
        await message.answer("Please enter the private invitation code:")

    elif step == 4:
        if text != "1924":
            await message.answer("❌ Invalid invitation code. Registration cancelled.")
            user_steps.pop(chat_id, None)
            return
        step_data["step"] = 5
        await message.answer("Would you like to enable auto-booking? (yes/no):")

    elif step == 5:
        step_data["auto_book"] = text.lower() == "yes"

        user_data = {
            "chat_id": chat_id,
            "name": message.from_user.full_name,
            "service": step_data["service"],
            "code": step_data["code"],
            "birthdate": step_data["birthdate"],
            "auto_book": step_data["auto_book"],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "skipped_dates": ""
        }

        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users (
                    chat_id, name, service, code, birthdate, auto_book, registered_at, skipped_dates
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data["chat_id"],
                user_data["name"],
                user_data["service"],
                user_data["code"],
                user_data["birthdate"],
                user_data["auto_book"],
                user_data["registered_at"],
                user_data["skipped_dates"]
            ))
            await db.commit()

        msg = (
            "✅ <b>Registration complete and saved to database!</b>\n\n"
            f"<b>Service:</b> {user_data['service']}\n"
            f"<b>Code:</b> {user_data['code']}\n"
            f"<b>Birthdate:</b> {user_data['birthdate']}\n"
            f"<b>Auto-booking:</b> {'Yes' if user_data['auto_book'] else 'No'}"
        )
        await message.answer(msg, parse_mode="HTML")
        user_steps.pop(chat_id, None)

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    executor.start_polling(dp, skip_updates=True)