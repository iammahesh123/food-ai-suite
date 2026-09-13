"""Live Event & Dining Night-Out Bundler Service."""
from typing import List, Dict, Any
from app.models.schemas import (
    EventDiningRequest,
    EventDiningResponse,
    DiningBookingSlot,
    TimelineStep
)
from app.data.events import get_event_by_id, LIVE_EVENTS
from app.data.restaurants import RESTAURANTS, get_restaurant_by_id

def run_itinerary_ai(request: EventDiningRequest) -> EventDiningResponse:
    event = get_event_by_id(request.event_id)
    if not event:
        event = LIVE_EVENTS[0]

    party_size = max(1, request.party_size)
    preferred_vibe = request.dining_vibe or "Romantic"
    timing_pref = request.timing_preference or "PRE_EVENT"

    # Find the optimal restaurant by vibe, distance, and rating
    candidate_restaurants = sorted(
        RESTAURANTS,
        key=lambda r: (
            1.0 if r["vibe"].lower() == preferred_vibe.lower() else 0.0,
            -r["distance_km"],
            r["rating"]
        ),
        reverse=True
    )
    chosen_rest = candidate_restaurants[0]

    # Calculate optimal dining slot based on event start/end
    event_start = event["start_time"]  # e.g. "20:00"
    event_end = event["end_time"]      # e.g. "22:15"

    start_hour, start_min = map(int, event_start.split(":"))
    end_hour, end_min = map(int, event_end.split(":"))

    if timing_pref == "PRE_EVENT":
        # Table 75-90 minutes prior to event
        pre_hour = (start_hour - 1) if start_min >= 30 else (start_hour - 2)
        pre_min = 30 if start_min < 30 else 0
        dinner_time = f"{pre_hour:02d}:{pre_min:02d}"
    else:
        # Table 30 minutes after event
        post_hour = end_hour
        post_min = (end_min + 30) % 60
        if end_min + 30 >= 60:
            post_hour = (post_hour + 1) % 24
        dinner_time = f"{post_hour:02d}:{post_min:02d}"

    cost_per_head = chosen_rest["avg_cost_for_two"] / 2.0
    total_dining_cost = cost_per_head * party_size
    total_tickets_cost = event["ticket_price"] * party_size
    total_budget = total_dining_cost + total_tickets_cost

    dining_slot = DiningBookingSlot(
        restaurant_id=chosen_rest["id"],
        restaurant_name=chosen_rest["name"],
        cuisine=chosen_rest["cuisine"],
        reserved_time=dinner_time,
        distance_to_venue_km=float(chosen_rest["distance_km"]),
        avg_cost_for_party=float(round(total_dining_cost, 0))
    )

    # Build optimized chronological timeline
    timeline: List[TimelineStep] = []
    if timing_pref == "PRE_EVENT":
        timeline.append(
            TimelineStep(
                time=dinner_time,
                title=f"Reserved Table: {chosen_rest['name']}",
                description=f"Seated dining for party of {party_size} with {chosen_rest['cuisine']} cuisine and {chosen_rest['vibe']} atmosphere.",
                category="DINING"
            )
        )
        timeline.append(
            TimelineStep(
                time=f"{start_hour - 1:02d}:45" if start_min == 0 else f"{start_hour:02d}:{start_min - 15:02d}",
                title=f"Short Transit to {event['venue']}",
                description=f"Quick {int(chosen_rest['distance_km'] * 6)} min cab or leisurely walk to avoid parking queue.",
                category="TRANSIT"
            )
        )
        timeline.append(
            TimelineStep(
                time=event_start,
                title=f"Main Event: {event['title']}",
                description=f"Doors open for {event['genre']} live performance at {event['venue']}.",
                category="EVENT"
            )
        )
    else:
        timeline.append(
            TimelineStep(
                time=event_start,
                title=f"Main Event: {event['title']}",
                description=f"Arrive at {event['venue']} for {event['genre']}.",
                category="EVENT"
            )
        )
        timeline.append(
            TimelineStep(
                time=dinner_time,
                title=f"Post-Show Dinner: {chosen_rest['name']}",
                description=f"Relaxing wind-down meal with {chosen_rest['cuisine']} and curated late-night cocktails.",
                category="DINING"
            )
        )

    curator_note = (
        f"AI Concierge synced your schedule for a seamless evening. "
        f"{chosen_rest['name']} is only {chosen_rest['distance_km']} km from {event['venue']}, "
        f"ensuring zero rush before {event['title']} begins."
    )

    return EventDiningResponse(
        event_title=event["title"],
        event_venue=event["venue"],
        dining_recommendation=dining_slot,
        timeline=timeline,
        total_estimated_budget=float(round(total_budget, 0)),
        ai_curator_note=curator_note
    )
