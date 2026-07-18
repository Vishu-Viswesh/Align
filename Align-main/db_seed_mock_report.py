import os
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def seed_mock_data():
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "aligned_db")
    collection_name = os.getenv("COLLECTION_NAME", "esg_data")
    
    if not mongo_uri:
        print("Error: MONGO_URI not set.")
        return

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Mock Master Report matching the CrewAI MasterReport schema
    mock_report = {
        "project_id": "mock_solar_vietnam",
        "created_at": datetime.datetime.utcnow(),
        "project_title": "Green Horizon Solar Farm",
        "description": "500MW Solar Photovoltaic Plant in Binh Thuan Province, Vietnam.",
        "analysis": {
            "final_weighted_score": 78.5,
            "executive_summary": "The Green Horizon Solar Farm is a highly viable renewable energy project with strong financial returns (12% ROI) and significant environmental benefits. However, it faces moderate limitations in board diversity and social engagement depth. The project aligns well with Vietnam's PDP8 goals.",
            "environmental": {
                "score": 92.0,
                "summary": "Excellent displacement of coal power; land use is non-arable, minimizing ecological conflict.",
                "strengths": [
                    "Displaces 600,000 tons of CO2 annually",
                    "Utilizes degraded land (no deforestation)",
                    "Grid-compliant inverter technology"
                ],
                "gaps": [
                    "Water usage in panel cleaning not detailed",
                    "End-of-life recycling plan missing"
                ],
                "action_items": [
                    "Implement dry-cleaning robots to save water",
                    "Partner with PV Cycle for recycling commitment"
                ]
            },
            "social": {
                "score": 65.0,
                "summary": "Commitment to local hiring is positive, but community consultation has been minimal.",
                "strengths": [
                    "70% local workforce target",
                    "Fair wage pledge verified"
                ],
                "gaps": [
                    "No formal grievance mechanism for locals",
                    "Lack of female representation in workforce planning"
                ],
                "action_items": [
                    "Establish a community liaison office",
                    "Set a 30% quota for female engineers"
                ]
            },
            "governance": {
                "score": 70.0,
                "summary": "Transparent bidding and clear ownership, but board composition is outdated.",
                "strengths": [
                    "Full disclosure of beneficial ownership",
                    "Anti-bribery policy in place"
                ],
                "gaps": [
                    "Board is 100% male",
                    "Audit committee not independent"
                ],
                "action_items": [
                    "Appoint 2 independent directors",
                    "Publish annual sustainability report"
                ]
            },
            "roi": {
                "score": 85.0,
                "summary": "Strong financials backed by a 20-year PPA with EVN.",
                "strengths": [
                    "12% IRR exceeds regional average",
                    "Secured feed-in tariff"
                ],
                "gaps": [
                    "High initial capex sensitivity",
                    "Currency fluctuation risk (VND/USD)"
                ],
                "action_items": [
                    "Hedge 50% of debt exposure",
                    "Optimize O&M costs via automation"
                ]
            },
            "risk": {
                "score": 60.0,
                "summary": "Moderate risks related to grid curtailment and tropical storms.",
                "strengths": [
                    "Insurance covers force majeure",
                    "Tier-1 panel suppliers"
                ],
                "gaps": [
                    "Binh Thuan grid is congested (curtailment risk)",
                    "Cyclone resilience not fully specified"
                ],
                "action_items": [
                    "Negotiate 'take-or-pay' clause in PPA",
                    "Upgrade racking to withstand Cat 3 storms"
                ]
            }
        }
    }

    # Upsert
    result = collection.update_one(
        {"project_id": mock_report["project_id"]},
        {"$set": mock_report},
        upsert=True
    )
    print(f"Mock Report Seeded! Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_id}")

if __name__ == "__main__":
    seed_mock_data()
