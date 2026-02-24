# services/booking_manager.py

from services.booking_state import BookingStep, BookingState
from include.util import extract_phone



class BookingManager:

    def handle(self, state: BookingState, user_message: str):

        if state.step == BookingStep.IDLE:
            state.step = BookingStep.ASK_DATE
            return "На яку дату вас записати?"

        if state.step == BookingStep.ASK_DATE:
            state.date = user_message
            state.step = BookingStep.ASK_TIME
            return "На який час вам зручно?"

        if state.step == BookingStep.ASK_TIME:
            state.time = user_message
            state.step = BookingStep.ASK_LOCATION
            return "Вкажіть, будь ласка, район або місто для виїзду."

        if state.step == BookingStep.ASK_LOCATION:
            state.location = user_message
            state.step = BookingStep.ASK_PHONE
            return "Залиште, будь ласка, номер телефону для підтвердження."

        if state.step == BookingStep.ASK_PHONE:
            state.phone = user_message
            phone = extract_phone(user_message)
            if phone:
                state.phone = phone
            # elif -  а якщо не phone? повторно спитати
            state.step = BookingStep.CONFIRMED
            return "Дякуємо за замовлення! Ми зв'яжемося з вами найближчим часом 🙌"

        return "Будь ласка, уточніть деталі запису."