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

        # Ensure users.json exists
        if not os.path.exists("users.json"):
            with open("users.json", "w", encoding="utf-8") as f:
                json.dump([], f)

        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        users.append(user_data)

        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        await message.answer(
            f"✅ <b>Registration complete and saved!</b>\n\n"
            f"<b>Service:</b> {user_data['service']}\n"
            f"<b>Code:</b> {user_data['code']}\n"
            f"<b>Birthdate:</b> {user_data['birthdate']}\n"
            f"<b>Auto-booking:</b> {'Yes' if user_data['auto_book'] else 'No'}"
        )
        user_steps.pop(chat_id, None)

# ====== Handle skipping appointments (in future) ======
@dp.callback_query_handler(lambda c: c.data == "ignore_booking")
async def ignore_booking(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    message_text = callback_query.message.text

    if "Appointment available on:" in message_text:
        date_line = message_text.split("Appointment available on:")[1].strip().split("\n")[0]
        date = date_line.strip()

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
    await bot.send_message(chat_id, "⏭️ Booking skipped. You won’t be notified again for this date.")

# Start polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)