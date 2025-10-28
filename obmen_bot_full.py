import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# 🔹 Bot tokenini shu yerga yozing
TOKEN = "8023020606:AAG1YTskBetuK-020LTvOPf6N6aiGIh4nPo"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

CHAT_ID = 1087968824
sending_messages = False  # holat (boshlangan yoki to‘xtagan)


# 🔹 Tugmalar
def control_buttons():
    keyboard = InlineKeyboardMarkup()
    if not sending_messages:
        keyboard.add(InlineKeyboardButton("🟢 Xabar yuborishni boshlash", callback_data='start_sending'))
    else:
        keyboard.add(InlineKeyboardButton("🔴 Xabar yuborishni to‘xtatish", callback_data='stop_sending'))
    return keyboard


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(
        "👋 Salom! Bu bot har 1 daqiqada xabar yuborishi mumkin.\n"
        "Quyidagi tugma orqali avtomatik xabar yuborishni yoqing yoki o‘chiring 👇",
        reply_markup=control_buttons()
    )


@dp.message_handler(content_types=types.ContentType.ANY)
async def get_chat_id(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    await message.reply(f"✅ Guruh/Chat ID aniqlandi: `{CHAT_ID}`")
    print(f"[INFO] Chat ID: {CHAT_ID}")


@dp.callback_query_handler(lambda c: c.data == 'start_sending')
async def start_sending_messages(callback_query: types.CallbackQuery):
    global sending_messages
    sending_messages = True
    await callback_query.message.edit_reply_markup(reply_markup=control_buttons())
    await bot.send_message(callback_query.message.chat.id, "🟢 Xabar yuborish boshlandi!")
    asyncio.create_task(send_message_every_minute())


@dp.callback_query_handler(lambda c: c.data == 'stop_sending')
async def stop_sending_messages(callback_query: types.CallbackQuery):
    global sending_messages
    sending_messages = False
    await callback_query.message.edit_reply_markup(reply_markup=control_buttons())
    await bot.send_message(callback_query.message.chat.id, "🔴 Xabar yuborish to‘xtatildi.")


async def send_message_every_minute():
    """Har 1 daqiqada xabar yuborish jarayoni"""
    global sending_messages, CHAT_ID
    while sending_messages:
        if CHAT_ID:
            try:
                await bot.send_message(CHAT_ID, "⏰ Har 1 daqiqada yuboriladigan avtomatik xabar!")
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
        await asyncio.sleep(60)


async def on_startup(_):
    print("✅ Bot ishga tushdi.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
