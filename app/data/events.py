"""Live events catalog for night-out and dining itinerary bundling."""
from typing import List, Dict, Any, Optional

LIVE_EVENTS: List[Dict[str, Any]] = [
    {
        "id": "event_1",
        "title": "Acoustic Sunset Sessions: Indie Live Gig",
        "genre": "Live Music",
        "venue": "Amphitheatre Cultural Grounds",
        "date": "2026-09-18",
        "start_time": "20:00",
        "end_time": "22:15",
        "ticket_price": 499,
        "vibe": "Romantic",
        "recommended_dining_distance_km": 2.0
    },
    {
        "id": "event_2",
        "title": "The Big Laugh Comedy Club Special",
        "genre": "Stand-up Comedy",
        "venue": "Downtown Comedy Vault",
        "date": "2026-09-19",
        "start_time": "19:30",
        "end_time": "21:00",
        "ticket_price": 599,
        "vibe": "Casual",
        "recommended_dining_distance_km": 1.5
    },
    {
        "id": "event_3",
        "title": "Neon Symphony: Electronic Melodic Night",
        "genre": "DJ / Electronic",
        "venue": "Midtown Warehouse 54",
        "date": "2026-09-20",
        "start_time": "21:30",
        "end_time": "01:30",
        "ticket_price": 799,
        "vibe": "Party",
        "recommended_dining_distance_km": 1.8
    }
]

def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    for e in LIVE_EVENTS:
        if e["id"] == event_id:
            return e
    return None
