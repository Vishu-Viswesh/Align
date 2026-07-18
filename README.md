# Align 🌍

**Align** is an intelligent platform that evaluates infrastructure projects based on their **Environmental, Social, and Governance (ESG)** alignment. It deploys a "brain trust" of specialized AI agents that perform multi-domain analysis — drawing insights from both internal retrieval-augmented knowledge and real-time external data — and generates a comprehensive **Master Report** with actionable insights, all accessible through a user-friendly web interface.

---

## 🏗️ Architecture Overview

```
Frontend User Interface
        │
        │  Sends requests to
        ▼
FastAPI Backend API
        │
        │  Triggers analysis by
        ▼
AI Agent Orchestration
     │          │
     │ Consults  │ Enriches
     │ for ctx   │ context via
     ▼          ▼
RAG Service   External Data Sourcing
     │                │
     │  Persists      │ Reads config from
     └──────┬─────────┘
            ▼
  Configuration & Data Persistence
```

The platform works as a pipeline:
1. The **Frontend UI** sends project evaluation requests to the backend
2. The **FastAPI Backend** orchestrates the AI agent pipeline
3. **AI Agent Orchestration** coordinates specialized ESG analysis agents
4. The **RAG Service** provides retrieval-augmented context from internal knowledge
5. **External Data Sourcing** enriches context with real-time data
6. Results are persisted and returned as a structured **Master Report**

---

## ✨ Features

- 🤖 **Multi-Agent AI Pipeline** — Specialized agents for Environmental, Social, and Governance analysis working in parallel
- 🔍 **RAG (Retrieval-Augmented Generation)** — Answers grounded in real sourced data via vector search
- 🌐 **Real-time External Data Sourcing** — Enriches analysis with live data beyond the internal knowledge base
- 📊 **Master Report Generation** — Comprehensive ESG report with actionable insights per project
- ⚡ **FastAPI Backend** — Fast and scalable REST API
- 🖥️ **React Frontend** — Clean UI to submit projects and view ESG reports
- 🐳 **Docker Support** — Fully containerized with Docker Compose for easy setup
- 🔄 **CI/CD** — GitHub Actions workflows for automated deployment

---

## 🗂️ Project Structure

```
Align/
├── backend/            # FastAPI backend — REST APIs, DB models, business logic
├── frontend/           # React frontend — project submission & report viewing UI
├── rag_agent/          # Multi-agent AI pipeline — ESG analysis & report generation
├── data_sourcing/      # Scripts for sourcing and ingesting external data
├── .github/workflows/  # CI/CD GitHub Actions workflows
├── docker-compose.yml  # Docker orchestration
├── .env.example        # Environment variable template
└── DEPLOYMENT.md       # Deployment guide
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, JavaScript |
| Backend | Python, FastAPI |
| AI Agents | CrewAI |
| RAG / Vector Store | Qdrant |
| Database | MongoDB |
| Cache | Redis |
| LLMs | Groq, Gemini |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- MongoDB instance
- API keys for your LLM provider (Groq / Gemini)

### 1. Clone the repository
```bash
git clone https://github.com/Saicharan-Billakanti/Align.git
cd Align
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Open .env and fill in your API keys and configuration
```

### 3. Run with Docker (recommended)
```bash
docker-compose up --build
```

### 4. Or run manually

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

**RAG Agent:**
```bash
cd rag_agent
pip install -r requirements.txt
python main.py
```

---

## 📄 Environment Variables

See [`.env.example`](.env.example) for all required variables. Key ones include:

```env
MONGO_URI=
GROQ_API_KEY=
GEMINI_API_KEY=
REDIS_URL=
QDRANT_URL=
```

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore` and should stay local only.

---

## 📊 How It Works

1. **Submit a Project** — Enter infrastructure project details via the frontend
2. **Agent Orchestration** — The backend triggers specialized AI agents for E, S, and G analysis
3. **RAG Context** — Agents consult the vector store for relevant internal knowledge
4. **External Enrichment** — Real-time data is fetched to enrich the analysis
5. **Master Report** — A consolidated ESG report with scores and actionable insights is generated and stored
6. **View Results** — The report is displayed in the frontend dashboard

---

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment instructions.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📃 License

This project is licensed under the MIT License.
