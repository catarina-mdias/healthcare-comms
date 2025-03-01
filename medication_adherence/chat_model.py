import logging

from openai import AsyncOpenAI

from medication_adherence.utils import StrEnum


class OpenAIKeys(str):
    ROLE = "role"
    CONTENT = "content"


class ChatModelRole(StrEnum):
    SYSTEM = "system"
    USER = "user"


class ChatModel:
    def __init__(self, openai_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_key)

    async def get_completion(self, **kwargs) -> str:
        try:
            chat_completion = await self.openai_client.chat.completions.create(
                **kwargs
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            raise


async def generate_message(
    chat_model: ChatModel,
    system_message: str,
    user_message: str,
    model: str,
    temperature: float = 0.3,
    json_format: bool = False,
) -> str:

    response = await chat_model.get_completion(
        temperature=temperature,
        model=model,
        messages=[
            {
                OpenAIKeys.ROLE: ChatModelRole.SYSTEM,
                OpenAIKeys.CONTENT: system_message,
            },
            {
                OpenAIKeys.ROLE: ChatModelRole.USER,
                OpenAIKeys.CONTENT: user_message,
            },
        ],
        response_format={"type": "json_object"} if json_format else None,
    )
    return response
