import os
from enum import Enum

from telethon import events, Button, TelegramClient
from typing import List
from .client import Client
import re

from .llm_operator import LLMOperator
from ai_chat_bot.model.dialog_data import DialogData
from .llm_research_service import LLMResearchService

MAX_SHOW_DIALOGS = 5
MAX_CHECK_CAHTS = 50

PREVIOUS_TEXT = "Прошлые"
PREVIOUS_PATTERN = "select_previouse"

NEXT_TEXT = "Следующие"
NEXT_PATTERN = "select_next"

MENU_TEXT = "Меню"
MENU_PATTERN = "load_main_buttons"

green_check_mark = '✅'
red_cross_mark = '❌'


class ChatAction(Enum):
    SWITCH_BOT = 0
    CLEAR = 1


class Bot:
    def __init__(self, telegram_bot, client: Client, llm_operator: LLMOperator,
                 llm_research_service: LLMResearchService):
        self.telegram_bot: TelegramClient = telegram_bot
        self.llm_research_service = llm_research_service
        self.client = client
        self.llm_operator = llm_operator
        self.bot_select_messages = []
        self.dialogs: List[DialogData] = []
        self.dialogs_active = {}
        self.selected_group = 0
        self.wait_json = False
        self.chat_action: ChatAction = ChatAction.SWITCH_BOT

    def register_handlers(self):
        @self.telegram_bot.on(events.NewMessage(pattern="/bot"))
        async def handler(event):
            await load_main_buttons(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern=MENU_PATTERN))
        async def load_main_buttons(event):
            chat = await event.get_chat()
            await self.try_load_available_chats()
            await self.delete_messages(chat)
            keyboard = [
                [
                    Button.inline("Подключение к чату", "on_set_bot"), ], [
                    Button.inline("Очистка чата", "on_clear_chats"), ], [
                    Button.inline(f"Подпись 'Бот ...' ({self.get_sign(self.client.show_bot_message)})",
                                  "switch_show_bot_message"), ], [
                    Button.inline(f"LLM: {self.llm_operator.current_llm_name()}", "switch_llm_type")
                ],
                [
                    Button.inline("Исследование", "research")
                ]
            ]
            message = await self.telegram_bot.send_message(chat, "Действие", buttons=keyboard)
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.CallbackQuery(pattern="on_set_bot"))
        async def call_handler(event):
            self.selected_group = 0
            self.chat_action = ChatAction.SWITCH_BOT
            await self.show_chats(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern="on_clear_chats"))
        async def call_handler(event):
            self.selected_group = 0
            self.chat_action = ChatAction.CLEAR
            await self.show_chats(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern="research"))
        async def call_handler(event):
            chat = await event.get_chat()
            await self.delete_messages(chat)
            self.wait_json = True
            message = await self.telegram_bot.send_message(chat,
                                                           "Ожидание json для анализа...")
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.NewMessage)
        async def handle_file(event):
            if not self.wait_json:
                return
            chat = await event.get_chat()
            await self.delete_messages(chat)
            if event.message.file:
                if event.message.file.mime_type in ['application/json', 'text/json']:
                    self.wait_json = False
                    await event.reply('Получен JSON файл, приступаю к обработке...')
                    file_path = await self.telegram_bot.download_media(event.message.media)
                    result = await self.llm_research_service.process_file(file_path)
                    await event.reply('Файл успешно обработан!\n' + result)
                    return
                message = await self.telegram_bot.send_message(chat,
                                                               "Некорректный файл или ...")
                self.bot_select_messages.append(message.id)
                return
            message = await self.telegram_bot.send_message(chat, "Ожидание json для анализа...")
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.CallbackQuery(pattern="switch_show_bot_message"))
        async def call_handler(event):
            self.client.switch_show_bot_text(self.client.show_bot_message == False)
            await load_main_buttons(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern="switch_llm_type"))
        async def call_handler(event):
            await self.show_models(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern=PREVIOUS_PATTERN))
        async def call_handler(event):
            if self.selected_group != 0:
                self.selected_group -= 1
            await self.show_chats(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern=NEXT_PATTERN))
        async def call_handler(event):
            if (self.selected_group + 1) * MAX_SHOW_DIALOGS < MAX_CHECK_CAHTS:
                self.selected_group += 1
            await self.show_chats(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern=re.compile(r"select_(\d+)")))
        async def select_handler(event):
            match = event.pattern_match
            if match:
                index = int(match.group(1))
                dialog = self.dialogs[index + MAX_SHOW_DIALOGS * self.selected_group]
                if self.chat_action == ChatAction.SWITCH_BOT:
                    mode: bool = self.dialogs_active[dialog.name]
                    self.dialogs_active[dialog.name] = mode == False
                    self.client.switch_bot(mode == False, dialog.id)
                elif self.chat_action == ChatAction.CLEAR:
                    self.client.clear_chat(dialog)
            await self.show_chats(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern=re.compile(r"select_model_(\d+)")))
        async def select_handler(event):
            match = event.pattern_match
            if match:
                index = int(match.group(1))
                self.llm_operator.switch_current_llm(self.llm_operator.get_models()[index].type)
            await self.show_models(event)

    async def delete_messages(self, chat):
        await self.telegram_bot.delete_messages(chat, self.bot_select_messages)

    async def send_buttons(self, chat, keyboard):
        PHRASE = "Настройка бота в..."

        return await self.telegram_bot.send_message(chat,
                                                    f"({self.selected_group + 1}/{int(MAX_CHECK_CAHTS / MAX_SHOW_DIALOGS)}) {PHRASE}",
                                                    buttons=keyboard)


    async def show_models(self, event):
        chat = await event.get_chat()
        await self.delete_messages(chat)
        keyboard = [
        ]
        i = 0
        for model in self.llm_operator.get_models():
            keyboard.append(
                [Button.inline(f"{model.name} ({self.get_sign(self.llm_operator.current_llm_name() == model.name)})",
                               "select_model_" + str(i))])
            i += 1
        keyboard.append([Button.inline(MENU_TEXT, MENU_PATTERN)])
        message = await self.telegram_bot.send_message(chat,
                                                       "Выбор модели",
                                                       buttons=keyboard)
        self.bot_select_messages.append(message.id)

    async def show_chats(self, event):
        chat = await event.get_chat()
        await self.delete_messages(chat)
        count = 0
        keyboard = []
        next_previouse = [
            Button.inline(PREVIOUS_TEXT, PREVIOUS_PATTERN),
            Button.inline(MENU_TEXT, MENU_PATTERN),
            Button.inline(NEXT_TEXT, NEXT_PATTERN),
        ]
        for i in range(MAX_SHOW_DIALOGS):
            dialog = self.dialogs[i + MAX_SHOW_DIALOGS * self.selected_group]
            keyboard.append(
                [Button.inline(self.get_dialog_select_text(dialog),
                               "select_" + str(count))])
            count += 1
        keyboard.append(next_previouse)
        message = await self.send_buttons(chat, keyboard)
        self.bot_select_messages.append(message.id)

    async def try_load_available_chats(self):
        if len(self.dialogs) != 0:
            return
        for dialog in await self.client.get_dialogs(MAX_CHECK_CAHTS):
            self.dialogs.append(dialog)
            self.dialogs_active[dialog.name] = False

    def get_sign(self, mode: bool):
        if mode:
            return green_check_mark
        return red_cross_mark

    def get_dialog_select_text(self, dialog: DialogData) -> str:
        if self.chat_action == ChatAction.SWITCH_BOT:
            return f"{dialog.name} ({self.get_sign(self.dialogs_active[dialog.name])})"
        elif self.chat_action == ChatAction.CLEAR:
            return f"{dialog.name} (сообщений: {self.client.get_dialog_messages_count(dialog)})"
