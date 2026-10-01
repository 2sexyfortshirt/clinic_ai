from ai.clients.openai_client import OpenAIClient
from ai.prompts.receptionist import SYSTEM_PROMPT


class AIService:
    client = OpenAIClient()
    @classmethod

    def generate_reply(cls,conversation):
        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
            ]
        for message in conversation.messages.all().order_by("created_at"):
            messages.append({
                "role": message.role,
                "content": message.content,
            }
            )
        reply = cls.client.chat(messages)

        return reply
