# services/intent_filter.py

ALLOWED_KEYWORDS = [
    "привіт",
    "вітаю",
    "добрий",
    "масаж",
    "запис",
    "ціна",
    "вартість",
    "години",
    "графік",
    "район",
    "місто",
    "сертифікат",
    "подарунок",
    "процедура",
    "майстер",
    "виїзд",
]

ALLOWED_INTENTS = [
    "запит про послугу",
    "запис",
    "ціна",
    "графік",
    "локація",
    "подарунковий сертифікат",
]


def is_massage_related(text: str) -> bool:
    print("is_massage_related >>> point 1")
    text = text.lower()
    print("is_massage_related >>> text: ", text)
    print("is_massage_related >>> point 2")
    is_related = any(keyword in text for keyword in ALLOWED_KEYWORDS)
    print("is_massage_related >>> is_related: ", is_related)
    return is_related
