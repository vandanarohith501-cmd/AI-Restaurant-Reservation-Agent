from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from agent.workflow import app as agent_app

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str
    current_state: Optional[Dict] = None

class ChatResponse(BaseModel):
    intent: str
    general_response: Optional[str] = None
    restaurant_name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    guest_count: Optional[int] = None
    is_ready_to_call: bool = False
    call_initiated: bool = False
    call_status_message: Optional[str] = None
    errors: List[str] = []
    restaurant_details: Optional[Dict] = None

import os

@router.post("/chat", response_model=ChatResponse)
def process_chat(request: ChatRequest):
    """
    Process user chat input, detect intent, and progress the reservation workflow across multiple turns.
    """

    initial_state = {
        "user_input": request.user_input,
        "errors": []
    }
    
    # Carry forward details previously gathered in earlier messages
    if request.current_state:
        for field in ["restaurant_name", "date", "time", "guest_count", "place_id", "restaurant_details"]:
            if request.current_state.get(field) is not None:
                initial_state[field] = request.current_state[field]

    try:
        # Run the LangGraph workflow
        final_state = agent_app.invoke(initial_state)
        
        is_ready = final_state.get("is_ready_to_call", False)
        call_initiated = False
        call_status_msg = None

        if is_ready:
            openai_key = os.getenv("OPENAI_API_KEY")
            # Check if voice API is active/configured
            if not openai_key or openai_key == "sk-your-openai-key-here":
                call_initiated = False
                call_status_msg = "Call cannot be initiated because the Voice Call API is not working or not configured."
            else:
                call_initiated = True
                call_status_msg = f"Initiating live voice call to {final_state.get('restaurant_name')}..."

        return ChatResponse(
            intent=final_state.get("intent", "unknown"),
            general_response=final_state.get("general_response"),
            restaurant_name=final_state.get("restaurant_name"),
            date=final_state.get("date"),
            time=final_state.get("time"),
            guest_count=final_state.get("guest_count"),
            is_ready_to_call=is_ready,
            call_initiated=call_initiated,
            call_status_message=call_status_msg,
            errors=final_state.get("errors", []),
            restaurant_details=final_state.get("restaurant_details")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

