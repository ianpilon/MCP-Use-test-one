"""Tests for the MCP server."""
import os
from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_files():
    """Test listing files endpoint."""
    response = client.get("/files")
    assert response.status_code == 200
    assert "files" in response.json()
    files = response.json()["files"]
    assert isinstance(files, list)
    assert all(isinstance(f, str) for f in files)


def test_mcp_functions():
    """Test MCP functions endpoint."""
    response = client.get("/mcp/functions")
    assert response.status_code == 200
    assert "functions" in response.json()
    functions = response.json()["functions"]
    assert isinstance(functions, list)
    assert len(functions) == 2  # list_files and get_file_content
    assert all(isinstance(f, dict) for f in functions)
    assert all("name" in f for f in functions)
    assert all("description" in f for f in functions)
    assert all("parameters" in f for f in functions)


@pytest.mark.asyncio
async def test_mcp_invoke_list_files():
    """Test MCP invoke endpoint with list_files function."""
    response = client.post(
        "/mcp/invoke",
        json={"name": "list_files", "parameters": {}}
    )
    assert response.status_code == 200
    assert "files" in response.json()
    files = response.json()["files"]
    assert isinstance(files, list)
    assert all(isinstance(f, str) for f in files)


@pytest.mark.asyncio
async def test_mcp_invoke_get_file_content():
    """Test MCP invoke endpoint with get_file_content function."""
    # First, ensure we have a test file
    test_file = "placeholder1.txt"
    test_content = "test content"
    test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "context_files", test_file)
    
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)

    try:
        response = client.post(
            "/mcp/invoke",
            json={"name": "get_file_content", "parameters": {"filename": test_file}}
        )
        assert response.status_code == 200
        assert "content" in response.json()
        assert response.json()["content"] == test_content
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
