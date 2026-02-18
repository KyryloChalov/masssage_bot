from openai import OpenAI, RateLimitError

from util import send_text

from util import send_text, send_photo
from sys_prompt import BUSINESS_INFO, SYSTEM_PROMPT
from from_env import TOKEN_GPT, TELEGRAM_KYRYLO_ID, TELEGRAM_ADMIN_ID, ADMIN_CHAT_IDS
from datetime import datetime

import json
import re
import time

# import phonenumbers
from phonenumbers import (
    NumberParseException,
    PhoneNumberMatcher,
    PhoneNumberFormat,
    is_valid_number,
    format_number,
)

MAX_HISTORY = 10  # обмежуємо історію повідомлень до останніх 10 повідомлень
ORDER_COOLDOWN = 300  # 5 хвилин
CONFIRM_MESSAGE = "Дякую! Передаю інформацію менеджеру.\n\n>>> Очікуйте на дзвінок 📞"
last_orders = {}


class ChatGptService:
    client: OpenAI
    message_list: list

    def __init__(self, token):
        self.client = OpenAI(base_url="https://openai.javarush.com/v1", api_key=token)
        self.message_list = []

    async def send_message_list(self, max_tokens=3000) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o",  # gpt-4o,  gpt-4-turbo,    gpt-3.5-turbo
            messages=self.message_list,
            max_tokens=max_tokens,
            temperature=0.9,
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return str(message.content)

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(
        self, prompt_text: str, message_text: str, max_tokens: int = 3000
    ) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        result = await self.send_message_list(max_tokens=max_tokens)
        return normalize_answer(result)


chatgpt = ChatGptService(token=TOKEN_GPT)


def normalize_answer(answer_raw):
    if isinstance(answer_raw, dict):
        return answer_raw.get("message")
    elif isinstance(answer_raw, str):
        try:
            data = json.loads(answer_raw)
            return data.get("message")
        except json.JSONDecodeError:
            return answer_raw  # рядок не JSON, просто друкуємо


async def handle_gpt(update, context):

    user = update.effective_user
    user_text = update.message.text.strip()
    user_data = context.user_data

    # print("handle_gpt: >>> user_data: ", user_data) # debug

    if "gpt_history" not in user_data:
        user_data["gpt_history"] = []
    user_data["mode"] = "gpt"
    user_data["gpt_history"].append(user_text)

    if "full_history" not in user_data:
        user_data["full_history"] = []
        # показати заставку при першому явному запуску /gpt
        await send_photo(update, context, "gpt")

    # повна історія діалогу - додаємо питання юзера
    user_data["full_history"].append(user_text)

    # print("user_data: ", user_data)  # debug

    # зберігаємо та обмежуємо історію юзера
    user_data["gpt_history"] = user_data["gpt_history"][-MAX_HISTORY:]
    user_history = "\n\n".join(user_data["gpt_history"])

    input_text = f"""
ІНФОРМАЦІЯ ПРО СЕРВІС:{BUSINESS_INFO}
ІСТОРІЯ ПИТАНЬ КЛІЄНТА:{user_history}
ПИТАННЯ КЛІЄНТА:{user_text}
"""

    try:
        my_message = await send_text(update, context, " . . . ")

        phone = extract_phone(user_text)

        if phone:
            now = time.time()
            user_id = user.id

            full_history = "\n- ".join(user_data["full_history"])
            full_history = full_history + "\n<<H.M>> " + CONFIRM_MESSAGE

            order_data = {
                "name": user.full_name,
                "username": user.username,
                "user_id": user.id,
                "phone": phone,
                "dialog": full_history,
            }

            if user_id in last_orders:
                if now - last_orders[user_id] < ORDER_COOLDOWN:
                    await my_message.edit_text(
                        "Ваше замовлення вже передано менеджеру 🙌\nОчікуйте дзвінка."
                    )
                    return

            last_orders[user_id] = now

            save_order_to_file(order_data)
            await notify_admin(context, order_data)

            await my_message.edit_text(CONFIRM_MESSAGE)

            # очищаємо діалог щоб не тригерити повторно
            user_data["gpt_history"] = []
            user_data["full_history"] = []
            user_data["mode"] = "main"

            return

        # якщо це не замовлення → працюємо через GPT
        # ---------- GPT RESPONSE ----------
        answer = await chatgpt.send_question(SYSTEM_PROMPT, input_text, max_tokens=300)

        # повна історія діалогу - додаємо Відповідь системи
        user_data["full_history"].append("<<H.M>> " + answer)

        await my_message.edit_text(answer)

    except RateLimitError:
        await send_text(
            update,
            context,
            "Зараз надто багато запитів. Спробуйте через кілька секунд.",
        )
    except Exception as e:
        await send_text(update, context, f"Виникла помилка: {e}")


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


async def notify_admin(context, order_data):

    message = f"""
🚀 СТАТУС: GPT режим
🆕 НОВЕ GPT-ЗАМОВЛЕННЯ

👤 Ім'я: {order_data.get("name")}
📎 Username: @{order_data.get("username")}
🆔 ID: {order_data.get("user_id")}
📞 Телефон: {order_data.get("phone")}

💬 Останній діалог:
{order_data.get("dialog")}
"""
    await context.bot.send_message(chat_id=TELEGRAM_KYRYLO_ID, text=message)

    # кілька адміністраторів - на майбутнє
    # for admin_id in ADMIN_CHAT_IDS:
    #     await context.bot.send_message(
    #         chat_id=admin_id,
    #         text=message
    #     )


def save_order_to_file(order_data):
    order_data["created_at"] = datetime.now().isoformat()

    with open("orders_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(order_data, ensure_ascii=False) + "\n")
