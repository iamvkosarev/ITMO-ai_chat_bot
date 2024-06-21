import json
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

    def to_dict(self):
        return {
            "text": self.text,
            "role": self.role.name  # Используем name, чтобы сохранить имя Enum
        }

    @classmethod
    def from_dict(cls, data):
        role = LLMRole[data["role"]]
        return cls(data["text"], role)


class LLMDialog:
    def __init__(self):
        self.messages: List[LLMMessage] = []
        self.context = ""

    def add_message(self, llm_message: LLMMessage, index: int = -1):
        if index != -1:
            self.messages.insert(index, llm_message)
        else:
            self.messages.append(llm_message)

    def get_messages(self) -> List[LLMMessage]:
        return self.messages

    def to_dict(self):
        return {
            "messages": [message.to_dict() for message in self.messages],
            "context": self.context
        }

    @classmethod
    def from_dict(cls, data):
        dialog = cls()
        dialog.messages = [LLMMessage.from_dict(msg) for msg in data["messages"]]
        dialog.context = data["context"]
        return dialog

    def save_to_json(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=4)

    @classmethod
    def load_from_json(cls, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return cls.from_dict(data)