from telethon import events


class Client:
    def __init__(self, telegram_client, telegram_bot, ai_client):
        self.telegram_client = telegram_client
        self.telegram_bot = telegram_bot
        self.ai_client = ai_client
        self.working_chats = []
        self.chat_history = {}

    async def send_to_gpt(self, chat_id, user_prompt) -> str:
        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = []

        self.chat_history[chat_id].append({"role": "user",
                                           "content": 'Ответь на сообщение, но не больше 100 слов, однако пиши, много, когда можно ответить кратко:\n' + user_prompt})

        chat_completion = await self.ai_client.chat.completions.create(
            messages=self.chat_history[chat_id],
            model="gpt-3.5-turbo",
        )

        chat_response = chat_completion.choices[0].message.content
        self.chat_history[chat_id].append({"role": "assistant", "content": chat_response})

        return chat_response

    async def client_send_message(self, chat, message):
        await self.telegram_client.send_message(chat, message)

    def register_handlers(self):
        @self.telegram_client.on(events.NewMessage(outgoing=True, pattern="/bot_off"))
        async def handler(event):
            chat = await event.get_chat()
            username = chat.username
            if username in self.working_chats:
                self.working_chats.remove(username)
            show_chats()
            await self.telegram_client.edit_message(chat, event.id, "__Бот выключен__")

        def show_chats():
            print("Рабочие чаты:", ', '.join(self.working_chats))

        @self.telegram_client.on(events.NewMessage(outgoing=True, pattern="/bot_on"))
        async def handler(event):
            chat = await event.get_chat()
            username = chat.username
            if username not in self.working_chats:
                self.working_chats.append(username)
            show_chats()
            await self.telegram_client.edit_message(chat, event.id, "__Бот включен. Можно с ним пообщаться__")

        @self.telegram_client.on(events.NewMessage())
        async def handler(event):
            chat = await event.get_chat()
            username = chat.username
            text = event.text
            if text == "/bot_on" or text == "/bot_off":
                if text == "/bot_off" and username in self.working_chats:
                    self.working_chats.remove(username)
                return
            if username in self.working_chats:
                await self.client_send_message(chat, "__Бот:__\n" + await send_to_gpt(chat.username, text))
