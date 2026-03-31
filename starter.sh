#!/bin/bash

# ============================================
# MCP Chat - Starter Commands
# ============================================

# ---------- Setup ----------
# Install uv (if not installed)
# pip install uv

# Create venv and install dependencies
# uv venv
# source .venv/bin/activate
# uv pip install -e .

# ---------- MCP Server ----------
# Run MCP server in dev/inspector mode
# uv run mcp dev mcp_server.py

# Run MCP server directly
# uv run python mcp_server.py

# ---------- MCP Client (Chat CLI) ----------
# Run the chat client
# uv run main.py

# ---------- Ollama ----------
# Start Ollama (must be running before using the client)
# ollama serve

# Pull the model (first time only)
# ollama pull llama3.2:latest
