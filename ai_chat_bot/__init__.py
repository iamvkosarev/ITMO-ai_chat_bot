from telegram import Update
from telethon import TelegramClient, events, sync, Button,custom
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
    client_bot = TelegramClient("bot_session", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY), device_model='Python Bot Desktop', system_version ='Windows 10')
    client = TelegramClient("my_account", os.getenv(APP_ID_ENV_KEY), os.getenv(APP_HASH_ENV_KEY), device_model='Python Client Desktop', system_version ='Windows 10').start()

WORKING_CHATS = []

@client.on(events.NewMessage(outgoing=True, pattern="/bot_off"))
async def handler(event):
    chat = await event.get_chat()
    username = chat.username
    if username in WORKING_CHATS:
        WORKING_CHATS.remove(username)
    show_chats()
    await client.edit_message(chat, event.id, "__Бот выключен__")

bot_select_messages = []

@client_bot.on(events.NewMessage(pattern="/bot"))
async def handler(event):
    await load_main_buttons(event)

@client_bot.on(events.CallbackQuery(pattern="load_main_buttons"))
async def load_main_buttons(event):
    chat = await event.get_chat()
    if len(available_chats) == 0:
        await load_available_chats()
    await delete_messages(chat)
    keyboard = [
        [  
            Button.inline("Запустить бота", "on_select_chat"), 
            Button.inline("Выключить бота", "off_select_chat"), 
        ]
    ]
    message = await client_bot.send_message(chat, "Действие", buttons=keyboard)
    bot_select_messages.append(message.id)

async def delete_messages(chat):
    await client_bot.delete_messages(chat, bot_select_messages)

MAX_SHOW_DIALOGS = 5
available_chats = []

@client_bot.on(events.CallbackQuery(pattern="on_select_chat"))
async def call_handler(event):
    global selcted_group
    selcted_group = 0
    global box_on
    box_on = True
    chat = await event.get_chat()
    await delete_messages(chat)
    count = -1
    keyboard = [
    ]
    next_previouse = [  
            Button.inline("Прошлые", "select_previouse"), 
            Button.inline("Меню", "load_main_buttons"), 
            Button.inline("Следующие", "select_next"),
        ]
    for i in range(MAX_SHOW_DIALOGS):
        keyboard.append([Button.inline(available_chats[i+MAX_SHOW_DIALOGS*selcted_group], "select_"+str(count))])
    keyboard.append(next_previouse)
    message = await send_buttons(chat, keyboard)
    bot_select_messages.append(message.id)


MAX_CHECK_CAHTS = 50
async def load_available_chats():
    count = 0
    async for dialog in client.iter_dialogs():
       available_chats.append(dialog.name)
       count += 1
       if count == MAX_CHECK_CAHTS:
           return   
            

@client_bot.on(events.CallbackQuery(pattern="off_select_chat"))
async def call_handler(event):
    selcted_group = 0
    global box_on
    box_on = False
    chat = await event.get_chat()
    await delete_messages(chat)
    count = -1
    keyboard = [
    ]
    next_previouse = [  
            Button.inline("Прошлые", "select_previouse"), 
            Button.inline("Меню", "load_main_buttons"), 
            Button.inline("Следующие", "select_next"),
        ]
    for i in range(MAX_SHOW_DIALOGS):
        keyboard.append([Button.inline(available_chats[i+MAX_SHOW_DIALOGS*selcted_group], "select_"+str(count))])
    keyboard.append(next_previouse)
    message = await send_buttons(chat, keyboard)
    bot_select_messages.append(message.id)

@client_bot.on(events.CallbackQuery(pattern="select_previouse"))
async def call_handler(event):
    global selcted_group
    if selcted_group != 0:
        selcted_group -= 1
    chat = await event.get_chat()
    await delete_messages(chat)
    count = -1
    keyboard = [
    ]
    next_previouse = [  
            Button.inline("Прошлые", "select_previouse"), 
            Button.inline("Меню", "load_main_buttons"), 
            Button.inline("Следующие", "select_next"),
        ]
    for i in range(MAX_SHOW_DIALOGS):
        keyboard.append([Button.inline(available_chats[i+MAX_SHOW_DIALOGS*selcted_group], "select_"+str(count))])
    keyboard.append(next_previouse)
    message = await send_buttons(chat, keyboard)
    bot_select_messages.append(message.id)

@client_bot.on(events.CallbackQuery(pattern="select_next"))
async def call_handler(event):
    global selcted_group
    if (selcted_group + 1) * MAX_SHOW_DIALOGS < MAX_CHECK_CAHTS:
        selcted_group += 1
    chat = await event.get_chat()
    await delete_messages(chat)
    count = -1
    keyboard = [
    ]
    next_previouse = [  
            Button.inline("Прошлые", "select_previouse"), 
            Button.inline("Меню", "load_main_buttons"), 
            Button.inline("Следующие", "select_next"),
        ]
    for i in range(MAX_SHOW_DIALOGS):
        keyboard.append([Button.inline(available_chats[i+MAX_SHOW_DIALOGS*selcted_group], "select_"+str(count))])
    keyboard.append(next_previouse)
    message = await send_buttons(chat, keyboard)
    bot_select_messages.append(message.id)

async def send_buttons(chat, keyboard):
    global box_on
    if box_on:
        return await client_bot.send_message(chat, f"({selcted_group+1}/{int(MAX_CHECK_CAHTS/MAX_SHOW_DIALOGS)}) Активировать бота в...", buttons=keyboard)
    else:
        return await client_bot.send_message(chat, f"({selcted_group+1}/{int(MAX_CHECK_CAHTS/MAX_SHOW_DIALOGS)}) Деактивировать бота в...", buttons=keyboard)

@client.on(events.NewMessage(outgoing=True, pattern="/bot_on"))
async def handler(event):
    chat = await event.get_chat()
    username = chat.username
    if username not in WORKING_CHATS:
        WORKING_CHATS.append(username)
    show_chats()
    await client.edit_message(chat, event.id, "__Бот включен. Можно с ним пообщаться__")
    # if me.username == chat.username:
    #     await client.send_message(chat, await message('base', event.text))

def show_chats():
    print("Рабочие чаты:",', '.join(WORKING_CHATS))

@client.on(events.NewMessage())
async def handler(event):
    chat = await event.get_chat()
    username = chat.username
    text = event.text
    if text == "/bot_on" or text == "/bot_off":
        if  text == "/bot_off" and username in WORKING_CHATS:
            WORKING_CHATS.remove(username)
        return
    if username in WORKING_CHATS:
        await message_telegram(chat, "__Бот:__\n"+await send_to_gpt(chat.username, text))

CHAT_HISTORY = {}
WORKING_CHATS = []

async def send_to_gpt(chat_id, user_prompt) -> None:
    if chat_id not in CHAT_HISTORY:
        CHAT_HISTORY[chat_id] = []

    CHAT_HISTORY[chat_id].append({"role": "user", "content": 'Ответь на сообщение, но не больше 100 слов, однако пиши, много, когда можно ответить кратко:\n'+user_prompt})

    chat_completion = await ai_client.chat.completions.create(
        messages=CHAT_HISTORY[chat_id],
        model="gpt-3.5-turbo",
    )

    chat_response = chat_completion.choices[0].message.content
    CHAT_HISTORY[chat_id].append({"role": "assistant", "content": chat_response})

    return chat_response

async def message_telegram(chat, message):
    await client.send_message(chat, message)

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
            print(color_text(f"GPT: {await send_to_gpt('base', prompt)}", color.GREEN))

if __name__ == '__main__':
    client_bot.start(bot_token=os.getenv(TELEGRAM_ENV_KEY))
    client.start()
    client_bot.run_until_disconnected()
    client.run_until_disconnected()
    

