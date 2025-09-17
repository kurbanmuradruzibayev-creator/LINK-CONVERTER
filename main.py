import os
import telebot
from dotenv import load_dotenv
import yt_dlp
from youtube_search import YoutubeSearch

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

# Musiqa yuklab olish va konvertatsiya qilish
def download_and_convert(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,  # 50 MB chegarasi
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            filename = f"{title}.mp3"
            return filename
        except Exception as e:
            raise ValueError(f"Yuklab olishda xato: {e}")

# YouTube'da qo'shiq qidirish
def search_youtube(query):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video_id = results[0]['id']
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            return None
    except Exception as e:
        raise ValueError(f"Qidiruvda xato: {e}")

# /start komandasiga javob
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "Salom! Men YouTube'dan qo'shiq yoki qo'shiqchi nomi orqali musiqa topuvchi botman. 😊\n\n"
                 "Qo'shiq yoki qo'shiqchi nomini yuboring:\n"
                 "Masalan: 'Billie Eilish Bad Guy' yoki 'Ozodbek Nazarbekov'\n\n"
                 "Men eng mos keluvchi musiqani topib, MP3 formatida yuboraman!")

# Musiqa qidiruv handler
@bot.message_handler(func=lambda message: True)
def handle_music(message):
    query = message.text.strip()
    if not query:
        bot.reply_to(message, "Iltimos, qo'shiq yoki qo'shiqchi nomini yuboring!")
        return
    
    try:
        bot.reply_to(message, "Musiqa qidirilmoqda... 🔍")
        # YouTube'da qidiruv
        video_url = search_youtube(query)
        if not video_url:
            bot.reply_to(message, "Afsus, hech qanday musiqa topilmadi. Boshqa nom bilan sinab ko'ring!")
            return
        
        bot.reply_to(message, "Musiqa yuklanmoqda... ⏳")
        filename = download_and_convert(video_url)
        with open(filename, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file, caption=f"Musiqa yuklandi: {filename}")
        os.remove(filename)  # Faylni o'chirish
    except Exception as e:
        bot.reply_to(message, f"Xato yuz berdi: {e}")

# Botni doimiy ravishda ishlatish
if __name__ == "__main__":
    bot.polling(none_stop=True)
