from telethon import events, Button

MAX_SHOW_DIALOGS = 5
MAX_CHECK_CAHTS = 50

PREVIOUS_TEXT = "Прошлые"
PREVIOUS_PATTERN = "select_previouse"

NEXT_TEXT = "Следующие"
NEXT_PATTERN = "select_next"

MENU_TEXT = "Меню"
MENU_PATTERN = "load_main_buttons"


class Bot:
    def __init__(self, telegram_bot, telegram_client):
        self.telegram_bot = telegram_bot
        self.telegram_client = telegram_client
        self.bot_select_messages = []
        self.available_chats = []
        self.selected_group = 0
        self.box_on = False

    async def delete_messages(self, chat):
        await self.telegram_bot.delete_messages(chat, self.bot_select_messages)

    async def send_buttons(self, chat, keyboard):
        ACTIVATE_PHRASE = "Активировать бота в..."
        DEACTIVATE_PHRASE = "Деактивировать бота в..."

        async def send_buttons_int(phrase):
            return await self.telegram_bot.send_message(chat,
                                                        f"({self.selected_group + 1}/{int(MAX_CHECK_CAHTS / MAX_SHOW_DIALOGS)}) {phrase}",
                                                        buttons=keyboard)

        if self.box_on:
            return await send_buttons_int(ACTIVATE_PHRASE)
        else:
            return await send_buttons_int(DEACTIVATE_PHRASE)



    async def load_available_chats(self):
        count = 0
        async for dialog in self.telegram_client.iter_dialogs():
            self.available_chats.append(dialog.name)
            count += 1
            if count == MAX_CHECK_CAHTS:
                return

    def register_handlers(self):
        @self.telegram_bot.on(events.NewMessage(pattern="/bot"))
        async def handler(event):
            await load_main_buttons(event)

        @self.telegram_bot.on(events.CallbackQuery(pattern=MENU_PATTERN))
        async def load_main_buttons(event):
            chat = await event.get_chat()
            if len(self.available_chats) == 0:
                await self.load_available_chats()
            await self.delete_messages(chat)
            keyboard = [
                [
                    Button.inline("Запустить бота", "on_select_chat"),
                    Button.inline("Выключить бота", "off_select_chat"),
                ]
            ]
            message = await self.telegram_bot.send_message(chat, "Действие", buttons=keyboard)
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.CallbackQuery(pattern="on_select_chat"))
        async def call_handler(event):
            self.selected_group = 0
            self.box_on = True
            chat = await event.get_chat()
            await self.delete_messages(chat)
            count = -1
            keyboard = []
            next_previouse = [
                Button.inline(PREVIOUS_TEXT, PREVIOUS_PATTERN),
                Button.inline(MENU_TEXT, MENU_PATTERN),
                Button.inline(NEXT_TEXT, NEXT_PATTERN),
            ]
            for i in range(MAX_SHOW_DIALOGS):
                keyboard.append(
                    [Button.inline(self.available_chats[i + MAX_SHOW_DIALOGS * self.selected_group],
                                   "select_" + str(count))])
            keyboard.append(next_previouse)
            message = await self.send_buttons(chat, keyboard)
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.CallbackQuery(pattern="off_select_chat"))
        async def call_handler(event):
            self.selected_group = 0
            self.box_on = False
            chat = await event.get_chat()
            await self.delete_messages(chat)
            count = -1
            keyboard = []
            next_previouse = [
                Button.inline(PREVIOUS_TEXT, PREVIOUS_PATTERN),
                Button.inline(MENU_TEXT, MENU_PATTERN),
                Button.inline(NEXT_TEXT, NEXT_PATTERN),
            ]
            for i in range(MAX_SHOW_DIALOGS):
                keyboard.append(
                    [Button.inline(self.available_chats[i + MAX_SHOW_DIALOGS * self.selected_group],
                                   "select_" + str(count))])
            keyboard.append(next_previouse)
            message = await self.send_buttons(chat, keyboard)
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.CallbackQuery(pattern=PREVIOUS_PATTERN))
        async def call_handler(event):
            if self.selected_group != 0:
                self.selected_group -= 1
            chat = await event.get_chat()
            await self.delete_messages(chat)
            count = -1
            keyboard = []
            next_previouse = [
                Button.inline(PREVIOUS_TEXT, PREVIOUS_PATTERN),
                Button.inline(MENU_TEXT, MENU_PATTERN),
                Button.inline(NEXT_TEXT, NEXT_PATTERN),
            ]
            for i in range(MAX_SHOW_DIALOGS):
                keyboard.append(
                    [Button.inline(self.available_chats[i + MAX_SHOW_DIALOGS * self.selected_group],
                                   "select_" + str(count))])
            keyboard.append(next_previouse)
            message = await self.send_buttons(chat, keyboard)
            self.bot_select_messages.append(message.id)

        @self.telegram_bot.on(events.CallbackQuery(pattern=NEXT_PATTERN))
        async def call_handler(event):
            if (self.selected_group + 1) * MAX_SHOW_DIALOGS < MAX_CHECK_CAHTS:
                self.selected_group += 1
            chat = await event.get_chat()
            await self.delete_messages(chat)
            count = -1
            keyboard = []
            next_previouse = [
                Button.inline(PREVIOUS_TEXT, PREVIOUS_PATTERN),
                Button.inline(MENU_TEXT, MENU_PATTERN),
                Button.inline(NEXT_TEXT, NEXT_PATTERN),
            ]
            for i in range(MAX_SHOW_DIALOGS):
                keyboard.append([Button.inline(self.available_chats[i + MAX_SHOW_DIALOGS * self.selected_group],
                                               "select_" + str(count))])
            keyboard.append(next_previouse)
            message = await self.send_buttons(chat, keyboard)
            self.bot_select_messages.append(message.id)
