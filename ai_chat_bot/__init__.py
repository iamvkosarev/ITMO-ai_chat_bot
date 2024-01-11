from telegram import Update
from telethon import TelegramClient, events, sync
from pyrogram import Client, filters
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from openai import OpenAI, AsyncOpenAI
import asyncio


CHAT_GPT_ENV_KEY = 'CHATBOT_CHAT_GPT'
TELEGRAM_ENV_KEY = 'CHATBOT_TELEGRAM'
APP_ID_ENV_KEY = 'CHATBOT_APP_ID'
APP_HASH_ENV_KEY = 'CHATBOT_APP_HASH'

async def client_main():
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    # print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    # print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # You can send messages to yourself...
    # await client.send_message('me', 'Hello, myself!')
    # ...to your contacts
    # await client.send_message('387064246', 'Hello, friend!')
    # ...or even to any username
    # await client.send_message('tainau', 'Testing Telethon!')

    # You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )

    # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # Or send files, songs, documents, albums...
    # await client.send_file('me', '/home/me/Pictures/holidays.jpg')

    # You can print the message history of any chat:
    count = 10
    async for message in client.iter_messages('me'):
        if count == 0:
            break
        if message.text:
            count-=1
            print(message.id, message.text)

        # You can download media from messages, too!
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media()
        #     print('File saved to', path)  # printed after download is done


if __name__ == '__main__':
    ai_client = AsyncOpenAI(api_key=os.getenv(CHAT_GPT_ENV_KEY))
    client = TelegramClient("my_account", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY), device_model='Python Bot Desktop', system_version ='Windows 10')

# @client.on(events.NewMessage(outgoing=True))
# async def handler(event):
#     chat = await event.get_chat()
#     me = await client.get_me()
#     if me.username == chat.username:
#         await client.send_message(chat, await message('base', event.text))

@client.on(events.NewMessage())
async def handler(event):
    chat = await event.get_chat()
    text = event.text
    if text.startswith("/bot"):
        text = text[5:]
        await client.send_message(chat, await message(chat.username, text))

CHAT_HISTORY = {}

async def message(chat_id, user_prompt) -> None:
    if chat_id not in CHAT_HISTORY:
        CHAT_HISTORY[chat_id] = []

    CHAT_HISTORY[chat_id].append({"role": "user", "content": user_prompt})

    chat_completion = await ai_client.chat.completions.create(
        messages=CHAT_HISTORY[chat_id],
        model="gpt-3.5-turbo",
    )

    chat_response = chat_completion.choices[0].message.content
    CHAT_HISTORY[chat_id].append({"role": "assistant", "content": chat_response})

    return chat_response

def color_text(text, color):
    r, g, b = color
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

class color():
    GREEN = (0, 200, 0)
    YELLOW = (200, 200, 0)
    ORANGE = (255, 110, 20)
    RED = (200, 0, 0)
    DARK_RED = (100, 0, 0),
    BLACK = (0, 0, 0)

async def main():
    while(True):
            prompt = input(color_text("Вы: ", color.BLACK))
            print(color_text(f"GPT: {await message('base', prompt)}", color.GREEN))

if __name__ == '__main__':
    #asyncio.run(main())
    client.start()
    client.run_until_disconnected()

