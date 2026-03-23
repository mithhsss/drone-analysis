# Drone Intelligence System — India 

An AI-powered central hub for drone intelligence, regulatory compliance, and business analytics specifically tailored for the Indian drone ecosystem. This system integrates Retrieval Augmented Generation (RAG) with a suite of specialized calculation tools to provide accurate, cited, and actionable insights.

---

##  System Architecture

The project follows a modular, decoupled architecture:

- **Frontend (React + Vite)**: A modern, responsive dashboard with dark mode support. It features a real-time chat interface, specialized tool panels, and live analytics visualizations.
- **Backend (FastAPI)**: A high-performance Python backend that routes requests, manages conversation state in SQLite, and bridges the AI models with the tool ecosystem.
- **AI Agent (Google Gemini 1.5/2.0/3.0)**: A central "Brain" that uses function calling to choose between searching the Knowledge Base or executing specific mathematical tools.
- **Vector DB (Pinecone)**: Stores high-dimensional embeddings of DGCA regulations, training institute lists, and industry reports for semantic retrieval.
- **MCP Server (Model Context Protocol)**: Implements specialized tools (Flight Time, ROI, Compliance, etc.) as modular extensions.

---

##  Tech Stack

- **Core**: Python 3.10+, TypeScript, React
- **Web**: FastAPI, Vite, Tailwind CSS, Lucide-React
- **AI**: Google Generative AI (Gemini), Pinecone Vector DB
- **Database**: SQLite (Transient & Persistent Chat Memory)
- **Visualization**: Recharts

---

##  Getting Started

### 1. Prerequisites
- Python installed on your system.
- Node.js and NPM installed.
- A Pinecone API Key and a Google Generative AI API Key.

### 2. Environment Setup
Create a `.env` file in the root directory based on `.env.example`:
```env
PINECONE_API_KEY=your_key
GOOGLE_API_KEY=your_key
MCP_LOG_LEVEL=INFO
```

### 3. Backend Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn api.main:app --reload --port 8000
```

### 4. Frontend Installation
```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

---

##  API Documentation

### Chat & History
- `POST /api/chat/`: Send a message to the AI Agent. Includes conversation memory and RAG citations.
- `GET /api/chats`: Retrieve a list of all existing chat sessions for the sidebar.
- `GET /api/chats/{chat_id}`: Load the full message history for a specific session.

### Specialized Tools (MCP)
- `POST /api/v1/calculate/flight-time`: Calculates drone flight endurance based on weight, battery, and environmental factors.
- `POST /api/v1/calculate/roi`: Generates financial projections for drone businesses (Agriculture, Mapping, etc.).
- `POST /api/v1/check/compliance`: Verifies DGCA Nano/Micro/Small/Medium category regulations based on weight and mission type.
- `POST /api/v1/recommend/drone`: Matches specific hardware from the internal `drone_models.csv` database to user requirements (Budget, Payload, etc.).

### System & Data
- `POST /api/v1/upload`: Upload PDF/TXT documents to be chunked and indexed into the Pinecone Vector DB.
- `GET /api/v1/analytics`: Real-time stats on request counts, vector density, and average response times.

---

##  Dashboard User Guide

###  Chat Assistant
The central area where you can ask anything about the Indian drone market. The AI automatically retrieves data from the vector database and provides **Source Citation Cards** (e.g., `regulations.csv`) that link directly to the source information.

###  Flight Time Calculator
Located in the right sidebar. Enter your battery capacity (mAh) and weights. It uses a mathematical model to forecast flight efficiency and provides range estimates.

###  ROI Calculator
Calculate when your drone business will break even. Input setup costs, monthly revenue targets, and operational expenses. It produces a multi-year profitability verdict.

###  Compliance Checker
Enter mission details to see if you are compliant with Indian laws. It checks if you need a UIN, Remote Pilot Licence, or specific flight approvals.

###  Drone Recommender
A structured search tool that scans the curated `drone_models.csv` database to find the perfect aircraft within your budget and payload requirements.

###  Global Analytics
View live system performance, popular queries, and vector database health.

---

## Project Structure
- `api/`: FastAPI routes, Pydantic models, and business logic services.
- `data/`: Structured (CSV) and unstructured data files + SQLite DB.
- `frontend/`: React source code, components, and styling.
- `mcp_server/`: Implementation of the Model Context Protocol tools.
- `rag/`: Script for ingesting and embedding knowledge into Pinecone.
- `scripts/`: Utility scripts for maintenance and testing.

---

*Verified for India DGCA DigitalSky Guidelines Level 2.1.*
