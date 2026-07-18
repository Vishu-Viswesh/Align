import os
import requests
import json
from typing import List, Dict, Any
from scrapegraphai.graphs import SmartScraperGraph
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --- structured output models ---
class ESGData(BaseModel):
    company_name: str = Field(description="Name of the company")
    esg_rating: str = Field(description="Overall ESG rating (e.g., AAA, A, BBB)")
    e_score: str = Field(description="Environmental score or details")
    s_score: str = Field(description="Social score or details")
    g_score: str = Field(description="Governance score or details")
    source: str = Field(description="Source of the data (e.g., MSCI, Sustainalytics)")

# --- search tools ---
class SearchTools:
    def __init__(self):
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")

    def search_serper(self, query: str) -> List[str]:
        """Search using Serper.dev API"""
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': self.serper_key,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            results = response.json().get("organic", [])
            return [r["link"] for r in results if "link" in r]
        except Exception as e:
            print(f"Serper error: {e}")
            return []

    def search_tavily(self, query: str) -> List[str]:
        """Search using Tavily API"""
        # Using requests for simplicity if SDK fails or just to keep it lightweight
        # create-vite auto-installed, but let's use direct API for control if needed.
        # But we added tavily-python, let's use it if available or fallback to requests.
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_key)
            response = client.search(query=query, search_depth="basic")
            return [r["url"] for r in response.get("results", [])]
        except Exception as e:
            print(f"Tavily error: {e}")
            return []

# --- scraper agent ---
class SpecializedScraper:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.search_tools = SearchTools()
        self.llm_config = {
            "llm": {
                "api_key": self.openai_key,
                "model": "openai/gpt-4o",
            },
            "verbose": True,
            "headless": False, # Open browser for visibility as requested
        }

    def scrape_msci(self, company: str):
        print(f"Searching MSCI data for {company}...")
        # 1. Search for the specific MSCI URL
        query = f"site:msci.com {company} ESG ratings"
        links = self.search_tools.search_serper(query)
        
        if not links:
            print("No links found using Serper, trying Tavily...")
            links = self.search_tools.search_tavily(query)
        
        if not links:
            return {"error": "No URL found"}
        
        target_url = links[0]
        print(f"Targeting URL: {target_url}")

        # 2. Scrape using ScrapeGraphAI
        graph = SmartScraperGraph(
            prompt=f"Extract ESG ratings for {company}. Look for the overall rating (AAA-CCC), and any specific E, S, G details. Return as structured JSON matching the schema.",
            source=target_url,
            config=self.llm_config,
            schema=ESGData
        )
        
        try:
            result = graph.run()
            return result
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test Block
    # Ensure keys are set in env or passed here
    # os.environ["SERPER_API_KEY"] = "..."
    # os.environ["OPENAI_API_KEY"] = "..."
    
    agent = SpecializedScraper()
    # Test MSCI
    data = agent.scrape_msci("Tesla")
    print(json.dumps(data, indent=2))
