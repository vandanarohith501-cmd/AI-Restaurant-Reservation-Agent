from typing import Optional, List, Dict
import random
import uuid

# Catalog of restaurants from knowledge base and testing
MOCK_RESTAURANTS = [
    {
        "place_id": "ocean-view-diner-chennai",
        "name": "Ocean View Diner",
        "address": "18 Marina Crescent, Chennai",
        "phone_number": "+91 44 2844 1100",
        "rating": "4.8",
        "opening_hours": "Daily, 11:00 AM - 10:30 PM",
        "cuisine": "Coastal Indian and seafood",
        "features": ["Smart Casual", "Pescatarian Options", "Seafood", "Reservations for 6+"]
    },
    {
        "place_id": "cedar-spice-chennai",
        "name": "Cedar & Spice",
        "address": "42 Garden Avenue, Chennai",
        "phone_number": "+91 44 2844 2200",
        "rating": "4.6",
        "opening_hours": "Tue-Sun, 12:00-3:30 PM and 6:30-11:00 PM (Closed Monday)",
        "cuisine": "North Indian and Mughlai",
        "features": ["Biryani", "Paneer Tikka", "Bookings 1-10", "Casual or Smart Casual"]
    },
    {
        "place_id": "green-fork-kitchen-chennai",
        "name": "Green Fork Kitchen",
        "address": "7 Lakeview Road, Chennai",
        "phone_number": "+91 44 2844 3300",
        "rating": "4.7",
        "opening_hours": "Mon-Sat 9:00 AM-9:00 PM; Sun 9:00 AM-5:00 PM",
        "cuisine": "Vegetarian and plant-forward",
        "features": ["Vegan Dishes", "Buddha Bowls", "Walk-ins Welcome", "Casual"]
    },
    {
        "place_id": "little-lantern-cafe-chennai",
        "name": "Little Lantern Café",
        "address": "11 Banyan Street, Chennai",
        "phone_number": "+91 44 2844 4400",
        "rating": "4.4",
        "opening_hours": "Daily, 8:00 AM - 9:00 PM",
        "cuisine": "Café food, sandwiches, and desserts",
        "features": ["Cold Coffee", "Sandwiches", "Walk-ins for 1-4", "Casual"]
    },
    {
        "place_id": "sakura-bento-house-chennai",
        "name": "Sakura Bento House",
        "address": "29 Orchid Lane, Chennai",
        "phone_number": "+91 44 2844 5500",
        "rating": "4.9",
        "opening_hours": "Wed-Mon, 12:00 PM - 10:00 PM (Closed Tuesday)",
        "cuisine": "Japanese-inspired bowls and sushi",
        "features": ["Teriyaki Bowl", "Sushi & Maki", "Reservations for 1-6", "Smart Casual"]
    },
    {
        "place_id": "brick-oven-social-chennai",
        "name": "Brick Oven Social",
        "address": "5 Station Square, Chennai",
        "phone_number": "+91 44 2844 6600",
        "rating": "4.5",
        "opening_hours": "Daily, 12:00 PM - 11:00 PM",
        "cuisine": "Pizza, pasta, and Italian-inspired food",
        "features": ["Wood-fired Pizza", "Pasta", "Reservations for 1-12", "Casual"]
    },
    {
        "place_id": "pepper-tree-breakfast-club-chennai",
        "name": "Pepper Tree Breakfast Club",
        "address": "63 Sunrise Road, Chennai",
        "phone_number": "+91 44 2844 7700",
        "rating": "4.6",
        "opening_hours": "Daily, 7:00 AM - 2:00 PM",
        "cuisine": "Breakfast, South Indian, and brunch",
        "features": ["Idli & Dosa", "Pongal", "Early Morning", "Casual"]
    },
    {
        "place_id": "the-copper-kettle-chennai",
        "name": "The Copper Kettle",
        "address": "14 Hilltop Boulevard, Chennai",
        "phone_number": "+91 44 2844 8800",
        "rating": "4.7",
        "opening_hours": "Mon-Sat 11:30 AM-10:00 PM; Sun 12:00 PM-9:00 PM",
        "cuisine": "Continental and comfort food",
        "features": ["Herb Grilled Chicken", "Mac & Cheese", "Smart Casual for Dinner", "Reservations 1-8"]
    },
    {
        "place_id": "barbeque-nation-chennai",
        "name": "Barbeque Nation",
        "address": "123 Food Street, Downtown",
        "phone_number": "+91 44 2844 9900",
        "rating": "4.5",
        "opening_hours": "11:00 AM - 11:00 PM",
        "cuisine": "Barbeque, Indian",
        "features": ["Unlimited Buffet", "Vegetarian Options", "Outdoor Seating"]
    },
    {
        "place_id": "paradise-biryani-chennai",
        "name": "Paradise Biryani",
        "address": "456 Spice Avenue, Midtown",
        "phone_number": "+91 44 2844 0000",
        "rating": "4.2",
        "opening_hours": "12:00 PM - 12:00 AM",
        "cuisine": "Indian, Biryani",
        "features": ["Spicy Food", "Takeaway"]
    }
]

def search_restaurants(query: str) -> List[Dict]:
    """
    Search restaurants matching the query string.
    """
    query_lower = query.lower()
    results = []
    
    for restaurant in MOCK_RESTAURANTS:
        name_lower = restaurant["name"].lower()
        if (query_lower in name_lower or 
            name_lower in query_lower or
            query_lower in restaurant["cuisine"].lower() or 
            any(query_lower in feature.lower() for feature in restaurant["features"])):
            results.append(restaurant)
            
    # Try partial word match if empty
    if not results:
        for restaurant in MOCK_RESTAURANTS:
            words = [w for w in query_lower.split() if len(w) > 3]
            for w in words:
                if w in restaurant["name"].lower() or w in restaurant["cuisine"].lower():
                    results.append(restaurant)
                    break

    if not results:
        return [MOCK_RESTAURANTS[0]]
        
    return results

def get_restaurant_details(place_id: str) -> Optional[Dict]:
    """
    Retrieve specific restaurant details by place_id.
    """
    for restaurant in MOCK_RESTAURANTS:
        if restaurant["place_id"] == place_id:
            return restaurant
    return None
