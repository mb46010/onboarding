import logging
from typing import TypedDict
from onboard.state import GraphState
from onboard.tracing import observe

logger = logging.getLogger(__name__)

# ============================================
# Mock MCP Tool (in real code, this would be actual MCP call)
# ============================================

@observe()
async def schedule_meeting(employee_email: str, manager_email: str, 
                          duration_mins: int) -> dict:
    """
    Mock schedule meeting.    
    
    Returns: {meeting_id: str, scheduled_time: str, calendar_link: str}
    """
    # In production: await mcp_client.call_tool("check_equipment", ...)
    return {
        "meeting_id": "123456",
        "scheduled_time": "2026-01-03 12:00:00",
        "calendar_link": "https://example.com/calendar/123456"
    }


# ============================================
# LangGraph Node
# ============================================

class MeetingUpdate(TypedDict):
    """State update from meeting scheduling."""
    meeting_info: dict


@observe()
async def schedule_meeting_node(state: GraphState) -> MeetingUpdate:
    """
    Schedule a meeting for the employee.
    
    Calls the meeting scheduling system to schedule a meeting.
    """
    employee_email = state["employee_email"]
    manager_email = state["manager_email"]
    duration_mins = state["duration_mins"]
    
    if not employee_email or not manager_email or not duration_mins:
        raise ValueError("Missing required fields")
    if not isinstance(duration_mins, int):
        raise ValueError("duration_mins must be an integer")
    if duration_mins < 1:
        raise ValueError("duration_mins must be greater than 0")
    if not isinstance(employee_email, str):
        raise ValueError("employee_email must be a string")
    if not isinstance(manager_email, str):
        raise ValueError("manager_email must be a string")
    if not duration_mins:
        duration_mins = 30
        logger.warning("No duration_mins provided, defaulting to 30 minutes")

    try:
        meeting_info = await schedule_meeting(employee_email, manager_email, duration_mins)
        return {"meeting_info": meeting_info}
    
    except Exception as e:
        # Graceful degradation - don't crash the whole workflow
        return {
            "meeting_info": {
                "meeting_id": None,
                "scheduled_time": None,
                "calendar_link": None,
                "status": f"Error scheduling meeting: {str(e)}"
            }
        }