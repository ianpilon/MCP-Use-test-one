from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import Dict, List, Optional
from pydantic import BaseModel

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
    name: str
    description: str
    parameters: Dict

class MCPToolCall(BaseModel):
    name: str
    parameters: Dict

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/files")
def list_files():
    try:
        files = [f for f in os.listdir(CONTEXT_DIR) if os.path.isfile(os.path.join(CONTEXT_DIR, f))]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{filename}")
def get_file(filename: str):
    filepath = os.path.join(CONTEXT_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)

# MCP Protocol Endpoints
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

@app.post("/mcp/invoke")
async def invoke_function(tool_call: MCPToolCall) -> JSONResponse:
    """Execute a function call and return the result."""
    if tool_call.name == "list_files":
        files = [f for f in os.listdir(CONTEXT_DIR) if os.path.isfile(os.path.join(CONTEXT_DIR, f))]
        return JSONResponse({"files": files})
    
    elif tool_call.name == "get_file_content":
        filename = tool_call.parameters.get("filename")
        if not filename:
            raise HTTPException(status_code=400, detail="Filename is required")
            
        filepath = os.path.join(CONTEXT_DIR, filename)
        if not os.path.isfile(filepath):
            raise HTTPException(status_code=404, detail="File not found")
            
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return JSONResponse({"content": content})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=400, detail=f"Unknown function: {tool_call.name}")
