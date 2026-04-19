# MCP Chat

MCP Chat is a command-line interface (CLI) application for interacting with local AI models via an Ollama server. It supports conversational workflows, document-aware querying, and command-based operations using the Model Control Protocol (MCP).

---

## Features

* Interactive chat with local LLMs (via Ollama)
* Document retrieval using inline references (`@document`)
* Command execution using MCP (`/commands`)
* Extensible architecture for adding tools and workflows
* CLI auto-completion support

---

## Prerequisites

* Python 3.9+
* Ollama installed and running

---

## Setup

### 1. Environment Configuration

Create a `.env` file in the project root:

```
OLLAMA_MODEL="llama3.2:latest"
# Optional
# OLLAMA_HOST="http://localhost:11434"
```

---

### 2. Installation

#### Option 1: Using uv (Recommended)

```
pip install uv

uv venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

uv pip install -e .
```

Run the application:

```
uv run main.py
```

---

#### Option 2: Standard Setup

```
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install ollama python-dotenv prompt-toolkit "mcp[cli]==1.8.0"

python main.py
```

---

## Ollama Setup

Start the Ollama server:

```
ollama serve
```

Pull the required model if not already available:

```
ollama pull llama3.2:latest
```

---

## Usage

### Chat

Type a message and press Enter:

```
> What is MCP architecture?
```

---

### Document Retrieval

Reference documents using `@`:

```
> Explain @deposition.md
```

This injects the document content into the model context.

---

### Commands

Use `/` to execute MCP commands:

```
> /summarize deposition.md
```

* Supports tab-based auto-completion
* Commands are handled via the MCP server

---

## Project Structure

* `main.py` → CLI entry point
* `mcp_client.py` → Handles model interaction and command routing
* `mcp_server.py` → Defines documents, commands, and tools

---

## Development

### Adding Documents

Update the `docs` dictionary in `mcp_server.py`:

```
docs = {
    "example.md": "Document content here"
}
```

---

### Adding Commands

1. Define a command handler in `mcp_server.py`
2. Register it with MCP
3. Ensure it is callable from the client

---

### Extending Functionality

You can extend MCP Chat by integrating:

* External APIs
* Retrieval pipelines (RAG)
* Custom tools and workflows

---

## Notes

* No linting or type checking is configured
* Designed for local-first AI workflows
* Easily extensible into a larger agent framework
