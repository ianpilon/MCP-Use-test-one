"""FastAPI server implementing MCP protocol for file access."""

from typing import Dict, List
import asyncio
import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

# Allow CORS for local testing and render.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONTEXT_DIR = os.path.join(os.path.dirname(__file__), "context_files")


class MCPFunction(BaseModel):
    """Model for MCP function definition."""
    name: str
    description: str
    parameters: Dict


class MCPToolCall(BaseModel):
    """Model for MCP tool call."""
    name: str
    parameters: Dict


@app.get("/")
def root() -> RedirectResponse:
    """Redirect root to API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/files")
def list_files() -> Dict[str, List[str]]:
    """List all files in the context directory."""
    try:
        files = [
            f for f in os.listdir(CONTEXT_DIR)
            if os.path.isfile(os.path.join(CONTEXT_DIR, f))
        ]
        return {"files": files}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/files/{filename}")
def get_file(filename: str) -> FileResponse:
    """Get a specific file from the context directory."""
    filepath = os.path.join(CONTEXT_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)


@app.get("/mcp/functions")
def get_functions() -> Dict[str, List[MCPFunction]]:
    """Return the list of available functions in this MCP server."""
    functions = [
        MCPFunction(
            name="list_files",
            description="List all available files in the context directory",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        MCPFunction(
            name="get_file_content",
            description="Get the content of a specific file",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to retrieve"
                    }
                },
                "required": ["filename"]
            }
        )
    ]
    return {"functions": functions}


@app.get("/mcp/sse")
async def sse_endpoint(request: Request) -> EventSourceResponse:
    """SSE endpoint for MCP protocol."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield {
                "data": json.dumps({"type": "ping"})
            }
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())


@app.post("/mcp/invoke")
async def invoke_function(tool_call: MCPToolCall) -> JSONResponse:
    """Execute a function call and return the result."""
    if tool_call.name == "list_files":
        files = [
            f for f in os.listdir(CONTEXT_DIR)
            if os.path.isfile(os.path.join(CONTEXT_DIR, f))
        ]
        return JSONResponse({"files": files})

    if tool_call.name == "get_file_content":
        filename = tool_call.parameters.get("filename")
        if not filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        filepath = os.path.join(CONTEXT_DIR, filename)
        if not os.path.isfile(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return JSONResponse({"content": content})
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=str(exc)
            ) from exc

    raise HTTPException(
        status_code=400,
        detail=f"Unknown function: {tool_call.name}"
    )
