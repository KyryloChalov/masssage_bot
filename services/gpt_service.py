import asyncio
from openai import AsyncOpenAI
from storage.gpt_repository import GptRepository

from include.business_formatter import build_system_context
from services.intent_filter import is_massage_related

from services.intent_classifier import detect_intent, Intent

# from services.booking_manager import BookingManager, handle, state
from services.booking_manager import *


class ConversationState:
    def __init__(self):
        self.booking_date = None
        self.booking_time = None
        self.location = None
        self.phone = None

class ChatGptService:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        max_history: int = 25,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_history = max_history
        self.repo = GptRepository()
        

    async def ask(self, user_id: int, user_message: str):
        
        print("ask >>> point 1")
        # 1️⃣ зберігаємо повідомлення користувача
        self.repo.save_message(user_id, "user", user_message)

        # print("ask >>> point 2")
        # # 0️⃣ чи стосується питання масажу?
        # print('ask >>> user_message: ', user_message)
        # if not is_massage_related(user_message):
        #     return "Я можу допомогти лише з питаннями щодо послуг масажу Home.Masssage 🙌 Якщо вас цікавить запис або консультація — із радістю допоможу."

        print("ask >>> point 3")
        # 0️⃣➕
        intent = detect_intent(user_message)
        if intent == Intent.OTHER:
            return "Я можу допомогти лише з питаннями щодо послуг масажу Home.Masssage 🙌"

        print("ask >>> point 4")
        # 0️⃣➕➕
        if intent == Intent.BOOKING:
            response = booking_manager.handle(state, user_message)
            # response = BookingManager.handle(state, user_message)
            return response

        print("ask >>> point 5")
        # 2️⃣ беремо історію
        history = self.repo.get_history(user_id, self.max_history)

        print("ask >>> point 6")
        # 3️⃣ додаємо system prompt
        messages = build_system_context() + history

        print("ask >>> point 7")
        # 4️⃣ виклик GPT з retry
        for attempt in range(3):
            try:
                response = await asyncio.wait_for(
                    self.client.responses.create(
                        model=self.model,
                        input=messages,
                        max_output_tokens=500,
                    ),
                    timeout=30,
                )

                answer = response.output_text

                # 5️⃣ зберігаємо відповідь
                self.repo.save_message(user_id, "assistant", answer)

                return answer, history

            except asyncio.TimeoutError:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)

            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2)

        return "Помилка GPT."
