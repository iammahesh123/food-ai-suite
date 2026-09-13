"""Restaurant registry for dining reservations and event pairings."""
from typing import List, Dict, Any, Optional

RESTAURANTS: List[Dict[str, Any]] = [
    {
        "id": "rest_1",
        "name": "The Spice Pavilion & Courtyard",
        "cuisine": "North Indian & Awadhi",
        "rating": 4.8,
        "price_tier": "₹₹₹",
        "avg_cost_for_two": 1400,
        "location": "Downtown Heritage District",
        "distance_km": 1.8,
        "vibe": "Romantic",
        "has_outdoor_seating": True,
        "live_music": True,
        "available_slots": ["18:30", "19:00", "19:30", "20:00", "21:00", "21:30"]
    },
    {
        "id": "rest_2",
        "name": "Trattoria Della Nonna",
        "cuisine": "Italian & Artisanal Pizza",
        "rating": 4.9,
        "price_tier": "₹₹₹",
        "avg_cost_for_two": 1600,
        "location": "Cultural Center Promenade",
        "distance_km": 0.6,
        "vibe": "FineDining",
        "has_outdoor_seating": True,
        "live_music": False,
        "available_slots": ["18:00", "19:00", "19:45", "21:15", "22:00"]
    },
    {
        "id": "rest_3",
        "name": "Neon Bonsai Asian Speakeasy",
        "cuisine": "Pan-Asian & Cocktails",
        "rating": 4.7,
        "price_tier": "₹₹",
        "avg_cost_for_two": 1100,
        "location": "Midtown Arts Lane",
        "distance_km": 1.2,
        "vibe": "Party",
        "has_outdoor_seating": False,
        "live_music": True,
        "available_slots": ["19:00", "20:00", "21:00", "22:30", "23:00"]
    },
    {
        "id": "rest_4",
        "name": "Green Garden Botanist Cafe",
        "cuisine": "Healthy & Organic Bowls",
        "rating": 4.6,
        "price_tier": "₹₹",
        "avg_cost_for_two": 850,
        "location": "Parkview Boulevard",
        "distance_km": 2.4,
        "vibe": "Casual",
        "has_outdoor_seating": True,
        "live_music": False,
        "available_slots": ["17:30", "18:30", "19:30", "20:30"]
    }
]

def get_restaurant_by_id(restaurant_id: str) -> Optional[Dict[str, Any]]:
    for r in RESTAURANTS:
        if r["id"] == restaurant_id:
            return r
    return None
