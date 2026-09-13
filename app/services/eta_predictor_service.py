"""Predictive Kitchen Prep & Logistics Delivery ETA Service."""
from typing import List
from app.models.schemas import (
    EtaPredictRequest,
    EtaPredictResponse,
    FactorsBreakdown,
    ConfidenceInterval
)

def run_eta_predictor_ai(request: EtaPredictRequest) -> EtaPredictResponse:
    # 1. Base Kitchen Prep Time
    # Each item adds ~3 mins, complexity multiplier between 1.0 (simple) and 1.8 (complex gourmet)
    complexity_multiplier = 0.8 + (request.dish_complexity_score * 0.25)
    base_prep = (10.0 + (request.order_item_count * 2.5)) * complexity_multiplier

    # 2. Queue Surge Delay
    # Each active order ahead in queue adds ~1.2 mins
    queue_delay = request.kitchen_current_queue * 1.25

    # 3. Transit Time (Base speed ~20 km/h in city)
    base_transit_mins = (request.distance_km / 20.0) * 60.0

    # 4. Weather Impact
    weather_multiplier = 1.0
    weather_delay = 0.0
    weather_upper = request.weather_condition.upper()
    if weather_upper == "RAIN":
        weather_multiplier = 1.35
        weather_delay = 6.0
    elif weather_upper == "STORM":
        weather_multiplier = 1.65
        weather_delay = 14.0

    # 5. Traffic Impact
    traffic_multiplier = 1.0
    traffic_delay = 0.0
    traffic_upper = request.traffic_level.upper()
    if traffic_upper == "MODERATE":
        traffic_multiplier = 1.25
        traffic_delay = 3.5
    elif traffic_upper == "HEAVY":
        traffic_multiplier = 1.60
        traffic_delay = 9.0

    total_transit = (base_transit_mins * weather_multiplier * traffic_multiplier)
    total_eta = base_prep + queue_delay + total_transit
    predicted_eta_mins = int(round(total_eta))

    # Variance margin for confidence interval
    uncertainty_margin = max(4, int(predicted_eta_mins * 0.15))
    min_eta = max(12, predicted_eta_mins - uncertainty_margin)
    max_eta = predicted_eta_mins + uncertainty_margin

    warnings: List[str] = []
    if request.kitchen_current_queue >= 7:
        warnings.append(f"Kitchen high load alert: {request.kitchen_current_queue} active orders currently ahead in queue.")
    if weather_upper in ["RAIN", "STORM"]:
        warnings.append(f"Weather alert: Safe delivery speed protocol active due to {weather_upper.lower()} conditions.")
    if traffic_upper == "HEAVY":
        warnings.append("Traffic congestion on delivery corridor: Courier is navigating alternative bypass route.")

    if predicted_eta_mins <= 25:
        status_msg = "Express dispatch: Kitchen has immediate capacity and transit route is clear."
    elif predicted_eta_mins <= 40:
        status_msg = "Order on steady schedule: Kitchen is preparing fresh ingredients."
    else:
        status_msg = "Extended prep window: Kitchen queue and transit factors are active, prioritizing food freshness."

    return EtaPredictResponse(
        predicted_eta_minutes=predicted_eta_mins,
        confidence_interval=ConfidenceInterval(
            min_eta_minutes=min_eta,
            max_eta_minutes=max_eta
        ),
        factors_breakdown=FactorsBreakdown(
            base_prep_minutes=round(base_prep, 1),
            queue_surge_delay_minutes=round(queue_delay, 1),
            transit_minutes=round(total_transit, 1),
            weather_delay_minutes=round(weather_delay, 1),
            traffic_delay_minutes=round(traffic_delay, 1)
        ),
        delay_warnings=warnings,
        customer_status_message=status_msg
    )
