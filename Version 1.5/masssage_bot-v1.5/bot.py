from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from gpt import handle_gpt

from util import (
    header,
    set_mode,
    send_text,
    send_html,
    show_main_menu,
    init_user_date,
    log_decorator
)
from order import (
    order_main,
    order_dialog,
    order_phone_button,
    order_certificate,
    order_certificate_button,
)
from buttons import (
    # BUTTONS_HELPER,
    # BUTTONS_HELPER_2,
    BUTTONS_MAIN,
    BUTTONS_ORDER_SERVICE,
    MODE_MAPPING,
    BUTTONS_MENU,
    # FAQ,
    FAQ_ANSWERS,
    FAQ_QUESTIONS,
    BUTTONS_SERVICE,
)

from from_env import TOKEN_TELEGRAM


# =======================
# CONSTANTS
# =======================

UNAVAILABLE = "Вибачте, вибір недоступний."


# =======================
# Button mapping
# =======================
async def main_button(update, context):
    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    mode = MODE_MAPPING.get(query)
    context.user_data["mode"] = mode
    if mode:
        if mode == "order":
            await order_main(update, context)
        elif mode == "info":
            await info(update, context)
        elif mode == "certificate":
            await order_certificate(update, context)
        elif mode == "massage":
            await massage(update, context)
        # elif mode == "helper":
        #     await helper(update, context)
        else:
            await set_mode(mode, update, context)
    else:
        await handle_gpt(update, context)


# =======================
# Info (FAQ) - найчастіші запитання ++
# =======================
#  TODO почистити тексти відповідей - там багато рудиментів, що залишилися від сайту
async def info(update, context):  # Найчастіші запитання
    context.user_data["mode"] = "info"

    # ask user to choose a question and show inline buttons
    await header(update, context, buttons=FAQ_QUESTIONS, columns=1)


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
            answer = f"*{question}*\n=====\n{answer}"
        await info(update, context)  # show header again
        await send_text(update, context, answer)
    else:
        await send_text(update, context, UNAVAILABLE)


# =======================
# Massage selection
# =======================
async def massage(update, context):
    context.user_data["mode"] = "massage"
    await header(update, context, from_service=True, buttons=BUTTONS_SERVICE)


async def services_button(update, context):
    user_data = context.user_data
    print("services_button 1 >>> user_data: ", user_data)

    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    service = BUTTONS_SERVICE.get(query)
    if service:
        user_data["mode"] = query
        user_data["service"] = service
        await header(update, context, from_service=True, buttons=BUTTONS_ORDER_SERVICE)
    else:
        await send_text(update, context, UNAVAILABLE)
        # user_data["service"] = ""

    print("services_button 2 >>> user_data: ", user_data)


async def choice_button(update, context):
    user_data = context.user_data

    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    if query == "choice_service":
        await order_dialog(update, context)
    elif query == "choice_go_back":
        user_data["service"] = ""
        user_data["mode"] = "massage"
        await massage(update, context)
    else:
        await send_text(update, context, UNAVAILABLE)


# # =======================
# # Helper
# # =======================
# async def helper(update, context):
#     context.user_data["mode"] = "helper"

#     await header(update, context, buttons=BUTTONS_HELPER, columns=1)


# async def helper_2(update, context):
#     context.user_data["mode"] = "helper"

#     await header(update, context, buttons=BUTTONS_HELPER, columns=1)
# # TODO зразок на сайті https://home.masssage.kyiv.ua/services/assistant.php?lang=ua


# =======================
# Command handlers
# =======================
@log_decorator
async def start(update, context):
    await init_user_date(update, context)
    context.user_data["mode"] = "main"
    await header(update, context, buttons=BUTTONS_MAIN)

    await show_main_menu(update, context, BUTTONS_MENU)


@log_decorator
async def hello(update, context):
    user_data = context.user_data

    print('hello >>> user_data["mode"]: ', user_data["mode"])
    if user_data["mode"] in ["gpt", "main"]:
        await handle_gpt(update, context)
    elif user_data["mode"] in [
        "order",
        "certificate",
        "massage",
    ] or user_data[
        "mode"
    ].startswith("service_"):
        await order_dialog(update, context)
    else:
        await send_text(update, context, f"Вітаю! \nТи написав: {update.message.text}")


# =======================
# Telegram bot setup
# =======================
if __name__ == "__main__":
    print("🤖 bot starting...")

    bot = Bot(str(TOKEN_TELEGRAM))
    app = ApplicationBuilder().token(str(TOKEN_TELEGRAM)).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gpt", handle_gpt))
    app.add_handler(CommandHandler("order", order_main))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("certificate", order_certificate))
    app.add_handler(CommandHandler("massage", massage))
    # app.add_handler(CommandHandler("helper", helper))

    # Other modes
    app.add_handler(CommandHandler("location", lambda u, c: set_mode("location", u, c)))
    app.add_handler(CommandHandler("time", lambda u, c: set_mode("time", u, c)))
    app.add_handler(CommandHandler("price", lambda u, c: set_mode("price", u, c)))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))
    app.add_handler(CallbackQueryHandler(order_phone_button, pattern="^order_phone_.*"))
    # app.add_handler(CallbackQueryHandler(order_massage_button, pattern="^massage_.*"))
    app.add_handler(CallbackQueryHandler(faq_button, pattern="^faq_.*"))
    app.add_handler(CallbackQueryHandler(services_button, pattern="^service_.*"))
    app.add_handler(
        CallbackQueryHandler(order_certificate_button, pattern="^order_certificate$")
    )
    app.add_handler(CallbackQueryHandler(choice_button, pattern="^choice_.*"))
    # app.add_handler(CallbackQueryHandler(helper, pattern="^helper_.*"))

    app.run_polling()
