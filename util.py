from telegram import (
    Chat,
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

from deco import log_decorator


# конвертує об'єкт user в рядок
def dialog_user_info_to_str(user) -> str:
    result = ""
    map = {
        "time": "Від",
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


# @log_decorator
# надсилає в чат текстове повідомлення
async def send_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
) -> Message:
    if text.count("_") % 2 != 0:
        message = f"Рядок '{text}' є невалідним з погляду markdown. Скористайтеся методом send_html()"
        print(message)
        return await update.effective_message.reply_text(message)

    # print(update.effective_chat.first_name)
    # print(update.effective_chat)
    # print(update.effective_message)
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
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict, columns: int = 2
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
            chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
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


class Dialog:
    mode: str
    list_: list
    user: dict
    counter: int

    def __init__(self):
        self.mode = ""
        self.list_ = []
        self.user = {}
        self.counter = 0
