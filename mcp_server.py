import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")

DOCS_PATH = Path(__file__).resolve().parent / "documents.json"


def load_docs() -> dict:
    if not DOCS_PATH.exists():
        raise FileNotFoundError(f"Documents file not found at {DOCS_PATH}")
    try:
        with open(DOCS_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse documents.json: {e}")


def save_docs(docs: dict):
    try:
        with open(DOCS_PATH, "w") as f:
            json.dump(docs, f, indent=2)
    except OSError as e:
        raise IOError(f"Failed to write to documents.json: {e}")
    # Verify the write
    saved = load_docs()
    if saved != docs:
        raise IOError("Verification failed: saved data does not match")




from pydantic import Field
from mcp.server.fastmcp.prompts import base


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="Id of the document to read"),
):
    if not doc_id or not doc_id.strip():
        raise ValueError("doc_id cannot be empty")
    docs = load_docs()
    if doc_id not in docs:
        available = ", ".join(docs.keys())
        raise ValueError(f"Doc '{doc_id}' not found. Available: {available}")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing its entire content with new content",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    new_content: str = Field(description="The new content for the document"),
):
    if not doc_id or not doc_id.strip():
        raise ValueError("doc_id cannot be empty")
    if not new_content or not new_content.strip():
        raise ValueError("new_content cannot be empty")
    docs = load_docs()
    if doc_id not in docs:
        available = ", ".join(docs.keys())
        raise ValueError(f"Doc '{doc_id}' not found. Available: {available}")
    docs[doc_id] = new_content
    save_docs(docs)
    # Verify the edit persisted
    verified = load_docs()
    if verified.get(doc_id) != new_content:
        raise IOError(f"Edit verification failed for '{doc_id}'")
    return f"Successfully updated '{doc_id}'. New content: {verified[doc_id]}"


@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(load_docs().keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    docs = load_docs()
    if doc_id not in docs:
        available = ", ".join(docs.keys())
        raise ValueError(f"Doc '{doc_id}' not found. Available: {available}")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """

    return [base.UserMessage(prompt)]


@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of a document.",
)
def summarize_document(
    doc_id: str = Field(description="Id of the document to summarize"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to summarize the following document concisely.

    The id of the document you need to summarize is:
    <document_id>
    {doc_id}
    </document_id>

    Use the 'read_doc_contents' tool to read the document, then provide a clear and concise summary.
    """

    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
