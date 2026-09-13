"""AI Foodie Concierge & Craving Interpreter Service."""
from typing import List, Dict, Any, Optional
from app.models.schemas import ConciergeRequest, ConciergeResponse, RecommendedDish
from app.data.catalog import CATALOG_ITEMS
from app.services.gemini_client import query_gemini_json, is_gemini_active

def _extract_intent_and_mood(prompt: str) -> (str, str):
    p = prompt.lower()
    mood = "Balanced & Satisfying"
    intent = "DISH_RECOMMENDATION"

    if any(w in p for w in ["spicy", "fire", "tikka", "chili", "hot"]):
        mood = "Fiery & Bold"
    elif any(w in p for w in ["comfort", "warm", "rain", "cozy", "lazy"]):
        mood = "Comfort & Nostalgic"
    elif any(w in p for w in ["healthy", "diet", "clean", "protein", "keto", "salad", "bowl"]):
        mood = "Wholesome & Energetic"
    elif any(w in p for w in ["sweet", "dessert", "chocolate", "sugar"]):
        mood = "Indulgent & Sweet"
    elif any(w in p for w in ["party", "friends", "binge", "movie", "gathering"]):
        mood = "Festive & Social"

    if any(w in p for w in ["where can i eat", "table", "reserve", "dine"]):
        intent = "DINING_DISCOVERY"

    return intent, mood

def run_concierge_ai(request: ConciergeRequest) -> ConciergeResponse:
    prompt_text = request.prompt
    user_prefs = request.user_preferences

    # If Gemini is configured, attempt LLM generation first
    if is_gemini_active():
        llm_prompt = f"""
        You are 'TasteBot', an elite AI Culinary Concierge for a food platform.
        User prompt: "{prompt_text}"
        User preferences: {user_prefs.dict() if user_prefs else 'None'}
        Available dishes catalog: {CATALOG_ITEMS}

        Output JSON matching:
        {{
          "reply": "Friendly conversational response explaining the picks",
          "intent": "DISH_RECOMMENDATION",
          "mood_extracted": "Extracted mood name",
          "recommended_dishes": [
             {{
               "id": "dish_id",
               "name": "dish_name",
               "cuisine": "cuisine_name",
               "price": 280,
               "rating": 4.8,
               "calories": 420,
               "match_reason": "Specific reason why this fits the user's craving",
               "is_veg": true,
               "allergens": ["Dairy"]
             }}
          ],
          "suggested_followups": ["Followup question 1", "Followup question 2"]
        }}
        """
        gemini_result = query_gemini_json(llm_prompt, "You are an expert culinary AI concierge.")
        if gemini_result and "recommended_dishes" in gemini_result:
            try:
                return ConciergeResponse(**gemini_result)
            except Exception:
                pass

    # Built-in High Precision Semantic Engine
    intent, mood = _extract_intent_and_mood(prompt_text)
    p = prompt_text.lower()

    # Filter by budget if provided
    max_budget = user_prefs.budget if user_prefs and user_prefs.budget else None
    dietary_filter = [d.lower() for d in (user_prefs.dietary if user_prefs and user_prefs.dietary else [])]

    # Keyword check
    wants_vegan = "vegan" in p or "vegan" in dietary_filter
    wants_spicy = any(w in p for w in ["spicy", "hot", "tikka", "chilli"])
    wants_healthy = any(w in p for w in ["healthy", "protein", "clean", "diet"])
    wants_italian = any(w in p for w in ["pizza", "pasta", "italian"])
    wants_indian = any(w in p for w in ["paneer", "naan", "dal", "curry", "indian", "roti"])
    no_dairy = "dairy" in p and ("no" in p or "without" in p or "free" in p) or "dairy" in dietary_filter

    scored_dishes: List[Dict[str, Any]] = []

    for dish in CATALOG_ITEMS:
        score = 0.0
        reasons = []

        # Budget check
        if max_budget and dish["price"] > max_budget:
            continue

        # Dairy allergen exclusion
        if no_dairy and "Dairy" in dish["allergens"]:
            continue

        # Vegan filter
        if wants_vegan and not dish["is_vegan"]:
            continue

        # Cuisine & flavor relevance
        if wants_indian and dish["cuisine"] == "North Indian":
            score += 3.0
            reasons.append("matches traditional rich Indian spice profiles")
        if wants_italian and dish["cuisine"] == "Italian":
            score += 3.0
            reasons.append("authentic wood-fired Italian flavor")
        if wants_spicy and ("Spicy" in dish.get("tags", []) or "Masala" in dish["name"] or "Curry" in dish["name"]):
            score += 2.5
            reasons.append("delivers a bold spicy kick")
        if wants_healthy and ("Healthy" in dish.get("tags", []) or dish["calories"] <= 400):
            score += 2.5
            reasons.append("high protein and nutrient-rich profile")

        # General quality score
        score += (dish["rating"] - 4.0) * 2.0

        if not reasons:
            reasons.append(f"high customer favorite ({dish['rating']}★) with balanced gourmet flavors")

        match_reason = f"Perfect match: {', '.join(reasons)}."
        scored_dishes.append({
            "dish": dish,
            "score": score,
            "match_reason": match_reason
        })

    # Sort by score descending
    scored_dishes.sort(key=lambda x: x["score"], reverse=True)
    top_picks = scored_dishes[:3] if scored_dishes else [{"dish": CATALOG_ITEMS[0], "match_reason": "Chef's top recommendation"}]

    recommended: List[RecommendedDish] = []
    for item in top_picks:
        d = item["dish"]
        recommended.append(
            RecommendedDish(
                id=d["id"],
                name=d["name"],
                cuisine=d["cuisine"],
                price=float(d["price"]),
                rating=float(d["rating"]),
                calories=int(d["calories"]),
                match_reason=item["match_reason"],
                is_veg=bool(d["is_veg"]),
                allergens=d["allergens"]
            )
        )

    dish_names = ", ".join([r.name for r in recommended[:2]])
    reply = f"I've tailored a {mood.lower()} culinary selection for you! Based on your craving, I highly recommend starting with {dish_names}."

    followups = [
        "Would you like me to add these to your smart cart with complementary drink pairings?",
        "Want to explore table booking options for dine-in tonight instead?",
        "Would you like lower calorie or gluten-free alternatives?"
    ]

    return ConciergeResponse(
        reply=reply,
        intent=intent,
        mood_extracted=mood,
        recommended_dishes=recommended,
        suggested_followups=followups
    )
