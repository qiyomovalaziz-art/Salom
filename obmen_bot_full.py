import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8023020606:AAG1YTskBetuK-020LTvOPf6N6aiGIh4nPo"
GROUP_ID = -100234567890  # Guruh ID-ni shu yerga yozing

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

saved_message = None
sending_active = False
waiting_for_message = False


def main_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📝 Xabarni kiritish", callback_data="enter_message"))
    if saved_message:
        keyboard.add(InlineKeyboardButton("✅ Tasdiqlash va yuborishni boshlash", callback_data="confirm"))
    if sending_active:
        keyboard.add(InlineKeyboardButton("🛑 To‘xtatish", callback_data="stop"))
    return keyboard


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "👋 Salom! Men har 1 daqiqada siz yuborgan postni guruhga yuboraman.\n"
        "📝 Tugmadan foydalanib postni yuboring (rasm, video yoki matn bo‘lishi mumkin):",
        reply_markup=main_buttons()
    )


@dp.callback_query_handler(lambda c: c.data == "enter_message")
async def ask_for_post(callback_query: types.CallbackQuery):
    global waiting_for_message
    waiting_for_message = True
    await callback_query.message.edit_text("✍️ Iltimos, guruhga yuboriladigan xabarni yuboring (rasm, video yoki matn bo‘lishi mumkin):")


@dp.message_handler(content_types=types.ContentType.ANY)
async def get_post(message: types.Message):
    global saved_message, waiting_for_message
    if waiting_for_message:
        saved_message = message
        waiting_for_message = False
        await message.answer("✅ Xabar saqlandi! Endi uni yuborishni boshlashingiz mumkin.", reply_markup=main_buttons())


@dp.callback_query_handler(lambda c: c.data == "confirm")
async def confirm(callback_query: types.CallbackQuery):
    global sending_active
    if not saved_message:
        await bot.send_message(callback_query.message.chat.id, "❌ Avval post yuboring.")
        return

    sending_active = True
    await bot.send_message(callback_query.message.chat.id, "✅ Post yuborish boshlandi! Har 1 daqiqada guruhga yuboriladi.", reply_markup=main_buttons())
    asyncio.create_task(send_post_every_minute())


@dp.callback_query_handler(lambda c: c.data == "stop")
async def stop(callback_query: types.CallbackQuery):
    global sending_active
    sending_active = False
    await bot.send_message(callback_query.message.chat.id, "🛑 Post yuborish to‘xtatildi.", reply_markup=main_buttons())


async def send_post_every_minute():
    global sending_active, saved_message
    while sending_active and saved_message:
        try:
            # Agar rasm, video yoki boshqa fayl bo‘lsa forward qilamiz
            if saved_message.photo:
                await bot.send_photo(GROUP_ID, saved_message.photo[-1].file_id, caption=saved_message.caption or "")
            elif saved_message.video:
                await bot.send_video(GROUP_ID, saved_message.video.file_id, caption=saved_message.caption or "")
            elif saved_message.text:
                await bot.send_message(GROUP_ID, saved_message.text)
            else:
                await bot.forward_message(GROUP_ID, saved_message.chat.id, saved_message.message_id)
        except Exception as e:
            print(f"Xabar yuborishda xatolik: {e}")

        await asyncio.sleep(60)  # 1 daqiqa kutish


async def on_startup(_):
    print("✅ Bot ishga tushdi.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
