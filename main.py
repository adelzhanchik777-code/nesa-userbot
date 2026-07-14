import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- Обманка портов для Render ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), WebServerHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Настройки Telegram ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
RAW_SESSION = os.environ.get("SESSION_STRING")

if not all([API_ID, API_HASH, RAW_SESSION]):
    print("Ошибка: API_ID, API_HASH или SESSION_STRING не заданы в Render!")
    exit(1)

# Автоматически очищаем строку сессии от переносов строк, пробелов и мусора
SESSION_STRING = "".join(RAW_SESSION.split())

client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)

# --- Логика работы с Llama ---
def ask_llama(prompt):
    url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Content-Type": "application/json"}
    payload = {
        "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nТы — Нэса, дерзкий и умный ИИ-ассистент. Отвечай кратко, чётко, на русском языке.<|eot_id|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n",
        "parameters": {"max_new_tokens": 250, "temperature": 0.7}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            result = data[0]["generated_text"].split("<|start_header_id|>assistant<|end_header_id|>\n")[-1]
            return result.strip()
        elif response.status_code == 503:
            return "Модель сейчас загружается на сервере Hugging Face, подожди пару секунд и повтори запрос."
        return f"Ошибка сервера Llama: статус {response.status_code}"
    except Exception as e:
        return f"Не удалось связаться с Llama: {str(e)}"

# --- Обработка команд в Telegram ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ии (.+)"))
async def ai_handler(event):
    question = event.pattern_match.group(1)
    await event.edit(f"**Нэса думает...** 🧠")
    
    # Запускаем запрос в отдельном потоке, чтобы Telegram не зависал
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, ask_llama, question)
    
    await event.edit(f"**Вопрос:** {question}\n\n**Ответ Нэсы:**\n{answer}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping"))
async def ping_handler(event):
    await event.edit("**Юзербот Нэса успешно работает, Llama на связи!**")

async def main():
    print("Нэса подключается к Telegram...")
    await client.start()
    print("Юзербот запущен и готов к работе!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
