
import json
import logging

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    def chat(self, messages, tools=None, tool_executor=None):
        api_key = getattr(settings, "OPENAI_API_KEY", "")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        client = OpenAI(api_key=api_key)

        for _ in range(5):
            kwargs = {
                "model": getattr(
                    settings,
                    "OPENAI_MODEL",
                    "gpt-4.1-mini",
                ),
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                if not assistant_message.content:
                    raise RuntimeError(
                        "OpenAI returned an empty response."
                    )
                return assistant_message.content

            messages.append(
                assistant_message.model_dump(exclude_none=True)
            )

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                try:
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    if tool_executor is None:
                        raise RuntimeError(
                            "Tool executor is not configured."
                        )

                    result = tool_executor(
                        tool_name,
                        arguments,
                    )

                except Exception:
                    logger.exception(
                        "AI tool execution failed: %s",
                        tool_name,
                    )
                    result = {
                        "success": False,
                        "message": (
                            "Не удалось выполнить операцию. "
                            "Попробуй ещё раз."
                        ),
                    }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    ),
                })

        raise RuntimeError(
            "OpenAI exceeded the maximum number of tool calls."
        )
