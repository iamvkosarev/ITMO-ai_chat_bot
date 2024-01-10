from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os


TELEGRAM_ENV_KEY = 'AI_CHATBOT'

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

def main():
    app = ApplicationBuilder().token(os.getenv(TELEGRAM_ENV_KEY)).build()
    app.add_handler(CommandHandler("hi", hello))
    app.run_polling()

if __name__ == '__main__':
    main()