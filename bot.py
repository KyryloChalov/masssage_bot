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

from buttons import BUTTONS_MAIN, BUTTONS_MENU, BUTTONS_MASSAGE

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
        # msg = load_message("helper")
        # await send_text(update, context, msg)
        return
    elif query == "main_price":
        dialog.mode = "price"
        await header(update, context)
        # msg = load_message("price")
        # await send_text(update, context, msg)
        return
    elif query == "main_location":
        dialog.mode = "place"
        await header(update, context)
        # msg = load_message("location")
        # await send_text(update, context, msg)
        return
    elif query == "main_info":
        dialog.mode = "info"
        await header(update, context)
        # msg = load_message("info")
        # await send_text(update, context, msg)
        return
    elif query == "main_order":
        # msg = load_message("main_order")
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

    # prompt = load_prompt("home_masssage")
    prompt = load_prompt(dialog.mode)
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


# async def date(update, context):
#     dialog.mode = "date"
#     msg = load_message("date")
#     await send_photo(update, context, "date")
#     await send_text_buttons(
#         update,
#         context,
#         msg,
#         {
#             "date_grande": "Аріана Гранде",
#             "date_robbie": "Марго Роббі",
#             "date_zendaya": "Зендея",
#             "date_gosling": "Райан Гослінг",
#             "date_hardy": "Том Харді",
#         },
#     )


# async def date_button(update, context):
#     dialog.mode = "date"
#     text = "Гарний вибір! \ud83d\ude05 \nВаше завдання - запросити зірку на побачення за 5 повідомлень ❤️"
#     query = update.callback_query.data
#     try:
#         await update.callback_query.answer()
#     except Exception:
#         pass
#     await send_photo(update, context, query)
#     await send_text(update, context, text)
#     prompt = load_prompt(query)
#     chatgpt.set_prompt(prompt)


# async def date_dialog(update, context):
#     dialog.mode = "date"
#     text = update.message.text
#     my_message = await send_text(update, context, "Друкує...")
#     answer = await chatgpt.add_message(text)
#     # await send_text(update, context, answer)
#     await my_message.edit_text(answer)


# async def message(update, context):
#     dialog.mode = "message"
#     msg = load_message("message")
#     await send_photo(update, context, "message")
#     await send_text_buttons(
#         update,
#         context,
#         msg,
#         {
#             "message_next": "Написати повідомлення",
#             "message_date": "Запросити на побачення",
#         },
#         columns=1,
#     )
#     dialog.list_.clear()


# async def message_dialog(update, context):
#     dialog.mode = "message"
#     text = update.message.text
#     print("text: ", text)
#     dialog.list_.append(text)


# async def message_button(update, context):
#     dialog.mode = "message"
#     query = update.callback_query.data
#     print("query: ", query)
#     await update.callback_query.answer()

#     prompt = load_prompt(query)
#     user_chat_history = "\n\n".join(dialog.list_)
#     chat_id = update.effective_chat.id if update.effective_chat else None

#     async def _handle_message_button(prompt_, history_, chat_id_, ctx):
#         try:
#             my_message = await ctx.bot.send_message(chat_id=chat_id_, text="Думаю...")
#             answer = await chatgpt.send_question(prompt_, history_)
#             await my_message.edit_text(answer)
#         except Exception:
#             pass

#     if chat_id:
#         asyncio.create_task(
#             _handle_message_button(prompt, user_chat_history, chat_id, context)
#         )


# async def profile(update, context):
#     dialog.mode = "profile"
#     msg = load_message("profile")
#     await send_photo(update, context, "profile")
#     await send_text(update, context, msg)

#     dialog.user.clear()
#     dialog.counter = 0
#     await send_text(update, context, "Скільки вам років?")


# async def profile_dialog(update, context):
#     dialog.mode = "profile"
#     text = update.message.text
#     dialog.counter += 1

#     if dialog.counter == 1:
#         dialog.user["age"] = text
#         await send_text(update, context, "Ким ви працюєте?")
#     if dialog.counter == 2:
#         dialog.user["occupation"] = text
#         await send_text(update, context, "У вас є хобі?")
#     if dialog.counter == 3:
#         dialog.user["hobby"] = text
#         await send_text(update, context, "Що вам не подобається в людях?")
#     if dialog.counter == 4:
#         dialog.user["annoys"] = text
#         await send_text(update, context, "Мета знайомства")
#     if dialog.counter == 5:
#         dialog.user["goals"] = text
#         prompt = load_prompt("profile")
#         user_info = dialog_user_info_to_str(dialog.user)
#         # print("user_info: ", user_info)

#         my_message = await send_text(
#             update, context, "Чат GPT 🧠 генерує ваш профіль. Зачекайте трошки"
#         )
#         answer = await chatgpt.send_question(prompt, user_info)
#         await my_message.edit_text(answer)


# async def opener(update, context):
#     dialog.mode = "opener"
#     msg = load_message("opener")
#     await send_photo(update, context, "opener")
#     await send_text(update, context, msg)

#     dialog.user.clear()
#     dialog.counter = 0
#     await send_text(update, context, "Ім'я партнера")


# async def opener_dialog(update, context):
#     dialog.mode = "opener"
#     text = update.message.text
#     dialog.counter += 1

#     if dialog.counter == 1:
#         dialog.user["name"] = text
#         await send_text(update, context, "Скільки років?")
#     if dialog.counter == 2:
#         dialog.user["age"] = text
#         await send_text(update, context, "Оцініть зовнішність: 1-10 балів")
#     if dialog.counter == 3:
#         dialog.user["handsome"] = text
#         await send_text(update, context, "Ким працює?")
#     if dialog.counter == 4:
#         dialog.user["occupation"] = text
#         await send_text(update, context, "Мета знайомства")
#     if dialog.counter == 5:
#         dialog.user["goals"] = text

#         prompt = load_prompt("opener")

#         user_info = dialog_user_info_to_str(dialog.user)
#         my_message = await send_text(
#             update, context, "Чат GPT 🧠 генерує ваше повідомлення. Зачекайте трошки"
#         )
#         answer = await chatgpt.send_question(prompt, user_info)
#         await my_message.edit_text(answer)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "main":
        await gpt_dialog(update, context)
    # elif dialog.mode == "date":
    #     await date_dialog(update, context)
    # elif dialog.mode == "message":
    #     await message_dialog(update, context)
    # elif dialog.mode == "profile":
    #     await profile_dialog(update, context)
    # elif dialog.mode == "opener":
    #     await opener_dialog(update, context)
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

    # \|/ видалити по готовності
    # app.add_handler(CommandHandler("date", date))
    # app.add_handler(CommandHandler("message", message))
    # app.add_handler(CommandHandler("profile", profile))
    # app.add_handler(CommandHandler("opener", opener))
    # /|\ видалити по готовності

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
    # \|/ видалити по готовності
    # app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
    # app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
    # /|\ видалити по готовності

    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))
    app.add_handler(CallbackQueryHandler(order_phone_button, pattern="^order_phone_.*"))
    app.add_handler(CallbackQueryHandler(order_massage_button, pattern="^massage_.*"))

    app.run_polling()
