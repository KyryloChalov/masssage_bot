# main.py

import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from order import get_order_conversation_handler
from gpt import get_gpt_conversation_handler
from gpt_service import ChatGptService

load_dotenv()
TOKEN = os.getenv("TOKEN_TELEGRAM")
OPENAI_TOKEN = os.getenv("TOKEN_GPT")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Вітаю 👋\n\n"
        "/order — запис на масаж\n"
        "/gpt — задати питання"
    )


def main():
    application = Application.builder().token(TOKEN).build()

    gpt_service = ChatGptService(OPENAI_TOKEN)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_order_conversation_handler())
    application.add_handler(get_gpt_conversation_handler(gpt_service))

    application.run_polling()


if __name__ == "__main__":
    main()
