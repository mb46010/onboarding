from typing import TypedDict
from onboard.state import GraphState
from onboard.tracing import observe


# ============================================
# Mock MCP Tool (in real code, this would be actual MCP call)
# ============================================

@observe()
async def check_equipment_order(employee_email: str) -> dict:
    """
    Mock equipment order check.
    
    Returns:
        dict: {laptop: bool, monitor: bool, headset: bool, status: str}
    """
    # In production: await mcp_client.call_tool("check_equipment", ...)
    return {
        "laptop": True,
        "monitor": True,
        "headset": False,
        "status": "Partially ordered"
    }


# ============================================
# LangGraph Node
# ============================================

class EquipmentUpdate(TypedDict):
    """State update from equipment check."""
    equipment_status: dict


@observe()
async def check_equipment_node(state: GraphState) -> EquipmentUpdate:
    """
    Check equipment order status for employee.
    
    Calls the equipment order system to verify what has been ordered.
    """
    employee_email = state["employee_email"]
    
    try:
        order_status = await check_equipment_order(employee_email)
        return {"equipment_status": order_status}
    
    except Exception as e:
        # Graceful degradation - don't crash the whole workflow
        return {
            "equipment_status": {
                "laptop": None,
                "monitor": None,
                "headset": None,
                "status": f"Error checking equipment: {str(e)}"
            }
        }