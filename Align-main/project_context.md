# Project Context: Aligned - Infrastructure & ESG Planning Agent

## 1. Project Mission
**Name**: Aligned
**Slogan**: "From Misplaced to Perfectly Placed"
**Goal**: An AI-powered decision support system that evaluates infrastructure projects (e.g., Solar Farms) against **ESG (Environmental, Social, Governance)** criteria to ensure sustainable development.

## 2. Technical Stack
- **Frontend**: React (Vite) + Tailwind CSS + Recharts (Radar/Accordion UI).
- **Backend**: FastAPI (Python) + Uvicorn.
- **Database**: MongoDB Atlas (Data + Vector Store).
- **AI/LLM Engine**:
  - **CrewAI**: Multi-Agent Orchestration.
  - **Groq (Mixtral-8x7b)**: Fast, quantitative inference (ROI, Risk).
  - **Gemini (Gemini 1.5 Flash)**: High-context qualitative analysis (Env, Soc, Gov).
  - **Embeddings**: BAAI/bge-large-en-v1.5 (via HuggingFace).
- **Data Sourcing**: ScrapeGraphAI + Tavily/Serper (Web Search).

## 3. Core Architecture
The system follows a linear pipeline:
1.  **Ingestion**: User Input -> PDF/Text Description of a project.
2.  **RAG Context**: `vector_service.py` searches MongoDB for similar past projects or regulatory standards.
3.  **Agent Analysis**: `crew_engine.py` spins up 5 specialized agents.
4.  **Scoring**: Agents calculate weighted scores ($E \times 0.3 + S \times 0.2 + G \times 0.2 + ROI \times 0.2 + Risk \times 0.1$).
5.  **Visualization**: React Dashboard displays a validation report with "Strengths", "Gaps", and "Fixes".

## 4. Key Components (File Map)
- **`backend/main.py`**: FastAPI entry point. Contains the **Fallback Logic** (`MOCK_PROJECT_DATA`) to serve the UI even if DB is offline.
- **`rag_agent/crew_agents.py`**: Defines the 5 Agents using `crewai.LLM` wrapper.
  - *Env/Soc/Gov Agents* use `gemini/gemini-pro`.
  - *ROI/Risk Agents* use `groq/mixtral-8x7b-32768`.
- **`rag_agent/crew_tasks.py`**: Defines strict JSON Pydantic schemas for agent outputs.
- **`rag_agent/crew_engine.py`**: Orchestrates the Crew run and handles MongoDB persistence.
- **`frontend/src/components/Dashboard.jsx`**: The UI rendering the Radar Chart and Accordions.
- **`vector_service.py`**: Handles embedding generation and MongoDB vector search.

## 5. Current MVP Status
- **Functional**: The Dashboard is LIVE at `http://localhost:5173`.
- **Simulation**: The Multi-Agent System has been code-verified.
- **Data Workaround**: Due to IP whitelist restrictions on the MongoDB Atlas cluster, the Backend currently uses a **High-Fidelity Mock Fallback** to ensure the presentation demo works 100% of the time without database errors.
- **Environment**: Keys (`GROQ`, `GOOGLE`) are set in `.env`.

## 6. How to Run
1.  **Backend**: `uvicorn backend.main:app --reload` (Port 8000)
2.  **Frontend**: `npm run dev` (Port 5173)

## 7. Next Steps (Roadmap)
- Fix MongoDB Atlas IP Whitelist.
- Enable live scraping in `scraper.py` (currently integrated but not in the main demo loop).
- Deploy to DigitalOcean.

## 8. Database Status
**State**: **FULLY OPERATIONAL**
- **Connected**: Verified connection to Atlas cluster `Cluster0`.
- **Authenticated**: Successfully resolved `bad auth` by consolidating `.env` variables and correcting password.
- **Data**: Mock analysis report seeded into `esg_data` collection.
- **Resilience**: Graceful fallback remains in `main.py` as a safety measure.

