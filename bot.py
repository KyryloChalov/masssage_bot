from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

TOKEN_TELEGRAM = '8447443613:AAE1Rb5onp05S6kdzd9Uzm68tP2MG24BuYY'
TOKEN_GPT = 'javcgk/s3WVH1V/3/eY+dOWWa+jvSy1lakmEGDVwq1h8XG3bvDbbBufJJRs/pGrIDgVhny5Qag1p3K8y+oGQU63QPq/fboIxvJ4mWTNtgIoURRvFdbWYXH1labl8JDmWT3NzSRnQIdxjFkbVj3g8fT19j15aM3UaKZYyeEcjXr01VSj3XHOhnumhEb+6+T71NKnk7rSZF/y42jb6LiZcPWoa5CqlyR0o6kXRXqzr7DWNDuQEQ='

bot = Bot(TOKEN_TELEGRAM)


async def start(update, context):
    dialog.mode = "main"
    msg = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, msg)
    await show_main_menu(update, context, {
        "start": "головне меню бота",
        "profile": "генерація Tinder - профілю 😎",
        "opener": "повідомлення для знайомства 🥰",
        "message": "листування від вашого імені 😈",
        "date": "листування із зірками 🔥",
        "gpt": "задати питання чату GPT 🧠"
    })


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
    await send_text_buttons(update, context, msg, {
    "date_grande": "Аріана Гранде",
    "date_robbie": "Марго Роббі",
    "date_zendaya": "Зендея",
    "date_gosling": "Райан Гослінг",
    "date_hardy": "Том Харді",
    })


async def date_button(update, context):
    dialog.mode = "date"
    text = "Гарний вибір! \uD83D\uDE05 \nВаше завдання - запросити зірку на побачення за 5 повідомлень ❤️"
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
    await send_text_buttons(update, context, msg, {
        "message_next": "Написати повідомлення",
        "message_date": "Запросити на побачення",
    })
    dialog.list.clear()


async def message_dialog(update, context):
    dialog.mode = "message"
    text = update.message.text
    dialog.list.append(text)


async def message_button(update, context):
    dialog.mode = "message"
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)

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

        my_message = await send_text(update, context, "Чат GPT 🧠 генерує ваш профіль. Зачекайте трошки")
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
        my_message = await send_text(update, context, "Чат GPT 🧠 генерує ваше повідомлення. Зачекайте трошки")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "Привіт!")
        await send_text(update, context, "Ти написав: " + update.message.text)

# async def buttons_handler(update, context):
#     query = update.callback_query.data
#     if query == "start":
#         await send_text(update, context, "Started")
#     elif query == "stop":
#         await send_text(update, context, "Stopped")

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user = {}
dialog.counter = 0

chatgpt = ChatGptService(token=TOKEN_GPT)

app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.run_polling()
