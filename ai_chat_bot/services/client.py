from typing import List, Dict

from telethon import events, TelegramClient
from telegram import Chat

from ai_chat_bot.model.dialog_data import DialogData
from ai_chat_bot.model.llm_chat_data import LLMDialog
from ai_chat_bot.services.dialogs_hide_service import DialogHideService
from ai_chat_bot.services.llm_operator import LLMOperator


class Client:
    def __init__(self, telegram_client: TelegramClient, telegram_bot: TelegramClient, llm_operator: LLMOperator,
                 show_bot_message, dialogs_hide_service: DialogHideService = None):
        self.show_bot_message = show_bot_message
        self.dialogs_hide_service = dialogs_hide_service
        self.telegram_client = telegram_client
        self.telegram_bot = telegram_bot
        self.llm_operator = llm_operator
        self.working_chats: List[int] = []
        self.dialogs: Dict[int, LLMDialog] = {}

    async def send_to_gpt(self, id, user_prompt) -> str:
        if id not in self.dialogs:
            self.dialogs[id] = LLMDialog()

        self.dialogs[id] = self.llm_operator.add_user_message(self.dialogs[id], user_prompt)
        response = await self.llm_operator.handle_prompt(self.dialogs[id])
        self.dialogs[id] = self.llm_operator.add_llm_response(self.dialogs[id], response)

        return response

    def get_dialog_messages_count(self, dialog: DialogData) -> int:
        if dialog.id in self.dialogs:
            return len(self.dialogs[dialog.id].messages)
        return 0

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
                                                self._get_bot_phrase() + await self.send_to_gpt(id, text))

    async def get_dialogs(self, max_count: int) -> List[DialogData]:
        count = 0
        available_chats: List[DialogData] = []
        async for dialog in self.telegram_client.iter_dialogs():
            dialog = DialogData(dialog.name, dialog.entity.id)
            if self.dialogs_hide_service != None:
                dialog = self.dialogs_hide_service.hide(dialog)
            available_chats.append(dialog)
            count += 1
            if count >= max_count:
                return available_chats
        return available_chats

    def _get_bot_phrase(self) -> str:
        if self.show_bot_message:
            return f"__Бот ({self.llm_operator.current_llm_name()}):__\n"
        return ""

    def clear_chat(self, dialog: DialogData):
        if dialog.id in self.dialogs:
            self.dialogs[dialog.id].messages.clear()
