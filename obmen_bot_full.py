import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# 🔹 Tokeningizni shu yerga yozing
TOKEN = "8023020606:AAG1YTskBetuK-020LTvOPf6N6aiGIh4nPo"

# 🔹 Guruh ID ni shu yerga yozing (pastda qanday olishni tushuntiraman)
GROUP_ID = -1087968824

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

MESSAGE_TEXT = None
sending_active = False
waiting_for_text = False


# 🔹 Tugmalarni shakllantirish
def main_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📝 Xabar matnini kiritish", callback_data='enter_text'))
    if MESSAGE_TEXT:
        keyboard.add(InlineKeyboardButton("✅ Tasdiqlash va yuborishni boshlash", callback_data='confirm'))
    if sending_active:
        keyboard.add(InlineKeyboardButton("🛑 To‘xtatish", callback_data='stop'))
    return keyboard


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(
        "👋 Salom! Bu bot guruhga har 1 daqiqada siz kiritgan xabarni yuboradi.\n\n"
        "🟢 Avval xabar matnini kiriting:",
        reply_markup=main_buttons()
    )


@dp.message_handler(content_types=types.ContentType.ANY)
async def get_message_text(message: types.Message):
    global MESSAGE_TEXT, waiting_for_text
    if waiting_for_text:
        MESSAGE_TEXT = message.text
        waiting_for_text = False
        await message.answer(
            f"✅ Xabar matni saqlandi:\n\n`{MESSAGE_TEXT}`",
            reply_markup=main_buttons()
        )


@dp.callback_query_handler(lambda c: c.data == 'enter_text')
async def ask_for_text(callback_query: types.CallbackQuery):
    global waiting_for_text
    waiting_for_text = True
    await callback_query.message.edit_text(
        "✍️ Iltimos, guruhga yuboriladigan xabar matnini kiriting:",
        reply_markup=None
    )


@dp.callback_query_handler(lambda c: c.data == 'confirm')
async def confirm_sending(callback_query: types.CallbackQuery):
    global sending_active
    if not MESSAGE_TEXT:
        await bot.send_message(callback_query.message.chat.id, "❌ Avval xabar matnini kiriting.")
        return

    sending_active = True
    await bot.send_message(callback_query.message.chat.id,
                           f"✅ Guruhga har 1 daqiqada quyidagi xabar yuboriladi:\n\n`{MESSAGE_TEXT}`",
                           reply_markup=main_buttons())
    asyncio.create_task(send_message_every_minute())


@dp.callback_query_handler(lambda c: c.data == 'stop')
async def stop_sending(callback_query: types.CallbackQuery):
    global sending_active
    sending_active = False
    await callback_query.message.edit_text("🛑 Xabar yuborish to‘xtatildi.", reply_markup=main_buttons())


async def send_message_every_minute():
    global MESSAGE_TEXT, sending_active
    while sending_active and MESSAGE_TEXT:
        try:
            await bot.send_message(GROUP_ID, MESSAGE_TEXT)
        except Exception as e:
            print(f"Xabar yuborishda xatolik: {e}")
        await asyncio.sleep(60)


async def on_startup(_):
    print("✅ Bot ishga tushdi.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
