from typing import List, Dict

from telethon import events, TelegramClient
from telegram import Chat

from ai_chat_bot.model.llm_chat_data import LLMDialog
from ai_chat_bot.services.llm_operator import LLMOperator


class Client:
    def __init__(self, telegram_client, telegram_bot, llm_operator, show_bot_message):
        self.show_bot_message = show_bot_message
        self.telegram_client: TelegramClient = telegram_client
        self.telegram_bot: TelegramClient = telegram_bot
        self.llm_operator: LLMOperator = llm_operator
        self.working_chats: List[int] = []
        self.dialogs: Dict[str, LLMDialog] = {}

    async def send_to_gpt(self, chat_id, user_prompt) -> str:
        if chat_id not in self.dialogs:
            self.dialogs[chat_id] = LLMDialog()

        self.dialogs[chat_id] = self.llm_operator.add_user_message(self.dialogs[chat_id], user_prompt)
        response = await self.llm_operator.handle_prompt(self.dialogs[chat_id])
        self.dialogs[chat_id] = self.llm_operator.add_llm_response(self.dialogs[chat_id], response)

        return response

    def switch_show_bot_text(self, mode: bool):
        self.show_bot_message = mode

    async def _client_send_message(self, chat, message: str):
        await self.telegram_client.send_message(chat, message)

    def switch_bot(self, mode, id: int):
        def show_chats():
            print("Рабочие чаты:", ', '.join(str(id) for id in self.working_chats))

        if mode:
            if id not in self.working_chats:
                self.working_chats.append(id)
        else:
            if id in self.working_chats:
                self.working_chats.remove(id)

        show_chats()

    def register_handlers(self):
        @self.telegram_client.on(events.NewMessage(outgoing=True, pattern="/bot_off"))
        async def handler(event):
            chat: Chat = await event.get_chat()
            self.switch_bot(False, chat.id)
            await self.telegram_client.edit_message(chat, event.id, "__Бот выключен__")

        @self.telegram_client.on(events.NewMessage(outgoing=True, pattern="/bot_on"))
        async def handler(event):
            chat: Chat = await event.get_chat()
            self.switch_bot(True, chat.id)
            await self.telegram_client.edit_message(chat, event.id, "__Бот включен. Можно с ним пообщаться__")

        @self.telegram_client.on(events.NewMessage())
        async def handler(event):
            chat: Chat = await event.get_chat()
            id = chat.id
            text = event.text
            if text == "/bot_on" or text == "/bot_off":
                if text == "/bot_off" and id in self.working_chats:
                    self.working_chats.remove(id)
                return
            if id in self.working_chats:
                await self._client_send_message(chat,
                                                self._get_bot_phrase() + await self.send_to_gpt(chat.username, text))

    async def get_dialogs(self, max_count: int):
        count = 0
        available_chats = []
        async for dialog in self.telegram_client.iter_dialogs():
            available_chats.append(dialog)
            count += 1
            if count >= max_count:
                return available_chats
        return available_chats

    def _get_bot_phrase(self) -> str:
        if self.show_bot_message:
            return "__Бот:__\n"
        return ""
