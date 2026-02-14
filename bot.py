import telebot
import requests
import time
import io
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- Configuration & Auth ---
API_TOKEN = '8593186812:AAFdVDpxVkeyGtDFUVnVfZ6eThdcSDEJdRM'
SUPABASE_URL = "https://vwmhbpgwhfwuwtattset.supabase.co/functions/v1"
# Animation URL
LOADING_GIF = "https://hostingchecker.com/wp-content/uploads/2020/06/server.webp"

HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6ImYyZTIyZWFhLTRhYjQtNDZhOC1hYzM3LTExYzA3YWQyNTgzNCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Z3bWhicGd3aGZ3dXd0YXR0c2V0LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI3YTRmMDliYy0wYmRlLTRlM2UtYTMyMi01YzhmMzM3N2YzZTMiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzcxMDQ0NzUxLCJpYXQiOjE3NzEwNDExNTEsImVtYWlsIjoiY2F0YWx5c3RtbUBnYW1pbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiY2F0YWx5c3RtbUBnYW1pbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiY2F0YWx5c3QiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6IjdhNGYwOWJjLTBiZGUtNGUzZS1hMzIyLTVjOGYzMzc3ZjNlMyJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzcxMDQxMTUxfV0sInNlc3Npb25faWQiOiI4ZGU2MGU5YS1kMTJmLTQ1MmItYWYyMi0yZGZlNDFkOGM3NzEiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.zk8qIenE0nLxuvs-WUMiHmiK49iQbLjHg5U15bG_32NJZbjLWlTrtSKYL39xrECbm4GViSRICWaP4GJCek02AQ",
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3bWhicGd3aGZ3dXd0YXR0c2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjczMjc0NjYsImV4cCI6MjA4MjkwMzQ2Nn0.LSMD2P4whDzoIW4UCig0ly0j6UOxd5fHhIkUhywnmrg",
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.132 Mobile Safari/537.36"
}

bot = telebot.TeleBot(API_TOKEN, threaded=True)
app = Flask(__name__)

@app.route('/')
def index():
    return "PROXIES FETCHER ⚡ IS ALIVE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_get = types.InlineKeyboardButton("🌐 Get Elite IP", callback_data="get_ip_start")
    btn_dev = types.InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/dev2dex")
    markup.add(btn_get, btn_dev)
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        "⚡ *PROXIES FETCHER ⚡*\n\n"
        "Bhai, system online hai! Niche diye gaye button se proxies nikalna shuru karo.\n\n"
        "✨ *Developer:* @dev2dex"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "get_ip_start")
def ask_amount(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "🔢 *How many proxies do you need?*\n(Minimum 1, Maximum 5000)")
    bot.register_next_step_handler(msg, process_harvesting)

def process_harvesting(message):
    try:
        qty = int(message.text)
        if not (1 <= qty <= 5000): raise ValueError
    except:
        bot.reply_to(message, "❌ *Galat number hai bhai!* 1 se 5000 ke beech mein dalo.")
        return

    # Using send_animation with the direct URL
    status_msg = bot.send_animation(
        message.chat.id, 
        animation=LOADING_GIF, 
        caption=f"🛰 *Engine Active:* Searching for `{qty}` online proxies..."
    )

    valid_proxies = []
    attempt = 0
    while len(valid_proxies) < qty and attempt < 25:
        attempt += 1
        try:
            bot.edit_message_caption(
                caption=f"🧪 *Testing Batch:* `{attempt}`\nFound: `{len(valid_proxies)}/{qty}` proxies...",
                chat_id=message.chat.id, message_id=status_msg.message_id
            )
            
            f_resp = requests.get(f"{SUPABASE_URL}/fetch-proxies", headers=HEADERS, timeout=20)
            raw_data = f_resp.json().get('proxies', [])
            if not raw_data: continue

            t_resp = requests.post(
                f"{SUPABASE_URL}/test-proxy", headers=HEADERS, 
                json={"proxies": raw_data[:100]}, timeout=60
            )
            
            for p in t_resp.json().get('results', []):
                if p.get('status') == 'Online' and len(valid_proxies) < qty:
                    valid_proxies.append(f"{p['ip']}:{p['port']}")
            
            time.sleep(1)
        except Exception as e:
            print(f"Loop Error: {e}")
            break

    bot.delete_message(message.chat.id, status_msg.message_id)

    if valid_proxies:
        proxy_str = "\n".join(valid_proxies)
        
        # --- Logic: If quantity < 100, send as message. Else, send as file ---
        if len(valid_proxies) < 100:
            result_msg = (
                f"✅ *Done!* Found `{len(valid_proxies)}` proxies:\n\n"
                f"`{proxy_str}`\n\n"
                f"🛡 *Developer:* @dev2dex"
            )
            bot.send_message(message.chat.id, result_msg, parse_mode="Markdown")
        else:
            file = io.BytesIO(proxy_str.encode())
            file.name = f"{len(valid_proxies)}proxys.txt"
            bot.send_document(
                message.chat.id, 
                file, 
                caption=f"✅ *Done!* Found `{len(valid_proxies)}` proxies.\n\n🛡 *Developer:* @dev2dex", 
                parse_mode="Markdown"
            )
    else:
        bot.send_message(message.chat.id, "❌ *Error:* Proxies nahi mil payin. Thodi der baad try karo.")

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("PROXIES FETCHER IS LIVE ⚡")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Bot Polling Error: {e}")
            time.sleep(5)
