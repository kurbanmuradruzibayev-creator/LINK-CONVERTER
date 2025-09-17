import telebot
import yt_dlp
import os

TOKEN = "YOUR_BOT_TOKEN"  # Bu yerga bot tokeningizni yozing
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Menga YouTube yoki Instagram link yuboring.\n"
                          "Men uni video (MP4) yoki musiqa (MP3) qilib qaytaraman.")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    bot.reply_to(message, "Yuklanmoqda...")

    # Yuklab olish opsiyalari (video uchun)
    video_opts = {
        'format': 'mp4',
        'outtmpl': 'video.%(ext)s'
    }

    try:
        # Video yuklab olish
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])

        # Video jo‘natish
        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as vid:
                bot.send_video(message.chat.id, vid)

        # Audio yuklab olish
        audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        # Audio jo‘natish
        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as aud:
                bot.send_audio(message.chat.id, aud)

        # Fayllarni tozalash
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")
        if os.path.exists("audio.mp3"):
            os.remove("audio.mp3")

    except Exception as e:
        bot.reply_to(message, f"Xatolik: {e}")

bot.polling()
