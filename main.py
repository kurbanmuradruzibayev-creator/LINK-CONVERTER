import os
import telebot
from telebot import types
from dotenv import load_dotenv
import yt_dlp
import re

# .env faylidan muhit o'zgaruvchilarini yuklash
load_dotenv()

# TELEGRAM_BOT_TOKEN ni muhit o'zgaruvchisidan olish
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Token mavjudligini va to'g'riligini tekshirish
if not TOKEN or ":" not in TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN noto'g'ri yoki o'rnatilmagan! Token shakli: '123456789:ABCDEF...' bo'lishi kerak.")

# Telegram botni ishga tushirish
try:
    bot = telebot.TeleBot(TOKEN)
    print("Bot muvaffaqiyatli ishga tushdi!")
except Exception as e:
    print(f"Botni ishga tushirishda xato: {e}")
    raise

# Instagram va YouTube linklarini tekshirish uchun regex
def is_valid_url(url):
    instagram_pattern = r'https?://(www\.)?instagram\.com/(p|reel)/[a-zA-Z0-9_-]+/?'
    youtube_pattern = r'https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+'
    return re.match(instagram_pattern, url) or re.match(youtube_pattern, url)

# Video yuklab olish va konvertatsiya qilish
def download_and_convert(url, format_type='video'):
    ydl_opts = {
        'format': 'best[height<=720]' if format_type == 'video' else 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if format_type == 'music' else [],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            if format_type == 'music':
                filename = f"{title}.mp3"
            else:
                filename = f"{title}.%(ext)s"
            return filename
        except Exception as e:
            raise ValueError(f"Yuklab olishda xato: {e}")

# /start komandasiga javob
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    video_btn = types.InlineKeyboardButton("Video yuklash", callback_data="video")
    music_btn = types.InlineKeyboardButton("Musiqa yuklash", callback_data="music")
    markup.add(video_btn, music_btn)
    
    bot.reply_to(message, 
                 "Salom! Men Instagram va YouTube'dan video yoki musiqa yuklab beruvchi botman. 😊\n\n"
                 "Link yuboring (Instagram post/reel yoki YouTube video):\n"
                 "Masalan: https://www.instagram.com/reel/ABC123/ yoki https://www.youtube.com/watch?v=XYZ\n\n"
                 "Qaysi turdagi yuklashni xohlaysiz?", 
                 reply_markup=markup)

# Callback query uchun handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "video":
        bot.edit_message_text("Video yuklash rejimida. Endi Instagram yoki YouTube linkini yuboring.", 
                              call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, handle_video)
    elif call.data == "music":
        bot.edit_message_text("Musiqa yuklash rejimida. Endi Instagram yoki YouTube linkini yuboring.", 
                              call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, handle_music)

# Video handler
def handle_video(message):
    url = message.text.strip()
    if not is_valid_url(url):
        bot.reply_to(message, "Noto'g'ri link! Instagram (post/reel) yoki YouTube linkini yuboring.")
        return
    
    try:
        bot.reply_to(message, "Video yuklanmoqda... ⏳")
        filename = download_and_convert(url, 'video')
        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption=f"Video yuklandi: {filename}")
        os.remove(filename)  # Faylni o'chirish
    except Exception as e:
        bot.reply_to(message, f"Xato yuz berdi: {e}")

# Music handler
def handle_music(message):
    url = message.text.strip()
    if not is_valid_url(url):
        bot.reply_to(message, "Noto'g'ri link! Instagram (post/reel) yoki YouTube linkini yuboring.")
        return
    
    try:
        bot.reply_to(message, "Musiqa yuklanmoqda... ⏳")
        filename = download_and_convert(url, 'music')
        with open(filename, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file, caption=f"Musiqa yuklandi: {filename}")
        os.remove(filename)  # Faylni o'chirish
    except Exception as e:
        bot.reply_to(message, f"Xato yuz berdi: {e}")

# Barcha matnli xabarlarga handler (agar /start bo'lmasa)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if is_valid_url(message.text):
        bot.reply_to(message, "Avval /start buyrug'ini yuboring va rejimni tanlang.")
    else:
        bot.reply_to(message, "Link yuboring yoki /start buyrug'ini ishlating.")

# Botni doimiy ravishda ishlatish
if __name__ == "__main__":
    bot.polling(none_stop=True)
