from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from order import get_order_conversation_handler
from gpt import get_gpt_conversation_handler
from services.gpt_service import ChatGptService

from from_env import TOKEN_TELEGRAM, TOKEN_GPT

from util import header, show_main_menu

from buttons import BUTTONS_START, BUTTONS_MENU


async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await header(update, context, buttons=BUTTONS_START)
    await show_main_menu(update, context, BUTTONS_MENU)


async def location(update, context):
    await header(update, context)


async def time(update, context):
    await header(update, context)


async def price(update, context):
    await header(update, context)


async def main_button(update, context):
    try:
        await update.callback_query.answer()
    except Exception:
        pass


def main():
    application = Application.builder().token(str(TOKEN_TELEGRAM)).build()

    gpt_service = ChatGptService(TOKEN_GPT)

    application.add_handler(CommandHandler("start", start_bot))
    application.add_handler(get_order_conversation_handler())
    application.add_handler(get_gpt_conversation_handler(gpt_service))

    # Other modes
    application.add_handler(CommandHandler("location", location))
    application.add_handler(CommandHandler("time", time))
    application.add_handler(CommandHandler("price", price))

    # Callback buttons
    application.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))

    application.run_polling()


if __name__ == "__main__":
    print("🤖 Home.Masssage v2️⃣ .0️⃣  starting...")
    main()
