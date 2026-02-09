from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CommandHandler,
)

# from gpt import *
from gpt import ChatGptService
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


async def start(update, context):
    dialog.mode = "main"
    msg = load_message("main")
    await send_photo(update, context, "main")
    # await send_text(update, context, msg)
    await send_text_buttons(
        update,
        context,
        msg,
        {
            "main_order": "Замовити масаж",
            "main_help": "Допомога у виборі масажу",
            "main_price": "Розклад роботи та ціни",
            "main_location": "Де ми працюємо",
            "main_info": "Інформація про Home.Masssage",
        },
    )

    await show_main_menu(
        update,
        context,
        {
            "start": "головне меню бота",
            "profile": "генерація Tinder - профілю 😎",
            "opener": "повідомлення для знайомства 🥰",
            "message": "листування від вашого імені 😈",
            "date": "листування із зірками 🔥",
            "gpt": "задати питання чату GPT 🧠",
        },
    )


async def main_dialog(update, context):
    dialog.mode = "main"
    text = update.message.text
    print("text: ", text)
    dialog.list_.append(text)


async def main_button(update, context):
    dialog.mode = "main"
    query = update.callback_query.data
    print(">>>>>>>>>>>>>>>>>> query: ", query, " <<<<<<<<<<<<<<<<<<")
    await update.callback_query.answer()

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


async def order(update, context):
    dialog.mode = "order"
    msg = load_message("order")
    await send_photo(update, context, "order")
    await send_text(update, context, msg)
    dialog.list_.clear()
    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Як до вас звертатися? \ud83d\ude4c")


async def order_dialog(update, context):
    dialog.mode = "order"
    text = update.message.text
    # print("text: ", text)
    # dialog.list_.append(text)
    dialog.counter += 1
    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Ваш номер телефону? \ud83d\ude4c")
    elif dialog.counter == 2:
        dialog.user["phone"] = text
        await send_text(
            update, context, "Який вид масажу ви хочете замовити? \ud83d\ude4c"
        )
    elif dialog.counter == 3:
        dialog.user["massage_type"] = text
        await send_text(update, context, "Коли вам зручно? (День, час)\ud83d\ude4c")
    elif dialog.counter == 4:
        dialog.user["date_time"] = text
        await send_text(update, context, "Ваша адреса \ud83d\ude4c")
    elif dialog.counter == 5:
        dialog.user["address"] = text
        await send_text(update, context, "Коментар, побажання (необов'язково) 🤔\nЛи напишіть 'готово' щоб пропустити")
    elif dialog.counter == 6:
        # Коментар може бути пустим
        skip_keywords = ["готово", "skip", "пропустити", "немає", "no"]
        if text.lower().strip() in skip_keywords:
            dialog.user["comment"] = ""
        else:
            dialog.user["comment"] = text
        
        await send_text(
            update,
            context,
            "Дякуємо за замовлення! Ми зв'яжемося з вами найближчим часом \ud83d\ude4c",
        )

        # Надсилаємо дані замовлення адміну
        order_info = dialog_user_info_to_str(dialog.user)
        print("order_info: ", order_info)
        admin_message = f"📋 Нове замовлення масажу:\n\n{order_info}"
        await context.bot.send_message(chat_id=TELEGRAM_KYRYLO_ID, text=admin_message)
        await context.bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=admin_message)

        dialog.counter = 0
        dialog.user.clear()

    # print("dialog.user: ", dialog.user)


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


async def date(update, context):
    dialog.mode = "date"
    msg = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(
        update,
        context,
        msg,
        {
            "date_grande": "Аріана Гранде",
            "date_robbie": "Марго Роббі",
            "date_zendaya": "Зендея",
            "date_gosling": "Райан Гослінг",
            "date_hardy": "Том Харді",
        },
    )


async def date_button(update, context):
    dialog.mode = "date"
    text = "Гарний вибір! \ud83d\ude05 \nВаше завдання - запросити зірку на побачення за 5 повідомлень ❤️"
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, text)
    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def date_dialog(update, context):
    dialog.mode = "date"
    text = update.message.text
    my_message = await send_text(update, context, "Друкує...")
    answer = await chatgpt.add_message(text)
    # await send_text(update, context, answer)
    await my_message.edit_text(answer)


async def message(update, context):
    dialog.mode = "message"
    msg = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(
        update,
        context,
        msg,
        {
            "message_next": "Написати повідомлення",
            "message_date": "Запросити на побачення",
        },
        columns=1,
    )
    dialog.list_.clear()


async def message_dialog(update, context):
    dialog.mode = "message"
    text = update.message.text
    print("text: ", text)
    dialog.list_.append(text)


async def message_button(update, context):
    dialog.mode = "message"
    query = update.callback_query.data
    print("query: ", query)
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list_)

    my_message = await send_text(update, context, "Думаю...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def profile(update, context):
    dialog.mode = "profile"
    msg = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Скільки вам років?")


async def profile_dialog(update, context):
    dialog.mode = "profile"
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Ким ви працюєте?")
    if dialog.counter == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "У вас є хобі?")
    if dialog.counter == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Що вам не подобається в людях?")
    if dialog.counter == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Мета знайомства")
    if dialog.counter == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)
        # print("user_info: ", user_info)

        my_message = await send_text(
            update, context, "Чат GPT 🧠 генерує ваш профіль. Зачекайте трошки"
        )
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = "opener"
    msg = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Ім'я партнера")


async def opener_dialog(update, context):
    dialog.mode = "opener"
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Скільки років?")
    if dialog.counter == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцініть зовнішність: 1-10 балів")
    if dialog.counter == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Ким працює?")
    if dialog.counter == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Мета знайомства")
    if dialog.counter == 5:
        dialog.user["goals"] = text

        prompt = load_prompt("opener")

        user_info = dialog_user_info_to_str(dialog.user)
        my_message = await send_text(
            update, context, "Чат GPT 🧠 генерує ваше повідомлення. Зачекайте трошки"
        )
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "main":
        await main_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("date", date))
    app.add_handler(CommandHandler("message", message))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("opener", opener))
    app.add_handler(CommandHandler("order", order))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
    app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
    app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))

    app.run_polling()
