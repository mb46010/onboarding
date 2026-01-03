import logging
from typing import TypedDict, List, Dict, Any
from onboard.state import GraphState
from onboard.tracing import observe

logger = logging.getLogger(__name__)

# ============================================
# Mock RAG Tool
# ============================================

@observe()
async def rag_retrieval(query: str) -> List[Dict[str, Any]]:
    """
    Mock RAG document retrieval.
    
    Returns:
        list: list of retrieved document snippets.
    """
    # In production: await rag_client.search(query)
    return [
        {
            "source": "equipment_policy.pdf",
            "content": "Employees are eligible for a laptop, one monitor, and a headset after their first week."
        },
        {
            "source": "first_week_schedule.pdf",
            "content": "Onboarding starts at 9:00 AM on Monday with a welcome session."
        },
        {
            "source": "offer_letter_template.pdf",
            "content": "Your start date is confirmed as per the signed letter."
        }
    ]


# ============================================
# LangGraph Node
# ============================================

class RAGUpdate(TypedDict):
    """State update from RAG retrieval."""
    retrieval_results: List[Dict[str, Any]]


@observe()
async def rag_node(state: GraphState) -> RAGUpdate:
    """
    Retrieve relevant documents based on the last user message.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"retrieval_results": []}
    
    # Get the text of the last message
    # Handle both Message objects and strings
    last_msg = messages[-1]
    if hasattr(last_msg, "content"):
        query = last_msg.content
    elif isinstance(last_msg, dict) and "content" in last_msg:
        query = last_msg["content"]
    else:
        query = str(last_msg)
    
    try:
        results = await rag_retrieval(query)
        return {"retrieval_results": results}
    
    except Exception as e:
        logger.error(f"Error in RAG retrieval: {e}")
        return {"retrieval_results": []}