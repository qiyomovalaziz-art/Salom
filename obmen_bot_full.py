import time
import threading
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ⚙️ Sozlamalar
TOKEN = "8023020606:AAEmI5pl2JF7spmfSmqVQ8SRXzSqsbN8Rpk"
GROUP_USERNAMES = ["@pubg_uzbchat1", "@sarmoyasiz_pulkopaytrish", "@sarmoyasiz_pul_ishlash_yolari"]  # Guruhlar ro'yxati
ADMIN_ID = 7973934849  # Faqat sizning Telegram ID'ingiz

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None


def start(update: Update, context: CallbackContext):
    """Start komandasi"""
    if update.message.from_user.id != ADMIN_ID:
        return
    update.message.reply_text("✏️ Guruhlarga yuboriladigan xabarni (matn yoki rasm) yuboring.")


def save_message(update: Update, context: CallbackContext):
    """Admin yuborgan xabarni saqlaydi"""
    global message_to_send
    if update.message.from_user.id != ADMIN_ID:
        return  # Faqat admin yuborganini oladi

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption if update.message.caption else ""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Botga kirish", url="https://t.me/Curupto_SotibOlish_SotishBot")]
        ])
        message_to_send = ("photo", photo, caption, keyboard)
        update.message.reply_text("📸 Rasmli xabar saqlandi va har 1 sekundda yuboriladi.")
    else:
        text = update.message.text
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Botga kirish", url="https://t.me/Curupto_SotibOlish_SotishBot")]
        ])
        message_to_send = ("text", text, keyboard)
        update.message.reply_text("✉️ Matnli xabar saqlandi va har 1 sekundda yuboriladi.")
    start_auto_send()


def start_auto_send():
    """Yuborish jarayonini ishga tushiradi"""
    global auto_send
    if not auto_send:
        auto_send = True
        threading.Thread(target=auto_sender, daemon=True).start()


def auto_sender():
    """Har 1 sekundda guruhlarga xabar yuboradi"""
    global auto_send, message_to_send
    while auto_send:
        if message_to_send:
            for group in GROUP_USERNAMES:
                try:
                    if message_to_send[0] == "text":
                        bot.send_message(chat_id=group, text=message_to_send[1], reply_markup=message_to_send[2])
                    elif message_to_send[0] == "photo":
                        bot.send_photo(chat_id=group, photo=message_to_send[1],
                                       caption=message_to_send[2], reply_markup=message_to_send[3])
                except Exception as e:
                    print(f"Xatolik {group} guruhida: {e}")
        time.sleep(1)  # har 1 sekundda


def stop(update: Update, context: CallbackContext):
    """To‘xtatish komandasi"""
    global auto_send
    if update.message.from_user.id != ADMIN_ID:
        return
    auto_send = False
    update.message.reply_text("⏹️ Avtomatik yuborish to‘xtatildi.")


def main():
    """Botni ishga tushirish"""
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, save_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
