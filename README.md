# Drone Intelligence System

A modular system for drone intelligence, featuring RAG-based analysis, MCP tools, and a FastAPI backend.

## Repository Structure

- `data/`: Raw, processed, and synthetic data for training and analysis.
- `rag/`: Vector DB and embedding logic for data retrieval.
- `mcp_server/`: Anthropic MCP implementation for tool-based interactions.
- `api/`: FastAPI backend for handling requests and routing.
- `frontend/`: User interface (React/Streamlit).
- `tests/`: Project tests.
- `docker-compose.yml`: Container orchestration setup.

## Getting Started

1. **Clone the repository and install backend dependencies:**
   Ensure you have Python installed, then install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Backend:**
   In the root directory of the project, run the `uvicorn` live-reload server:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```
   The API will now be successfully running on `http://localhost:8000`.

3. **Start the Frontend UI:**
   Open a new terminal session, navigate to the `frontend/` folder, and launch the Vite development server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Your user interface will now be actively accessible via `http://localhost:3000`.
