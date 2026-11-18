import json
from datetime import datetime, timezone
from typing import Dict, Any
from app.agents.state import DecisionIntelligenceState
from app.core.llm import GeminiService, calculate_token_cost

PLANNING_PROMPT = """You are the Query Planning Agent in ATLAS Enterprise Decision Intelligence.
Determine what information sources are needed to answer the user's question:
1. requires_sql: boolean (true if question requires tabular, aggregated, or relational data like budgets, numbers, counts).
2. requires_docs: boolean (true if question requires policies, reasons, contracts, explanations).
3. reasoning: short explanation.

Return strict JSON:
{"requires_sql": true, "requires_docs": true, "reasoning": "..."}"""

def query_planning_agent(state: DecisionIntelligenceState, llm: GeminiService) -> Dict[str, Any]:
    logs = list(state.get("workflow_logs", []))
    raw, in_t, out_t = llm.generate(PLANNING_PROMPT, state["question"])
    cost = calculate_token_cost(in_t, out_t)

    req_sql = True
    req_docs = True
    reasoning = "Query requires both tabular budget analysis and documented policy explanations."

    try:
        cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)
        req_sql = bool(parsed.get("requires_sql", True))
        req_docs = bool(parsed.get("requires_docs", True))
        reasoning = parsed.get("reasoning", reasoning)
    except Exception:
        pass

    logs.append({
        "agent": "QueryPlanningAgent",
        "action": "ROUTE_SOURCES",
        "details": f"Sources: SQL={req_sql}, Documents={req_docs}. Plan: {reasoning}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "requires_sql": req_sql,
        "requires_docs": req_docs,
        "planning_reasoning": reasoning,
        "total_input_tokens": state.get("total_input_tokens", 0) + in_t,
        "total_output_tokens": state.get("total_output_tokens", 0) + out_t,
        "total_cost_usd": round(state.get("total_cost_usd", 0.0) + cost, 6),
        "workflow_logs": logs
    }
