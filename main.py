import os
import sys
from telethon import TelegramClient, events

# Получаем настройки из переменных окружения Render
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not API_ID or not API_HASH or not SESSION_STRING:
    print("Ошибка: Переменные API_ID, API_HASH или SESSION_STRING не заданы в Render!")
    sys.exit(1)

# Подключаем сессию юзербота
from telethon.sessions import StringSession
client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.пинг'))
async def ping(event):
    await event.edit("**Юзербот Нэса успешно запущен на Render!.**")

print("Юзербот запускается...")
client.start()
client.run_until_disconnected()
