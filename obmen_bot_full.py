import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔑 Bot token
TOKEN = "8023020606:AAHx3KQrsPF5ypxE96scoPw1LSaLyfhLECs"

# 📢 Guruhlar (username yoki ID ko‘rinishida)
GROUPS = [
    "@pubg_uzbchat1",
    "@sarmoyasiz_pulkopaytrish",
    "@pubg_chat_uzbbb",
    "@PUBG_MOBILE_SAVDO_2025",
    "-1001234567890",   # private guruh misoli (ID bilan)
    "@reklama_guruh3"
]

# 👑 Faqat bitta admin ID
ADMIN_ID = 7973934849

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None


def start(update: Update, context: CallbackContext):
    """Boshlanish komandasi"""
    if update.message.from_user.id != ADMIN_ID:
        return
    update.message.reply_text("📩 Guruhlarga yuboriladigan xabarni yuboring (rasm, video yoki matn).")


def save_message(update: Update, context: CallbackContext):
    """Admin yuborgan xabarni saqlaydi"""
    global message_to_send
    if update.message.from_user.id != ADMIN_ID:
        return

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    message_to_send = (chat_id, message_id)

    update.message.reply_text("✅ Xabar saqlandi. Har 30 sekundda guruhlarga yuboriladi.")
    start_auto_send()


def start_auto_send():
    """Avtomatik yuborishni ishga tushirish"""
    global auto_send
    if not auto_send:
        auto_send = True
        threading.Thread(target=auto_sender, daemon=True).start()


def auto_sender():
    """Har 30 sekundda xabar yuboradi"""
    global auto_send, message_to_send
    while auto_send:
        if message_to_send:
            from_chat_id, message_id = message_to_send
            for group in GROUPS:
                try:
                    bot.forward_message(chat_id=group, from_chat_id=from_chat_id, message_id=message_id)
                    print(f"✅ Xabar yuborildi → {group}")
                    time.sleep(3)  # har guruh orasida 3 soniya tanaffus
                except Exception as e:
                    print(f"⚠️ {group} guruhida xato: {e}")
        time.sleep(30)  # Har 30 sekundda qayta yuboriladi


def stop(update: Update, context: CallbackContext):
    """Avtomatik yuborishni to‘xtatish"""
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

    print("🚀 Bot ishga tushdi...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
