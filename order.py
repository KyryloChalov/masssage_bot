from util import (
    header,
    send_text,
    send_text_buttons,
    dialog_user_info_to_str,
)

from buttons import BUTTONS_MAIN, BUTTONS_SERVICE, BUTTON_CERTIFICATE

from from_env import TELEGRAM_ADMIN_ID, TELEGRAM_KYRYLO_ID

UNKNOWN = "-< ❓❓❓ >-"


# =======================
# certificate order
# =======================
async def order_certificate(update, context):
    user_data = context.user_data

    if "order" not in user_data:
        user_data["order"] = {}

    context.user_data["mode"] = "certificate"
    await header(
        update,
        context,
        buttons=BUTTON_CERTIFICATE,
        columns=1,
    )


async def order_certificate_button(update, context):
    """CallbackQuery handler for the 'Замовити сертифікат' button."""
    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    if query == "order_certificate":
        await order_case_0(update, context)


async def order_choice_certificate(update, context):
    user_data = context.user_data

    context.user_data["mode"] = "certificate"
    user_data["order"]["massage_type"] = "+++ сертифікат 📄✍️"
    user_data["order"]["date_time"] = UNKNOWN
    user_data["order"]["address"] = UNKNOWN
    await send_text(
        update,
        context,
        "Коментар, побажання щодо сертифікату",
    )


# =======================
# order загальний
# =======================
async def order_main(update, context, from_service=False):
    user_data = context.user_data
    context.user_data["mode"] = "order"

    if "order" not in user_data:
        user_data["order"] = {}

    if not from_service:
        user_data["service"] = ""

    user_data["order"] = {}  #
    await header(update, context, from_service=from_service)  # show header again

    if not from_service:
        await order_case_0(update, context)


# загальний обробник для замовлення масажу і замовлення сертифікату(як окремий вид масажу)
# він буде викликатися при кожному повідомленні користувача,
# який знаходиться в режимі "order" або "certificate",
# і буде визначати, який саме кейс виконувати,
# в залежності від кількості вже зібраної інформації про замовлення
# (кількості полів в user_data["order"])
# --- також при виклику в режимі "massage" він має працювати коректно !!!
# наприклад, якщо користувач тільки що вибрав "Замовити масаж" і ввів своє ім'я,
# то в user_data["order"] буде тільки поле "name",
# і тоді виконається order_case_2,
# який запитає телефон і запропонує вибір між дзвінком і продовженням оформлення через бота.
# Якщо користувач вибрав "Продовжити оформлення", то наступним кроком буде вибір виду масажу,
# і тоді виконається order_case_3, який запитає про вид масажу і потім про день і час.
# І так далі, поки не буде зібрана вся необхідна інформація для замовлення.
# Таким чином, order_dialog є універсальним обробником для всього процесу оформлення замовлення,
# і він визначає, який саме крок виконувати, в залежності від того, яка інформація вже зібрана в user_data["order"].
# time -> name -> phone -> (дзвінок або <продовжити>) -> вид масажу -> день і час -> адреса -> коментар -> завершення замовлення
# time -> name -> phone -> (<дзвінок> або продовжити) -> завершення замовлення
# time -> name -> phone -> (context.user_data["mode"]=="certificate") -> коментар -> завершення замовлення
async def order_dialog(update, context):
    user_data = context.user_data
    if "order" not in user_data:
        user_data["order"] = {}
    func = globals().get(f"order_case_{len(user_data["order"])}")

    if func is not None:
        await func(update, context)
    else:
        print(f"order_case_{len(user_data["order"])} not found")


async def order_case_0(update, context):  # time + name
    # цей кейс потрібен, щоб одразу встановити час оформлення замовлення, не чекаючи вводу користувача
    # але виконуватися він буде тільки при виклику функції order(), а не при виклику order_dialog(), бо час встановлюється одразу при виклику функції order()
    from datetime import datetime

    user_data = context.user_data
    user_data["order"]["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await send_text(update, context, "Як до вас звертатися? \ud83d\ude4c")


async def order_case_1(update, context):  # name + phone
    user_data = context.user_data

    user_data["order"]["name"] = update.message.text
    await send_text(update, context, "Ваш номер телефону? \ud83d\ude4c")


async def order_case_2(update, context):
    user_data = context.user_data

    # phone + buttons (продовжити або дзвінок)
    user_data["order"]["phone"] = update.message.text

    if user_data["mode"] in ["certificate", "service_certificate"]:
        await order_choice_certificate(update, context)
    else:
        await send_text_buttons(
            update,
            context,
            "🔔 Чекаю на дзвінок – продовжимо телефоном\n✅ Продовжити – оформляємо заявку за допомогою бота",
            {
                "order_phone_call": "🔔 Чекаю на дзвінок",
                "order_phone_continue": "✅ Продовжити оформлення",
            },
        )


async def order_phone_button(update, context):
    user_data = context.user_data

    # обробник кнопок після вводу телефону (продовжити або дзвінок)
    query = update.callback_query.data
    try:
        await update.callback_query.answer()
    except Exception:
        pass

    if query == "order_phone_call":
        # Встановити фіктивні значення для решти полів і перейти до order_call_to_admin, щоб не ускладнювати діалог з користувачем, який вибрав дзвінок, додатковими питаннями
        if user_data["service"]:
            user_data["order"]["massage_type"] = user_data["service"]
        else:
            user_data["order"]["massage_type"] = UNKNOWN
        user_data["order"]["date_time"] = UNKNOWN
        user_data["order"]["address"] = UNKNOWN
        user_data["order"]["comment"] = "чекаю на дзвінок 📞->☎️"
        await order_call_to_admin(update, context)

    elif query == "order_phone_continue":
        if user_data["service"]:
            user_data["order"]["massage_type"] = user_data["service"]
            await order_day_time(update, context)
        else:
            await send_text_buttons(
                update,
                context,
                "Який вид масажу ви б хотіли?",
                BUTTONS_SERVICE,
            )


async def order_case_3(update, context):  # massage_type + date_time
    # вид масажу - при переході з переліку масажів ми вже знаємо вид масажу, це треба оформити
    user_data = context.user_data

    if user_data["mode"] in ["certificate", "service_certificate"]:
        await order_choice_certificate(update, context)

    else:
        try:
            user_data["order"]["massage_type"] = update.message.text
        except Exception:
            user_data["order"]["massage_type"] = (
                user_data["service"] if user_data["service"] else update.message.text
            )
        await order_day_time(update, context)


async def order_day_time(update, context):
    # питання про час і день масажу, виконується після вибору виду масажу або після вибору "Свій варіант"
    await send_text(
        update,
        context,
        "Коли вам зручно? (День, час)\ud83d\ude4c \n\nНаприклад: \n\t\t'завтра після 18:00' \n\t\t  або 'щоп'ятниці вдень' \n\t\t  або 'на вихідних' і т.д.",
    )


async def order_case_4(update, context):  # date_time + address
    user_data = context.user_data

    user_data["order"]["date_time"] = update.message.text
    await send_text(update, context, "Ваша адреса \ud83d\ude4c")


async def order_case_5(update, context):  # address + comment
    user_data = context.user_data

    user_data["order"]["address"] = update.message.text
    await send_text(
        update,
        context,
        "Коментар, побажання щодо масажу \ud83d\ude4c \n\nНаприклад: \n\t\t'хочу інтенсивний масаж обличчя' \n\t\t  або 'попередньо хочу консультацію'  і т.д.",
    )


async def order_case_6(update, context):  # comment + order_call_to_admin
    user_data = context.user_data

    user_data["order"]["comment"] = update.message.text

    await order_call_to_admin(update, context)


async def order_call_to_admin(update, context):
    user_data = context.user_data
    user = update.effective_user
    order_data = [user.full_name, user.username, user.id, user.is_bot]

    # завершення оформлення замовлення

    # 1. надсилаємо адміну повідомлення з інформацією про замовлення
    order_info = dialog_user_info_to_str(user_data["order"])
    admin_message = f"📋 Нове замовлення масажу:\n {order_data}\n\n{order_info}"
    await context.bot.send_message(chat_id=TELEGRAM_KYRYLO_ID, text=admin_message)
    # await context.bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=admin_message)

    # 2. надсилаємо користувачу повідомлення про успішне оформлення замовлення
    context.user_data["mode"] = "thanks"
    await header(update, context, buttons=BUTTONS_MAIN)
