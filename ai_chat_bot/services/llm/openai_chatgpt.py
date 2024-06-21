from openai import AsyncOpenAI
from typing import List, Dict

from ai_chat_bot.model.llm_chat_data import LLMDialog, LLMRole
from ai_chat_bot.services.llm.llm import LLM


class OpenAIChatGPT(LLM):
    def __init__(self, api_key):
        assert isinstance(api_key, str)
        self.ai_client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)

    async def handle_prompt(self, dialog: LLMDialog) -> str:
        chat_completion = await self.ai_client.chat.completions.create(
            messages=self._get_message_from_dialog(dialog),
            model="gpt-3.5-turbo",
        )

        chat_response = chat_completion.choices[0].message.content
        return chat_response

    def _get_message_from_dialog(self, dialog: LLMDialog) -> List[Dict[str, str]]:
        messages_list = []
        for message in dialog.messages:
            new_message = {"role": self._get_role(message.role), "content": message.text}
            messages_list.append(new_message)
        return messages_list

    def _get_role(self, role: LLMRole) -> str:
        if role == LLMRole.USER:
            return "user"
        elif role == LLMRole.ASSISTANT:
            return "assistant"
        elif role == LLMRole.SYSTEM:
            return "system"
        return "system"
