from tkinter import dialog
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
    load_message,
    load_prompt,
    send_text,
    send_photo,
    send_text_buttons,
    dialog_user_info_to_str,
    show_main_menu,
    Dialog,
)
import os
from dotenv import load_dotenv

# Читаємо ключі API з файла .env
load_dotenv()
TOKEN_TELEGRAM = str(os.getenv("TOKEN_TELEGRAM"))
TOKEN_GPT = str(os.getenv("TOKEN_GPT"))
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
TELEGRAM_KYRYLO_ID = int(os.getenv("TELEGRAM_KYRYLO_ID", "0"))

BUTTONS_MAIN = {
    "main_order": "Замовити масаж",
    "main_help": "Допомога у виборі масажу",
    "main_price": "Розклад роботи та ціни",
    "main_location": "Де ми працюємо",
    "main_info": "Інформація про Home.Masssage",
}

BUTTONS_MENU = {
    "start": "головне меню бота",
    "order": "Замовити масаж",
    "helper": "Допомога у виборі масажу",
    "price": "Розклад роботи та ціни",
    "location": "Де ми працюємо",
    "info": "Інформація про Home.Masssage",
    "gpt": "задати питання чату GPT 🧠",
}

BUTTONS_MASSAGE = {
    "massage_1": "Масаж загальний",
    "massage_2": "Масаж спини",
    "massage_3": "Масаж ног",
    "massage_4": "Масаж тайський",
    "massage_5": "Масаж антицелюлітний",
    "massage_custom": "Свій варіант 🙌",
}


async def header(update, context, buttons: dict = {}):
    await send_photo(update, context, dialog.mode)
    msg = load_message(dialog.mode)
    if buttons == {}:
        await send_text(update, context, msg)
    else:
        await send_text_buttons(update, context, msg, buttons)


async def price(update, context):
    dialog.mode = "price"
    await header(update, context)


async def start(update, context):
    dialog.mode = "start"
    await header(update, context, BUTTONS_MAIN)

    await show_main_menu(
        update,
        context,
        BUTTONS_MENU,
    )


# async def main_dialog(update, context):
#     text = update.message.text
#     print("text: ", text)
#     dialog.list_.append(text)
#     print("dialog.list_: ", dialog.list_)


async def main_button(update, context):
    dialog.mode = "main"
    query = update.callback_query.data
    print(">>>>>>>>>>>>>>>>>> query: ", query, " <<<<<<<<<<<<<<<<<<")
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    if query == "main_help":
        msg = load_message("main_help")
        await send_text(update, context, msg)
        return
    elif query == "main_price":
        msg = load_message("main_price")
        await send_text(update, context, msg)
        return
    elif query == "main_location":
        msg = load_message("main_location")
        await send_text(update, context, msg)
        return
    elif query == "main_info":
        msg = load_message("main_info")
        await send_text(update, context, msg)
        return
    elif query == "main_order":
        # msg = load_message("main_order")
        await order(update, context)

    # prompt = load_prompt(query)
    # user_chat_history = "\n\n".join(dialog.list_)

    # my_message = await send_text(update, context, "Думаю...")
    # answer = await chatgpt.send_question(prompt, user_chat_history)
    # await my_message.edit_text(answer)


async def order_case_0(update, context):  # time + name
    # цей кейс потрібен, щоб одразу встановити час оформлення замовлення, не чекаючи вводу користувача
    # але виконуватися він буде тільки при виклику функції order(), а не при виклику order_dialog(), бо час встановлюється одразу при виклику функції order()
    from datetime import datetime

    dialog.user["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await send_text(update, context, "Як до вас звертатися? \ud83d\ude4c")


async def order_case_1(update, context):  # name + phone
    dialog.user["name"] = update.message.text
    await send_text(update, context, "Ваш номер телефону? \ud83d\ude4c")


async def order_case_2(update, context):  # phone + buttons (продовжити або дзвінок)
    dialog.user["phone"] = update.message.text
    await send_text_buttons(
        update,
        context,
        "🔔 Чекаю на дзвінок – продовжимо телефоном\n✅ Продовжити – оформляємо заявку за допомогою бота",
        {
            "order_phone_call": "🔔 Чекаю на дзвінок",
            "order_phone_continue": "✅ Продовжити оформлення",
        },
        # columns=2,
    )


async def order_phone_button(update, context):
    # обробник кнопок після вводу телефону (продовжити або дзвінок)
    query = update.callback_query.data
    print("order_phone_button query: ", query)
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    if query == "order_phone_call":
        # Встановити фіктивні значення для решти полів і перейти до call_to_admin, щоб не ускладнювати діалог з користувачем, який вибрав дзвінок, додатковими питаннями
        dialog.user["massage_type"] = "на телефон"
        dialog.user["date_time"] = "за дзвінком"
        dialog.user["address"] = "за телефоном"
        dialog.user["comment"] = "чекаю на дзвінок"
        await call_to_admin(update, context)

    elif query == "order_phone_continue":
        await send_text_buttons(
            update,
            context,
            "Який вид масажу ви б хотіли?",
            BUTTONS_MASSAGE,
            # columns=3,
        )


async def day_time(update, context):
    await send_text(
        update,
        context,
        "Коли вам зручно? (День, час)\ud83d\ude4c \n\nНаприклад: \n\t\t'завтра після 18:00' \n\t\t  або 'щоп'ятниці вдень' \n\t\t  або 'на вихідних' і т.д.",
    )


async def order_case_3(update, context):  # massage_type + date_time
    dialog.user["massage_type"] = update.message.text
    await day_time(update, context)


async def order_massage_button(update, context):
    """Handle massage selection buttons, set `massage_type` and ask for date/time."""
    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    mapping = BUTTONS_MASSAGE

    choice = mapping.get(query, None)
    if choice is None:
        await send_text(update, context, "Невідомий вибір. Спробуйте ще раз.")
        return

    if query == list(BUTTONS_MASSAGE.keys())[-1]:  # якщо вибрали "Свій варіант"
        print("BUTTONS_MASSAGE query: ", query)
        await send_text(
            update, context, "Вкажіть, будь ласка, свої побажання щодо масажу:"
        )
    else:
        dialog.user["massage_type"] = choice

        await day_time(update, context)


async def order_case_4(update, context):  # date_time + address
    dialog.user["date_time"] = update.message.text
    await send_text(update, context, "Ваша адреса \ud83d\ude4c")


async def order_case_5(update, context):  # address + comment
    dialog.user["address"] = update.message.text
    await send_text(
        update,
        context,
        "Коментар, побажання (необов'язково) 🤔\nпросто напишіть '.' щоб пропустити",
    )


async def order_case_6(update, context):  # comment + call_to_admin
    # Коментар може бути пустим TODO: додати можливість пропустити коментар кнопкою, щоб не було проблем з markdown, якщо користувач введе лише крапку або інший символ, який використовується для пропуску
    skip_keywords = [".", "готово", "skip", "пропустити", "немає", "no"]
    if update.message.text.lower().strip() in skip_keywords:
        dialog.user["comment"] = ""
    else:
        dialog.user["comment"] = update.message.text

    await call_to_admin(update, context)


async def call_to_admin(update, context):
    # завершення оформлення замовлення
    await send_text(
        update,
        context,
        "Дякуємо за замовлення! \nМи зв'яжемося з вами найближчим часом \ud83d\ude4c",
    )

    # надсилаємо адміну повідомлення з інформацією про замовлення
    order_info = dialog_user_info_to_str(dialog.user)
    print("order_info: ", order_info)
    admin_message = f"📋 Нове замовлення масажу:\n\n{order_info}"
    await context.bot.send_message(chat_id=TELEGRAM_KYRYLO_ID, text=admin_message)
    # await context.bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=admin_message)


async def order(update, context):
    dialog.mode = "order"
    await header(update, context)

    dialog.user.clear()
    await order_case_0(update, context)


async def order_dialog(update, context):

    func = globals().get(f"order_case_{len(dialog.user)}")
    if func is not None:
        await func(update, context)
    else:
        print(f"order_case_{len(dialog.user)} not found")


async def gpt(update, context):
    dialog.mode = "gpt"
    await send_photo(update, context, "gpt")
    msg = load_message("gpt")
    await send_text(update, context, msg)


async def gpt_dialog(update, context):
    dialog.mode = "gpt"
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


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
    # elif dialog.mode == "main":
    #     await main_dialog(update, context)
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

    dialog = Dialog()

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
