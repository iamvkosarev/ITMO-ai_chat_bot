import os

from telethon import TelegramClient

from ai_chat_bot.model.llm_wrapper import LLMWrapper
from ai_chat_bot.services.dialogs_hide_service import DialogHideService
from ai_chat_bot.services.llm.yandex_gpt import YandexGPT
from ai_chat_bot.services.llm_operator import LLMOperator
from ai_chat_bot.services.llm.chat_gpt import ChatGPT
from ai_chat_bot.services.llm.llm import LLMType
from ai_chat_bot.services.llm_research_service import LLMResearchService
from services.bot import Bot
from services.client import Client

OPENAI_CHAT_GPT_ENV_KEY = 'CHATBOT_CHAT_GPT'
YANDEX_CHAT_GPT_ENV_KEY = 'YANDEX_CHATBOT_CHAT_GPT'
TELEGRAM_ENV_KEY = 'CHATBOT_TELEGRAM'
APP_ID_ENV_KEY = 'CHATBOT_APP_ID'
APP_HASH_ENV_KEY = 'CHATBOT_APP_HASH'
START_PROMPT_PREFIX = 'Ответь на сообщение, но не больше 100 слов, однако пиши, много, когда можно ответить кратко:\n'

SHOW_BOT_MESSAGE = False

if __name__ == '__main__':
    telegram_bot = TelegramClient("bot_session", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY))
    telegram_client = TelegramClient("my_account", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY),
                                     device_model='Python Client Desktop', system_version='Windows 10').start()

    llm_chat_gpt_3_5_turbo = ChatGPT(os.getenv(OPENAI_CHAT_GPT_ENV_KEY), "gpt-3.5-turbo")
    llm_chat_gpt_4_turbo = ChatGPT(os.getenv(OPENAI_CHAT_GPT_ENV_KEY), "gpt-4-turbo")
    llm_chat_gpt_4o = ChatGPT(os.getenv(OPENAI_CHAT_GPT_ENV_KEY), "gpt-4o")
    llm_yandex_gpt = YandexGPT(os.getenv(YANDEX_CHAT_GPT_ENV_KEY), "b1gvjdn3rhefcg7rf39i")

    llm_operator = LLMOperator()
    llm_operator.add_llm(LLMWrapper(llm_chat_gpt_3_5_turbo, LLMType.OPEN_AI_CHATGPT_3_5_TURBO, "ChatGPT 3.5 turbo"))
    llm_operator.add_llm(LLMWrapper(llm_chat_gpt_4_turbo, LLMType.OPEN_AI_CHATGPT_4_TURBO, "ChatGPT 4 turbo"))
    llm_operator.add_llm(LLMWrapper(llm_chat_gpt_4o, LLMType.OPEN_AI_CHATGPT_4O, "ChatGPT 4o"))
    llm_operator.add_llm(LLMWrapper(llm_yandex_gpt, LLMType.YANDEX_CHATGPT, "YandexGPT"))

    telegram_client.start()
    telegram_bot.start(bot_token=os.getenv(TELEGRAM_ENV_KEY))

    client = Client(telegram_client, telegram_bot, llm_operator, SHOW_BOT_MESSAGE, START_PROMPT_PREFIX,
                    DialogHideService("394620235"))
    client.register_handlers()

    llm_research_service = LLMResearchService(llm_operator)

    bot = Bot(telegram_bot, client, llm_operator, llm_research_service)
    bot.register_handlers()

    telegram_bot.run_until_disconnected()
    telegram_client.run_until_disconnected()
