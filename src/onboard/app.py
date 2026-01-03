import argparse
import json
import os
from datetime import datetime
from onboard.graph.graph import make_graph
from onboard.model import get_default_llm
from onboard.state import GraphState
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

def main():
    parser = argparse.ArgumentParser(description="Run the HR onboarding assistant graph.")
    parser.add_argument("--query", type=str, required=False, default="Is the laptop ready? Do we need to schedule a meeting?")
    parser.add_argument("--employee_email", type=str, required=False, default="employee@onboard.ai", help="Employee email")
    parser.add_argument("--manager_email", type=str, required=False, default="manager@onboard.ai", help="Manager email")
    parser.add_argument("--duration_mins", type=int, required=False, default=30, help="Duration in minutes")
    parser.add_argument("--max_attempts", type=int, required=False, default=3, help="Max attempts")
    args = parser.parse_args()

    llm = get_default_llm()
    graph = make_graph(llm, max_attempts=args.max_attempts)
    state = GraphState(
        messages=[("user", args.query)],
        employee_email=args.employee_email,
        manager_email=args.manager_email,
        duration_mins=args.duration_mins
    )
    from onboard.tracing import get_langfuse_callback
    langfuse_handler = get_langfuse_callback()
    config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}

    result = graph.invoke(state, config=config)
    print(result)

    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Serialize results to JSON with timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Use a custom encoder or handle non-serializable objects (like message objects)
    # LangGraph results often contain langchain message objects which need serialization
    def serialize(obj):
        if hasattr(obj, "dict"):
            return obj.dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    with open(filepath, "w") as f:
        json.dump(result, f, indent=4, default=serialize)
    
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    main()