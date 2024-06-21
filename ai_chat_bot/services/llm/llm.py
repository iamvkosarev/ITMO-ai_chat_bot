from abc import abstractmethod
from enum import Enum

from ai_chat_bot.model.llm_chat_data import LLMDialog


class LLMType(Enum):
    OPEN_AI_CHATGPT = 1
    YANDEX_CHATGPT = 2

class LLM:
    @abstractmethod
    async def handle_prompt(self, dialog : LLMDialog) -> str:
        return """Обработать промпт"""