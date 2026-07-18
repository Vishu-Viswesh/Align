import os
from dotenv import load_dotenv
load_dotenv()

# Enable CrewAI Tracing
os.environ['CREWAI_TRACING_ENABLED'] = 'true'
os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
os.environ['OTEL_SDK_DISABLED'] = 'true'

from fastapi import FastAPI, HTTPException
from redis import Redis
import sys


# Add parent directory to path to allow importing from data_sourcing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_sourcing.scraper import SpecializedScraper, ESGData

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Aligned Backend", version="1.0.0")

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis Connection (Placeholder)
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = Redis(host=redis_host, port=redis_port, db=0)

@app.get("/health")
async def health_check():
    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return {
        "status": "healthy", 
        "redis": redis_status,
        "module": "Aligned Backend"
    }

from pymongo import MongoClient

# MongoDB Setup
mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME", "aligned_db")
collection_name = os.getenv("COLLECTION_NAME", "esg_data")

mongo_client = None
mongo_collection = None

if mongo_uri:
    try:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        mongo_collection = mongo_client[db_name][collection_name]
    except Exception as e:
        print(f"MongoDB Init Fail: {e}")

# MOCK DATA FALLBACK
MOCK_PROJECT_DATA = {
    "project_id": "mock_solar_vietnam",
    "project_title": "Green Horizon Solar Farm",
    "description": "500MW Solar Photovoltaic Plant in Binh Thuan Province, Vietnam.",
    "analysis": {
        "final_weighted_score": 78.5,
        "executive_summary": "The Green Horizon Solar Farm is a highly viable renewable energy project with strong financial returns (12% ROI) and significant environmental benefits. However, it faces moderate limitations in board diversity and social engagement depth.",
        "environmental": {
            "score": 92.0,
            "summary": "Excellent displacement of coal power; land use is non-arable.",
            "strengths": ["Displaces 600,000 tons of CO2 annually", "Utilizes degraded land", "Grid-compliant inverter technology"],
            "gaps": ["Water usage in panel cleaning not detailed", "End-of-life recycling plan missing"],
            "action_items": ["Implement dry-cleaning robots", "Partner with PV Cycle"]
        },
        "social": {
            "score": 65.0,
            "summary": "Commitment to local hiring is positive, but community consultation has been minimal.",
            "strengths": ["70% local workforce target", "Fair wage pledge verified"],
            "gaps": ["No formal grievance mechanism", "Lack of female representation"],
            "action_items": ["Establish a community liaison office", "Set a 30% quota for female engineers"]
        },
        "governance": {
            "score": 70.0,
            "summary": "Transparent bidding, but board composition is outdated.",
            "strengths": ["Full disclosure of beneficial ownership", "Anti-bribery policy in place"],
            "gaps": ["Board is 100% male", "Audit committee not independent"],
            "action_items": ["Appoint 2 independent directors", "Publish annual sustainability report"]
        },
        "roi": {
            "score": 85.0,
            "summary": "Strong financials backed by a 20-year PPA with EVN.",
            "strengths": ["12% IRR exceeds regional average", "Secured feed-in tariff"],
            "gaps": ["High initial capex sensitivity", "Currency fluctuation risk (VND/USD)"],
            "action_items": ["Hedge 50% of debt exposure", "Optimize O&M costs"]
        },
        "risk": {
            "score": 60.0,
            "summary": "Moderate risks related to grid curtailment and tropical storms.",
            "strengths": ["Insurance covers force majeure", "Tier-1 panel suppliers"],
            "gaps": ["Binh Thuan grid is congested", "Cyclone resilience not fully specified"],
            "action_items": ["Negotiate 'take-or-pay' clause", "Upgrade racking to Cat 3 standard"]
        }
    }
}

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from typing import List

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/projects/analyze")
async def analyze_project(payload: dict):
    """
    Trigger live CrewAI analysis.
    Pushes status updates via WebSockets.
    """
    title = payload.get("title", "Unknown Project")
    description = payload.get("description", "")
    
    if not description:
        raise HTTPException(status_code=400, detail="Description is required")

    try:
        # Import here to avoid circular dependencies if any
        from rag_agent.crew_engine import CrewEngine
        engine = CrewEngine()
        
        weights = payload.get("weights")
        
        # 1. Status Callback Definition
        import asyncio
        loop = asyncio.get_event_loop()
        def status_callback(message: str):
            # Use run_coroutine_threadsafe to broadcast from the simulation thread
            asyncio.run_coroutine_threadsafe(manager.broadcast(message), loop)

        # 2. Signal Start
        await manager.broadcast(f"Starting analysis for: {title}")
        
        # 3. Final Execution & DB Save (now with live callbacks)
        # Note: run_simulation is a blocking call, but in FastAPI it's usually run in a thread 
        # when using 'def' instead of 'async def'. 
        # However, since this is 'async def', we should ideally run it in a threadpool.
        from fastapi.concurrency import run_in_threadpool
        result = await run_in_threadpool(engine.run_simulation, title, description, weights, status_callback) 
        
        await manager.broadcast("COMPLETED: Report saved to MongoDB Atlas.")
        
        # Wrap result for frontend (Dashboard expects data.analysis)
        response_data = {
            "project_id": title.lower().replace(" ", "_"),
            "project_title": title,
            "description": description,
            "analysis": result
        }
        return response_data
        
    except Exception as e:
        await manager.broadcast(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects")
async def list_projects():
    """
    Fetch list of all projects for selection.
    """
    projects = []
    if mongo_collection is not None:
        try:
            # Fetch project_id and project_title
            cursor = mongo_collection.find({}, {"project_id": 1, "project_title": 1, "_id": 0})
            for doc in cursor:
                pid = doc.get("project_id")
                if not pid:
                    continue
                
                title = doc.get("project_title")
                if not title:
                    title = pid.replace("_", " ").title()
                
                projects.append({"project_id": pid, "project_title": title})
            
            if projects:
                return projects
        except Exception as e:
            print(f"DB List Error VERIFIED_V2: {e}")
    
    # Mock Fallback if DB empty or unreachable
    return [{"project_id": "mock_solar_vietnam", "project_title": "Green Horizon Solar Farm"}]

@app.get("/projects/{project_id}")
async def get_project_report(project_id: str):
    """
    Fetch comprehensive project analysis.
    Falls back to mock data if DB is unreachable or data is missing (for demo purposes).
    """
    # 1. Try MongoDB
    if mongo_collection is not None:
        try:
            doc = mongo_collection.find_one({"project_id": project_id})
            if doc:
                 # Convert ObjectId to str
                doc["_id"] = str(doc["_id"])
                return doc
        except Exception as e:
            print(f"DB Read Error: {e}")
            # Fallthrough to mock
            
    # 2. Mock Fallback
    if project_id == "mock_solar_vietnam" or project_id == "simulation":
        return MOCK_PROJECT_DATA
    
    raise HTTPException(status_code=404, detail="Project not found (and no mock available)")

@app.post("/scrape", response_model=ESGData)
async def scrape_company(entity: str, source: str = "MSCI"):
    """
    Trigger the scraper for a specific entity.
    """
    scraper = SpecializedScraper()
    if source.upper() == "MSCI":
        result = scraper.scrape_msci(entity)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        # Ensure result matches ESGData schema, ScrapeGraphAI returns dict
        return result
    else:
        raise HTTPException(status_code=400, detail="Source not supported yet")
