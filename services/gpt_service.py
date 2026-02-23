import asyncio
from openai import AsyncOpenAI
from storage.gpt_repository import GptRepository

from include.sys_prompt import BUSINESS_INFO, SYSTEM_PROMPT


class ChatGptService:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        max_history: int = 20,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_history = max_history
        self.repo = GptRepository()

    async def ask(self, user_id: int, user_message: str) -> str:

        # 1️⃣ зберігаємо повідомлення користувача
        self.repo.save_message(user_id, "user", user_message)

        # 2️⃣ беремо історію
        history = self.repo.get_history(user_id, self.max_history)

        # 3️⃣ додаємо system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        # messages.append(BUSINESS_INFO)

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

        return "Помилка GPT."
