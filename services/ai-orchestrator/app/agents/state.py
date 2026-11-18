from typing import TypedDict, List, Dict, Any, Optional

class DecisionIntelligenceState(TypedDict):
    # User Input
    question: str
    user_role: str

    # Agent 1: Query Planning Agent
    requires_sql: bool
    requires_docs: bool
    planning_reasoning: str

    # Agent 2: Document Retrieval Agent (Qdrant RAG)
    retrieved_documents: List[Dict[str, Any]]

    # Agent 3: SQL Query Agent (NL-to-SQL + Rust SQL Guard)
    generated_sql: str
    sql_results: List[Dict[str, Any]]
    sql_guard_status: str

    # Agent 4: Evidence Validation Agent
    is_evidence_grounded: bool
    validation_feedback: str

    # Agent 5: Answer Generation Agent
    final_answer: str
    citations: List[Dict[str, Any]]
    has_sufficient_evidence: bool

    # Observability & Cost Tracking
    workflow_logs: List[Dict[str, Any]]
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    total_latency_seconds: float
