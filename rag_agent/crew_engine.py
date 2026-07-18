import os
import json
from dotenv import load_dotenv
load_dotenv()

# Enable CrewAI Tracing
os.environ['CREWAI_TRACING_ENABLED'] = 'true'
os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
os.environ['OTEL_SDK_DISABLED'] = 'true'

from crewai import Crew, Process
from rag_agent.crew_agents import AlignedAgents
from rag_agent.crew_tasks import AlignedTasks
from pymongo import MongoClient

class CrewEngine:
    def __init__(self):
        self.agents = AlignedAgents()
        self.tasks = AlignedTasks()

        # MongoDB Setup
        self.mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
        self.db_name = os.getenv("DB_NAME", "aligned_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "esg_data")

        if self.mongo_uri:
            self.client = MongoClient(self.mongo_uri)
            self.collection = self.client[self.db_name][self.collection_name]
        else:
            self.collection = None

    def run_analysis(self, project_content: str, project_id: str = "simulation_001", weights=None, status_callback=None):
        env_agent = self.agents.environmental_specialist()
        soc_agent = self.agents.social_impact_evaluator()
        gov_agent = self.agents.governance_analyst()
        roi_agent = self.agents.roi_analyst()
        risk_agent = self.agents.risk_assessor()
        coordinator = self.agents.aggregator()  # IMPORTANT

        t_env = self.tasks.analysis_task(env_agent, project_content, "Environmental")
        t_soc = self.tasks.analysis_task(soc_agent, project_content, "Social")
        t_gov = self.tasks.analysis_task(gov_agent, project_content, "Governance")
        t_roi = self.tasks.analysis_task(roi_agent, project_content, "ROI")
        t_risk = self.tasks.analysis_task(risk_agent, project_content, "Risk")

        import time
        domain_findings = ""

        for t, label in [
            (t_env, "Environmental"),
            (t_soc, "Social"),
            (t_gov, "Governance"),
            (t_roi, "ROI"),
            (t_risk, "Risk"),
        ]:
            if status_callback:
                status_callback(f"Agent: {label} is analyzing the project...")

            crew = Crew(
                agents=[t.agent],
                tasks=[t],
                verbose=True,
                process=Process.sequential,
                memory=False,
                tracing=True
            )

            try:
                res = crew.kickoff()
                raw_text = res.raw if hasattr(res, 'raw') else str(res)
                domain_findings += f"\n### {label} Findings:\n{raw_text}\n"
                time.sleep(75)  # safer for Groq TPM
            except Exception as e:
                domain_findings += f"\n### {label} Findings:\nERROR: {str(e)}\n"

        if status_callback:
            status_callback("Aggregating all domain findings into Master Report...")

        t_agg = self.tasks.aggregation_task(coordinator, domain_findings, weights=weights)
        crew_agg = Crew(
            agents=[coordinator],
            tasks=[t_agg],
            verbose=True,
            process=Process.sequential,
            memory=False,
            tracing=True
        )

        try:
            res_agg = crew_agg.kickoff()
            final_result = res_agg
        except Exception as e:
            print(f"Aggregation Exception: {e}")
            final_result = {}

        final_json = {}

        if hasattr(final_result, 'json_dict') and final_result.json_dict:
            final_json = final_result.json_dict
        elif hasattr(final_result, 'pydantic') and final_result.pydantic:
            final_json = final_result.pydantic.model_dump()

        def extract_json(raw_str):
            if not raw_str:
                return {}

            try:
                start = raw_str.find('{')
                end = raw_str.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(raw_str[start:end + 1])
            except:
                pass

            try:
                clean = raw_str.strip()
                if '```json' in clean:
                    clean = clean.split('```json')[1].split('```')[0].strip()
                elif '```' in clean:
                    clean = clean.split('```')[1].split('```')[0].strip()
                return json.loads(clean)
            except:
                pass

            return {}

        if not final_json and hasattr(final_result, 'raw'):
            final_json = extract_json(final_result.raw)

        # Final check: Ensure we have at least an executive summary if parsing fails
        if not final_json:
            raw_output = str(final_result.raw) if hasattr(final_result, 'raw') else str(final_result)
            final_json = {
                "executive_summary": "Warning: Data parsing failed. Raw output preserved below.",
                "environmental": {"score": 0, "summary": raw_output[:500]},
                "social": {"score": 0, "summary": "Full raw data in DB."},
                "governance": {"score": 0, "summary": ""},
                "roi": {"score": 0, "summary": ""},
                "risk": {"score": 0, "summary": ""},
                "final_weighted_score": 0
            }

        if hasattr(final_json, 'model_dump'):
            final_json = final_json.model_dump()

        if self.collection is not None:
            document = {
                "project_id": project_id,
                "project_title": project_id.replace("_", " ").title(),
                "analysis": final_json,
                "original_content_snippet": project_content[:200]
            }

            self.collection.update_one(
                {"project_id": project_id},
                {"$set": document},
                upsert=True
            )

        return final_json

    def run_simulation(self, title: str, description: str, weights=None, status_callback=None):
        extra_context = ""

        try:
            from data_sourcing.scraper import SpecializedScraper
            scraper = SpecializedScraper()
            if status_callback:
                status_callback(f"Scraper: Searching MSCI database for '{title}'...")
            scraped_res = scraper.scrape_msci(title)
            if scraped_res and "error" not in scraped_res:
                extra_context = f"\n\n### Scraped ESG Data (MSCI):\n{json.dumps(scraped_res, indent=2)}"
        except:
            pass

        content = f"Project Title: {title}\nDescription: {description}{extra_context}"
        project_id = title.lower().replace(" ", "_")

        result = self.run_analysis(content, project_id=project_id, weights=weights, status_callback=status_callback)

        if self.collection is not None:
            self.collection.update_one(
                {"project_id": project_id},
                {"$set": {"project_title": title}},
                upsert=True
            )

        return result
