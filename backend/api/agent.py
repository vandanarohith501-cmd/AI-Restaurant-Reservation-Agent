from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent.workflow import app as agent_app

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    intent: str
    general_response: str = None
    restaurant_name: str = None
    date: str = None
    time: str = None
    guest_count: int = None
    is_ready_to_call: bool = False
    errors: list = []
    restaurant_details: dict = None

import os

@router.post("/chat", response_model=ChatResponse)
def process_chat(request: ChatRequest):
    """
    Process user chat input, detect intent, and progress the reservation workflow.
    """

    initial_state = {
        "user_input": request.user_input,
        "errors": []
    }
    
    try:
        # Run the LangGraph workflow
        final_state = agent_app.invoke(initial_state)
        
        return ChatResponse(
            intent=final_state.get("intent", "unknown"),
            general_response=final_state.get("general_response"),
            restaurant_name=final_state.get("restaurant_name"),
            date=final_state.get("date"),
            time=final_state.get("time"),
            guest_count=final_state.get("guest_count"),
            is_ready_to_call=final_state.get("is_ready_to_call", False),
            errors=final_state.get("errors", []),
            restaurant_details=final_state.get("restaurant_details")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
