from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Optional
from .state import AgentState
from services.places import search_restaurants, get_restaurant_details
import os

# Initialize LLM based on available keys
if os.getenv("GEMINI_API_KEY"):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=os.getenv("GEMINI_API_KEY"))
elif os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-your-openai-key-here":
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
else:
    # Fallback mock for testing if no keys at all
    llm = None

# Models for structured output
class IntentExtraction(BaseModel):
    intent: str = Field(description="Must be either 'book_table' or 'general_query'")
    restaurant_name: Optional[str] = Field(description="Name of the restaurant if mentioned")
    date: Optional[str] = Field(description="Date for the reservation if mentioned")
    time: Optional[str] = Field(description="Time for the reservation if mentioned")
    guest_count: Optional[int] = Field(description="Number of guests if mentioned")
    general_response: Optional[str] = Field(description="If intent is general_query, provide a helpful response here.")

def detect_intent(state: AgentState):
    """
    Analyzes user input to detect intent and extract any immediately available reservation details.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI restaurant reservation assistant. Determine if the user wants to book a table or has a general question. Extract details if they want to book. If general, answer it."),
        ("user", "{user_input}")
    ])
    
    if llm is None:
        # Mock mode if no keys are provided
        return {
            "intent": "book_table",
            "restaurant_name": "Mocked Barbeque Nation",
            "date": "2026-08-01",
            "time": "19:00",
            "guest_count": 2,
            "general_response": "[MOCK MODE] Sure! I'll call Barbeque Nation for 2 people on August 1st at 7:00 PM."
        }
        
    chain = prompt | llm.with_structured_output(IntentExtraction)
    result = chain.invoke({"user_input": state["user_input"]})
    
    return {
        "intent": result.intent,
        "restaurant_name": result.restaurant_name,
        "date": result.date,
        "time": result.time,
        "guest_count": result.guest_count,
        "general_response": result.general_response
    }

def find_restaurant(state: AgentState):
    """
    Searches for the restaurant using the mocked Places API if a name is provided.
    """
    if not state.get("restaurant_name"):
        return {"errors": state.get("errors", []) + ["Restaurant name is required to search."]}
        
    results = search_restaurants(state["restaurant_name"])
    if results:
        # Just pick the first match for now
        best_match = results[0]
        return {
            "place_id": best_match["place_id"],
            "restaurant_details": best_match
        }
    return {"errors": state.get("errors", []) + [f"Could not find a restaurant named {state['restaurant_name']}"]}

def validate_reservation_data(state: AgentState):
    """
    Checks if we have all required fields (date, time, guests, place_id) to initiate a call.
    """
    errors = state.get("errors", [])
    
    if not state.get("date"):
        errors.append("Missing date.")
    if not state.get("time"):
        errors.append("Missing time.")
    if not state.get("guest_count"):
        errors.append("Missing guest count.")
    if not state.get("place_id"):
        errors.append("Missing restaurant selection.")
        
    is_ready = len(errors) == 0
    return {"errors": errors, "is_ready_to_call": is_ready}
