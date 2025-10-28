import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# 🔹 Tokenni shu yerga yozing
TOKEN = "BOT_TOKENINGIZNI_BUYERGA_YOZING"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 🔹 Global o'zgaruvchilar
CHAT_ID = None
INTERVAL = 1  # daqiqa (standart)
MESSAGE_TEXT = "🔔 Salom guruh! Bu avtomatik yuborilgan xabar."  # standart xabar


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(
        "👋 Salom! Men avtomatik xabar yuboradigan botman.\n\n"
        "Meni guruhga qo‘shing va admin qiling.\n\n"
        "⚙️ Sozlash komandalar:\n"
        "• `/settime 5` → har 5 daqiqada yuboradi\n"
        "• `/settext Salom hammaga!` → xabar matnini o‘zgartiradi\n"
        "• `/status` → joriy sozlamalarni ko‘rsatadi\n"
        "• `/help` → yordam"
    )


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(
        "🧭 Yordam:\n"
        "`/settime [daqiqa]` — yuborish oralig‘ini o‘rnatish\n"
        "`/settext [matn]` — yuboriladigan xabar matnini belgilash\n"
        "`/status` — joriy sozlamalarni ko‘rish"
    )


@dp.message_handler(commands=['settime'])
async def set_time_command(message: types.Message):
    global INTERVAL
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2:
            INTERVAL = int(parts[1])
            await message.reply(f"✅ Xabar yuborish oralig‘i {INTERVAL} daqiqa qilib o‘rnatildi.")
        else:
            await message.reply("❌ Noto‘g‘ri format.\nNamuna: `/settime 5`")
    except ValueError:
        await message.reply("❌ Faqat butun son kiriting. Masalan: `/settime 3`")


@dp.message_handler(commands=['settext'])
async def set_text_command(message: types.Message):
    global MESSAGE_TEXT
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2:
            MESSAGE_TEXT = parts[1]
            await message.reply("✅ Xabar matni muvaffaqiyatli o‘zgartirildi.")
        else:
            await message.reply("❌ Namuna: `/settext Salom do‘stlar!`")
    except Exception as e:
        await message.reply(f"Xatolik: {e}")


@dp.message_handler(commands=['status'])
async def status_command(message: types.Message):
    await message.reply(
        f"📋 **Joriy sozlamalar:**\n"
        f"• Guruh ID: `{CHAT_ID}`\n"
        f"• Interval: {INTERVAL} daqiqa\n"
        f"• Xabar matni: {MESSAGE_TEXT}"
    )


@dp.message_handler(content_types=types.ContentType.ANY)
async def get_chat_id(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    await message.reply(f"✅ Guruh/Chat ID aniqlandi: `{CHAT_ID}`")
    print(f"[INFO] Chat ID: {CHAT_ID}")


async def send_message_periodically():
    global CHAT_ID, INTERVAL, MESSAGE_TEXT
    while True:
        if CHAT_ID:
            try:
                await bot.send_message(CHAT_ID, MESSAGE_TEXT)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
        await asyncio.sleep(INTERVAL * 60)  # INTERVAL daqiqa kutish


async def on_startup(_):
    asyncio.create_task(send_message_periodically())
    print("✅ Bot ishga tushdi va tayyor.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
