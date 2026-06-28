import os
import re
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import subprocess

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = "8935027291:AAGRZOKKwoAYTVGzH2LfrtY4oSHlhsqEdbk"
bot = telebot.TeleBot(BOT_TOKEN)

TEMP_FOLDER = "downloads"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

storage = {}

# === ПРОВЕРКА FFMPEG ===
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False

# === ФУНКЦИЯ ИЗВЛЕЧЕНИЯ ID ===
def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]{11})',
        r'(?:youtu\.be\/)([\w-]{11})',
        r'(?:youtube\.com\/embed\/)([\w-]{11})',
        r'(?:youtube\.com\/shorts\/)([\w-]{11})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

# === УЛУЧШЕННАЯ ЗАГРУЗКА С ДИАГНОСТИКОЙ ===
def download_with_ytdlp(url, output_path, format_type='video', quality='720'):
    """
    Скачивает видео/аудио с YouTube.
    Возвращает: (путь_к_файлу, название, сообщение_об_ошибке)
    """
    
    # Проверяем FFmpeg
    if not check_ffmpeg():
        return None, None, "❌ FFmpeg не установлен! Установите FFmpeg для работы бота."
    
    # Базовые опции
    base_opts = {
        'quiet': False,  # Включаем вывод для отладки
        'no_warnings': False,
        'verbose': True,  # Подробный лог
        'no_check_certificate': True,
        'ignoreerrors': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
        }
    }
    
    # Настраиваем в зависимости от типа
    if format_type == 'audio':
        opts = {
            **base_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }
    else:
        # Для видео пробуем разные варианты
        quality_formats = {
            '360': ['bestvideo[height<=360]+bestaudio/best[height<=360]', 'best[height<=360]', 'best'],
            '720': ['bestvideo[height<=720]+bestaudio/best[height<=720]', 'best[height<=720]', 'best'],
            '1080': ['bestvideo[height<=1080]+bestaudio/best[height<=1080]', 'best[height<=1080]', 'best']
        }
        
        formats_to_try = quality_formats.get(quality, ['best'])
        
        last_error = None
        for fmt in formats_to_try:
            try:
                opts = {
                    **base_opts,
                    'format': fmt,
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }]
                }
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = re.sub(r'[\\/*?:"<>|]', '', info.get('title', 'video'))
                    
                    # Ищем скачанный файл
                    for f in os.listdir(output_path):
                        if title in f or (info.get('id') and info.get('id') in f):
                            full_path = os.path.join(output_path, f)
                            if os.path.isfile(full_path) and time.time() - os.path.getctime(full_path) < 300:
                                return full_path, title, None
                    
                    # Если не нашли по названию
                    files = [os.path.join(output_path, f) for f in os.listdir(output_path) 
                            if os.path.isfile(os.path.join(output_path, f))]
                    if files:
                        latest = max(files, key=os.path.getctime)
                        if time.time() - os.path.getctime(latest) < 300:
                            return latest, title, None
                    
                    return None, title, "Файл не найден после загрузки"
                    
            except Exception as e:
                last_error = str(e)
                print(f"Попытка с форматом {fmt} не удалась: {last_error}")
                continue
        
        return None, None, f"Не удалось скачать видео: {last_error}"
    
    # Для аудио
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = re.sub(r'[\\/*?:"<>|]', '', info.get('title', 'video'))
            
            # Ищем файл
            for f in os.listdir(output_path):
                if title in f or (info.get('id') and info.get('id') in f):
                    full_path = os.path.join(output_path, f)
                    if os.path.isfile(full_path) and time.time() - os.path.getctime(full_path) < 300:
                        return full_path, title, None
            
            files = [os.path.join(output_path, f) for f in os.listdir(output_path) 
                    if os.path.isfile(os.path.join(output_path, f))]
            if files:
                latest = max(files, key=os.path.getctime)
                if time.time() - os.path.getctime(latest) < 300:
                    return latest, title, None
            
            return None, title, "Файл не найден после загрузки"
            
    except Exception as e:
        return None, None, f"Ошибка загрузки аудио: {str(e)}"

# === ОЧИСТКА СТАРЫХ ДАННЫХ ===
def cleanup_storage():
    current_time = time.time()
    to_delete = []
    for key, value in storage.items():
        if 'timestamp' in value and current_time - value['timestamp'] > 600:
            to_delete.append(key)
    for key in to_delete:
        del storage[key]

# === ОБРАБОТЧИКИ ===
@bot.message_handler(commands=['start'])
def start(msg):
    ffmpeg_status = "✅ Установлен" if check_ffmpeg() else "❌ НЕ УСТАНОВЛЕН!"
    bot.reply_to(msg, 
        f"🎬 YouTube Downloader Bot\n\n"
        f"Отправь ссылку на YouTube.\n"
        f"FFmpeg: {ffmpeg_status}\n\n"
        f"Если бот не работает, установи FFmpeg!"
    )

@bot.message_handler(func=lambda m: True)
def handle_link(msg):
    cleanup_storage()
    
    url = msg.text.strip()
    vid = extract_video_id(url)
    
    if not vid:
        bot.reply_to(msg, "❌ Это не ссылка YouTube.")
        return
    
    try:
        # Проверяем доступность
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = re.sub(r'[\\/*?:"<>|]', '', info.get('title', 'Видео'))
            
            key = f"{vid}_{msg.chat.id}_{int(time.time())}"
            storage[key] = {
                'url': url,
                'title': title,
                'timestamp': time.time()
            }
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("📹 360p", callback_data=f"v|360|{key}"),
                InlineKeyboardButton("📹 720p", callback_data=f"v|720|{key}")
            )
            markup.add(
                InlineKeyboardButton("📹 1080p", callback_data=f"v|1080|{key}"),
                InlineKeyboardButton("🎵 MP3", callback_data=f"a|{key}")
            )
            
            bot.reply_to(msg, 
                f"🎬 <b>{title}</b>\n\nВыбери качество:",
                parse_mode='HTML',
                reply_markup=markup
            )
    except Exception as e:
        bot.reply_to(msg, f"❌ Ошибка: {str(e)[:300]}")

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    cleanup_storage()
    
    parts = call.data.split('|')
    action = parts[0]
    key = parts[-1]
    
    data = storage.get(key)
    if not data:
        bot.answer_callback_query(call.id, "❌ Данные устарели.")
        bot.edit_message_text(
            "⏳ Отправь ссылку заново.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    url = data['url']
    title = data['title']
    del storage[key]
    
    bot.answer_callback_query(call.id, "⏳ Загрузка...")
    bot.edit_message_text(
        f"⏳ Загружаю <b>{title}</b>...\nЭто может занять до 2 минут.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML'
    )
    
    try:
        format_type = 'audio' if action == 'a' else 'video'
        quality = parts[2] if action == 'v' else '720'
        
        # Скачиваем с диагностикой
        file_path, downloaded_title, error_msg = download_with_ytdlp(
            url, TEMP_FOLDER, format_type, quality
        )
        
        if error_msg:
            bot.send_message(
                call.message.chat.id,
                f"❌ Ошибка загрузки:\n<code>{error_msg[:500]}</code>\n\n"
                f"💡 Решения:\n"
                f"1. Установи FFmpeg (см. /start)\n"
                f"2. Проверь ссылку\n"
                f"3. Попробуй другое качество\n"
                f"4. Включи VPN (если YouTube заблокирован)",
                parse_mode='HTML'
            )
            return
        
        if not file_path or not os.path.exists(file_path):
            bot.send_message(call.message.chat.id, "❌ Файл не создан. Попробуй другое качество.")
            return
        
        # Проверяем размер
        size_mb = get_file_size_mb(file_path)
        if size_mb > 50:
            bot.send_message(
                call.message.chat.id,
                f"⚠️ Файл {size_mb:.1f} МБ (>50 МБ). Выбери качество ниже."
            )
            os.remove(file_path)
            return
        
        # Отправляем
        with open(file_path, 'rb') as f:
            if action == 'a':
                bot.send_audio(
                    call.message.chat.id,
                    f,
                    caption=f"🎵 {downloaded_title or title}",
                    title=downloaded_title or title
                )
            else:
                bot.send_video(
                    call.message.chat.id,
                    f,
                    caption=f"🎬 {downloaded_title or title}",
                    supports_streaming=True
                )
        
        os.remove(file_path)
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
            
    except Exception as e:
        error_text = str(e)
        bot.send_message(
            call.message.chat.id,
            f"❌ Критическая ошибка:\n<code>{error_text[:500]}</code>",
            parse_mode='HTML'
        )
        
        # Чистка
        for f in os.listdir(TEMP_FOLDER):
            if title in f or '.mp4' in f or '.mp3' in f:
                try:
                    os.remove(os.path.join(TEMP_FOLDER, f))
                except:
                    pass

# === ЗАПУСК ===
if __name__ == "__main__":
    print("🚀 Бот запущен")
    print(f"✅ FFmpeg: {'Установлен' if check_ffmpeg() else 'НЕ УСТАНОВЛЕН!'}")
    print(f"✅ Папка: {TEMP_FOLDER}")
    bot.infinity_polling()
