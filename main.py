import telebot
import yt_dlp
import os
from telebot import types

TOKEN = "YOUR_BOT_TOKEN"  # Bu yerga token yozing
bot = telebot.TeleBot(TOKEN)

# URL vaqtincha saqlash uchun
user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Menga YouTube yoki Instagram link yuboring.")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    chat_id = message.chat.id

    if url.startswith("http"):
        user_links[chat_id] = url

        # Tugmalar yaratamiz
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🎬 Video (MP4)")
        btn2 = types.KeyboardButton("🎵 Musiqa (MP3)")
        markup.add(btn1, btn2)

        bot.send_message(chat_id, "Nimani yuklamoqchisiz?", reply_markup=markup)

    elif message.text == "🎬 Video (MP4)":
        if chat_id in user_links:
            download_video(chat_id, user_links[chat_id])
    elif message.text == "🎵 Musiqa (MP3)":
        if chat_id in user_links:
            download_audio(chat_id, user_links[chat_id])
    else:
        bot.reply_to(message, "Menga YouTube yoki Instagram link yuboring.")

def download_video(chat_id, url):
    bot.send_message(chat_id, "🎬 Video yuklanmoqda...")

    opts = {
        'format': 'mp4',
        'outtmpl': 'video.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as vid:
                bot.send_video(chat_id, vid)
            os.remove("video.mp4")

    except Exception as e:
        bot.send_message(chat_id, f"Xatolik: {e}")

def download_audio(chat_id, url):
    bot.send_message(chat_id, "🎵 Musiqa yuklanmoqda...")

    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as aud:
                bot.send_audio(chat_id, aud)
            os.remove("audio.mp3")

    except Exception as e:
        bot.send_message(chat_id, f"Xatolik: {e}")

bot.polling()
