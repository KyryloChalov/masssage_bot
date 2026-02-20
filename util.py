from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    BotCommand,
    MenuButtonCommands,
    BotCommandScopeChat,
    MenuButtonDefault,
)
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# import phonenumbers
from phonenumbers import (
    NumberParseException,
    PhoneNumberMatcher,
    PhoneNumberFormat,
    is_valid_number,
    format_number,
)
import re

from pprint import pprint

from colors import RED, RESET, YELLOW, LIGHTBLUE


# =======================
# Допоміжні functions
# =======================
# декоратор щоб побачити user_data на початку та після виконання функції
def log_decorator(func):
    def wrapper(update, context, *args, **kwargs):
        # print(f"func {func.__name__} args {args} kwargs {kwargs}")
        print(f"{LIGHTBLUE}<<< {YELLOW}{func.__name__} {LIGHTBLUE}>>> {RESET}")
        # print(f"\t begin: {context}")
        print(f"\t begin: {context.user_data}")
        print(f"\t  args: {args}")
        # print(f"\tkwargs: {kwargs}")

        result = func(update, context, *args, **kwargs)

        print(f"\t   end: {context.user_data}")
        # print(f"        update: {update}")
        return result

    return wrapper

@log_decorator
async def init_user_date(update, context):
    user_data = context.user_data
    user_data["service"] = ""
    user_data["mode"] = ""
    user_data["order"] = {}
    user_data["gpt_history"] = []
    user_data["full_history"] = []


# формує header: фото + текст + кнопки
# TODO зробити single response
@log_decorator
async def header(
    update, context, from_service=False, buttons: dict = {}, columns: int = 2
):
    user_data = context.user_data

    await send_photo(update, context, user_data["mode"])

    if "gpt_history" not in user_data:
        user_data["gpt_history"] = []
    if not from_service:
        user_data["service"] = ""
        user_data["order"] = {}

    # print("header >>> context.user_data: ", user_data) # debug

    msg = load_message(context.user_data["mode"])
    if buttons == {}:
        await send_text(update, context, msg)
    else:
        await send_text_buttons(update, context, msg, buttons, columns=columns)


async def set_mode(mode_name, update, context):
    context.user_data["mode"] = mode_name
    await header(update, context)


# конвертує об'єкт user в рядок
def dialog_user_info_to_str(user) -> str:
    result = ""
    map = {
        "time": "+",
        "name": "Ім'я",
        "phone": "Номер телефону",
        "massage_type": "Вид масажу",
        "date_time": "Час та дата масажу",
        "address": "Адреса",
        "comment": "Коментар",
    }
    for key, name in map.items():
        if key in user:
            result += name + ": " + user[key] + "\n"
    return result


def extract_phone(text: str, region="UA"):
    """
    Повертає номер у форматі +380XXXXXXXXX
    або None якщо номер невалідний
    """
    try:
        for match in PhoneNumberMatcher(text, region):
            number = match.number

            # перевірка валідності
            if is_valid_number(number):
                # повертаємо у міжнародному форматі
                return format_number(number, PhoneNumberFormat.E164)

    except NumberParseException:
        return None

    return None


def normalize_phone(phone_raw: str) -> str:

    # патерн українського телефону
    # phone_pattern = r"(\+?38)?[\s\-()]*0\d{2}[\s\-()]*\d{3}[\s\-()]*\d{2}[\s\-()]*\d{2}"
    # phone_match = re.search(phone_pattern, user_text)

    # # якщо телефон знайдено → це замовлення
    # if phone_match:
    #     raw_phone = phone_match.group()
    #     phone = normalize_phone(raw_phone)
    # ===========================================================
    # залишаємо тільки цифри
    digits = re.sub(r"\D", "", phone_raw)

    # якщо номер починається з 0 → додаємо 38
    if digits.startswith("0"):
        digits = "38" + digits

    # якщо починається з 380 → ок
    if digits.startswith("380"):
        return "+" + digits

    return None


# надсилає в чат текстове повідомлення
async def send_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
) -> Message:
    if text.count("_") % 2 != 0:
        message = f"Рядок '{text}' є невалідним з погляду markdown. Скористайтеся методом send_html()"
        print(message)
        return await update.effective_message.reply_text(message)

    text = text.encode("utf16", errors="surrogatepass").decode("utf16")
    return await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN
    )


# надсилає в чат html-повідомлення
async def send_html(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
) -> Message:
    text = text.encode("utf16", errors="surrogatepass").decode("utf16")
    return await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML
    )


# надсилає в чат текстове повідомлення та додає до нього кнопки
async def send_text_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = "",
    buttons: dict = {},
    columns: int = 2,
) -> Message:
    text = text.encode("utf16", errors="surrogatepass").decode("utf16")
    keyboard = []
    row = []
    for i, (key, value) in enumerate(buttons.items()):
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        row.append(button)
        # when row is full, push it to keyboard and start a new row
        if (i + 1) % columns == 0:
            keyboard.append(row)
            row = []
    # append any remaining buttons
    if row:
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    # reply in a way that works for both message and callback_query contexts
    if getattr(update, "effective_message", None) is not None:
        return await update.effective_message.reply_text(
            text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )
    # fallback to bot.send_message when no message object is available
    chat_id = None
    if getattr(update, "effective_chat", None) is not None:
        chat_id = update.effective_chat.id
    elif getattr(update, "message", None) is not None:
        chat_id = update.message.chat.id
    if chat_id is not None:
        return await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    # last resort: raise informative error
    raise RuntimeError("No chat/message available to send buttons reply")


# надсилає в чат фото
async def send_photo(
    update: Update, context: ContextTypes.DEFAULT_TYPE, name: str
) -> Message:
    with open("resources/images/" + name + ".jpg", "rb") as photo:
        return await context.bot.send_photo(
            chat_id=update.effective_chat.id, photo=photo
        )


# відображає команди та головне меню
async def show_main_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict
):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(
        command_list, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )
    await context.bot.set_chat_menu_button(
        menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id
    )


# приховує команди та головне меню
async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )
    await context.bot.set_chat_menu_button(
        menu_button=MenuButtonDefault(), chat_id=update.effective_chat.id
    )


# завантажує повідомлення з папки /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


# завантажує промпт з папки /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()
