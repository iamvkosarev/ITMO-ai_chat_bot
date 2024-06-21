import os

from telethon import TelegramClient

from ai_chat_bot.handlers.llm_operator import LLMOperator
from ai_chat_bot.llm.chatgpt import OpenAIChatGPT
from ai_chat_bot.llm.llm import LLMType
from handlers.bot import Bot
from handlers.client import Client

CHAT_GPT_ENV_KEY = 'CHATBOT_CHAT_GPT'
TELEGRAM_ENV_KEY = 'CHATBOT_TELEGRAM'
APP_ID_ENV_KEY = 'CHATBOT_APP_ID'
APP_HASH_ENV_KEY = 'CHATBOT_APP_HASH'
START_PROMPT_PREFIX = 'Ответь на сообщение, но не больше 100 слов, однако пиши, много, когда можно ответить кратко:\n'

SHOW_BOT_MESSAGE = False

if __name__ == '__main__':
    telegram_bot = TelegramClient("bot_session", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY))
    telegram_client = TelegramClient("my_account", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY),
                                     device_model='Python Client Desktop', system_version='Windows 10').start()

    llm_chatgpt = OpenAIChatGPT(os.getenv(CHAT_GPT_ENV_KEY))

    llm_operator = LLMOperator(START_PROMPT_PREFIX)
    llm_operator.add_llm(llm_chatgpt, LLMType.OPEN_AI_CHATGPT)

    telegram_client.start()
    telegram_bot.start(bot_token=os.getenv(TELEGRAM_ENV_KEY))

    client = Client(telegram_client, telegram_bot, llm_operator, SHOW_BOT_MESSAGE)
    client.register_handlers()

    bot = Bot(telegram_bot, client)
    bot.register_handlers()

    telegram_bot.run_until_disconnected()
    telegram_client.run_until_disconnected()
