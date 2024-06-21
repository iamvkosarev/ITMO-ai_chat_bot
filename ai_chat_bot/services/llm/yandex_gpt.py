import json

import requests
from typing import List, Dict

from ai_chat_bot.model.llm_chat_data import LLMDialog, LLMRole
from ai_chat_bot.services.llm.llm import LLM


class YandexGPT(LLM):
    def __init__(self, api_key: str, catalog_id : str):
        self.api_key = api_key
        self.catalog_id = catalog_id

    async def handle_prompt(self, dialog: LLMDialog) -> str:
        prompt = {
            "modelUri": f"gpt://{self.catalog_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": self._get_message_from_dialog(dialog)
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            f"Authorization": f"Api-Key {self.api_key}"
        }

        response = requests.post(url, headers=headers, json=prompt)
        return self._extract_message(response.text)

    def _extract_message(self, json_data : str) -> str:
        data = json.loads(json_data)

        if 'error' in data:
            return f"Error: {data['error']['message']}"

        if 'result' in data:
            alternatives = data['result'].get('alternatives', [])
            if alternatives:
                message = alternatives[0].get('message', {})
                text = message.get('text', '')
                return text

        return "No relevant data found"
    def _get_message_from_dialog(self, dialog: LLMDialog) -> List[Dict[str, str]]:
        messages_list = []
        for message in dialog.messages:
            new_message = {"role": self._get_role(message.role), "text": message.text}
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
