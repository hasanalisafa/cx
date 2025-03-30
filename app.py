import os
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

# Load .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# تخزين خطوات كل مستخدم
user_steps = {}

# Logging setup
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    user_steps[chat_id] = {'step': 1}
    await message.answer("Welcome! Please enter the service type (e.g., Segurança Privada):")

@dp.message_handler(lambda message: True)
async def handle_steps(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    step_data = user_steps.get(chat_id)

    if not step_data:
        await message.answer("Please type /start to begin.")
        return

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
            await message.answer("❌ Invalid invitation code.")
            user_steps.pop(chat_id, None)
            return
        step_data["invite"] = text
        step_data["step"] = 5
        await message.answer("Would you like to enable auto-booking? (yes/no)")
    elif step == 5:
        step_data["auto_book"] = text.lower() == "yes"

        # حفظ البيانات
        user_data = {
            "chat_id": chat_id,
            "name": message.from_user.full_name,
            "service": step_data["service"],
            "code": step_data["code"],
            "birthdate": step_data["birthdate"],
            "auto_book": step_data["auto_book"],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = []

        users.append(user_data)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        await message.answer("✅ Your data has been saved. We will notify you when an appointment is found.")
        user_steps.pop(chat_id, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)