from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CommandHandler,
)

# import asyncio

from gpt import *

# from gpt import ChatGptService
from util import (
    header,
    load_message,
    load_prompt,
    send_text,
    send_photo,
    send_text_buttons,
    dialog_user_info_to_str,
    show_main_menu,
    dialog,
)

# from order_util import order, order_dialog, order_phone_button, order_massage_button
from order_util import *

from buttons import BUTTONS_MAIN, BUTTONS_MENU

import os
from dotenv import load_dotenv

# Читаємо ключі API з файла .env
load_dotenv()
TOKEN_TELEGRAM = str(os.getenv("TOKEN_TELEGRAM"))
TOKEN_GPT = str(os.getenv("TOKEN_GPT"))


async def start(update, context):
    dialog.mode = "main"
    await header(update, context, BUTTONS_MAIN)

    await show_main_menu(
        update,
        context,
        BUTTONS_MENU,
    )


async def main_button(update, context):
    dialog.mode = "main"
    query = update.callback_query.data
    print(">>>>>>main_button>>>>>>>>>>>> query: ", query, " <<<<<<<<<<<<<<<<<<")
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    if query == "main_helper":
        dialog.mode = "helper"
        await header(update, context)
        return
    elif query == "main_price":
        dialog.mode = "price"
        await header(update, context)
        return
    elif query == "main_location":
        dialog.mode = "place"
        await header(update, context)
        return
    elif query == "main_info":
        dialog.mode = "info"
        await header(update, context)
        return
    elif query == "main_order":
        dialog.mode = "order"
        await order(update, context)
    else:
        await gpt(update, context)


async def gpt(update, context):
    dialog.mode = "gpt"
    await header(update, context)


async def gpt_dialog(update, context):

    text = update.message.text
    print("text: ", text)
    dialog.list_.append(text)
    print("dialog.list_: ", dialog.list_)

    text = update.message.text
    print("text: ", text)
    user_chat_history = "\n\n".join(dialog.list_)

    prompt = load_prompt("home_masssage")
    # prompt = load_prompt(dialog.mode)
    # використовуємо dialog.mode, щоб завантажити відповідний prompt для кожного режиму, а не тільки для gpt

    my_message = await send_text(update, context, " . . . ")
    answer = await chatgpt.send_question(prompt, user_chat_history + "\n\n" + text)
    await my_message.edit_text(answer)


async def info(update, context):
    dialog.mode = "info"
    await header(update, context)


async def place(update, context):
    dialog.mode = "place"
    await header(update, context)


async def location(update, context):
    dialog.mode = "place"
    await header(update, context)


async def time(update, context):
    dialog.mode = "time"
    await header(update, context)


async def massage(update, context):
    dialog.mode = "massage"
    await header(update, context)


async def helper(update, context):
    dialog.mode = "helper"
    await header(update, context)


async def price(update, context):
    dialog.mode = "price"
    await header(update, context)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "main":
        await gpt_dialog(update, context)
    elif dialog.mode == "order":
        await order_dialog(update, context)
    else:
        await send_text(update, context, "Привіт!")
        await send_text(update, context, "Ти написав: " + update.message.text)


# async def buttons_handler(update, context):
#     query = update.callback_query.data
#     if query == "start":
#         await send_text(update, context, "Started")
#     elif query == "stop":
#         await send_text(update, context, "Stopped")


if __name__ == "__main__":

    print("bot starting... \ndialog: ", dialog.mode, dialog.list_, dialog.user)

    bot = Bot(TOKEN_TELEGRAM)
    chatgpt = ChatGptService(token=TOKEN_GPT)

    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()

    app.add_handler(CommandHandler("gpt", gpt))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("location", place))
    app.add_handler(CommandHandler("place", place))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("massage", massage))
    app.add_handler(CommandHandler("helper", helper))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))
    app.add_handler(CallbackQueryHandler(order_phone_button, pattern="^order_phone_.*"))
    app.add_handler(CallbackQueryHandler(order_massage_button, pattern="^massage_.*"))

    app.run_polling()
