from langgraph.graph import StateGraph, END
import time
from typing import Dict, Any

from app.agents.state import DecisionIntelligenceState
from app.agents.planning_agent import query_planning_agent
from app.agents.retrieval_agent import document_retrieval_agent
from app.agents.sql_agent import sql_query_agent
from app.agents.validation_agent import evidence_validation_agent
from app.agents.answer_agent import answer_generation_agent
from app.core.llm import GeminiService

class MultiSourceDecisionGraph:
    def __init__(self):
        self.llm = GeminiService()
        self.graph = self._compile_graph()

    def _compile_graph(self):
        workflow = StateGraph(DecisionIntelligenceState)

        # Register Agent Nodes
        workflow.add_node("planner", lambda s: query_planning_agent(s, self.llm))
        workflow.add_node("retriever", document_retrieval_agent)
        workflow.add_node("sql_executor", lambda s: sql_query_agent(s, self.llm))
        workflow.add_node("validator", evidence_validation_agent)
        workflow.add_node("synthesizer", lambda s: answer_generation_agent(s, self.llm))

        # Workflow DAG
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "retriever")
        workflow.add_edge("retriever", "sql_executor")
        workflow.add_edge("sql_executor", "validator")
        workflow.add_edge("validator", "synthesizer")
        workflow.add_edge("synthesizer", END)

        return workflow.compile()

    def execute(self, question: str, user_role: str = "FinanceExecutive") -> Dict[str, Any]:
        start = time.perf_counter()
        initial_state: DecisionIntelligenceState = {
            "question": question,
            "user_role": user_role,
            "requires_sql": True,
            "requires_docs": True,
            "planning_reasoning": "",
            "retrieved_documents": [],
            "generated_sql": "",
            "sql_results": [],
            "sql_guard_status": "",
            "is_evidence_grounded": False,
            "validation_feedback": "",
            "final_answer": "",
            "citations": [],
            "has_sufficient_evidence": False,
            "workflow_logs": [],
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_seconds": 0.0
        }

        final_state = self.graph.invoke(initial_state)
        final_state["total_latency_seconds"] = round(time.perf_counter() - start, 3)
        return final_state
