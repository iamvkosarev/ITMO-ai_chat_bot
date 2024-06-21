from openai import AsyncOpenAI

from ai_chat_bot.llm.llm import LLM


class OpenAIChatGPT(LLM):
    def __init__(self, api_key):
        assert isinstance(api_key, str)
        self.ai_client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)

    async def handle_prompt(self, chat_history) -> str:
        chat_completion = await self.ai_client.chat.completions.create(
            messages=chat_history,
            model="gpt-3.5-turbo",
        )

        chat_response = chat_completion.choices[0].message.content
        return chat_response
