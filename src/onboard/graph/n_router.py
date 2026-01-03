# src/onboard/graph/n_router.py
import logging
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from onboard.state import GraphState
from onboard.prompts.intent import INTENT_PROMPT
from onboard.tracing import observe
from onboard.tools.mock_meeting import schedule_meeting_node
from onboard.tools.mock_equipment import check_equipment_node
from onboard.tools.mock_rag import rag_retrieval

logger = logging.getLogger(__name__)
def make_router_node(llm):
    """Creates a node for intent classification."""
    
    @observe()
    async def create_router_node(state: GraphState) -> Dict[str, Any]:
        logger.info("Router node started")
        messages = state["messages"]
        intent = state["intent"]

        parallel_tools = []
        if intent=="doc_only":
            parallel_tools = [rag_retrieval] 
        elif intent=="equipment_only":
            parallel_tools = [check_equipment_node]
        elif intent=="meeting_only":
            parallel_tools = [schedule_meeting_node]
        elif intent=="doc + equipment":
            parallel_tools = [check_equipment_node]
        elif intent=="all_three":
            parallel_tools = [check_equipment_node, schedule_meeting_node]
        else:
            raise ValueError(f"Unknown intent: {intent}")

        logger.info("Router node finished, returning parallel tools")
        return parallel_tools

    return create_router_node