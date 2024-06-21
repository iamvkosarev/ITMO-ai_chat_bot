from abc import abstractmethod
from enum import Enum

from ai_chat_bot.model.llm_chat_data import LLMDialog


class LLMType(Enum):
    YANDEX_CHATGPT = 0
    OPEN_AI_CHATGPT_4_TURBO = 1
    OPEN_AI_CHATGPT_3_5_TURBO = 2
    OPEN_AI_CHATGPT_4O = 3

class LLM:
    @abstractmethod
    async def handle_prompt(self, dialog : LLMDialog) -> str:
        return """Обработать промпт"""