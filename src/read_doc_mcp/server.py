"""
MCP server for reader documentation from stdio type server.
"""

from pathlib import Path
import glob
import sys

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

mcp = FastMCP("ReaderDocumentationMCPServer")

local_data = Path(__file__).parent / "data_files"
parsed_files = []
documents_list = list(local_data.glob("**/*.md"))
number_of_files = len(documents_list)


@mcp.resource("file://file_list")
def list_data_files() -> list[str]:
    """List all markdown files in the local data directory."""
    return local_data.glob("**/*.md")


def read_md_data_files(file_path: Path) -> str:
    """Read the content of a markdown file."""
    if not file_path.exists() and not file_path.endswith(".md"):
        raise FileNotFoundError(f"Data file {file_path} not found.")

    try:
        return file_path.read_text()
    except Exception as e:
        return f"Error reading {file_path}: {e}"


@mcp.tool()
async def read_data_file(full_path: str) -> str:
    """Parse the markdown compatible with Pinecone vector database."""
    return read_md_data_files(Path(full_path))


# If the function already run once, it will not run again
@mcp.tool()
async def read_all_documents(
    ctx: Context[ServerSession, None], steps: int = number_of_files
) -> str:
    """Read all the documents one by one.
    Please run this tool iteratively until all documents are read.

    """

    await ctx.info(
        f"## Reading all documents for task: task_name with documents numbers {steps}"
    )
    if len(parsed_files) < len(documents_list):
        document = documents_list[len(parsed_files)]
        content = read_md_data_files(document)
        parsed_files.append(document)
        # Call API to process each document if needed to parse the data into Pinecone
        # Example: pinecone_client.upsert(index_name="documents", documents=[{"id": str(file_path).replace(".md", "").replace("/", "_"), "text": contents[-1]}])
        progress = (len(parsed_files) + 1) / steps * 100
        await ctx.report_progress(progress=progress, 
                                  message=f"Reading document {document}")
        return f"File name: {document}"
        # return f"Parsed content in pinecone database: {content}"
    else:
        # return read_md_data_files(
        #     documents_list[0]
        # )
        return f"All documents have of number of {len(documents_list)} been read and parsed {len(parsed_files)}."


if __name__ == "__main__":
    mcp.run()