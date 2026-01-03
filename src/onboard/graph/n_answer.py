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
        state_messages = state.get("messages", [])
        intent = state.get("intent")
        meeting_info = state.get("meeting_info", None)
        equipment_status = state.get("equipment_status", None)
        retrieval_results = state.get("retrieval_results", None)

        context_parts = []
        
        if state.get("retrieval_results"):
            docs = "\n".join([r["content"] for r in state["retrieval_results"]])
            context_parts.append(f"Documents:\n{docs}")
        
        if state.get("equipment_status"):
            eq = state["equipment_status"]
            if "error" not in eq.get("status", "").lower():
                context_parts.append(f"Equipment: {eq}")
        
        if state.get("meeting_info"):
            context_parts.append(f"Meeting: {state['meeting_info']}")
        
        context = "\n\n".join(context_parts)


        # Format the system message with all available context
        filled_prompt = ANSWER_PROMPT.format(
            intent=intent,
            context=context,
        )
        
        messages = [
            SystemMessage(content=filled_prompt),
            *state["messages"]
        ]
        
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | structured_llm
        result = chain.invoke({"messages": messages})

        if not result or not result.final_answer:
            raise ValueError("Final answer result is empty")

        return {"final_response": result.final_answer}

    return create_final_answer_node