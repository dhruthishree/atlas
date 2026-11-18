from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.core.config import settings
from app.agents.orchestrator import MultiSourceDecisionGraph

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ATLAS Enterprise Decision Intelligence & LangGraph Multi-Source RAG",
    version="1.0.0"
)

decision_graph = MultiSourceDecisionGraph()

class DecisionQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Complex enterprise cross-source question")
    user_role: str = Field(default="Executive", description="User role for permission gating")

@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "atlas-ai-orchestrator",
        "engine": "Python LangGraph + Gemini 2.5 Flash"
    }

@app.post("/api/v1/reason")
def reason_across_sources(payload: DecisionQueryRequest) -> Dict[str, Any]:
    try:
        result = decision_graph.execute(
            question=payload.question,
            user_role=payload.user_role
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision reasoning failed: {str(e)}")
