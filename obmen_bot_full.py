import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8023020606:AAG1YTskBetuK-020LTvOPf6N6aiGIh4nPo"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

CHAT_ID = None
MESSAGE_TEXT = None
sending_active = False
waiting_for_text = False


def main_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📝 Xabar matnini kiritish", callback_data='enter_text'))
    if MESSAGE_TEXT:
        keyboard.add(InlineKeyboardButton("✅ Tasdiqlash va yuborishni boshlash", callback_data='confirm'))
    return keyboard


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(
        "👋 Salom! Men guruhga har 1 daqiqada siz kiritgan xabarni yuboraman.\n"
        "Quyidagi tugmalar orqali sozlang 👇",
        reply_markup=main_buttons()
    )


@dp.message_handler(content_types=types.ContentType.ANY)
async def get_chat_id(message: types.Message):
    global CHAT_ID, waiting_for_text, MESSAGE_TEXT
    CHAT_ID = message.chat.id

    # Agar matn kiritish rejimida bo‘lsa
    if waiting_for_text:
        MESSAGE_TEXT = message.text
        waiting_for_text = False
        await message.answer(
            f"✅ Xabar matni saqlandi:\n\n`{MESSAGE_TEXT}`",
            reply_markup=main_buttons()
        )
    else:
        print(f"[INFO] Chat ID: {CHAT_ID}")


@dp.callback_query_handler(lambda c: c.data == 'enter_text')
async def ask_for_text(callback_query: types.CallbackQuery):
    global waiting_for_text
    waiting_for_text = True
    await callback_query.message.edit_text("✍️ Iltimos, yuboriladigan xabar matnini kiriting:")


@dp.callback_query_handler(lambda c: c.data == 'confirm')
async def confirm_sending(callback_query: types.CallbackQuery):
    global sending_active
    if not MESSAGE_TEXT:
        await bot.send_message(callback_query.message.chat.id, "❌ Avval xabar matnini kiriting.")
        return

    sending_active = True
    await bot.send_message(callback_query.message.chat.id,
                           f"✅ Har 1 daqiqada quyidagi xabar yuboriladi:\n\n`{MESSAGE_TEXT}`")
    asyncio.create_task(send_message_every_minute())


async def send_message_every_minute():
    global CHAT_ID, MESSAGE_TEXT, sending_active
    while sending_active and CHAT_ID and MESSAGE_TEXT:
        try:
            await bot.send_message(CHAT_ID, MESSAGE_TEXT)
        except Exception as e:
            print(f"Xabar yuborishda xatolik: {e}")
        await asyncio.sleep(60)


async def on_startup(_):
    print("✅ Bot ishga tushdi.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
