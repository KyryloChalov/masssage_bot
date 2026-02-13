import openai
from openai import OpenAI


class ChatGptService:
    client: OpenAI
    message_list: list

    def __init__(self, token):
        self.client = openai.OpenAI(base_url="https://openai.javarush.com/v1", api_key=token)
        self.message_list = []

    async def send_message_list(self, max_tokens=3000) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o",  # gpt-4o,  gpt-4-turbo,    gpt-3.5-turbo
            messages=self.message_list,
            max_tokens=max_tokens,
            temperature=0.9
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return str(message.content)

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str, max_tokens: int = 3000) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list(max_tokens=max_tokens)
