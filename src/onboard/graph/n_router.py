# src/onboard/graph/n_router.py
import logging
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from onboard.state import GraphState
from onboard.prompts.intent import INTENT_PROMPT
from onboard.tracing import observe
import asyncio
from onboard.tools.mock_meeting import schedule_meeting_node
from onboard.tools.mock_equipment import check_equipment_node
from onboard.tools.mock_rag import rag_node

logger = logging.getLogger(__name__)

def make_router_node(llm):
    """Creates a node that executes tools based on classified intent."""
    
    @observe()
    async def create_router_node(state: GraphState) -> Dict[str, Any]:
        logger.info("Router node started")
        intent = state.get("intent")
        
        tasks = []
        
        # Map intents to the appropriate tool nodes
        if intent in ["doc_only", "doc_equipment", "doc_meeting", "all_three"]:
            tasks.append(rag_node(state))
        
        if intent in ["equipment_only", "doc_equipment", "equipment_meeting", "all_three"]:
            tasks.append(check_equipment_node(state))
            
        if intent in ["meeting_only", "doc_meeting", "equipment_meeting", "all_three"]:
            tasks.append(schedule_meeting_node(state))

        if not tasks:
            logger.warning(f"No tools to run for intent: {intent}")
            return {}

        logger.info(f"Executing {len(tasks)} tools in parallel for intent: {intent}")
        
        # Run all selected tool nodes in parallel
        results = await asyncio.gather(*tasks)
        
        # Merge all partial state updates into one dictionary
        combined_updates = {}
        for r in results:
            if r:
                combined_updates.update(r)
                
        logger.info("Router node finished tool execution")
        return combined_updates

    return create_router_node