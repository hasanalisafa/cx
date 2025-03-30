import os
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# Load .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

user_steps = {}
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
        step_data["step"] = 5
        await message.answer("Would you like to enable auto-booking? (yes/no)")
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
            "skipped_dates": []
        }

        try:
            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = []

        users.append(user_data)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        await message.answer("✅ Your data has been saved.")

        # زر تجريبي لاختبار ignore_booking
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("❌ No, skip", callback_data="ignore_booking")
        )
        await message.answer("Test skip button (for now only test):", reply_markup=markup)

        user_steps.pop(chat_id, None)

# ========= التعامل مع رفض الموعد =========
@dp.callback_query_handler(lambda c: c.data == "ignore_booking")
async def ignore_booking(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    message_text = callback_query.message.text

    # التاريخ التجريبي من الزر
    date = "2024-04-05"

    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
        for user in users:
            if user["chat_id"] == chat_id:
                if "skipped_dates" not in user:
                    user["skipped_dates"] = []
                if date not in user["skipped_dates"]:
                    user["skipped_dates"].append(date)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Failed to save skipped date: {e}")

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id, f"⏭️ Skipped test date: {date}")