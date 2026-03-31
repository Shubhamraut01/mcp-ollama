import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.ollama_llm import OllamaLLM

from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# Ollama Config
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
ollama_host = os.getenv("OLLAMA_HOST", "")

if not ollama_model:
    print("Error: OLLAMA_MODEL cannot be empty. Update .env")
    sys.exit(1)


async def main():
    try:
        llm_service = OllamaLLM(model=ollama_model, host=ollama_host or None)
    except Exception as e:
        print(f"Error: Failed to initialize Ollama LLM: {e}")
        sys.exit(1)

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    try:
        async with AsyncExitStack() as stack:
            try:
                doc_client = await stack.enter_async_context(
                    MCPClient(command=command, args=args)
                )
            except Exception as e:
                print(f"Error: Failed to connect to MCP server: {e}")
                sys.exit(1)
            clients["doc_client"] = doc_client

            for i, server_script in enumerate(server_scripts):
                client_id = f"client_{i}_{server_script}"
                try:
                    client = await stack.enter_async_context(
                        MCPClient(command="uv", args=["run", server_script])
                    )
                    clients[client_id] = client
                except Exception as e:
                    print(f"Warning: Failed to connect to server '{server_script}': {e}")

            chat = CliChat(
                doc_client=doc_client,
                clients=clients,
                llm_service=llm_service,
            )

            cli = CliApp(chat)
            await cli.initialize()
            await cli.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: Unexpected failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
