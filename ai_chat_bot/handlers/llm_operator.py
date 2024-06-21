from typing import List, Dict

from ai_chat_bot.llm.llm import LLM


class LLMOperator:
    def __init__(self, prompt_prefix):
        self.llms: Dict[int, LLM] = {}
        self.prompt_prefix: str = prompt_prefix

    def add_llm(self, llm, type: int):
        assert isinstance(llm, LLM)
        if type not in self.llms:
            self.llms[type] = llm
            if len(self.llms) == 1:
                self.switch_current_llm(type)

    def switch_current_llm(self, type: int):
        self.current_type = type

    async def handle_prompt(self, chat_history) -> str:
        assert len(self.llms) > 0
        llm = self.llms[self.current_type]

        return await llm.handle_prompt(chat_history)

    def add_user_message(self, chat_history, user_prompt) -> List[Dict[str, str]]:
        chat_history.append({"role": "user",
                             "content": self.prompt_prefix + user_prompt})
        return chat_history

    def add_llm_response(self, chat_history, response) -> List[Dict[str, str]]:
        chat_history.append({"role": "assistant", "content": response})
        return chat_history
