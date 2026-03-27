from typing import Any, Optional

import ollama


class OllamaLLM:
    def __init__(self, model: str, host: Optional[str] = None):
        self.model = model
        self.client = ollama.Client(host=host) if host else ollama

    def add_user_message(self, messages: list[dict[str, Any]], message: Any):
        if isinstance(message, dict):
            messages.append(message)
        else:
            messages.append({"role": "user", "content": str(message)})

    def add_assistant_message(
        self, messages: list[dict[str, Any]], response: Any
    ):
        message = response["message"] if isinstance(response, dict) else response.message
        if not isinstance(message, dict):
            if hasattr(message, "model_dump"):
                message = message.model_dump()
            else:
                message = {
                    "role": getattr(message, "role", "assistant"),
                    "content": getattr(message, "content", ""),
                    "tool_calls": getattr(message, "tool_calls", None),
                }
        messages.append(message)

    def text_from_message(self, response: Any) -> str:
        message = response["message"] if isinstance(response, dict) else response.message
        if isinstance(message, dict):
            return message.get("content", "")
        return getattr(message, "content", "") or ""

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[list[str]] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        thinking: bool = False,
    ):
        params: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        if system:
            params["messages"] = [
                {"role": "system", "content": system},
                *messages,
            ]

        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if stop_sequences:
            options["stop"] = stop_sequences
        if options:
            params["options"] = options

        if tools:
            params["tools"] = tools

        if thinking:
            params["think"] = True

        return self.client.chat(**params)
