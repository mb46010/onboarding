from onboard.state import GraphState
from onboard.graph.n_intent import make_intent_classification_node
from onboard.graph.n_router import make_router_node
from onboard.graph.n_answer import make_final_answer_node
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


# graph.py - CORRECT VERSION
def make_graph(llm, max_attempts: int=3):
    graph_builder = StateGraph(GraphState)
    retry_policy = RetryPolicy(max_attempts=max_attempts)

    # Add ALL nodes
    graph_builder.add_node("intent", make_intent_node(llm), retry=retry_policy)
    graph_builder.add_node("retrieve_docs", rag_node, retry=retry_policy)
    graph_builder.add_node("check_equipment", check_equipment_node, retry=retry_policy)
    graph_builder.add_node("schedule_meeting", schedule_meeting_node, retry=retry_policy)
    graph_builder.add_node("answer", make_final_answer_node(llm), retry=retry_policy)
    
    # Entry point
    graph_builder.add_edge(START, "intent")
    
    # CONDITIONAL ROUTING
    graph_builder.add_conditional_edges(
        "intent",
        route_based_on_intent,  # Returns list of tool nodes
        {
            "retrieve_docs": "retrieve_docs",
            "check_equipment": "check_equipment",
            "schedule_meeting": "schedule_meeting",
        }
    )
    
    # All tools → answer
    graph_builder.add_edge("retrieve_docs", "answer")
    graph_builder.add_edge("check_equipment", "answer")
    graph_builder.add_edge("schedule_meeting", "answer")
    
    graph_builder.add_edge("answer", END)
    
    return graph_builder.compile()


# Router is now a ROUTING FUNCTION, not a node
def route_based_on_intent(state: GraphState) -> list[str]:
    """Returns list of nodes to execute - LangGraph handles parallelism."""
    intent = state["intent"]
    
    routing = {
        "doc_only": ["retrieve_docs"],
        "equipment_only": ["check_equipment"],
        "meeting_only": ["schedule_meeting"],
        "doc_equipment": ["retrieve_docs", "check_equipment"],
        "all_three": ["retrieve_docs", "check_equipment", "schedule_meeting"],
    }
    
    return routing.get(intent, [])
