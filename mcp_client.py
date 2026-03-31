import sys
import asyncio
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

import json
from pydantic import AnyUrl


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        try:
            server_params = StdioServerParameters(
                command=self._command,
                args=self._args,
                env=self._env,
            )
            stdio_transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            _stdio, _write = stdio_transport
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(_stdio, _write)
            )
            await self._session.initialize()
        except FileNotFoundError:
            raise ConnectionError(
                f"Command '{self._command}' not found. Is it installed and in PATH?"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MCP server: {e}")

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    # async def list_tools(self) -> list[types.Tool]:
    #     # TODO: Return a list of tools defined by the MCP server
    #     return []

    # async def call_tool(
    #     self, tool_name: str, tool_input: dict
    # ) -> types.CallToolResult | None:
    #     # TODO: Call a particular tool and return the result
    #     return None

    # async def list_prompts(self) -> list[types.Prompt]:
    #     # TODO: Return a list of prompts defined by the MCP server
    #     return []

    # async def get_prompt(self, prompt_name, args: dict[str, str]):
    #     # TODO: Get a particular prompt defined by the MCP server
    #     return []

    # async def read_resource(self, uri: str) -> Any:
    #     # TODO: Read a resource, parse the contents and return it
    #     return []

    async def list_tools(self) -> list[types.Tool]:
        try:
            result = await self.session().list_tools()
            return result.tools
        except ConnectionError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to list tools: {e}")

    async def call_tool(
        self, tool_name: str, tool_input
    ) -> types.CallToolResult | None:
        try:
            result = await self.session().call_tool(tool_name, tool_input)
            if result and result.isError:
                content_texts = [
                    item.text for item in (result.content or [])
                    if isinstance(item, types.TextContent)
                ]
                error_msg = " ".join(content_texts) or "Unknown tool error"
                raise RuntimeError(f"Tool '{tool_name}' returned error: {error_msg}")
            return result
        except ConnectionError:
            raise
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to call tool '{tool_name}': {e}")

    async def list_prompts(self) -> list[types.Prompt]:
        try:
            result = await self.session().list_prompts()
            return result.prompts
        except ConnectionError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to list prompts: {e}")

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        try:
            result = await self.session().get_prompt(prompt_name, args)
            return result.messages
        except ConnectionError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to get prompt '{prompt_name}': {e}")

    async def read_resource(self, uri: str) -> Any:
        try:
            result = await self.session().read_resource(AnyUrl(uri))
            if not result.contents:
                raise ValueError(f"Resource '{uri}' returned no content")
            resource = result.contents[0]

            if isinstance(resource, types.TextResourceContents):
                if resource.mimeType == "application/json":
                    return json.loads(resource.text)
                return resource.text

            raise ValueError(f"Unsupported resource type for '{uri}'")
        except (ConnectionError, ValueError):
            raise
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from resource '{uri}': {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read resource '{uri}': {e}")

    async def cleanup(self):
        try:
            await self._exit_stack.aclose()
        except Exception:
            pass
        finally:
            self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
async def main():
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        pass


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
