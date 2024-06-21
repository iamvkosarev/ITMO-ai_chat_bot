from enum import Enum
from typing import List


class LLMRole(Enum):
    SYSTEM = 0
    USER = 1
    ASSISTANT = 2

class LLMMessage:
    def __init__(self, text: str, role: LLMRole):
        self.text = text
        self.role = role


class LLMDialog:
    def __init__(self, system_message: LLMMessage = None):
        self.messages: List[LLMMessage] = []
        if system_message is not None:
            self.messages.append(system_message)

    def add_message(self, llm_message: LLMMessage):
        self.messages.append(llm_message)

    def get_messages(self) -> List[LLMMessage]:
        return self.messages
