import os
import re
import time
import telebot
import tempfile
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# ==================================================
# 1. ВСТАВЬ СВОИ КУКИ В ПЕРЕМЕННУЮ НИЖЕ
# ==================================================
COOKIES_STRING = """# Netscape HTTP Cookie File
[# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1798149841	VISITOR_INFO1_LIVE	MU0Lzr6KuLo
.youtube.com	TRUE	/	TRUE	1798149841	VISITOR_PRIVACY_METADATA	CgJSVRIEGgAgMw%3D%3D
.youtube.com	TRUE	/	FALSE	1816565473	HSID	ABdJsO3jb2U2z8vCu
.youtube.com	TRUE	/	TRUE	1816565473	SSID	AjEz-RS53LYKubnGd
.youtube.com	TRUE	/	FALSE	1816565473	APISID	D77dFzfSuNJBjJIe/AF6IT_iyHSpd6jLx7
.youtube.com	TRUE	/	TRUE	1816565473	SAPISID	mwgVH0_i7f0imNcz/A4fAYDzHM1jqJfTrn
.youtube.com	TRUE	/	TRUE	1816565473	__Secure-1PAPISID	mwgVH0_i7f0imNcz/A4fAYDzHM1jqJfTrn
.youtube.com	TRUE	/	TRUE	1816565473	__Secure-3PAPISID	mwgVH0_i7f0imNcz/A4fAYDzHM1jqJfTrn
.youtube.com	TRUE	/	FALSE	1816565475	SID	g.a000_Qi_Tqr7e1MtTjwHtKvm7hmGIBL9okFKS-ewaNVCEfpPqsr34HTdL4tpWtIA6Hlm4McOeQACgYKAVASARUSFQHGX2MiQlmK0VSvDVnuPi4Yl8pBUhoVAUF8yKrLZmSHz6_eQ_i1_6whszi40076
.youtube.com	TRUE	/	TRUE	1816565475	__Secure-1PSID	g.a000_Qi_Tqr7e1MtTjwHtKvm7hmGIBL9okFKS-ewaNVCEfpPqsr3gwQe7pLRB2aULMMMma-A4gACgYKAe0SARUSFQHGX2MiEb2-iS6XL2R-4E_tOOUCyBoVAUF8yKqmxcO4r8DxxC56p4dbDict0076
.youtube.com	TRUE	/	TRUE	1816565475	__Secure-3PSID	g.a000_Qi_Tqr7e1MtTjwHtKvm7hmGIBL9okFKS-ewaNVCEfpPqsr3L_CrWTvKyjbslcDodyXuSQACgYKATYSARUSFQHGX2Mi8iLnS-1HxNGvwVm8p8y24hoVAUF8yKrf8NKM7YmgLWaSkh3oljO60076
.youtube.com	TRUE	/	TRUE	1816688031	LOGIN_INFO	AFmmF2swRQIhAOAfT8A6MOOoouK71BOe28FeEewJFC_W506V0kZS5SscAiA1RVMQ1VsEmj5UvL7luCxQi9iXvQrZhJAOmO90Mipc7w:QUQ3MjNmd1dGZXp0UzYzOTFEbkp6QWVZRHlydVBvVmNEZmJlU0FBcXdzcU9mZVBScS15X04yT1gwLW9rbS1vSnNBY2s3OGh2SEhxaGNoRXhnWmxqVm9iQXhYbVRYTjFYU1BqUjZQMlgxNnh0Y0NOVEowLXRpQnVsWVVxSmRhZnlkSGFhSm1JQVFJZG54Wk4zVGRfOUw2RENDUi1QV2ktZFRR
.youtube.com	TRUE	/	TRUE	1817226683	PREF	f6=40000000&tz=Europe.Moscow&f7=100&f5=30000
.youtube.com	TRUE	/	TRUE	1798148335	__Secure-YNID	19.YT=DIZdgrsD1BvDhG9_sim3gGKJFhNN8QT-8_S-rauRB--CWq-5rFcgHIOv9PTIxgbWmzIrw286L_ahlKdUBcmTuozxIZqzDHsdc5hcGdkYXswK6EBFzVdWTl3cwICAh3RRRksdaIUiU-E2DMijcWcqL6L6fdOVFlPFdHh9GWLL3B1IxqNqv5badlgrPYb5Fv2fVvrk9L5AvfPJ_3v9RwH-FEs7Mv-gQepeNMviBpG4yO0OHUodERL-taFm6eEtIFrTgDfMrD-Q1v0Np1Qhpk1QTouyaltysQ3v7teKywG_6sKdxhDKXWOMEkdAUpU7O30s42HVuycs5PjG0EoZNG3eGA
.youtube.com	TRUE	/	TRUE	1814202681	__Secure-1PSIDTS	sidts-CjYByojQU55mpozVnvNs0YHjeMn7DdW9jd_gfvKC3ua7tW8U7I1uBwy-tprLW-r-VVY_zsjNHgEQAA
.youtube.com	TRUE	/	TRUE	1782667281	__Secure-1PSIDRTS	sidts-CjYByojQU55mpozVnvNs0YHjeMn7DdW9jd_gfvKC3ua7tW8U7I1uBwy-tprLW-r-VVY_zsjNHgEQAA
.youtube.com	TRUE	/	TRUE	1814202681	__Secure-3PSIDTS	sidts-CjYByojQU55mpozVnvNs0YHjeMn7DdW9jd_gfvKC3ua7tW8U7I1uBwy-tprLW-r-VVY_zsjNHgEQAA
.youtube.com	TRUE	/	TRUE	1782667281	__Secure-3PSIDRTS	sidts-CjYByojQU55mpozVnvNs0YHjeMn7DdW9jd_gfvKC3ua7tW8U7I1uBwy-tprLW-r-VVY_zsjNHgEQAA
.youtube.com	TRUE	/	FALSE	1782666688	ST-tladcw	session_logininfo=AFmmF2swRQIhAOAfT8A6MOOoouK71BOe28FeEewJFC_W506V0kZS5SscAiA1RVMQ1VsEmj5UvL7luCxQi9iXvQrZhJAOmO90Mipc7w%3AQUQ3MjNmd1dGZXp0UzYzOTFEbkp6QWVZRHlydVBvVmNEZmJlU0FBcXdzcU9mZVBScS15X04yT1gwLW9rbS1vSnNBY2s3OGh2SEhxaGNoRXhnWmxqVm9iQXhYbVRYTjFYU1BqUjZQMlgxNnh0Y0NOVEowLXRpQnVsWVVxSmRhZnlkSGFhSm1JQVFJZG54Wk4zVGRfOUw2RENDUi1QV2ktZFRR
.youtube.com	TRUE	/	FALSE	1782666688	ST-xuwub9	session_logininfo=AFmmF2swRQIhAOAfT8A6MOOoouK71BOe28FeEewJFC_W506V0kZS5SscAiA1RVMQ1VsEmj5UvL7luCxQi9iXvQrZhJAOmO90Mipc7w%3AQUQ3MjNmd1dGZXp0UzYzOTFEbkp6QWVZRHlydVBvVmNEZmJlU0FBcXdzcU9mZVBScS15X04yT1gwLW9rbS1vSnNBY2s3OGh2SEhxaGNoRXhnWmxqVm9iQXhYbVRYTjFYU1BqUjZQMlgxNnh0Y0NOVEowLXRpQnVsWVVxSmRhZnlkSGFhSm1JQVFJZG54Wk4zVGRfOUw2RENDUi1QV2ktZFRR
.youtube.com	TRUE	/	FALSE	1782666691	ST-3opvp5	session_logininfo=AFmmF2swRQIhAOAfT8A6MOOoouK71BOe28FeEewJFC_W506V0kZS5SscAiA1RVMQ1VsEmj5UvL7luCxQi9iXvQrZhJAOmO90Mipc7w%3AQUQ3MjNmd1dGZXp0UzYzOTFEbkp6QWVZRHlydVBvVmNEZmJlU0FBcXdzcU9mZVBScS15X04yT1gwLW9rbS1vSnNBY2s3OGh2SEhxaGNoRXhnWmxqVm9iQXhYbVRYTjFYU1BqUjZQMlgxNnh0Y0NOVEowLXRpQnVsWVVxSmRhZnlkSGFhSm1JQVFJZG54Wk4zVGRfOUw2RENDUi1QV2ktZFRR
.youtube.com	TRUE	/	FALSE	1814202687	SIDCC	AKEyXzVjABRa59oDSwODiZB0GfrEnKWbAHFs1HswSaL7zNJ0pZ9qlEacU0dkkpSbMQHjvAxt-A
.youtube.com	TRUE	/	TRUE	1814202687	__Secure-1PSIDCC	AKEyXzVBKp3wMaov4oUmJYpfuwIKgvHU_EFymQOXvAjeXBNPO7WxfnXU0VckVurw2g85uh0dgX8
.youtube.com	TRUE	/	TRUE	1814202687	__Secure-3PSIDCC	AKEyXzVcZthXXpQ4ZzQqLHLARA1BRI_rYWprkoHcE4veN_dBFUPc4TMkpOyTdQI3PuDEKr1GNg
.youtube.com	TRUE	/	TRUE	1798218681	VISITOR_INFO1_LIVE	MU0Lzr6KuLo
.youtube.com	TRUE	/	TRUE	1798218681	VISITOR_PRIVACY_METADATA	CgJSVRIEGgAgMw%3D%3D
.youtube.com	TRUE	/	TRUE	1798115412	__Secure-YNID	19.YT=dw0dlB39NQfcDF1h9KdLxzXoVAFIGwp_xLKNSMwHZ3dIppKc8FModrJauDLdVd9U34YtXqd4Vm9n85ZV9k_kj6XWw-nZZj6Q7tt1A2uHyl2BgjsuCQhZD8GLD9jpiJdhqh_gCcd6zmBtgsafqnxMJBJbAE-L2rDiU3zVHhZN1bBKA1mdhp2rXOl7D5pT2oFDmPtYeHQ2UVF_F_kkVAiH1n9YhQloVLTwTaKOO3Zo_Ui9ESEghKDqneBbfc_i658v_ACR5F0UdCxq9jkE_C2e-5F0cuQDPZttZo4JvKKkF4TQKqgylrcuwuwNW1ha3hv8XKhyN0gcfTTzNK5I_kKq9Q
.youtube.com	TRUE	/	TRUE	0	YSC	gv-PcuixNYg
.youtube.com	TRUE	/	TRUE	1798217825	__Secure-ROLLOUT_TOKEN	CMbloLfk3IHPzAEQms-m1oeUlQMYvNy02rOqlQM%3D]
"""
# ==================================================
def get_cookies_file():
    """Создаёт временный файл с куками и возвращает его путь"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(COOKIES_STRING)
            return f.name
    except Exception as e:
        print(f"Ошибка создания файла кук: {e}")
        return None
        
BOT_TOKEN = "8935027291:AAGRZOKKwoAYTVGzH2LfrtY4oSHlhsqEdbk"
bot = telebot.TeleBot(BOT_TOKEN)

TEMP_FOLDER = "downloads"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

storage = {}

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

def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🎬 YouTube Downloader Bot\n\nОтправь ссылку на YouTube")

@bot.message_handler(func=lambda m: True)
def handle_link(msg):
    url = msg.text.strip()
    vid = extract_video_id(url)
    
    if not vid:
        bot.reply_to(msg, "❌ Это не ссылка YouTube.")
        return
    
    try:
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
        bot.reply_to(msg, f"❌ Ошибка: {str(e)[:200]}")

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    parts = call.data.split('|')
    action = parts[0]
    key = parts[-1]
    
    data = storage.get(key)
    if not data:
        bot.answer_callback_query(call.id, "❌ Данные устарели.")
        return
    
    url = data['url']
    title = data['title']
    del storage[key]
    
    bot.answer_callback_query(call.id, "⏳ Загрузка...")
    bot.edit_message_text(
        f"⏳ Загружаю <b>{title}</b>...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML'
    )
    
    try:
        format_type = 'audio' if action == 'a' else 'video'
        quality = parts[2] if action == 'v' else '720'
        
        # ==================================================
        # 2. НАСТРОЙКИ YT-DLP С КУКАМИ (ОНИ ЗДЕСЬ)
        # ==================================================
        opts = {
            'quiet': True,
            'no_warnings': True,
            'no_check_certificate': True,
            'cookiefile': get_cookies_file(),  # <--- КУКИ ПОДСТАВЛЯЮТСЯ АВТОМАТИЧЕСКИ
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        # ==================================================
        
        if format_type == 'audio':
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(TEMP_FOLDER, '%(title)s.%(ext)s'),
            })
        else:
            quality_map = {
                '360': 'best[height<=360]',
                '720': 'best[height<=720]',
                '1080': 'best[height<=1080]'
            }
            opts.update({
                'format': quality_map.get(quality, 'best'),
                'outtmpl': os.path.join(TEMP_FOLDER, '%(title)s.%(ext)s'),
            })
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_title = re.sub(r'[\\/*?:"<>|]', '', info.get('title', 'video'))
            
            file_path = None
            for f in os.listdir(TEMP_FOLDER):
                if downloaded_title in f or (info.get('id') and info.get('id') in f):
                    full_path = os.path.join(TEMP_FOLDER, f)
                    if os.path.isfile(full_path):
                        file_path = full_path
                        break
            
            if not file_path:
                files = [os.path.join(TEMP_FOLDER, f) for f in os.listdir(TEMP_FOLDER) 
                        if os.path.isfile(os.path.join(TEMP_FOLDER, f))]
                if files:
                    file_path = max(files, key=os.path.getctime)
            
            if not file_path or not os.path.exists(file_path):
                bot.send_message(call.message.chat.id, "❌ Файл не найден.")
                return
            
            size_mb = get_file_size_mb(file_path)
            if size_mb > 50:
                bot.send_message(
                    call.message.chat.id,
                    f"⚠️ Файл {size_mb:.1f} МБ (>50 МБ). Выбери качество ниже."
                )
                os.remove(file_path)
                return
            
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
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {str(e)[:300]}")

if __name__ == "__main__":
    bot.remove_webhook()  # <--- ЭТА СТРОКА ДОБАВЛЕНА
    print("🚀 Бот запущен!")
    bot.infinity_polling()
