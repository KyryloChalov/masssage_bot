# from telegram import Bot
# from telegram.ext import (
#     ApplicationBuilder,
#     MessageHandler,
#     filters,
#     CallbackQueryHandler,
#     CommandHandler,
# )


import os
from dotenv import load_dotenv


from gpt import *

# from gpt import ChatGptService
from util import (
    header,
    # load_message,
    # load_prompt,
    send_text,
    # send_photo,
    send_text_buttons,
    dialog_user_info_to_str,
    # show_main_menu,
    dialog,
)

from buttons import BUTTONS_MASSAGE

load_dotenv()
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
TELEGRAM_KYRYLO_ID = int(os.getenv("TELEGRAM_KYRYLO_ID", "0"))


async def order(update, context):
    dialog.mode = "order"
    await header(update, context)

    await order_case_0(update, context)


async def order_dialog(update, context):
    func = globals().get(f"order_case_{len(dialog.user)}")
    if func is not None:
        await func(update, context)
    else:
        print(f"order_case_{len(dialog.user)} not found")


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
        # Встановити фіктивні значення для решти полів і перейти до order_call_to_admin, щоб не ускладнювати діалог з користувачем, який вибрав дзвінок, додатковими питаннями
        dialog.user["massage_type"] = "на телефон"
        dialog.user["date_time"] = "за дзвінком"
        dialog.user["address"] = "за телефоном"
        dialog.user["comment"] = "чекаю на дзвінок"
        await order_call_to_admin(update, context)

    elif query == "order_phone_continue":
        await send_text_buttons(
            update,
            context,
            "Який вид масажу ви б хотіли?",
            BUTTONS_MASSAGE,
            # columns=3,
        )


async def order_day_time(update, context):
    await send_text(
        update,
        context,
        "Коли вам зручно? (День, час)\ud83d\ude4c \n\nНаприклад: \n\t\t'завтра після 18:00' \n\t\t  або 'щоп'ятниці вдень' \n\t\t  або 'на вихідних' і т.д.",
    )


async def order_case_3(update, context):  # massage_type + date_time
    dialog.user["massage_type"] = update.message.text
    await order_day_time(update, context)


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
        await order_day_time(update, context)


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


async def order_case_6(update, context):  # comment + order_call_to_admin
    # Коментар може бути пустим TODO: додати можливість пропустити коментар кнопкою, щоб не було проблем з markdown, якщо користувач введе лише крапку або інший символ, який використовується для пропуску
    if len(update.message.text.strip()) == 1 or update.message.text.strip() in [
        "готово",
        "skip",
        "пропустити",
        "немає",
        "no",
    ]:
        dialog.user["comment"] = "-"
    else:
        dialog.user["comment"] = update.message.text

    await order_call_to_admin(update, context)


async def order_call_to_admin(update, context):
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

    dialog.mode = "main"
    await header(update, context)
