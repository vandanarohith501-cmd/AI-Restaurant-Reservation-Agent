from typing import Optional, List, Dict
import random
import uuid

# Mocked database of restaurants
MOCK_RESTAURANTS = [
    {
        "place_id": str(uuid.uuid4()),
        "name": "Barbeque Nation",
        "address": "123 Food Street, Downtown",
        "phone_number": "+1234567890",
        "rating": "4.5",
        "opening_hours": "11:00 AM - 11:00 PM",
        "cuisine": "Barbeque, Indian",
        "features": ["Vegetarian Options", "Buffet", "Outdoor Seating"]
    },
    {
        "place_id": str(uuid.uuid4()),
        "name": "Paradise Biryani",
        "address": "456 Spice Avenue, Midtown",
        "phone_number": "+1987654321",
        "rating": "4.2",
        "opening_hours": "12:00 PM - 12:00 AM",
        "cuisine": "Indian, Biryani",
        "features": ["Spicy Food", "Takeaway"]
    },
    {
        "place_id": str(uuid.uuid4()),
        "name": "Ocean View Diner",
        "address": "789 Beach Road",
        "phone_number": "+1122334455",
        "rating": "4.8",
        "opening_hours": "08:00 AM - 10:00 PM",
        "cuisine": "American, Seafood",
        "features": ["Breakfast", "Scenic View"]
    }
]

def search_restaurants(query: str) -> List[Dict]:
    """
    Mock search function for Google Places API.
    Filters the mocked restaurants based on the query string.
    """
    query_lower = query.lower()
    results = []
    
    for restaurant in MOCK_RESTAURANTS:
        if (query_lower in restaurant["name"].lower() or 
            query_lower in restaurant["cuisine"].lower() or 
            any(query_lower in feature.lower() for feature in restaurant["features"])):
            results.append(restaurant)
            
    # If no specific match, return a random one as a fallback suggestion for testing
    if not results:
        return [random.choice(MOCK_RESTAURANTS)]
        
    return results

def get_restaurant_details(place_id: str) -> Optional[Dict]:
    """
    Mock function to get specific restaurant details.
    """
    for restaurant in MOCK_RESTAURANTS:
        if restaurant["place_id"] == place_id:
            return restaurant
    return None
