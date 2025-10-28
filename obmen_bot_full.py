import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "8023020606:AAEmI5pl2JF7spmfSmqVQ8SRXzSqsbN8Rpk"
GROUP_USERNAME = "@pubg_uzbchat1"  # Masalan: "@MyGroupName"

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None


def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Salom! Menga yubormoqchi bo‘lgan xabaringni (matn yoki rasm bilan) yubor.")


def save_message(update: Update, context: CallbackContext):
    global message_to_send
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption if update.message.caption else ""
        message_to_send = ("photo", photo, caption)
        update.message.reply_text("📸 Rasmli xabar qabul qilindi. Bot uni har 30 sekundda guruhga yuboradi.")
    else:
        message_to_send = ("text", update.message.text)
        update.message.reply_text("✉️ Matnli xabar qabul qilindi. Bot uni har 30 sekundda guruhga yuboradi.")
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
            if message_to_send[0] == "text":
                bot.send_message(chat_id=GROUP_USERNAME, text=message_to_send[1])
            elif message_to_send[0] == "photo":
                bot.send_photo(chat_id=GROUP_USERNAME, photo=message_to_send[1], caption=message_to_send[2])
        time.sleep(30)


def stop(update: Update, context: CallbackContext):
    global auto_send
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
