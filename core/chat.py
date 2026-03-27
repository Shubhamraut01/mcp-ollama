from typing import Any

from core.ollama_llm import OllamaLLM
from mcp_client import MCPClient
from core.tools import ToolManager


class Chat:
    def __init__(
        self, llm_service: OllamaLLM, clients: dict[str, MCPClient]
    ):
        self.llm_service: OllamaLLM = llm_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[dict[str, Any]] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            response = self.llm_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            self.llm_service.add_assistant_message(self.messages, response)

            tool_calls = (
                response.get("message", {}).get("tool_calls", [])
                if isinstance(response, dict)
                else getattr(response.message, "tool_calls", [])
            )
            if tool_calls and not isinstance(tool_calls[0], dict):
                normalized_calls = []
                for call in tool_calls:
                    if hasattr(call, "model_dump"):
                        normalized_calls.append(call.model_dump())
                    else:
                        function = getattr(call, "function", None)
                        normalized_calls.append(
                            {
                                "type": getattr(call, "type", "function"),
                                "function": {
                                    "name": getattr(function, "name", None),
                                    "arguments": getattr(
                                        function, "arguments", {}
                                    ),
                                },
                            }
                        )
                tool_calls = normalized_calls
            if tool_calls:
                print(self.llm_service.text_from_message(response))
                tool_result_messages = await ToolManager.execute_tool_requests(
                    self.clients, tool_calls
                )
                self.messages.extend(tool_result_messages)
            else:
                final_text_response = self.llm_service.text_from_message(
                    response
                )
                break

        return final_text_response
