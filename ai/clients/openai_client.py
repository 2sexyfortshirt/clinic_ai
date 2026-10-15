


from django.conf import settings
from openai import OpenAI


class OpenAIClient:
    def chat(self, messages):
        api_key = getattr(settings, "OPENAI_API_KEY", "")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured in .env"
            )

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=getattr(
                settings,
                "OPENAI_MODEL",
                "gpt-4.1-mini",
            ),
            messages=messages,
        )

        reply = response.choices[0].message.content

        if not reply:
            raise RuntimeError("OpenAI returned an empty response")

        return reply
