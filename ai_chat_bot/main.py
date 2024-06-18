from telethon import TelegramClient
import os
from openai import AsyncOpenAI
from handlers.bot import Bot
from handlers.client import Client

CHAT_GPT_ENV_KEY = 'CHATBOT_CHAT_GPT'
TELEGRAM_ENV_KEY = 'CHATBOT_TELEGRAM'
APP_ID_ENV_KEY = 'CHATBOT_APP_ID'
APP_HASH_ENV_KEY = 'CHATBOT_APP_HASH'

SHOW_BOT_MESSAGE = False

ai_client = AsyncOpenAI(api_key=os.getenv(CHAT_GPT_ENV_KEY))
telegram_bot = TelegramClient("bot_session", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY))
telegram_client = TelegramClient("my_account", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY), device_model='Python Client Desktop', system_version ='Windows 10').start()

if __name__ == '__main__':
    telegram_client.start()
    telegram_bot.start(bot_token=os.getenv(TELEGRAM_ENV_KEY))

    client = Client(telegram_client, telegram_bot, ai_client, SHOW_BOT_MESSAGE)
    client.register_handlers()

    bot = Bot(telegram_bot, client)
    bot.register_handlers()

    telegram_bot.run_until_disconnected()
    telegram_client.run_until_disconnected()