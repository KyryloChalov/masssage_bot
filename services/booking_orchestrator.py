from services.booking_state import BookingStep, BookingState
import re
from datetime import datetime


class BookingOrchestrator:

    def __init__(self, business):
        self.business = business

    def handle(self, state: BookingState, message: str):

        if state.step == BookingStep.IDLE:
            state.step = BookingStep.ASK_DATE
            return "На яку дату вас записати? (формат: 25.02.2026)"

        if state.step == BookingStep.ASK_DATE:
            date = validate_date(message)

            if not date:
                state.increment_retry()
                if state.exceeded_retries():
                    state.step = BookingStep.CANCELLED
                    return "Не вдалося визначити дату. Спробуйте пізніше 🙌"
                return "Будь ласка, вкажіть дату у форматі ДД.ММ.РРРР"

            state.date = date
            state.reset_retries()
            state.step = BookingStep.ASK_TIME
            return "О котрій годині вам зручно? (формат: 14:30)"

        if state.step == BookingStep.ASK_TIME:
            time = validate_time(message, self.business.working_hours)

            if not time:
                state.increment_retry()
                return "Будь ласка, вкажіть коректний час у межах робочого графіка."

            state.time = time
            state.reset_retries()
            state.step = BookingStep.ASK_LOCATION
            return "Вкажіть район або місто для виїзду."

        if state.step == BookingStep.ASK_LOCATION:
            location = validate_location(message, self.business.allowed_locations)

            if not location:
                state.increment_retry()
                return "Ми працюємо лише у визначених районах. Уточніть, будь ласка."

            state.location = location
            state.reset_retries()
            state.step = BookingStep.ASK_PHONE
            return "Залиште номер телефону для підтвердження."

        if state.step == BookingStep.ASK_PHONE:
            phone = validate_phone(message)

            if not phone:
                state.increment_retry()
                return "Будь ласка, вкажіть коректний номер телефону."

            state.phone = phone
            state.step = BookingStep.CONFIRMATION

            return (
                f"Підтвердьте запис:\n"
                f"Дата: {state.date}\n"
                f"Час: {state.time}\n"
                f"Локація: {state.location}\n"
                f"Телефон: {state.phone}\n\n"
                f"Напишіть 'так' для підтвердження."
            )

        if state.step == BookingStep.CONFIRMATION:
            if message.lower() in ["так", "yes", "підтверджую"]:
                state.step = BookingStep.COMPLETED
                return "Дякуємо за замовлення! Ми зв'яжемося з вами найближчим часом 🙌"

            state.step = BookingStep.CANCELLED
            return "Запис скасовано. Якщо потрібно — створимо новий 🙌"

        return "Будь ласка, уточніть деталі запису."
    
    
def validate_date(text: str):
    try:
        parsed = datetime.strptime(text, "%d.%m.%Y")
        if parsed.date() < datetime.today().date():
            return None
        return parsed.date()
    except:
        return None

def validate_time(text: str, working_hours: tuple):
    try:
        parsed = datetime.strptime(text, "%H:%M").time()
        start, end = working_hours
        if start <= parsed <= end:
            return parsed
        return None
    except:
        return None

def validate_location(text: str, allowed_locations: list):
    text_lower = text.lower()
    for location in allowed_locations:
        if location.lower() in text_lower:
            return location
    return None


def validate_phone(text: str):
    match = re.search(r'\+?\d{10,15}', text)
    return match.group() if match else None