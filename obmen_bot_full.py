import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔑 Bot tokeni
TOKEN = "8023020606:AAEmI5pl2JF7spmfSmqVQ8SRXzSqsbN8Rpk"

# 📢 10 tagacha guruh username (public guruhlar)
GROUP_USERNAMES = [
    "@pubg_uzbchat1",
    "@sarmoyasiz_pulkopaytrish",
    "@sarmoyasiz_pul_ishlash_yolari",
    "@reklama_guruh1",
    "@reklama_guruh2",
    "@reklama_guruh3",
    "@reklama_guruh4",
    "@reklama_guruh5",
    "@reklama_guruh6",
    "@reklama_guruh7"
]

# 👑 Admin ID (faqat siz yuborgan xabarni qabul qiladi)
ADMIN_ID = 7973934849

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None


def start(update: Update, context: CallbackContext):
    """Start komandasi"""
    if update.message.from_user.id != ADMIN_ID:
        return
    update.message.reply_text(
        "✏️ Guruhlarga yuboriladigan xabarni yuboring (rasm, video yoki matn bo‘lishi mumkin)."
    )


def save_message(update: Update, context: CallbackContext):
    """Admin yuborgan xabarni saqlash"""
    global message_to_send
    if update.message.from_user.id != ADMIN_ID:
        return

    chat_id = update.message.chat_id
    message_id = update.message.message_id

    message_to_send = (chat_id, message_id)
    update.message.reply_text("📸 Xabar saqlandi. Har 1 sekundda guruhlarga yuboriladi.")
    start_auto_send()


def start_auto_send():
    """Avtomatik yuborishni ishga tushirish"""
    global auto_send
    if not auto_send:
        auto_send = True
        threading.Thread(target=auto_sender, daemon=True).start()


def auto_sender():
    """Har 1 sekundda saqlangan xabarni 10 tagacha guruhga yuboradi"""
    global auto_send, message_to_send
    while auto_send:
        if message_to_send:
            from_chat_id, message_id = message_to_send
            for group in GROUP_USERNAMES:
                try:
                    bot.forward_message(chat_id=group, from_chat_id=from_chat_id, message_id=message_id)
                    print(f"{group} guruhiga yuborildi ✅")
                except Exception as e:
                    print(f"⚠️ Xatolik {group} guruhida: {e}")
        time.sleep(1)  # bu joyni 30 qilsang 30 sekundda yuboradi


def stop(update: Update, context: CallbackContext):
    """Yuborishni to‘xtatish"""
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
    dp.add_handler(MessageHandler(Filters.all, save_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
