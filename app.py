import os
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

# تحميل .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_steps = {}

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    chat_id = message.chat.id
    user_steps[chat_id] = {'step': 1}
    await message.answer("Welcome! Please enter the service type (e.g., Segurança Privada):")

@dp.message_handler(lambda message: True)
async def step_handler(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_steps:
        await message.answer("Please type /start to begin.")
        return

    step = user_steps[chat_id].get("step", 1)

    if step == 1:
        user_steps[chat_id]["service"] = text
        user_steps[chat_id]["step"] = 2
        await message.answer("Please enter your request number:")
    
    elif step == 2:
        user_steps[chat_id]["code"] = text
        user_steps[chat_id]["step"] = 3
        await message.answer("Please enter your date of birth (dd/mm/yyyy):")
    
    elif step == 3:
        user_steps[chat_id]["birthdate"] = text
        user_steps[chat_id]["step"] = 4
        await message.answer("Please enter the private invitation code:")
    
    elif step == 4:
        if text != "1924":
            await message.answer("❌ Invalid invitation code. Registration cancelled.")
            user_steps.pop(chat_id, None)
            return
        user_steps[chat_id]["invite"] = text
        user_steps[chat_id]["step"] = 5
        await message.answer("Would you like to enable auto-booking? (yes/no):")
    
    elif step == 5:
        user_steps[chat_id]["auto_book"] = text.lower() == "yes"

        # تحضير البيانات للحفظ
        data = user_steps[chat_id]
        user_data = {
            "chat_id": chat_id,
            "name": message.from_user.full_name,
            "service": data["service"],
            "code": data["code"],
            "birthdate": data["birthdate"],
            "auto_book": data["auto_book"],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "skipped_dates": []
        }

        # حفظ البيانات في users.json
        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = []

        users.append(user_data)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        summary = (
            f"✅ Registration complete and saved!\n\n"
            f"<b>Service:</b> {data['service']}\n"
            f"<b>Code:</b> {data['code']}\n"
            f"<b>Birthdate:</b> {data['birthdate']}\n"
            f"<b>Auto-booking:</b> {'Yes' if data['auto_book'] else 'No'}"
        )
        await message.answer(summary, parse_mode="HTML")
        user_steps.pop(chat_id, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)