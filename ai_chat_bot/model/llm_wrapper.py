from ai_chat_bot.services.llm.llm import LLM, LLMType


class LLMWrapper:
    def __init__(self, llm: LLM, type: LLMType, name: str):
        self.llm = llm
        self.type = type
        self.name = name