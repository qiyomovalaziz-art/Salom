from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

BOT_TOKEN = "8023020606:AAEmI5pl2JF7spmfSmqVQ8SRXzSqsbN8Rpk"

# Xabar matni
saved_message = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Iltimos, yuboriladigan xabar matnini kiriting:")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global saved_message
    saved_message = update.message.text
    await update.message.reply_text("✅ Xabar saqlandi! Endi 1 daqiqada bir marta barcha guruhlarga yuboriladi.")
    asyncio.create_task(send_to_all_groups(context))

async def send_to_all_groups(context: ContextTypes.DEFAULT_TYPE):
    global saved_message

    while True:
        updates = await context.bot.get_updates()
        group_ids = set()

        for update in updates:
            if update.message and update.message.chat.type in ["group", "supergroup"]:
                group_ids.add(update.message.chat.id)

        for chat_id in group_ids:
            try:
                await context.bot.send_message(chat_id=chat_id, text=saved_message)
            except Exception as e:
                print(f"Guruhga yuborishda xato: {e}")

        await asyncio.sleep(60)  # 1 daqiqa kutadi

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

print("✅ Bot ishga tushdi...")
app.run_polling()
