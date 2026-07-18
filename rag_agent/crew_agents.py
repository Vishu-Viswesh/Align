import os
from dotenv import load_dotenv
load_dotenv()

# Enable CrewAI Tracing
os.environ['CREWAI_TRACING_ENABLED'] = 'true'
os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
os.environ['OTEL_SDK_DISABLED'] = 'true'

from crewai import Agent, LLM

class AlignedAgents:
    def __init__(self):
        # For domain agents (short outputs)
        self.domain_llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1,
            max_tokens=500,  # Increased to avoid truncation
            max_retries=5
        )

        # For aggregator (large structured JSON)
        self.aggregator_llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.0,
            max_tokens=2000, # Increased to accommodate full MasterReport
            max_retries=5
        )

    def environmental_specialist(self):
        return Agent(
            role='Environmental Specialist',
            goal='Analyze environmental impact and sustainability.',
            backstory="Expert in carbon footprint and resource efficiency.",
            verbose=True,
            allow_delegation=False,
            llm=self.domain_llm,
            max_rpm=1,
            max_retry_limit=5
        )

    def social_impact_evaluator(self):
        return Agent(
            role='Social Impact Evaluator',
            goal='Assess labor and community engagement.',
            backstory="Specialist in social responsibility and fair labor.",
            verbose=True,
            allow_delegation=False,
            llm=self.domain_llm,
            max_rpm=1,
            max_retry_limit=5
        )

    def governance_analyst(self):
        return Agent(
            role='Governance Analyst',
            goal='Evaluate ethics and transparency.',
            backstory="Expert in ethical standards and leadership transparency.",
            verbose=True,
            allow_delegation=False,
            llm=self.domain_llm,
            max_rpm=1,
            max_retry_limit=5
        )

    def roi_analyst(self):
        return Agent(
            role='ROI Analyst',
            goal='Predict financial viability.',
            backstory="Seasoned financial analyst ensuring sustainability.",
            verbose=True,
            allow_delegation=False,
            llm=self.domain_llm,
            max_rpm=1,
            max_retry_limit=5
        )

    def risk_assessor(self):
        return Agent(
            role='Risk Assessor',
            goal='Identify regulatory and operational risks.',
            backstory="Identifies hurdles, pitfalls, and greenwashing.",
            verbose=True,
            allow_delegation=False,
            llm=self.domain_llm,
            max_rpm=1,
            max_retry_limit=5
        )

    def aggregator(self):
        return Agent(
            role='Master ESG Coordinator',
            goal='Combine all findings into a single structured JSON report.',
            backstory="Ensures consistent scoring and structured ESG output.",
            verbose=True,
            allow_delegation=False,
            llm=self.aggregator_llm,
            max_rpm=1,
            max_retry_limit=5
        )
