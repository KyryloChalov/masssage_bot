# services/intent_classifier.py

from enum import Enum

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

    if "ціна" in text or "вартість" in text:
        return Intent.PRICE

    if "запис" in text or "хочу записатися" in text:
        return Intent.BOOKING

    if "сертифікат" in text:
        return Intent.CERTIFICATE

    if any(w in text for w in ["де", "район", "місто", "приїхати"]):
        return Intent.LOCATION

    if any(w in text for w in ["години", "графік", "коли"]):
        return Intent.HOURS

    if any(w in text for w in ["масаж", "послуга"]):
        return Intent.SERVICE

    if any(char.isdigit() for char in text) and len(text) >= 9:
        return Intent.PHONE

    return Intent.OTHER