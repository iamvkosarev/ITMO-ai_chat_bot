from abc import abstractmethod
from enum import Enum

class LLMType(Enum):
    OPEN_AI_CHATGPT = 1
    YANDEX_CHATGPT = 2

class LLM:
    @abstractmethod
    async def handle_prompt(self, chat_history) -> str:
        return """Обработать промпт"""