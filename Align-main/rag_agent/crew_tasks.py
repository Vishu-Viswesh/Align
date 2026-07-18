import os
from dotenv import load_dotenv
load_dotenv()

# Enable CrewAI Tracing
os.environ['CREWAI_TRACING_ENABLED'] = 'true'
os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
os.environ['OTEL_SDK_DISABLED'] = 'true'

from crewai import Task
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List

class AnalysisReport(BaseModel):
    score: float = Field(description="Score between 0 and 100.")
    summary: str
    strengths: List[str]
    gaps: List[str]
    action_items: List[str]

class MasterReport(BaseModel):
    environmental: AnalysisReport
    social: AnalysisReport
    governance: AnalysisReport
    roi: AnalysisReport
    risk: AnalysisReport
    final_weighted_score: float
    executive_summary: str

class AlignedTasks:
    def analysis_task(self, agent, context_data, domain):
        return Task(
            description=dedent(f"""
Analyze the project for {domain}.
Return ONLY valid JSON matching this schema:
{{ "score": number, "summary": string, "strengths": [], "gaps": [], "action_items": [] }}

Project:
{context_data[:1000]}
"""),
            expected_output="Pure JSON matching AnalysisReport. No prose.",
            agent=agent,
            output_json=AnalysisReport
        )

    def aggregation_task(self, agent, domain_findings, weights=None):
        if weights is None:
            weights = {"e": 0.3, "s": 0.2, "g": 0.2, "roi": 0.2, "risk": 0.1}

        return Task(
            description=dedent(f"""
You are a strict JSON generator.

Return ONLY valid JSON with this exact structure:
{{
  "environmental": {{ score, summary, strengths[], gaps[], action_items[] }},
  "social": {{ score, summary, strengths[], gaps[], action_items[] }},
  "governance": {{ score, summary, strengths[], gaps[], action_items[] }},
  "roi": {{ score, summary, strengths[], gaps[], action_items[] }},
  "risk": {{ score, summary, strengths[], gaps[], action_items[] }},
  "final_weighted_score": number,
  "executive_summary": string
}}

Rules:
- Output PURE JSON only.
- Ensure all scores are numbers.
- Provide a comprehensive executive_summary (approx 2-3 paragraphs).

Use formula to calculate final_weighted_score:
E*{weights['e']} + S*{weights['s']} + G*{weights['g']} + ROI*{weights['roi']} + Risk*{weights['risk']}

Domain Findings:
{domain_findings}
"""),
            expected_output="Pure JSON matching MasterReport.",
            agent=agent,
            output_json=MasterReport
        )
