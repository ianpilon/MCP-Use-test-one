# Project Memory: Model Context Protocol (MCP) Server

**Note:**
As you complete tasks and reference relevant files, update this file as our memory to help with future tasks.

---

## Project Goal
Build a Model Context Protocol (MCP) server following the design of the mcp_use server. The server will be hosted on render.com. Start simple with a folder containing specific files (for now, 3 placeholder .txt files; these will be swapped out with PDFs later).

## Tasks

- [x] 1. Set up the basic folder structure for the MCP server project.
- [x] 2. Create a folder (e.g., `context_files/`) and add 3 placeholder .txt files.
- [x] 3. Scaffold a minimal FastAPI server with endpoints to list and serve files from `context_files/`.
- [x] 4. Test the FastAPI server locally:
    - a. Install dependencies: `pip install -r requirements.txt`
    - b. Run the server: `uvicorn main:app --reload`
    - c. Visit `http://127.0.0.1:8000/health` to check the health endpoint.
    - d. Visit `http://127.0.0.1:8000/files` to see the list of files.
    - e. Download a file via `http://127.0.0.1:8000/files/placeholder1.txt`.
- [x] 5. Deploy to render.com:
    - a. Push code to GitHub
    - b. Connect GitHub repo to render.com
    - c. Deploy using the provided render.yaml configuration
    - d. Share the deployed URL for others to use
- [ ] 6. (Next steps will be added as the project progresses)

---

**Notes:**
- Created `context_files/` directory with `placeholder1.txt`, `placeholder2.txt`, and `placeholder3.txt` as placeholders for future PDFs.
- Added `main.py` (FastAPI server), `requirements.txt` (dependencies), and `Procfile` (for Render deployment). Server exposes `/health`, `/files`, and `/files/{filename}` endpoints.
