"""FastAPI Router exposing all 7 AI capabilities."""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    ConciergeRequest,
    ConciergeResponse,
    VisualSearchRequest,
    VisualSearchResponse,
    SmartCartRequest,
    SmartCartResponse,
    MenuCopilotRequest,
    MenuCopilotResponse,
    ReviewSentimentRequest,
    ReviewSentimentResponse,
    EventDiningRequest,
    EventDiningResponse,
    EtaPredictRequest,
    EtaPredictResponse
)
from app.services import (
    run_concierge_ai,
    run_visual_search_ai,
    run_smart_cart_ai,
    run_menu_copilot_ai,
    run_sentiment_ai,
    run_itinerary_ai,
    run_eta_predictor_ai
)
from app.data.catalog import CATALOG_ITEMS
from app.services.gemini_client import is_gemini_active

router = APIRouter(prefix="/api/ai", tags=["Food AI Suite"])

@router.get("/health", summary="Health check & AI Engine status")
def health_check() -> Dict[str, Any]:
    """Check AI service health and active intelligence mode."""
    return {
        "status": "healthy",
        "gemini_active": is_gemini_active(),
        "mode": "Google Gemini LLM/Vision" if is_gemini_active() else "High-Precision Heuristic & Semantic Intelligence",
        "catalog_size": len(CATALOG_ITEMS),
        "version": "1.0.0"
    }

@router.get("/catalog", summary="Get food catalog items for reference")
def get_catalog() -> List[Dict[str, Any]]:
    """Returns the platform's reference food catalog with macro & allergen tags."""
    return CATALOG_ITEMS

@router.post(
    "/concierge",
    response_model=ConciergeResponse,
    summary="1. TasteBot Conversational AI Concierge",
    description="Understands natural language cravings, budget limits, dietary restrictions, and returns scored dish recommendations."
)
def concierge_endpoint(payload: ConciergeRequest) -> ConciergeResponse:
    try:
        return run_concierge_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/visual-search",
    response_model=VisualSearchResponse,
    summary="2. 'Snap & Crave' Multi-Modal Food & Macro Recognizer",
    description="Analyzes food photos or preset identifiers to classify the dish, estimate macros (protein, carbs, fats, calories), detect allergens, and match catalog items."
)
def visual_search_endpoint(payload: VisualSearchRequest) -> VisualSearchResponse:
    try:
        return run_visual_search_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/smart-cart",
    response_model=SmartCartResponse,
    summary="3. Smart Cart Dynamic Pairing & Dietary Safety Guard",
    description="Real-time contextual pairing upsells, comprehensive macro nutrient breakdown, and allergen conflict alerts."
)
def smart_cart_endpoint(payload: SmartCartRequest) -> SmartCartResponse:
    try:
        return run_smart_cart_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/menu-copilot",
    response_model=MenuCopilotResponse,
    summary="4. Merchant AI Studio & Menu Description Copilot",
    description="Generates mouth-watering dish descriptions, culinary SEO tags, allergen classifications, and dynamic pricing benchmark recommendations."
)
def menu_copilot_endpoint(payload: MenuCopilotRequest) -> MenuCopilotResponse:
    try:
        return run_menu_copilot_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/review-sentiment",
    response_model=ReviewSentimentResponse,
    summary="5. Customer Review Sentiment & Auto-Reply Drafter",
    description="Aspect-based sentiment analysis across Taste, Delivery, Packaging, and Value, highlighting praise/pain-points and generating tailored response drafts."
)
def review_sentiment_endpoint(payload: ReviewSentimentRequest) -> ReviewSentimentResponse:
    try:
        return run_sentiment_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/event-dining-bundler",
    response_model=EventDiningResponse,
    summary="6. Night-Out Live Event & Dining Bundler",
    description="Bundles live event tickets with optimal restaurant reservations, constructing a synchronized timeline and budget calculation."
)
def event_dining_endpoint(payload: EventDiningRequest) -> EventDiningResponse:
    try:
        return run_itinerary_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/predict-eta",
    response_model=EtaPredictResponse,
    summary="7. Dynamic Kitchen Prep & Logistics ETA Engine",
    description="Calculates realistic delivery arrival time by analyzing kitchen queue congestion, dish complexity, transit distance, weather condition, and traffic level."
)
def predict_eta_endpoint(payload: EtaPredictRequest) -> EtaPredictResponse:
    try:
        return run_eta_predictor_ai(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
