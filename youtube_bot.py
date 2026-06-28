import os
import re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytube import YouTube

BOT_TOKEN = "8935027291:AAGRZOKKwoAYTVGzH2LfrtY4oSHlhsqEdbk"
bot = telebot.TeleBot(BOT_TOKEN)

TEMP_FOLDER = "downloads"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]{11})',
        r'(?:youtu\.be\/)([\w-]{11})',
        r'(?:youtube\.com\/shorts\/)([\w-]{11})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🎬 Отправь ссылку на YouTube (без кук!)")

@bot.message_handler(func=lambda m: True)
def handle_link(msg):
    url = msg.text.strip()
    vid = extract_video_id(url)
    
    if not vid:
        bot.reply_to(msg, "❌ Это не ссылка YouTube.")
        return
    
    try:
        # Получаем информацию о видео
        yt = YouTube(url)
        title = re.sub(r'[\\/*?:"<>|]', '', yt.title)
        
        # Кнопки
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📹 360p", callback_data=f"360|{url}"),
            InlineKeyboardButton("📹 720p", callback_data=f"720|{url}")
        )
        markup.add(
            InlineKeyboardButton("📹 1080p", callback_data=f"1080|{url}"),
            InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}")
        )
        
        bot.reply_to(msg, f"🎬 <b>{title}</b>\n\nВыбери качество:", parse_mode='HTML', reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(msg, f"❌ Ошибка: {str(e)[:200]}")

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    parts = call.data.split('|')
    quality = parts[0]
    url = parts[1]
    
    bot.answer_callback_query(call.id, "⏳ Загрузка...")
    bot.edit_message_text(
        f"⏳ Загружаю {quality}...",
        call.message.chat.id,
        call.message.message_id
    )
    
    try:
        yt = YouTube(url)
        
        if quality == 'mp3':
            # Скачиваем аудио
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                bot.send_message(call.message.chat.id, "❌ Нет аудио")
                return
            file_path = stream.download(output_path=TEMP_FOLDER)
            
            # Переименовываем в MP3
            base, ext = os.path.splitext(file_path)
            new_path = base + '.mp3'
            os.rename(file_path, new_path)
            
            with open(new_path, 'rb') as f:
                bot.send_audio(call.message.chat.id, f, caption="🎵 Аудио")
            os.remove(new_path)
            
        else:
            # Скачиваем видео в нужном качестве
            resolution_map = {
                '360': '360p',
                '720': '720p',
                '1080': '1080p'
            }
            target_res = resolution_map.get(quality, '720p')
            
            # Пробуем найти progressive stream (видео+аудио)
            stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=target_res).first()
            
            # Если нет — берём адаптивный (только видео) и скачиваем отдельно аудио
            if not stream:
                stream = yt.streams.filter(adaptive=True, file_extension='mp4', resolution=target_res).first()
                if stream:
                    # Скачиваем видео
                    video_path = stream.download(output_path=TEMP_FOLDER, filename_prefix='video_')
                    # Скачиваем аудио
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    if audio_stream:
                        audio_path = audio_stream.download(output_path=TEMP_FOLDER, filename_prefix='audio_')
                        # Склеиваем видео и аудио (нужен ffmpeg)
                        # Если ffmpeg нет — отправляем только видео
                        try:
                            import subprocess
                            output_path = os.path.join(TEMP_FOLDER, f"{yt.title}.mp4")
                            subprocess.run([
                                'ffmpeg', '-i', video_path, '-i', audio_path,
                                '-c:v', 'copy', '-c:a', 'aac', output_path
                            ], check=True)
                            os.remove(video_path)
                            os.remove(audio_path)
                            with open(output_path, 'rb') as f:
                                bot.send_video(call.message.chat.id, f, caption=f"🎬 {quality}")
                            os.remove(output_path)
                            bot.delete_message(call.message.chat.id, call.message.message_id)
                            return
                        except:
                            # Если ffmpeg нет — отправляем только видео без звука
                            with open(video_path, 'rb') as f:
                                bot.send_video(call.message.chat.id, f, caption=f"🎬 {quality} (без звука)")
                            os.remove(video_path)
                            if audio_path and os.path.exists(audio_path):
                                os.remove(audio_path)
                            bot.delete_message(call.message.chat.id, call.message.message_id)
                            return
            
            if stream:
                file_path = stream.download(output_path=TEMP_FOLDER)
                with open(file_path, 'rb') as f:
                    bot.send_video(call.message.chat.id, f, caption=f"🎬 {quality}")
                os.remove(file_path)
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.send_message(call.message.chat.id, f"❌ Нет качества {quality}")
        
    except Exception as e:
        error_text = str(e)
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {error_text[:300]}")
        
        # Чистка временных файлов
        for f in os.listdir(TEMP_FOLDER):
            try:
                os.remove(os.path.join(TEMP_FOLDER, f))
            except:
                pass

if __name__ == "__main__":
    print("🚀 Бот на pytube запущен!")
    bot.infinity_polling()
