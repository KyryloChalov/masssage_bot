from phonenumbers import (
    NumberParseException,
    PhoneNumberMatcher,
    PhoneNumberFormat,
    is_valid_number,
    format_number,
)
import re

import inspect

from datetime import datetime

from pprint import pprint

from include.colors import RED, RESET, YELLOW, LIGHTBLUE


# =======================
# Допоміжні functions
# =======================
# декоратор щоб побачити user_data на початку та після виконання функції
def log_decorator(func, echo=False):
    # def wrapper(update, context, *args, **kwargs):
    def wrapper(*args, **kwargs):
        print(f"{LIGHTBLUE}<<< {YELLOW}{func.__name__} {LIGHTBLUE}>>> {RESET}")
        # if echo:
        #     print(f"\t begin: {context.user_data}")
        #     print(f"\t  args: {args}")
        # print(f"\tkwargs: {kwargs}")

        # result = func(update, context, *args, **kwargs)
        result = func(*args, **kwargs)
        # if echo:
        #     print(f"\t   end: {context.user_data}")
        return result

    return wrapper


# вже не треба???
def caller_name():
    return inspect.stack()[2].function


# конвертує об'єкт user в рядок
@log_decorator
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


# замість normalize_phone поставити цю
@log_decorator
def extract_phone(text: str, region="UA"):
    """
    Повертає номер у форматі +380XXXXXXXXX
    або None якщо номер невалідний
    """
    # print('extract_phone >>> text: ', text)
    try:
        for match in PhoneNumberMatcher(text, region):
            number = match.number

            # перевірка валідності
            if is_valid_number(number):
                # повертаємо у міжнародному форматі
                result = format_number(number, PhoneNumberFormat.E164)
                print("extract_phone >>> result: ", result)
                return result

    except NumberParseException:
        return None

    return None


# -----------------------------
# 📌 PHONE NORMALIZATION
# -----------------------------
@log_decorator
def normalize_phone(phone: str) -> str | None:
    """
    Приймає телефон у будь-якому форматі:
    +380677977166
    067 797-71-66
    +38(067) 797-71-66
    і повертає +380XXXXXXXXX
    """

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10 and digits.startswith("0"):
        return "+38" + digits

    if len(digits) == 12 and digits.startswith("380"):
        return "+" + digits

    if len(digits) == 13 and digits.startswith("380"):
        return "+" + digits

    return None


def normalize_phone_(phone_raw: str) -> str:

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


def validate_date(text: str):
    print("validate_date: ", text)
    try:
        parsed = datetime.strptime(text, "%d.%m.%Y")
        print("validate_date >>> parsed: ", parsed)
        if parsed.date() < datetime.today().date():
            return None
        return parsed.date()
    except Exception:
        return None


def validate_time(text: str, working_hours: tuple):
    print("validate_time: ", text)
    print("working_hours: ", working_hours)
    try:
        parsed = datetime.strptime(text, "%H:%M").time()
        start, end = working_hours
        if start <= parsed <= end:
            return parsed
        return None
    except Exception:
        return None


def validate_location(text: str, allowed_locations: list):
    text_lower = text.lower()
    for location in allowed_locations:
        if location.lower() in text_lower:
            return location
    return None


def validate_phone(text: str):
    match = re.search(r"\+?\d{10,15}", text)
    return match.group() if match else None