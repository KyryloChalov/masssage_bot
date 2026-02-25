# services/booking_state.py

from enum import Enum


class BookingStep(str, Enum):
    IDLE = "idle"
    ASK_DATE = "ask_date"
    ASK_TIME = "ask_time"
    ASK_LOCATION = "ask_location"
    ASK_PHONE = "ask_phone"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingState:
    def __init__(self):
        self.step = BookingStep.IDLE

        self.date = None
        self.time = None
        self.location = None
        self.phone = None

        self.retry_count = 0
        self.max_retries = 2

    def reset_retries(self):
        self.retry_count = 0

    def increment_retry(self):
        self.retry_count += 1

    def exceeded_retries(self):
        return self.retry_count > self.max_retries
