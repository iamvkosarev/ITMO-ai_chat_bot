from typing import List, Dict

from ai_chat_bot.model.llm_chat_data import LLMDialog, LLMMessage, LLMRole
from ai_chat_bot.services.llm.llm import LLM, LLMType


class LLMOperator:
    def __init__(self, prompt_prefix):
        self.current_type = None
        self.llms: Dict[LLMType, LLM] = {}
        self.prompt_prefix: str = prompt_prefix

    def add_llm(self, llm, type: LLMType):
        assert isinstance(llm, LLM)
        if type not in self.llms:
            self.llms[type] = llm
            if len(self.llms) == 1:
                self.switch_current_llm(type)

    def switch_current_llm(self, type: LLMType):
        self.current_type = type

    async def handle_prompt(self, chat_history) -> str:
        assert len(self.llms) > 0
        llm = self.llms[self.current_type]

        return await llm.handle_prompt(chat_history)

    def add_user_message(self, dialog: LLMDialog, user_prompt) -> LLMDialog:
        dialog.add_message(LLMMessage(self.prompt_prefix + user_prompt, LLMRole.USER))
        return dialog

    def add_llm_response(self, dialog, response) -> LLMDialog:
        dialog.add_message(LLMMessage(response, LLMRole.ASSISTANT))
        return dialog

    def current_llm(self) -> str:
        if self.current_type == LLMType.YANDEX_CHATGPT:
            return "Yandex"
        elif self.current_type == LLMType.OPEN_AI_CHATGPT:
            return "OpenAI"
        return "none"

    def get_not_using_llm(self) -> LLMType:
        if self.current_type == LLMType.OPEN_AI_CHATGPT:
            return LLMType.YANDEX_CHATGPT
        return LLMType.OPEN_AI_CHATGPT
