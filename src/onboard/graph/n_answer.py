# src/onboard/graph/n_intent.py
import logging
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from onboard.state import GraphState
from onboard.prompts.answer import ANSWER_PROMPT
from onboard.tracing import observe
from langchain_core.prompts import ChatPromptTemplate
from langchain.messages import HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)
class FinalAnswer(BaseModel):
    """Structured output for intent classification."""
    final_answer: str = Field(description="Final answer to the user query")

def make_final_answer_node(llm):
    """Creates a node for final answer synthesis."""
    
    # Configure the llm with structured output once
    structured_llm = llm.with_structured_output(FinalAnswer)

    @observe()
    def create_final_answer_node(state: GraphState) -> Dict[str, Any]:
        state_messages = state["messages"]
        system_message = SystemMessage(content=ANSWER_PROMPT)
        messages = [system_message] + state_messages

        intent = state.get("intent")
        meeting_info = state.get("meeting_info", None)
        equipment_status = state.get("equipment_status", None)
        retrieval_results = state.get("retrieval_results", None)

        # Combine messages with the prompt
        # Use simple string formatting or prompt templates correctly
        # Note: ANSWER_PROMPT.bind is for tool binding usually, not simple string templates.
        # Assuming ANSWER_PROMPT might be a template string or ChatPromptTemplate.
        # If it's a string, we might need to format it.
        # For now, let's ensure variables are defined.
        
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | structured_llm
        result = chain.invoke({"messages": messages})

        if not result or not result.final_answer:
            raise ValueError("Final answer result is empty")

        return {"final_response": result.final_answer}

    return create_final_answer_node