# services/intent_classifier.py

from enum import Enum
from repositories.business_repository import BusinessRepository

business = BusinessRepository


class Intent(str, Enum):
    GREETING = "greeting"
    SERVICE = "service_question"
    PRICE = "price_question"
    BOOKING = "booking_request"
    HOURS = "working_hours"
    LOCATION = "location_question"
    CERTIFICATE = "certificate_question"
    PHONE = "provide_phone"
    OTHER = "other"


def detect_intent(text: str) -> Intent:
    text = text.lower()

    if any(w in text for w in ["привіт", "доброго", "добрий", "вітаю", "хай"]):
        return Intent.GREETING

    # if "ціна" in text or "вартість" in text:
    if any(
        w in text
        for w in [
            "ціна",
            "вартість",
            "коштує",
            "коштують",
            "гривень",
            "скільки",
            "грошей",
            "ціни",
        ]
    ):
        return Intent.PRICE

    # if "запис" in text or "записатися" in text:
    if any(
        w in text
        for w in [
            "запис",
            "записатися",
            "замовити",
            "оформити",
            # "хочу",
            "забронювати",
            "бронювання",
            "телефон",
        ]
    ):
        return Intent.BOOKING

    # if "сертифікат" in text:
    if any(
        w in text
        for w in [
            "сертифікат",
            "подарунок",
            "подарунковий",
            "подарувати",
            "сертифікати",
        ]
    ):
        return Intent.CERTIFICATE

    if any(
        w in text
        for w in [
            "де",
            "район",
            "місто",
            "приїхати",
            "виїзд",
            "локація",
            "вдома",
            "адреса",
            "вулиця",
            "номер",
            "квартира",
            "будинок",
            "готель",
        ]
    ):
        return Intent.LOCATION

    towns = [t.casefold() for t in business.get(1).allowed_locations]

    if any(w in text for w in towns):
        return Intent.LOCATION

    if any(
        w in text
        for w in [
            "години",
            "графік",
            "коли",
            "працюєте",
            "працює",
            "час",
            "робочі",
        ]
    ):
        return Intent.HOURS

    if any(
        w in text
        for w in [
            "масаж",
            "масажист",
            "послуга",
            "спина",
            "загальний",
            "ноги",
            "терапія",
            "розслаблення",
            "розім'яти",
            "лікувальний",
            "лікування",
            "релакс",
            "антистрес",
            "тіло",
            "ломі",
        ]
    ):
        return Intent.SERVICE

    services = [s.casefold() for s in business.get(1).services]
    services = [s.replace('масаж', '').strip() for s in services]

    if any(w in text for w in services):
        return Intent.SERVICE

    if any(char.isdigit() for char in text) and len(text) >= 9:
        return Intent.PHONE

    return Intent.OTHER
