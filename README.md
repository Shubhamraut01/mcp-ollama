## MCP Chat

**MCP Chat** is a command-line interface (CLI) application that provides interactive chat with AI models via a local Ollama server. It supports:

* Conversational interaction
* Document retrieval using inline references
* Command-based operations
* Extensible tooling through the Model Control Protocol (MCP)

---

## Prerequisites

* Python 3.9 or higher
* Ollama installed and running locally

---

## Setup

### 1. Configure Environment Variables

Create or update a `.env` file in the project root:

```env
OLLAMA_MODEL="llama3.2:latest"
# Optional: specify a custom Ollama host
# OLLAMA_HOST="http://localhost:11434"
```

---

### 2. Install Dependencies

#### Option A: Using `uv` (Recommended)

`uv` is a fast Python package manager and dependency resolver.

1. Install `uv` (if not already installed):

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

3. Install project dependencies:

```bash
uv pip install -e .
```

4. Run the application:

```bash
uv run main.py
```

---

#### Option B: Standard Setup (without `uv`)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install ollama python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Run the application:

```bash
python main.py
```

---

## Ollama Setup

Ensure the Ollama service is running before starting the CLI:

```bash
ollama serve
```

If the model is not yet available locally:

```bash
ollama pull llama3.2:latest
```

---

## Usage

### Basic Chat

Type a message and press Enter to interact with the model.

---

### Document Retrieval

Reference a document using `@` followed by its identifier:

```bash
> Tell me about @deposition.md
```

This injects the document content into the prompt.

---

### Commands

Use `/` to invoke predefined MCP commands:

```bash
> /summarize deposition.md
```

* Commands support tab-based auto-completion
* Defined and handled within the MCP server

---

## Development

### Adding Documents

Modify `mcp_server.py` and update the `docs` dictionary to include new documents.

---

### Implementing MCP Features

To complete MCP functionality:

1. Resolve pending TODOs in `mcp_server.py`
2. Implement missing logic in `mcp_client.py`

---

### Linting and Type Checking

No linting or static type checks are currently configured.
