import asyncio
from openai import AsyncOpenAI


from business.business_formatter import build_system_context

from services.intent_classifier import detect_intent, Intent
from services.booking_manager import BookingOrchestrator
from services.booking_state import BookingState, BookingStep
from services.intent_filter import is_massage_related

from storage.gpt_repository import GptRepository

from repositories.business_repository import BusinessRepository



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
        business_id: int,
        model: str = "gpt-4.1-mini",
        max_history: int = 25,
        user_states: dict | None = None,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_history = max_history
        self.user_states = user_states if user_states is not None else {}
        self.repo = GptRepository()
        self.business = BusinessRepository.get(business_id)
        self.booking_manager = BookingOrchestrator(self.business)

    async def history_from_db(self, user_id: int):
        print("history_from_db >>> point 1")
        # беремо історію і одразу віддаємо (викликається з двох місць, тому виніс в окрему функцію)
        return self.repo.get_history(user_id, self.max_history)

    async def ask(self, user_id: int, user_message: str):

        # тут GPT-логіка
        print("ask >>> point 1")
        # 1️⃣ зберігаємо повідомлення користувача
        self.repo.save_message(user_id, "user", user_message)

        if user_id not in self.user_states:
            self.user_states[user_id] = BookingState()

        state = self.user_states[user_id]

        # print("ask >>> point 2")
        # # 0️⃣ чи стосується питання масажу?
        # print('ask >>> user_message: ', user_message)
        # if not is_massage_related(user_message):
        #     return "Я можу допомогти лише з питаннями щодо послуг масажу Home.Masssage 🙌 Якщо вас цікавить запис або консультація — із радістю допоможу."

        intent = detect_intent(user_message)
        print("ask >>> intent: ", intent)

        print("ask >>> point 3")
        # 0️⃣➕➕ важливий нюанс — якщо ми в процесі бронювання, то неважливо, що запитує користувач. Ми повинні довести бронювання до кінця.
        print("ask >>> state.step: ", state.step)
        if state.step != BookingStep.IDLE or intent == Intent.BOOKING:
            return self.booking_manager.handle(state, user_message)

        # цей запобіжник спрацьовує занадто часто, тому поки що вимкнув. 
        # Але він потрібен, щоб не перевантажувати GPT запитами, які не стосуються масажу.
        # print("ask >>> point 4")
        # # 0️⃣➕
        # if intent == Intent.OTHER:
        #     return "Я можу допомогти лише з питаннями щодо послуг масажу Home.Masssage 🙌 Якщо вас цікавить запис або консультація — із радістю допоможу."

        print("ask >>> point 5")
        # 2️⃣ беремо історію
        history = await self.history_from_db(user_id)
        # history = self.repo.get_history(user_id, self.max_history)

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

                return answer

            except asyncio.TimeoutError:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)

            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(2)

        if state.step in (BookingStep.CANCELLED, BookingStep.COMPLETED):
            self.user_states.pop(user_id, None)

        return "Помилка GPT."
