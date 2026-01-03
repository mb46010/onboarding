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
        system_message = SystemMessage(content=AN)
        messages = [system_message] + state_messages

        meeting_info = state.get("meeting_info", None)
        equipment_status = state.get("equipment_status", None)
        retrieval_results = state.get("retrieval_results", None)


        # Combine messages with the prompt (assuming prompt is a ChatPromptTemplate or list of messages)
        # If prompt is a string, we should wrap it in a HumanMessage or SystemMessage if needed
        # But usually in these setups, prompt is passed as a list of messages or a template.
        filled_prompt = ANSWER_PROMPT.bind(
            intent=intent,
            retrieval_results=retrieval_results,
            equipment_status=equipment_status,
            meeting_info=meeting_info
        )
        
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | structured_llm
        result = chain.invoke({"messages": messages})

        if not result or not result.final_answer:
            raise ValueError("Final answer result is empty")

        return {"final_answer": result.final_answer}

    return create_final_answer_node