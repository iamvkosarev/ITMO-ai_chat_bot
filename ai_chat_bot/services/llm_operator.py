from typing import List, Dict

from ai_chat_bot.model.llm_chat_data import LLMDialog, LLMMessage, LLMRole
from ai_chat_bot.model.llm_wrapper import LLMWrapper
from ai_chat_bot.services.llm.llm import LLM, LLMType


class LLMOperator:
    def __init__(self):
        self.current_type = None
        self.llms_wrappers: Dict[LLMType, LLMWrapper] = {}

    def add_llm(self, llm_data: LLMWrapper):
        assert isinstance(llm_data.llm, LLM)
        if type not in self.llms_wrappers:
            self.llms_wrappers[llm_data.type] = llm_data
            if len(self.llms_wrappers) == 1:
                self.switch_current_llm(llm_data.type)

    def switch_current_llm(self, type: LLMType):
        self.current_type = type

    async def handle_prompt(self, dialog: LLMDialog, context: str = "") -> str:
        assert len(self.llms_wrappers) > 0
        llm_wrapper = self.llms_wrappers[self.current_type]
        if context != "":
            dialog.add_message(LLMMessage(context, LLMRole.SYSTEM), 0)
        return await llm_wrapper.llm.handle_prompt(dialog)

    def add_user_message(self, dialog: LLMDialog, user_prompt) -> LLMDialog:
        dialog.add_message(LLMMessage(user_prompt, LLMRole.USER))
        return dialog

    def add_llm_response(self, dialog, response) -> LLMDialog:
        dialog.add_message(LLMMessage(response, LLMRole.ASSISTANT))
        return dialog

    def current_llm_name(self) -> str:
        return self.llms_wrappers[self.current_type].name

    def get_models(self) -> List[LLMWrapper]:
        return [chat_data for chat_data in self.llms_wrappers.values()]
