import json
from typing import Any, Optional, Literal, List

from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[Tool]:
        """Gets all tools from the provided clients."""
        tools = []
        for name, client in clients.items():
            try:
                tool_models = await client.list_tools()
                tools += [
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.inputSchema,
                        },
                    }
                    for t in tool_models
                ]
            except Exception as e:
                print(f"Warning: Failed to get tools from client '{name}': {e}")
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            try:
                tools = await client.list_tools()
                tool = next((t for t in tools if t.name == tool_name), None)
                if tool:
                    return client
            except Exception:
                continue
        return None

    @classmethod
    def _build_tool_result_part(
        cls,
        tool_name: str,
        text: str,
        status: Literal["success"] | Literal["error"],
    ) -> dict[str, Any]:
        """Builds a tool result part dictionary."""
        return {
            "role": "tool",
            "tool_name": tool_name,
            "content": text,
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], tool_calls: list[dict[str, Any]]
    ) -> List[dict[str, Any]]:
        """Executes a list of tool requests against the provided clients."""
        tool_result_blocks: list[dict[str, Any]] = []
        for tool_request in tool_calls:
            function = tool_request.get("function", {})
            tool_name = function.get("name")
            tool_input = function.get("arguments", {})

            if not tool_name:
                tool_result_blocks.append(
                    cls._build_tool_result_part(
                        "unknown_tool",
                        "Tool call missing name",
                        "error",
                    )
                )
                continue

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_result_part = cls._build_tool_result_part(
                    tool_name, "Could not find that tool", "error"
                )
                tool_result_blocks.append(tool_result_part)
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                items = tool_output.content if tool_output else []
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                if not content_list:
                    content_json = json.dumps(["Tool returned no content"])
                else:
                    content_json = json.dumps(content_list)
                is_error = tool_output.isError if tool_output else True
                tool_result_part = cls._build_tool_result_part(
                    tool_name,
                    content_json,
                    "error" if is_error else "success",
                )
            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                tool_result_part = cls._build_tool_result_part(
                    tool_name,
                    json.dumps({"error": error_message}),
                    "error",
                )

            tool_result_blocks.append(tool_result_part)
        return tool_result_blocks
