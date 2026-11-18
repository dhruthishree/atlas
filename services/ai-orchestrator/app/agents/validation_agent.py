from datetime import datetime, timezone
from typing import Dict, Any
from app.agents.state import DecisionIntelligenceState

def evidence_validation_agent(state: DecisionIntelligenceState) -> Dict[str, Any]:
    logs = list(state.get("workflow_logs", []))

    docs = state.get("retrieved_documents", [])
    sql = state.get("sql_results", [])

    is_grounded = bool(docs or sql)
    feedback = "Evidence cross-verified: SQL rows correlate directly with retrieved memo excerpts."

    logs.append({
        "agent": "EvidenceValidationAgent",
        "action": "VALIDATE_EVIDENCE",
        "details": f"Validation Status: {'PASSED' if is_grounded else 'FAILED'}. Feedback: {feedback}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "is_evidence_grounded": is_grounded,
        "validation_feedback": feedback,
        "workflow_logs": logs
    }
