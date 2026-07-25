from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import detect_intent, find_restaurant, validate_reservation_data

def should_search(state: AgentState):
    """Routing logic based on intent"""
    if state.get("intent") == "general_query":
        return END
    
    if state.get("restaurant_name") and not state.get("place_id"):
        return "find_restaurant"
        
    return "validate_reservation_data"

def should_call(state: AgentState):
    """Routing logic after validation"""
    if state.get("is_ready_to_call"):
        # In the future, this will trigger the real phone call node
        return END
    return END # If not ready, we end for now (in full app, we ask user for missing info)

# Initialize Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("find_restaurant", find_restaurant)
workflow.add_node("validate_reservation_data", validate_reservation_data)

# Add Edges
workflow.set_entry_point("detect_intent")
workflow.add_conditional_edges("detect_intent", should_search)
workflow.add_edge("find_restaurant", "validate_reservation_data")
workflow.add_conditional_edges("validate_reservation_data", should_call)

# Compile
app = workflow.compile()
