# src/onboard/graph/n_intent.py
import logging
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from onboard.state import GraphState
from onboard.prompts.intent import INTENT_PROMPT
from onboard.tracing import observe
from langchain_core.prompts import ChatPromptTemplate
from langchain.messages import HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)

class IntentClassification(BaseModel):
    """Structured output for intent classification."""
    intent: Literal[
        "doc_only",
        "equipment_only",
        "meeting_only",
        "doc_equipment",
        "doc_meeting",
        "equipment_meeting",
        "all_three"
    ] = Field(description="Classified intent of the user query")

def make_intent_classification_node(llm):
    """Creates a node for intent classification."""
    
    # Configure the llm with structured output once
    structured_llm = llm.with_structured_output(IntentClassification)

    @observe()
    def create_intent_classification_node(state: GraphState) -> Dict[str, Any]:
        logger.info("Node intent_classification started")
        state_messages = state["messages"]
        system_message = SystemMessage(content=INTENT_PROMPT)
        messages = [system_message] + state_messages

        # Combine messages with the prompt (assuming prompt is a ChatPromptTemplate or list of messages)
        # If prompt is a string, we should wrap it in a HumanMessage or SystemMessage if needed
        # But usually in these setups, prompt is passed as a list of messages or a template.
        prompt = ChatPromptTemplate.from_messages(messages)        
        
        chain = prompt | structured_llm
        result = chain.invoke({"messages": messages})

        if not result or not result.intent:
            raise ValueError("Intent classification result is empty")
            
        logger.info("Node intent_classification finished, intent: %s", result.intent)
        return {"intent": result.intent}

    return create_intent_classification_node