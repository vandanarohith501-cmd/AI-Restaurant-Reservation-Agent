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

import re

def detect_intent(state: AgentState):
    """
    Analyzes user input to detect intent and extract any immediately available reservation details.
    """
    user_text = state["user_input"]
    user_lower = user_text.lower()
    
    # 1. If LLM is available, use structured output
    if llm is not None:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an AI restaurant reservation assistant. Determine if the user wants to book a table or has a general question. Extract details (restaurant_name, date, time, guest_count) ONLY if explicitly provided. Do NOT assume or make up values. If general, answer it."),
                ("user", "{user_input}")
            ])
            chain = prompt | llm.with_structured_output(IntentExtraction)
            result = chain.invoke({"user_input": user_text})
            return {
                "intent": result.intent,
                "restaurant_name": result.restaurant_name or state.get("restaurant_name"),
                "date": result.date or state.get("date"),
                "time": result.time or state.get("time"),
                "guest_count": result.guest_count or state.get("guest_count"),
                "general_response": result.general_response
            }
        except Exception as e:
            print("LLM intent extraction failed, falling back to rule-based parser:", e)
            
    # 2. Preserve existing state from previous turns
    extracted_restaurant = state.get("restaurant_name")
    extracted_date = state.get("date")
    extracted_time = state.get("time")
    extracted_guest_count = state.get("guest_count")

    # Match all restaurants from PDF dataset
    if "ocean" in user_lower or "diner" in user_lower:
        extracted_restaurant = "Ocean View Diner"
    elif "cedar" in user_lower or "spice" in user_lower:
        extracted_restaurant = "Cedar & Spice"
    elif "green" in user_lower or "fork" in user_lower:
        extracted_restaurant = "Green Fork Kitchen"
    elif "lantern" in user_lower:
        extracted_restaurant = "Little Lantern Café"
    elif "sakura" in user_lower or "bento" in user_lower or "sushi" in user_lower:
        extracted_restaurant = "Sakura Bento House"
    elif "brick" in user_lower or "oven" in user_lower:
        extracted_restaurant = "Brick Oven Social"
    elif "pepper" in user_lower or "breakfast club" in user_lower:
        extracted_restaurant = "Pepper Tree Breakfast Club"
    elif "copper" in user_lower or "kettle" in user_lower:
        extracted_restaurant = "The Copper Kettle"
    elif "barbeque" in user_lower or "bbq" in user_lower:
        extracted_restaurant = "Barbeque Nation"
    elif "paradise" in user_lower or "biryani" in user_lower:
        extracted_restaurant = "Paradise Biryani"

    is_question = any(q_word in user_lower for q_word in ["?", "what", "how", "does", "is", "are", "do", "can", "when", "tell me", "policy", "menu", "hours", "timing", "dress code", "vegan", "vegetarian"])
    is_booking = any(b_word in user_lower for b_word in ["book", "boook", "reserve", "reservation", "booking", "table for", "seat"])

    # If user is asking a question (even if naming a restaurant), route to RAG
    if is_question and not is_booking:
        return {
            "intent": "general_query",
            "restaurant_name": extracted_restaurant,
            "date": None,
            "time": None,
            "guest_count": None,
            "general_response": None
        }

    # Match guest count (e.g. "for 2", "for 2 at 4pm", "2 people", "table for 2", "2 guests", "party of 2")
    guest_match = re.search(r'(?:for|table\s+for|party\s+of)\s+(\d+)\b', user_lower)
    if not guest_match:
        guest_match = re.search(r'(\d+)\s*(?:people|persons?|guests?|seats?|pax)', user_lower)
    if guest_match:
        extracted_guest_count = int(guest_match.group(1))

    # Match time (e.g. "4pm", "4 pm", "at 4", "16:00", "7:30 pm")
    time_match = re.search(r'\b(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b', user_lower)
    if not time_match:
        time_match = re.search(r'\b([01]?\d|2[0-3]):([0-5]\d)\b', user_text)
    if time_match:
        extracted_time = time_match.group(0).replace("at ", "").strip()

    # Match date with typo tolerance (e.g. "tommorow", "tomorrow", "tmrw", "today", "tonight", days of week, or YYYY-MM-DD)
    date_match = re.search(r'\b(today|tonight|tomorrow|tommorow|tommorrow|tmrw|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', user_lower)
    if not date_match:
        date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', user_text)
    if date_match:
        found_date = date_match.group(0)
        if found_date in ["tommorow", "tommorrow", "tmrw"]:
            found_date = "tomorrow"
        extracted_date = found_date

    return {
        "intent": "book_table",
        "restaurant_name": extracted_restaurant,
        "date": extracted_date,
        "time": extracted_time,
        "guest_count": extracted_guest_count,
        "general_response": None
    }

def find_restaurant(state: AgentState):
    """
    Searches for the restaurant using the Places catalog if a name is provided.
    """
    if not state.get("restaurant_name"):
        return {"errors": state.get("errors", []) + ["Please let me know which restaurant you'd like to book."]}
        
    results = search_restaurants(state["restaurant_name"])
    if results:
        best_match = results[0]
        return {
            "place_id": best_match["place_id"],
            "restaurant_details": best_match
        }
    return {"errors": state.get("errors", []) + [f"Could not find a restaurant named '{state['restaurant_name']}'."]}

def validate_reservation_data(state: AgentState):
    """
    Checks which fields are missing and returns polite prompt asking for only the missing details.
    """
    errors = state.get("errors", [])
    missing = []
    
    if not state.get("place_id") and not state.get("restaurant_name"):
        missing.append("which restaurant you want")
    if not state.get("date"):
        missing.append("the date")
    if not state.get("time"):
        missing.append("the time")
    if not state.get("guest_count"):
        missing.append("how many guests")
        
    is_ready = len(missing) == 0 and len(errors) == 0
    if not is_ready and not errors:
        rest_name = state.get("restaurant_name")
        rest_mention = f" at {rest_name}" if rest_name else ""
        errors.append(f"I can help you book a table{rest_mention}! Could you please tell me {', '.join(missing)}?")
        
    return {"errors": errors, "is_ready_to_call": is_ready}


def answer_general_query(state: AgentState):
    """
    Uses RAG to answer general queries cleanly based on the restaurant knowledge base.
    """
    from services.rag import search_knowledge_base
    
    query = state["user_input"]
    matching_docs = search_knowledge_base(query)
    
    if llm is not None:
        try:
            context = "\n".join([f"- {doc.page_content}" for doc in matching_docs])
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an AI restaurant assistant. Use the following context to answer the user's question directly, politely, and concisely. Never include raw prompts, headers or system labels.\n\nContext:\n{context}"),
                ("user", "{user_input}")
            ])
            chain = prompt | llm
            result = chain.invoke({"user_input": query, "context": context})
            return {"general_response": result.content.strip()}
        except Exception as e:
            print("LLM generation failed, falling back to clean context answer:", e)
            
    query_lower = query.lower()
    
    # Extract precise bullet point or sentence answering the user's specific question
    for doc in matching_docs:
        text = doc.page_content
        items = re.split(r'[•\.\n]', text)
        for item in items:
            item_clean = item.strip()
            item_lower = item_clean.lower()
            if not item_clean or len(item_clean) < 10:
                continue
                
            # Dress code inquiries
            if "dress code" in query_lower or "wear" in query_lower:
                if "dress code" in item_lower or "beachwear" in item_lower:
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}
                    
            # Cancellation inquiries
            if "cancel" in query_lower or "cancellation" in query_lower:
                if "cancel" in item_lower:
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}
                    
            # Hours, Days & Open/Close inquiries
            if any(w in query_lower for w in ["open", "close", "hours", "timing", "monday", "tuesday", "sunday"]):
                if any(w in item_lower for w in ["open", "closed", "hours", "closing", "daily"]):
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}
                    
            # Vegan / Vegetarian inquiries
            if "vegan" in query_lower:
                if "vegan" in item_lower:
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}
            elif "vegetarian" in query_lower or "veg" in query_lower:
                if "vegetarian" in item_lower:
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}
                    
            # Gluten / Allergen inquiries
            if "gluten" in query_lower or "allergen" in query_lower:
                if "gluten" in item_lower or "allergen" in item_lower or "shared kitchen" in item_lower:
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}
                    
            # Group / Party size booking questions (e.g. table for 8, table for 10)
            if any(w in query_lower for w in ["table for", "booking for", "group", "party"]):
                if any(w in item_lower for w in ["table for", "booking for", "reservations", "walk-in", "limit"]):
                    return {"general_response": item_clean + ("." if not item_clean.endswith(".") else "")}

    # Fallback to the most relevant document's concise summary
    return {"general_response": matching_docs[0].page_content}


