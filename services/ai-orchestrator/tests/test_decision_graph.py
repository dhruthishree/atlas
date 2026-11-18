import pytest
from app.agents.orchestrator import MultiSourceDecisionGraph

def test_multi_source_decision_graph():
    graph = MultiSourceDecisionGraph()
    question = "Which departments exceeded their quarterly budgets, and what documented reasons explain the overspending?"
    
    result = graph.execute(question, user_role="VP_Finance")

    # 1. State assertions
    assert result["question"] == question
    assert result["requires_sql"] is True
    assert result["requires_docs"] is True
    assert len(result["retrieved_documents"]) > 0
    assert len(result["sql_results"]) > 0
    assert result["is_evidence_grounded"] is True
    assert len(result["citations"]) > 0
    assert "[1]" in result["final_answer"]

    # 2. Check full DAG auditability
    executed_agents = [log["agent"] for log in result["workflow_logs"]]
    assert "QueryPlanningAgent" in executed_agents
    assert "DocumentRetrievalAgent" in executed_agents
    assert "SQLQueryAgent" in executed_agents
    assert "EvidenceValidationAgent" in executed_agents
    assert "AnswerGenerationAgent" in executed_agents
