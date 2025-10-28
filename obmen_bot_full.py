import time
import threading
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "8023020606:AAEmI5pl2JF7spmfSmqVQ8SRXzSqsbN8Rpk"
GROUP_USERNAME = "@pubg_uzbchat1 ,@sarmoyasiz_pulkopaytrish"  # Masalan: @MyGroupName
ADMIN_ID = 7973934849  # Faqat sizning Telegram ID'ingizni yozing

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None


def start(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    update.message.reply_text("✏️ Iltimos, guruhga yuboriladigan xabarni (rasm + matn yoki faqat matn) yuboring.")


def save_message(update: Update, context: CallbackContext):
    global message_to_send
    if update.message.from_user.id != ADMIN_ID:
        return  # Faqat siz yuborgan xabarni qabul qiladi

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption if update.message.caption else ""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Botga kirish", url="https://t.me/Curupto_SotibOlish_SotishBot")]
        ])
        message_to_send = ("photo", photo, caption, keyboard)
        update.message.reply_text("📸 Rasmli xabar qabul qilindi. Har 30 sekundda guruhga yuboriladi.")
    else:
        text = update.message.text
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Botga kirish", url="https://t.me/YOUR_BOT_USERNAME")]
        ])
        message_to_send = ("text", text, keyboard)
        update.message.reply_text("✉️ Matnli xabar qabul qilindi. Har 30 sekundda guruhga yuboriladi.")
    start_auto_send()


def start_auto_send():
    global auto_send
    if not auto_send:
        auto_send = True
        threading.Thread(target=auto_sender, daemon=True).start()


def auto_sender():
    global auto_send, message_to_send
    while auto_send:
        if message_to_send:
            try:
                if message_to_send[0] == "text":
                    bot.send_message(chat_id=GROUP_USERNAME, text=message_to_send[1], reply_markup=message_to_send[2])
                elif message_to_send[0] == "photo":
                    bot.send_photo(chat_id=GROUP_USERNAME, photo=message_to_send[1],
                                   caption=message_to_send[2], reply_markup=message_to_send[3])
            except Exception as e:
                print(f"Xatolik: {e}")
        time.sleep(1)


def stop(update: Update, context: CallbackContext):
    global auto_send
    if update.message.from_user.id != ADMIN_ID:
        return
    auto_send = False
    update.message.reply_text("⏹️ Avtomatik yuborish to‘xtatildi.")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, save_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
