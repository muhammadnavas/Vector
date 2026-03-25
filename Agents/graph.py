"""
LangGraph Workflow Definition
Coordinates all 6 agents in a state machine pipeline
"""

from langgraph.graph import StateGraph, END
from graph_state import VectorAgentState
from nodes import (
    github_integration_agent,
    code_understanding_agent,
    test_case_generator_agent,
    test_executor_agent,
    failure_analysis_agent,
    report_generator_agent
)


def should_analyze_failures(state) -> str:
    """
    Conditional edge: If tests failed, route to failure analyzer
    Otherwise, go directly to report generator
    """
    state_obj = state if isinstance(state, VectorAgentState) else VectorAgentState(**state)
    if state_obj.tests_failed > 0:
        return "analyze_failures"
    else:
        return "generate_report"


def build_vector_graph():
    """
    Builds the LangGraph workflow for Vector pipeline

    Architecture:
        GitHub Agent
            ↓
        Code Agent
            ↓
        Test Generator
            ↓
        Test Executor
            ↓
        [Decision: Did tests fail?]
        ↙                    ↘
    YES                        NO
     ↓                          ↓
    Failure Analyzer      Report Generator
     ↓                          ↓
    Report Generator ←─────────┘
     ↓
    END
    """

    workflow = StateGraph(VectorAgentState)

    # Add nodes (agents)
    workflow.add_node("github_agent", github_integration_agent)
    workflow.add_node("code_agent", code_understanding_agent)
    workflow.add_node("test_generator", test_case_generator_agent)
    workflow.add_node("test_executor", test_executor_agent)
    workflow.add_node("analyze_failures", failure_analysis_agent)
    workflow.add_node("generate_report", report_generator_agent)

    # Add edges (sequential flow)
    workflow.add_edge("github_agent", "code_agent")
    workflow.add_edge("code_agent", "test_generator")
    workflow.add_edge("test_generator", "test_executor")

    # Conditional edge: based on test results
    workflow.add_conditional_edges(
        "test_executor",
        should_analyze_failures,
        {
            "analyze_failures": "analyze_failures",
            "generate_report": "generate_report"
        }
    )

    # Both paths converge to report generator
    workflow.add_edge("analyze_failures", "generate_report")

    # Final edge to end
    workflow.add_edge("generate_report", END)

    # Set entry point
    workflow.set_entry_point("github_agent")

    return workflow.compile()


# Create the compiled graph
vector_pipeline = build_vector_graph()

if __name__ == "__main__":
    print("✓ Vector LangGraph pipeline compiled successfully")
    print("  Graph structure created with 6 coordinated agents")
