import os
import telebot

like_str = "1"
dislike_str = "2"

# Bot tokenını ortam değişkeninden alıyoruz
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Kullanıcılar arası iletişim eşleşmesini tutan global sözlük
communications = {}

# Kullanıcı eşleştirme fonksiyonu
def add_communications(user1, user2):
    communications[user1] = {"UserTo": user2}
    communications[user2] = {"UserTo": user1}

# Kullanıcının eşleşip eşleşmediğini kontrol eder
def connect_user(user_id):
    return user_id in communications and "UserTo" in communications[user_id]

# Mesaj işleme fonksiyonu
@bot.message_handler(content_types=["text", "sticker", "photo", "audio", "video", "voice"])
def handle_messages(message):
    user_id = message.from_user.id

    if message.content_type == "sticker":
        if not connect_user(user_id):
            return
        bot.send_sticker(communications[user_id]["UserTo"], message.sticker.file_id)

    elif message.content_type == "photo":
        if not connect_user(user_id):
            return
        file_id = message.photo[-1].file_id
        bot.send_photo(communications[user_id]["UserTo"], file_id, caption=message.caption)

    elif message.content_type == "audio":
        if not connect_user(user_id):
            return
        bot.send_audio(communications[user_id]["UserTo"], message.audio.file_id, caption=message.caption)

    elif message.content_type == "video":
        if not connect_user(user_id):
            return
        bot.send_video(communications[user_id]["UserTo"], message.video.file_id, caption=message.caption)

    elif message.content_type == "voice":
        if not connect_user(user_id):
            return
        bot.send_voice(communications[user_id]["UserTo"], message.voice.file_id)

    elif message.content_type == "text":
        if message.text not in ["/start", "/stop", dislike_str, like_str, "NewChat"]:
            if not connect_user(user_id):
                return
            if message.reply_to_message is None:
                bot.send_message(communications[user_id]["UserTo"], message.text)
            elif message.from_user.id != message.reply_to_message.from_user.id:
                bot.send_message(
                    communications[user_id]["UserTo"],
                    message.text,
                    reply_to_message_id=message.reply_to_message.message_id - 1,
                )
            else:
                bot.send_message(user_id, m_send_some_messages)

# Callback sorgu işleyici
@bot.callback_query_handler(func=lambda call: True)
def echo(call):
    if call.data == "NewChat":
        user_id = call.message.chat.id
        user_to_id = None

        add_users(chat=call.message.chat)

        if len(free_users) < 2:
            bot.send_message(user_id, m_is_not_free_users)
            return

        if free_users[user_id]["state"] == 0:
            return

        for user in free_users:
            if user["state"] == 0:
                user_to_id = user["ID"]
                break

        if user_to_id is None:
            bot.send_message(user_id, m_is_not_free_users)
            return

        keyboard = generate_markup()

        add_communications(user_id, user_to_id)

        bot.send_message(user_id, m_is_connect, reply_markup=keyboard)
        bot.send_message(user_to_id, m_is_connect, reply_markup=keyboard)

def recovery_data():
    print("🔄 Recovery başlatıldı... (şimdilik sadece test için çalışıyor)")

if __name__ == "__main__":
    recovery_data()
    bot.polling(none_stop=True)