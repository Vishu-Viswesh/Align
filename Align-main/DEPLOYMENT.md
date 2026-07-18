# Deployment Strategy: EcoAlign on DigitalOcean

This document outlines the strategy for deploying the EcoAlign platform (FastAPI + React + MongoDB + Redis) to DigitalOcean.

## Architecture Overview

- **Frontend**: React (Vite) deployed as a **DigitalOcean App Platform** Static Site.
- **Backend**: FastAPI deployed as a **DigitalOcean App Platform** Web Service (Dockerized).
- **Database**: 
  - **MongoDB**: DigitalOcean Managed MongoDB or MongoDB Atlas (Global).
  - **Redis**: DigitalOcean Managed Redis for caching and rate-limiting handles.
- **Async Tasks**: CrewAI runs within the FastAPI process (sequential execution to manage rate limits).

## Environment Variables Required

### Backend (.env)
- `MONGO_URI`: Connection string for MongoDB.
- `REDIS_HOST`, `REDIS_PORT`: Connection details for Redis.
- `GROQ_API_KEY`: API key for Llama 3.1 inference.
- `OPENAI_API_KEY`: Required for ScrapeGraphAI (GPT-4o).
- `SERPER_API_KEY`: For web searching.
- `TAVILY_API_KEY`: Alternative search tool.

### Frontend (.env.production)
- `VITE_API_URL`: URL of the deployed FastAPI backend.
- `VITE_WS_URL`: WebSocket URL for real-time updates.

## Deployment Steps

### 1. Containerization
The project includes a `Dockerfile` in the `backend` directory. Ensure it's optimized for production:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. DigitalOcean App Platform Configuration
1. **GitHub Integration**: Connect your repository to DigitalOcean.
2. **Add Backend Service**:
   - Point to the `backend/` directory or root with the specific Dockerfile.
   - Set HTTP port to `8080`.
   - Add all environment variables.
3. **Add Frontend Static Site**:
   - Use the `frontend/` directory.
   - Build Command: `npm run build`.
   - Output Directory: `dist`.
   - Set `VITE_API_URL` to the Backend Service URL.

### 3. Managed Services
1. **Database**: Spin up a MongoDB cluster in the same region as the App Platform.
2. **Redis**: Spin up a Redis cluster (or use the smallest available instance).

## Continuous Integration (GitHub Actions)
A `.github/workflows/deploy.yml` can be added to automate the process:
```yaml
name: Deploy to DigitalOcean
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
      - name: Deploy to App Platform
        run: doctl apps create-deployment <app-id>
```

## Scaling Considerations
- **Vertical Scaling**: Increase CPU/RAM for the Backend Service if CrewAI needs more processing power (though most work is LLM-based).
- **Rate Limiting**: The current sequential execution with 60s delays is vital for remaining within Groq tier limits.
