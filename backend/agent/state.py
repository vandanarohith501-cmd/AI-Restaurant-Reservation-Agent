from typing import TypedDict, Annotated, List, Dict, Optional
import operator

class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]  # 'book_table' or 'general_query'
    general_response: Optional[str]
    restaurant_name: Optional[str]
    date: Optional[str]
    time: Optional[str]
    guest_count: Optional[int]
    place_id: Optional[str]
    restaurant_details: Optional[Dict]
    is_ready_to_call: bool
    call_sid: Optional[str]
    errors: List[str]
