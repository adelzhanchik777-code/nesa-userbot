import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- Обманка для Render (запуск фейкового веб-сервера) ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), WebServerHandler)
    print(f"Фейковый веб-сервер запущен на порту {port}")
    server.serve_forever()

# Запускаем сервер в отдельном потоке, чтобы он не мешал боту
threading.Thread(target=run_web_server, daemon=True).start()
# --------------------------------------------------------

# Получаем данные из настроек Render
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

if not all([API_ID, API_HASH, SESSION_STRING]):
    print("Ошибка: Переменные API_ID, API_HASH или SESSION_STRING не заданы в Render!")
    exit(1)

client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)

async def main():
    print("Нэса успешно подключается к Telegram...")
    await client.start()
    print("Юзербот запущен и готов к работе!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
    
