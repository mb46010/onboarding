from onboard.state import GraphState
from onboard.graph.n_intent import make_intent_classification_node
from onboard.graph.n_router import make_router_node
from onboard.graph.n_answer import make_final_answer_node
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


def make_graph(llm, max_attempts: int=3):
    graph_builder = StateGraph(GraphState)
    
    # Define a common retry policy for nodes
    retry_policy = RetryPolicy(max_attempts=max_attempts)

    graph_builder.add_node(
        "intent_classification", 
        make_intent_classification_node(llm),
        retry=retry_policy
    )
    graph_builder.add_node(
        "router", 
        make_router_node(llm),
        retry=retry_policy
    )
    graph_builder.add_node(
        "final_answer", 
        make_final_answer_node(llm),
        retry=retry_policy
    )
    
    graph_builder.add_edge(START, "intent_classification")
    graph_builder.add_edge("intent_classification", "router")
    graph_builder.add_edge("router", "final_answer")
    graph_builder.add_edge("final_answer", END)
    
    return graph_builder.compile()

