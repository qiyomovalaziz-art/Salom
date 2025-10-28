from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
import asyncio

TOKEN = "8023020606:AAEmI5pl2JF7spmfSmqVQ8SRXzSqsbN8Rpk"  # bu yerga tokeningizni yozing
bot = Bot(token=TOKEN)

group_id = None
message_text = None
auto_send_task = None
sending = False


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Iltimos, yuboriladigan xabar matnini kiriting:")
    return


# Foydalanuvchi yozgan matnni saqlash
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_text
    message_text = update.message.text

    keyboard = [[InlineKeyboardButton("✅ Tasdiqlash va yuborishni boshlash", callback_data="start_send")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"✅ Xabar saqlandi:\n\n{message_text}", reply_markup=reply_markup)


# Guruhni aniqlash (bot guruhga qo‘shilganda)
async def detect_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global group_id
    chat = update.message.chat
    if chat.type in ["group", "supergroup"]:
        group_id = chat.id
        await update.message.reply_text("✅ Guruh aniqlandi! Endi siz botdan yuborishni boshlashingiz mumkin.")
    return


# Har 1 daqiqada xabar yuborish funksiyasi
async def send_periodic():
    global bot, group_id, message_text, sending
    while sending:
        try:
            if group_id and message_text:
                await bot.send_message(chat_id=group_id, text=message_text)
        except Exception as e:
            print("Xatolik:", e)
        await asyncio.sleep(60)


# Tugma bosilganda ishlovchi funksiya
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sending, auto_send_task

    query = update.callback_query
    await query.answer()

    if query.data == "start_send":
        if not sending:
            sending = True
            auto_send_task = asyncio.create_task(send_periodic())

            keyboard = [[InlineKeyboardButton("🛑 To‘xtatish", callback_data="stop_send")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text("✅ Post yuborish boshlandi! Har 1 daqiqada guruhga yuboriladi.", reply_markup=reply_markup)

    elif query.data == "stop_send":
        sending = False
        if auto_send_task:
            auto_send_task.cancel()

        keyboard = [[InlineKeyboardButton("✅ Qaytadan boshlash", callback_data="start_send")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("🛑 Post yuborish to‘xtatildi.", reply_markup=reply_markup)


# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, detect_group))
app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, detect_group))
app.add_handler(CallbackQueryHandler(button_callback))

print("🤖 Bot ishga tushdi...")
app.run_polling()
