import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔑 Bot token
TOKEN = "8023020606:AAHx3KQrsPF5ypxE96scoPw1LSaLyfhLECs"

# 📢 Guruhlar (10 tagacha)
GROUP_USERNAMES = [
    "@pubg_uzbchat1",
    "@sarmoyasiz_pulkopaytrish",
    "@pubg_chat_uzbbb",
    "@PUBG_MOBILE_SAVDO_2025",
    "@reklama_guruh3",
    "@reklama_guruh4",
    "@reklama_guruh5",
    "@reklama_guruh6",
    "@reklama_guruh7",
    "@reklama_guruh8"
]

# 👑 Faqat admin xabar yuboradi
ADMIN_ID = 7973934849

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None


def start(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    update.message.reply_text("✏️ Guruhlarga yuboriladigan xabarni yuboring (rasm, video yoki matn).")


def save_message(update: Update, context: CallbackContext):
    global message_to_send
    if update.message.from_user.id != ADMIN_ID:
        return

    chat_id = update.message.chat_id
    message_id = update.message.message_id

    message_to_send = (chat_id, message_id)
    update.message.reply_text("📸 Xabar saqlandi. Bot har 35 sekundda barcha guruhlarga yuboradi.")
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
            from_chat_id, message_id = message_to_send
            for group in GROUP_USERNAMES:
                try:
                    bot.forward_message(chat_id=group, from_chat_id=from_chat_id, message_id=message_id)
                    print(f"✅ {group} guruhiga yuborildi.")
                except Exception as e:
                    print(f"⚠️ Xatolik {group} guruhida: {e}")
                time.sleep(35)  # Telegram flood limitdan o‘tmaslik uchun
        else:
            time.sleep(5)


def stop(update: Update, context: CallbackContext):
    global auto_send
    if update.message.from_user.id != ADMIN_ID:
        return
    auto_send = False
    update.message.reply_text("⏹️ Yuborish to‘xtatildi.")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(MessageHandler(Filters.all, save_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
