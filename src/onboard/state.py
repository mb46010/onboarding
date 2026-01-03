from typing_extensions import TypedDict
from typing import Optional, Dict, Any

from langgraph.graph.message import add_messages
from typing import Annotated

class GraphState(TypedDict):
    # Input
    messages: Annotated[list, add_messages]
    employee_email: str
    manager_email: Optional[str]
    duration_mins: Optional[int]
    
    # Workflow control
    intent: Optional[str]
    
    # Data from tools
    retrieval_results: Optional[list[Dict[str, Any]]]  # More specific than "retrieval"
    equipment_status: Optional[Dict[str, Any]]
    meeting_info: Optional[Dict[str, Any]]
    
    # Output
    final_response: Optional[str]
    error: Optional[str]