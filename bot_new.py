import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from openai import RateLimitError
from gpt import ChatGptService
from util import (
    header,
    send_text,
    send_html,
    show_main_menu,
    dialog,
)
from order_util import (
    order,
    order_dialog,
    order_phone_button,
    order_massage_button,
    order_certificate,
    order_certificate_button,
)
from buttons import BUTTONS_MAIN, BUTTONS_MENU, BUSINESS_INFO, SYSTEM_PROMPT, FAQ

# =======================
# Load API keys
# =======================
load_dotenv()
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
TOKEN_GPT = os.getenv("TOKEN_GPT")


# =======================
# Допоміжні functions
# =======================
async def set_mode(mode_name, update, context):
    dialog.mode = mode_name
    await header(update, context)


async def handle_gpt(update, context):
    dialog.mode = "gpt"
    user_text = update.message.text
    dialog.list_.append(user_text)

    # обмежуємо історію до останніх 10 повідомлень
    MAX_HISTORY = 5
    dialog.list_ = dialog.list_[-MAX_HISTORY:]

    user_history = "\n\n".join(dialog.list_)

    input_text = f"""
ІНФОРМАЦІЯ ПРО СЕРВІС:
{BUSINESS_INFO}

ІСТОРІЯ ПИТАНЬ КЛІЄНТА:
{user_history}

ПИТАННЯ КЛІЄНТА:
{user_text}
"""
    try:
        my_message = await send_text(update, context, " . . . ")
        answer = await chatgpt.send_question(SYSTEM_PROMPT, input_text, max_tokens=300)
        await my_message.edit_text(answer)
    except RateLimitError:
        await send_text(
            update, context, "Зараз дуже багато запитів. Спробуйте через кілька секунд."
        )
    except Exception as e:
        await send_text(update, context, f"Виникла помилка: {e}")


# =======================
# Button mapping
# =======================
MODE_MAPPING = {
    "main_helper": "helper",
    "main_price": "price",
    "main_location": "location",
    "main_info": "info",
    "main_order": "order",
    "main_types": "massage",
    "main_certificate": "certificate",
}


async def main_button(update, context):
    query = update.callback_query.data
    print(">>>>>> main_button >>>>>>> query:", query) # debug
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    mode = MODE_MAPPING.get(query)
    dialog.mode = mode
    print('mode: ', mode)
    if mode:
        if mode == "order":
            await order(update, context)
        elif mode == "info":
            await info(update, context)
        elif mode == "certificate":
            await order_certificate(update, context)
        else:
            await set_mode(mode, update, context)
    else:
        await handle_gpt(update, context)


# mapping from callback_data -> answer text for FAQ buttons
FAQ_ANSWERS = {f"faq_{i}": value for i, (key, value) in enumerate(FAQ.items())}
FAQ_QUESTIONS = {f"faq_{i}": key for i, (key, value) in enumerate(FAQ.items())}


async def faq_button(update, context):
    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    answer = FAQ_ANSWERS.get(query)
    if answer:
        question = FAQ_QUESTIONS.get(query)
        if question:
            answer = f"<b>{question}</b>\n=====\n{answer}"
            # await send_html(update, context, f"<b>{question}</b>")
        await info(update, context)  # show header again
        await send_html(update, context, answer)
    else:
        await send_text(update, context, "Вибачте, відповідь недоступна.")


# =======================
# Command handlers
# =======================
async def start(update, context):
    dialog.mode = "main"
    await header(update, context, BUTTONS_MAIN)
    await show_main_menu(update, context, BUTTONS_MENU)


async def hello(update, context):
    if dialog.mode in ["gpt", "main"]:
        await handle_gpt(update, context)
    elif dialog.mode in ["order", "certificate"]:
        await order_dialog(update, context)
    else:
        await send_text(update, context, f"Привіт! \nТи написав: {update.message.text}")


async def info(update, context):
    dialog.mode = "info"

    # build buttons mapping: callback_data -> question text
    buttons = {f"faq_{i}": question for i, (question, _) in enumerate(FAQ.items())}

    # ask user to choose a question and show inline buttons
    await header(update, context, buttons=buttons, columns=1)


# =======================
# Telegram bot setup
# =======================
if __name__ == "__main__":
    print("bot starting... \ndialog:", dialog.mode, dialog.list_, dialog.user)

    bot = Bot(str(TOKEN_TELEGRAM))
    chatgpt = ChatGptService(token=TOKEN_GPT)
    app = ApplicationBuilder().token(str(TOKEN_TELEGRAM)).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gpt", handle_gpt))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("certificate", order_certificate))

    # Other modes
    # app.add_handler(CommandHandler("info", lambda u, c: set_mode("info", u, c)))
    app.add_handler(CommandHandler("location", lambda u, c: set_mode("location", u, c)))
    # app.add_handler(CommandHandler("place", lambda u, c: set_mode("place", u, c)))
    app.add_handler(CommandHandler("time", lambda u, c: set_mode("time", u, c)))
    app.add_handler(CommandHandler("massage", lambda u, c: set_mode("massage", u, c)))
    app.add_handler(CommandHandler("helper", lambda u, c: set_mode("helper", u, c)))
    app.add_handler(CommandHandler("price", lambda u, c: set_mode("price", u, c)))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))
    app.add_handler(CallbackQueryHandler(order_phone_button, pattern="^order_phone_.*"))
    app.add_handler(CallbackQueryHandler(order_massage_button, pattern="^massage_.*"))
    app.add_handler(CallbackQueryHandler(faq_button, pattern="^faq_.*"))
    app.add_handler(CallbackQueryHandler(order_certificate_button, pattern="^order_certificate$"))
    app.add_handler(CallbackQueryHandler(order_certificate, pattern="^order_certificate_.*"))

    app.run_polling()
