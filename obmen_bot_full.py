import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re

# 🔑 Token
TOKEN = "8023020606:AAHx3KQrsPF5ypxE96scoPw1LSaLyfhLECs"

# 📢 Guruhlar
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
]

# 👑 Faqat sizning ID
ADMIN_ID = 7973934849

bot = Bot(token=TOKEN)
auto_send = False
message_to_send = None

# ⏱ Flood control holatini saqlash
blocked_groups = {}  # {group_username: time_to_retry}


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
    update.message.reply_text("📸 Xabar saqlandi. Bot avtomatik ravishda yuborishni boshlaydi.")
    start_auto_send()


def start_auto_send():
    global auto_send
    if not auto_send:
        auto_send = True
        threading.Thread(target=auto_sender, daemon=True).start()


def auto_sender():
    """Flood controlni hisobga olgan holda xabar yuboradi"""
    global auto_send, message_to_send, blocked_groups
    while auto_send:
        if message_to_send:
            from_chat_id, message_id = message_to_send
            current_time = time.time()

            for group in GROUP_USERNAMES:
                # Agar guruh hozircha bloklangan bo‘lsa — o‘tkazib yubor
                if group in blocked_groups and current_time < blocked_groups[group]:
                    continue

                try:
                    bot.forward_message(chat_id=group, from_chat_id=from_chat_id, message_id=message_id)
                    print(f"✅ {group} guruhiga yuborildi.")
                    time.sleep(10)  # har guruh orasida 10 soniya kutish
                except Exception as e:
                    error_message = str(e)
                    print(f"⚠️ Xatolik {group} guruhida: {error_message}")

                    # Flood limitni aniqlab, qancha sekund kutish kerakligini topamiz
                    if "Flood control exceeded" in error_message:
                        match = re.search(r"Retry in (\d+)", error_message)
                        if match:
                            wait_seconds = int(match.group(1))
                            blocked_groups[group] = current_time + wait_seconds
                            print(f"⏳ {group} uchun {wait_seconds} soniyaga kutish belgilandi.")
                        else:
                            blocked_groups[group] = current_time + 600  # agar aniqlanmasa 10 daqiqa
                    elif "Chat not found" in error_message:
                        print(f"🚫 {group} topilmadi — o‘tkazib yuborildi.")
                        blocked_groups[group] = current_time + 3600  # 1 soatga blok
                    else:
                        blocked_groups[group] = current_time + 120  # boshqa xato — 2 daqiqa kutish

        time.sleep(5)


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
    dp.add_handler(MessageHandler(Filters.all, save_message))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
