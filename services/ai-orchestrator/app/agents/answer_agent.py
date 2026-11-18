from datetime import datetime, timezone
from typing import Dict, Any, List
from app.agents.state import DecisionIntelligenceState
from app.core.llm import GeminiService, calculate_token_cost

SYNTHESIS_PROMPT = """You are the Answer Generation Agent in ATLAS Enterprise Decision Intelligence.
Your task: Synthesize verified tabular SQL data and unstructured document evidence into an executive-ready response.

Guidelines:
1. Provide exact numbers from SQL data (e.g. variances, budget ceilings).
2. Connect numbers to qualitative justifications from documents.
3. Cite sources with bracketed indicators, e.g. [1], [2].
4. Maintain technical, objective, and executive clarity."""

def answer_generation_agent(state: DecisionIntelligenceState, llm: GeminiService) -> Dict[str, Any]:
    logs = list(state.get("workflow_logs", []))

    docs = state.get("retrieved_documents", [])
    sql = state.get("sql_results", [])

    citations: List[Dict[str, Any]] = []
    doc_context = []
    for idx, d in enumerate(docs, start=1):
        citations.append({
            "citation_id": idx,
            "document_title": d["title"],
            "page_number": d.get("page_number", 1),
            "excerpt": d["excerpt"]
        })
        doc_context.append(f"[{idx}] {d['title']} (Page {d.get('page_number', 1)}): {d['excerpt']}")

    user_prompt = (
        f"USER QUESTION: {state['question']}\n\n"
        f"STRUCTURED SQL ROWS:\n{sql}\n\n"
        f"UNSTRUCTURED DOCUMENT EVIDENCE:\n" + "\n\n".join(doc_context)
    )

    answer, in_t, out_t = llm.generate(SYNTHESIS_PROMPT, user_prompt)
    cost = calculate_token_cost(in_t, out_t)

    logs.append({
        "agent": "AnswerGenerationAgent",
        "action": "SYNTHESIZE_DECISION",
        "details": f"Generated final grounded answer with {len(citations)} citations.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "final_answer": answer,
        "citations": citations,
        "has_sufficient_evidence": True,
        "total_input_tokens": state.get("total_input_tokens", 0) + in_t,
        "total_output_tokens": state.get("total_output_tokens", 0) + out_t,
        "total_cost_usd": round(state.get("total_cost_usd", 0.0) + cost, 6),
        "workflow_logs": logs
    }
